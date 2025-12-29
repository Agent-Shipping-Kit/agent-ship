"""
Debug API Router for the Debug UI.

Provides endpoints for:
- Listing available agents and their schemas
- Streaming chat responses
- Feedback tracking
- Session management
- Log capture for debugging
"""

import io
import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.agents.registry import list_agents, get_agent_instance, get_agent_class
from src.models.base_models import AgentChatRequest, FeatureMap

logger = logging.getLogger(__name__)
router = APIRouter()


# ============== Log Capture ==============

class LogCaptureHandler(logging.Handler):
    """Captures logs during agent execution for debug display."""
    
    def __init__(self):
        super().__init__()
        self.logs: List[Dict[str, Any]] = []
        self.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(message)s', datefmt='%H:%M:%S'))
    
    def emit(self, record: logging.LogRecord):
        try:
            # Categorize logs
            category = "info"
            msg = record.getMessage()
            
            # Detect tool calls
            if any(kw in msg.lower() for kw in ['tool', 'function', 'calling', 'executing']):
                category = "tool"
            elif any(kw in msg.lower() for kw in ['llm', 'model', 'gemini', 'gpt', 'claude', 'response']):
                category = "llm"
            elif record.levelno >= logging.WARNING:
                category = "warning"
            elif record.levelno >= logging.ERROR:
                category = "error"
            
            self.logs.append({
                "timestamp": self.format(record).split(' | ')[0],
                "logger": record.name,
                "level": record.levelname,
                "message": msg,
                "category": category
            })
        except Exception:
            pass
    
    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs
    
    def clear(self):
        self.logs = []


@contextmanager
def capture_logs():
    """Context manager to capture logs during agent execution."""
    handler = LogCaptureHandler()
    handler.setLevel(logging.DEBUG)
    
    # Add handler to root logger and relevant agent loggers
    root_logger = logging.getLogger()
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    
    # Also capture google.adk logs for tool calls
    adk_logger = logging.getLogger('google.adk')
    adk_logger.addHandler(handler)
    
    try:
        yield handler
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(original_level)
        adk_logger.removeHandler(handler)


# ============== Models ==============

class AgentInfo(BaseModel):
    """Basic agent information."""
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    """A chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    feedback: Optional[str] = None  # "up", "down", or None


class DebugChatRequest(BaseModel):
    """Request for debug chat."""
    agent_name: str
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    """Request to save feedback."""
    session_id: str
    message_index: int
    feedback: str  # "up" or "down"
    agent_name: str
    user_message: str
    assistant_message: str


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str
    agent_name: str
    created_at: str
    message_count: int


# ============== In-Memory Storage ==============
# For tracking feedback and sessions in debug mode

_feedback_store: List[Dict[str, Any]] = []
_sessions: Dict[str, SessionInfo] = {}


# ============== Helper Functions ==============

def _find_schema_classes_from_module(agent_class) -> tuple:
    """Find Input/Output schema classes from the agent's module."""
    import inspect
    
    module = inspect.getmodule(agent_class)
    input_schema = None
    output_schema = None
    
    if module:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, 'model_json_schema'):
                if name.endswith("Input"):
                    input_schema = obj
                elif name.endswith("Output"):
                    output_schema = obj
    
    return input_schema, output_schema


