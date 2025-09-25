from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from fastapi.encoders import jsonable_encoder
from src.agent_models.base_models import ChatInput
from src.agent_registry import discover_agents, get_agent_instance
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AgentChatRequest(BaseModel):
    agent_name: str
    user_id: str = None
    session_id: str = None
    chat_input: ChatInput

class AgentChatResponse(BaseModel):
    success: bool
    user_id: str
    session_id: str
    result: Any


@router.post("/chat")
async def chat(request: AgentChatRequest) -> AgentChatResponse:
    """
    Generic chat endpoint that routes to the requested agent using the registry.
    """
    try:
        logger.info(f"Chatting with agent: {request.agent_name}")

        # Get agent instance from registry (singleton)
        agent = get_agent_instance(request.agent_name)

        # Delegate chat to the agent implementation
        result = await agent.chat(user_id=request.user_id,
                                  session_id=request.session_id,
                                  input=request.chat_input)
        logger.info(f"Result from agent chat: {result}")

        # Let FastAPI handle proper serialization
        normalized = jsonable_encoder(result)

        return AgentChatResponse(
            success=True, user_id=request.user_id,
            session_id=request.session_id, result=normalized)
            
    except KeyError as e:
        logger.error(f"Agent not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Agent chat failed")
        raise HTTPException(status_code=500, detail=str(e))

