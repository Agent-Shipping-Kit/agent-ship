"""Action items fetching tool for health assistant agent."""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import opik
from src.agents.tools.base_tool import BaseTool
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


class ActionItemsTool(BaseTool):
    """Tool for fetching action items for a user from the backend API."""
    
    def __init__(self):
        super().__init__(
            name="fetch_action_items_tool",
            description="Fetches action items, tasks, or to-dos for a user from the backend. REQUIRED when user asks: 'What are my action items?', 'Show me my tasks', 'What do I need to do?', 'What are my pending items?', 'Show me completed tasks', or any question about their task list. Input: JSON with 'user_id' (required) and optionally 'status' (TODO/IN_PROGRESS/DONE/SKIPPED), 'limit' (default: 20), 'offset' (default: 0). Returns list of action items with details."
        )
        # Get backend URL from environment variable
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        if not self.backend_url.endswith("/"):
            self.backend_url = self.backend_url.rstrip("/")
        # Get AI backend communication key for authentication
        self.ai_backend_communication_key = os.getenv("AI_BACKEND_COMMUNICATION_KEY", "")
    
    @opik.track(name="action_items_tool_run", tags=["action_items_tool"])
    def run(self, input: str) -> str:
        """Run the action items tool with the given input.
        
        Args:
            input: JSON string containing user_id and optionally status, limit, offset
            Format: {"user_id": "user-123", "status": "TODO" (optional), "limit": 20 (optional), "offset": 0 (optional)}
            
        Returns:
            JSON string containing the action items
        """
        try:
            # Parse the input
            params = json.loads(input) if isinstance(input, str) else input
            user_id = params.get("user_id")
            status = params.get("status")  # Optional: TODO, IN_PROGRESS, DONE, SKIPPED
            limit = params.get("limit", 20)
            offset = params.get("offset", 0)
            
            if not user_id:
                return json.dumps({
                    "error": "user_id is required",
                    "format": {
                        "user_id": "string (required)",
                        "status": "string (optional: TODO, IN_PROGRESS, DONE, SKIPPED)",
                        "limit": "integer (optional, default: 20, max: 100)",
                        "offset": "integer (optional, default: 0)"
                    }
                })
            
            logger.info(f"Fetching action items for user: {user_id}, status: {status}, limit: {limit}, offset: {offset}")
            print(f"🔧 ACTION ITEMS TOOL: Fetching action items for user: {user_id}")
            
            # Call the backend API
            endpoint = f"{self.backend_url}/api/action-items/users/{user_id}"
            params_query = {
                "limit": limit,
                "offset": offset
            }
            if status:
                params_query["status"] = status
            
            # Prepare headers with AI backend communication key for authentication
            headers = {}
            if self.ai_backend_communication_key:
                headers["X-AI-Service-Key"] = self.ai_backend_communication_key
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(endpoint, params=params_query, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    total = data.get("total", 0)
                    has_more = data.get("has_more", False)
                    
                    logger.info(f"Successfully fetched {len(items)} action items (total: {total})")
                    
                    # Format the response for the agent
                    formatted_response = {
                        "success": True,
                        "count": len(items),
                        "total": total,
                        "has_more": has_more,
                        "status_filter": status if status else "all",
                        "action_items": items
                    }
                    return json.dumps(formatted_response, default=str)
                elif response.status_code == 404:
                    logger.warning(f"No action items found for user: {user_id}")
                    return json.dumps({
                        "success": True,
                        "count": 0,
                        "total": 0,
                        "has_more": False,
                        "status_filter": status if status else "all",
                        "action_items": [],
                        "message": "No action items found for this user"
                    })
                else:
                    error_text = response.text[:500] if response.text else "No error message"
                    error_msg = f"Backend API error: {response.status_code} - {error_text}"
                    logger.error(f"Action items tool error: {error_msg}")
                    logger.error(f"Request URL: {endpoint}")
                    logger.error(f"Request params: {params_query}")
                    logger.error(f"Request headers: {headers}")
                    return json.dumps({
                        "error": error_msg,
                        "status_code": response.status_code,
                        "details": "Failed to fetch action items. Please check backend logs for more information."
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
            error_msg = f"Unexpected error in action items tool: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @opik.track(name="action_items_tool_to_function_tool", tags=["action_items_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        # Use the base class implementation which properly handles function metadata
        return super().to_function_tool()

