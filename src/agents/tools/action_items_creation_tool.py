"""Action items creation tool for health assistant agent."""

import json
import logging
import os
from typing import Dict, Any
import httpx
import opik
from src.agents.tools.base_tool import BaseTool
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


class ActionItemsCreationTool(BaseTool):
    """Tool for creating action items for a user via the backend API."""
    
    def __init__(self):
        super().__init__(
            name="create_action_item_tool",
            description="Creates a new action item for a user. Use this when the user wants to create a new action item, task, or reminder. The action item should be specific, actionable, and patient-focused."
        )
        # Get backend URL from environment variable
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        if not self.backend_url.endswith("/"):
            self.backend_url = self.backend_url.rstrip("/")
        # Get AI backend communication key for authentication
        self.ai_backend_communication_key = os.getenv("AI_BACKEND_COMMUNICATION_KEY", "")
    
    @opik.track(name="action_items_creation_tool_run", tags=["action_items_creation_tool"])
    def run(self, input: str) -> str:
        """Run the action items creation tool with the given input.
        
        Args:
            input: JSON string containing user_id, action_item, source_id, source_type, and optionally status
            Format: {
                "user_id": "user-123",
                "action_item": "Schedule a follow-up appointment in 2 weeks",
                "source_id": "conversation-456" or "manual",
                "source_type": "CONVERSATION" or "MANUAL",
                "status": "TODO" (optional, default: TODO)
            }
            
        Returns:
            JSON string containing the created action item
        """
        try:
            # Parse the input
            params = json.loads(input) if isinstance(input, str) else input
            user_id = params.get("user_id")
            action_item_text = params.get("action_item")
            source_id = params.get("source_id", "manual")
            source_type = params.get("source_type", "GENERAL")
            status = params.get("status", "TODO")
            
            if not user_id:
                return json.dumps({
                    "error": "user_id is required",
                    "format": {
                        "user_id": "string (required)",
                        "action_item": "string (required)",
                        "source_id": "string (optional, default: 'manual')",
                        "source_type": "string (optional, default: 'GENERAL', options: CONVERSATION, MEDICAL_REPORT, JOURNAL, GENERAL)",
                        "status": "string (optional, default: 'TODO', options: TODO, IN_PROGRESS, DONE, SKIPPED)"
                    }
                })
            
            if not action_item_text:
                return json.dumps({
                    "error": "action_item is required",
                    "format": {
                        "user_id": "string (required)",
                        "action_item": "string (required)",
                        "source_id": "string (optional, default: 'manual')",
                        "source_type": "string (optional, default: 'GENERAL')",
                        "status": "string (optional, default: 'TODO')"
                    }
                })
            
            logger.info(f"Creating action item for user: {user_id}, text: {action_item_text[:50]}...")
            print(f"🔧 ACTION ITEMS CREATION TOOL: Creating action item for user: {user_id}")
            
            # Call the backend API
            endpoint = f"{self.backend_url}/api/action-items"
            payload = {
                "user_id": user_id,  # Required for AI service authentication
                "action_item": action_item_text,
                "source_id": source_id,
                "source_type": source_type,
                "status": status
            }
            
            # Prepare headers with AI backend communication key for authentication
            headers = {
                "Content-Type": "application/json"
            }
            if self.ai_backend_communication_key:
                headers["X-AI-Service-Key"] = self.ai_backend_communication_key
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                
                if response.status_code == 200 or response.status_code == 201:
                    created_item = response.json()
                    logger.info(f"Successfully created action item: {created_item.get('action_item_id')}")
                    
                    # Format the response for the agent
                    formatted_response = {
                        "success": True,
                        "message": "Action item created successfully",
                        "action_item": created_item
                    }
                    return json.dumps(formatted_response, default=str)
                else:
                    error_msg = f"Backend API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return json.dumps({
                        "error": error_msg,
                        "status_code": response.status_code
                    })
                    
        except httpx.TimeoutException:
            error_msg = "Request to backend API timed out"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except httpx.RequestError as e:
            error_msg = f"Error connecting to backend API: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON input: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"Unexpected error in action items creation tool: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @opik.track(name="action_items_creation_tool_to_function_tool", tags=["action_items_creation_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        return FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            function=self.run
        )

