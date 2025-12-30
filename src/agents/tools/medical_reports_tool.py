"""Medical reports fetching tool for health assistant agent."""

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


class MedicalReportsTool(BaseTool):
    """Tool for fetching medical reports from the backend API (past 30 days only)."""
    
    def __init__(self):
        super().__init__(
            name="fetch_medical_reports_tool",
            description="Fetches medical report summaries (AI-generated insights) for a user from the past 30 days. Returns summaries, key findings, and recommendations - NOT the raw PDF files. Use this when the user asks about their medical reports, lab results, test results, or uploaded medical documents."
        )
        # Get backend URL from environment variable
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        if not self.backend_url.endswith("/"):
            self.backend_url = self.backend_url.rstrip("/")
        # Get AI backend communication key for authentication
        self.ai_backend_communication_key = os.getenv("AI_BACKEND_COMMUNICATION_KEY", "")
    
    @opik.track(name="medical_reports_tool_run", tags=["medical_reports_tool"])
    def run(self, input: str) -> str:
        """Run the medical reports tool with the given input.
        
        Args:
            input: JSON string containing user_id and optionally limit (default: 10)
            Format: {"user_id": "user-123", "limit": 10}
            
        Returns:
            JSON string containing the medical reports (past 30 days only)
        """
        try:
            # Parse the input
            params = json.loads(input) if isinstance(input, str) else input
            user_id = params.get("user_id")
            limit = params.get("limit", 10)
            
            if not user_id:
                return json.dumps({
                    "error": "user_id is required",
                    "format": {"user_id": "string", "limit": "integer (optional, default: 10)"}
                })
            
            logger.info(f"Fetching medical reports for user: {user_id}, limit: {limit}")
            print(f"🔧 MEDICAL REPORTS TOOL: Fetching reports for user: {user_id} (past 30 days)")
            
            # Calculate date 30 days ago
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            start_date = thirty_days_ago.isoformat() + "Z"
            
            # Call the backend API with date filter
            endpoint = f"{self.backend_url}/api/medical-reports/users/{user_id}/recent"
            params_query = {
                "limit": limit,
                "start_date": start_date
            }
            
            # Prepare headers with AI backend communication key for authentication
            headers = {}
            if self.ai_backend_communication_key:
                headers["X-AI-Service-Key"] = self.ai_backend_communication_key
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(endpoint, params=params_query, headers=headers)
                
                if response.status_code == 200:
                    reports = response.json()
                    logger.info(f"Successfully fetched {len(reports)} medical reports")
                    
                    # Extract only the relevant summary data (ai_insights) for the agent
                    # Filter out raw file data (blob_url, blob_name) to keep response focused
                    formatted_reports = []
                    for report in reports:
                        report_data = {
                            "report_id": report.get("report_id"),
                            "file_name": report.get("file_name"),
                            "upload_date": report.get("upload_date"),
                            "status": report.get("status"),
                            "ai_insights": report.get("ai_insights")  # This contains summary, key_findings, recommendations
                        }
                        formatted_reports.append(report_data)
                    
                    # Format the response for the agent
                    formatted_response = {
                        "success": True,
                        "count": len(formatted_reports),
                        "date_range": f"Past 30 days (from {start_date})",
                        "note": "These are AI-generated summaries and insights, not raw PDF files",
                        "reports": formatted_reports
                    }
                    return json.dumps(formatted_response, default=str)
                elif response.status_code == 404:
                    logger.warning(f"No medical reports found for user: {user_id}")
                    return json.dumps({
                        "success": True,
                        "count": 0,
                        "date_range": f"Past 30 days (from {start_date})",
                        "reports": [],
                        "message": "No medical reports found for this user in the past 30 days"
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
            error_msg = f"Unexpected error in medical reports tool: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    @opik.track(name="medical_reports_tool_to_function_tool", tags=["medical_reports_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        # Use the base class implementation which properly handles function metadata
        return super().to_function_tool()

