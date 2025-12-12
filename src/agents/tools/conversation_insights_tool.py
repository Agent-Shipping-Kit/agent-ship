"""Conversation insights fetching tool for health assistant agent."""

import json
import logging
import os
from typing import Dict, Any, List, Optional
import httpx
import opik
from src.agents.tools.base_tool import BaseTool
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


class ConversationInsightsTool(BaseTool):
    """Tool for fetching conversation insights from the backend API."""
    
    def __init__(self):
        super().__init__(
            name="fetch_conversation_insights_tool",
            description="Fetches the latest top 5 conversation insights for a user from the backend. Use this when the user asks about their past conversations, health summaries, or key findings from their medical consultations."
        )
        # Get backend URL from environment variable
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        if not self.backend_url.endswith("/"):
            self.backend_url = self.backend_url.rstrip("/")
        # Get AI backend communication key for authentication
        self.ai_backend_communication_key = os.getenv("AI_BACKEND_COMMUNICATION_KEY", "")
    
    @opik.track(name="conversation_insights_tool_run", tags=["conversation_insights_tool"])
    def run(self, input: str) -> str:
        """Run the conversation insights tool with the given input.
        
        Args:
            input: JSON string containing user_id and optionally limit (default: 5)
            Format: {"user_id": "user-123", "limit": 5}
            
        Returns:
            JSON string containing the conversation insights
        """
        try:
            # Parse the input
            params = json.loads(input) if isinstance(input, str) else input
            user_id = params.get("user_id")
            limit = params.get("limit", 5)
            
            if not user_id:
                return json.dumps({
                    "error": "user_id is required",
                    "format": {"user_id": "string", "limit": "integer (optional, default: 5)"}
                })
            
            logger.info(f"Fetching conversation insights for user: {user_id}, limit: {limit}")
            print(f"🔧 CONVERSATION INSIGHTS TOOL: Fetching insights for user: {user_id}")
            
            # Call the backend API
            endpoint = f"{self.backend_url}/api/insights/users/{user_id}/latest"
            params_query = {"limit": limit}
            
            # Prepare headers with AI backend communication key for authentication
            headers = {}
            if self.ai_backend_communication_key:
                headers["X-AI-Service-Key"] = self.ai_backend_communication_key
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(endpoint, params=params_query, headers=headers)
                
                if response.status_code == 200:
                    insights = response.json()
                    logger.info(f"Successfully fetched {len(insights)} conversation insights")
                    
                    # Format the response for the agent
                    formatted_response = {
                        "success": True,
                        "count": len(insights),
                        "insights": insights
                    }
                    return json.dumps(formatted_response, default=str)
                elif response.status_code == 404:
                    logger.warning(f"No conversation insights found for user: {user_id}")
                    return json.dumps({
                        "success": True,
                        "count": 0,
                        "insights": [],
                        "message": "No conversation insights found for this user"
                    })
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
            error_msg = f"Unexpected error in conversation insights tool: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @opik.track(name="conversation_insights_tool_to_function_tool", tags=["conversation_insights_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        return FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            function=self.run
        )

