"""Medical conversation insights generation agent using Google ADK."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest
from google.adk.tools import FunctionTool, AgentTool
from src.agents.all_agents.health_assistant_agent.sub_agents.conversation_insights_summary_agent import ConversationInsightsSummaryAgent


class HealthAssistantInput(BaseModel):
    """Input for answering questions about user's health data, conversations, action items, etc."""
    message: str = Field(description="The message to answer.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class HealthAssistantOutput(BaseModel):
    """Output for answering questions about user's health data, conversations, action items, etc."""
    answer: str = Field(description="The answer to the question.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class HealthAssistantAgent(BaseAgent):
    """Agent for answering questions about user's health data, conversations, action items, etc."""

    def __init__(self):
        """Initialize the health assistant agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=HealthAssistantInput,
            output_schema=HealthAssistantOutput
        )

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with message, session_id, and user_id."""
        return HealthAssistantInput(
            message=request.query if isinstance(request.query, str) else str(request.query),
            session_id=request.session_id,
            user_id=request.user_id,
        )

    # Tools are now configured via YAML (`tools` section in main_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().