def _get_agent_schema(agent_name: str) -> Dict[str, Any]:
    """Get input/output schema for an agent without instantiating it."""
    try:
        agent_class = get_agent_class(agent_name)
        input_schema_class, output_schema_class = _find_schema_classes_from_module(agent_class)
        
        result = {"input": {}, "output": {}}
        
        if input_schema_class:
            schema = input_schema_class.model_json_schema()
            result["input"] = {
                "title": schema.get("title", "Input"),
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        
        if output_schema_class:
            schema = output_schema_class.model_json_schema()
            result["output"] = {
                "title": schema.get("title", "Output"),
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        
        return result
    except Exception as e:
        logger.warning(f"Could not get schema for {agent_name}: {e}")
        return {"input": {}, "output": {}}


# ============== Endpoints ==============

@router.get("/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get list of all available agents with their schemas."""
    try:
        agent_names = list_agents()
        agents = []
        
        for name in agent_names:
            schema = _get_agent_schema(name)
            agents.append(AgentInfo(
                name=name,
                description=f"Agent: {name}",
                input_schema=schema.get("input"),
                output_schema=schema.get("output")
            ))
        
        return agents
    except Exception as e:
        logger.exception("Failed to list agents")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/schema")
async def get_agent_schema(agent_name: str):
    """Get detailed schema for a specific agent."""
    try:
        schema = _get_agent_schema(agent_name)
        return schema
    except Exception as e:
        logger.exception(f"Failed to get schema for {agent_name}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def debug_chat(request: DebugChatRequest):
    """
    Non-streaming chat endpoint for debug UI.
    Returns the full response at once with captured logs.
    """
    captured_logs = []
    
    try:
        # Generate IDs if not provided
        session_id = request.session_id or f"debug_{uuid.uuid4().hex[:12]}"
        user_id = request.user_id or f"debug_user_{uuid.uuid4().hex[:8]}"
        
        # Build query from features (form data) or message
        if request.features:
            query = dict(request.features)
            query['session_id'] = session_id
            query['user_id'] = user_id
        else:
            query = {"text": request.message}
        
        # Create chat request
        chat_request = AgentChatRequest(
            agent_name=request.agent_name,
            user_id=user_id,
            session_id=session_id,
            sender="USER",
            query=query,
            features=[]
        )
        
        logger.info(f"Debug chat request: agent={request.agent_name}")
        
        # Capture logs during agent execution
        with capture_logs() as log_handler:
            # Get agent and chat
            agent = get_agent_instance(request.agent_name)
            result = await agent.chat(chat_request)
            captured_logs = log_handler.get_logs()
        
        # Extract response text - handle various response formats
        response_text = ""
        if hasattr(result, 'agent_response'):
            resp = result.agent_response
            
            # Handle Pydantic models
            if hasattr(resp, 'model_dump'):
                resp = resp.model_dump()
            elif hasattr(resp, 'dict'):
                resp = resp.dict()
            
            if isinstance(resp, dict):
                response_text = (
                    resp.get('response') or 
                    resp.get('text') or 
                    resp.get('answer') or 
                    resp.get('translated_text') or
                    resp.get('summary') or
                    resp.get('message') or
                    resp.get('flight_plan') or
                    resp.get('hotel_plan') or
                    json.dumps(resp, indent=2)
                )
            elif isinstance(resp, str):
                response_text = resp
            else:
                try:
                    if hasattr(resp, '__dict__'):
                        resp_dict = {k: v for k, v in resp.__dict__.items() if not k.startswith('_')}
                        response_text = json.dumps(resp_dict, indent=2, default=str)
                    else:
                        response_text = str(resp)
                except:
                    response_text = str(resp)
        
        # Track session
        if session_id not in _sessions:
            _sessions[session_id] = SessionInfo(
                session_id=session_id,
                agent_name=request.agent_name,
                created_at=datetime.now().isoformat(),
                message_count=0
            )
        _sessions[session_id].message_count += 1
        
        # Filter logs to show only interesting ones
        filtered_logs = [
            log for log in captured_logs 
            if log['category'] in ['tool', 'llm', 'warning', 'error'] 
            or 'agent' in log['logger'].lower()
            or 'adk' in log['logger'].lower()
        ]
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "response": response_text,
            "success": True,
            "logs": filtered_logs[-50:]  # Last 50 relevant logs
        }
        
    except Exception as e:
        logger.exception("Debug chat failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def debug_chat_stream(request: DebugChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.
    Streams tokens as they're generated.
    """
    async def event_generator():
        try:
            session_id = request.session_id or f"debug_{uuid.uuid4().hex[:12]}"
            user_id = request.user_id or f"debug_user_{uuid.uuid4().hex[:8]}"
            
            # Send session info first
            yield {
                "event": "session",
                "data": json.dumps({"session_id": session_id, "user_id": user_id})
            }
            
            # Build features
            features = []
            if request.features:
                for key, value in request.features.items():
                    features.append(FeatureMap(feature_name=key, feature_value=value))
            
            # Create request
            chat_request = AgentChatRequest(
                agent_name=request.agent_name,
                user_id=user_id,
                session_id=session_id,
                sender="USER",
                query={"text": request.message},
                features=features
            )
            
            # Get agent and chat
            agent = get_agent_instance(request.agent_name)
            result = await agent.chat(chat_request)
            
            # Extract and stream response
            response_text = ""
            if hasattr(result, 'agent_response'):
                if isinstance(result.agent_response, dict):
                    response_text = result.agent_response.get('response',
                                   result.agent_response.get('text', str(result.agent_response)))
                else:
                    response_text = str(result.agent_response)
            
            # Simulate streaming by chunking the response
            # In a real implementation, you'd stream from the LLM directly
            chunk_size = 20
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i + chunk_size]
                yield {
                    "event": "token",
                    "data": json.dumps({"token": chunk})
                }
            
            yield {
                "event": "done",
                "data": json.dumps({"complete": True})
            }
            
        except Exception as e:
            logger.exception("Streaming chat failed")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@router.post("/feedback")
async def save_feedback(request: FeedbackRequest):
    """Save feedback for a message."""
    try:
        feedback_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "session_id": request.session_id,
            "message_index": request.message_index,
            "feedback": request.feedback,
            "agent_name": request.agent_name,
            "user_message": request.user_message,
            "assistant_message": request.assistant_message
        }
        
        _feedback_store.append(feedback_entry)
        logger.info(f"Feedback saved: {request.feedback} for {request.agent_name}")
        
        return {"success": True, "id": feedback_entry["id"]}
        
    except Exception as e:
        logger.exception("Failed to save feedback")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback")
async def get_feedback():
    """Get all feedback (for debugging/export)."""
    return _feedback_store


@router.get("/sessions")
async def get_sessions():
    """Get all debug sessions."""
    return list(_sessions.values())


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a debug session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/sessions")
async def create_session(agent_name: str):
    """Create a new debug session."""
    session_id = f"debug_{uuid.uuid4().hex[:12]}"
    _sessions[session_id] = SessionInfo(
        session_id=session_id,
        agent_name=agent_name,
        created_at=datetime.now().isoformat(),
        message_count=0
    )
    return _sessions[session_id]

