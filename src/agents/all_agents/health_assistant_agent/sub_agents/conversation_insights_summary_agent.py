"""Medical conversation insights generation agent using Google ADK."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, FeatureMap
from src.agents.tools.conversation_insights_tool import ConversationInsightsTool
from google.adk.tools import FunctionTool
import opik


class ConversationInsightsSummaryInput(BaseModel):
    """Input for generating a summary from conversation insights."""
    user_id: str = Field(description="The user id to fetch the conversation insights for.")
    limit: int = Field(description="The number of conversation insights to fetch. Default is 5.")


class ConversationInsightsSummaryOutput(BaseModel):
    """Output for generating a summary from conversation insights."""
    summary: str = Field(description="The summary of the conversation insights.")


class ConversationInsightsSummaryAgent(BaseAgent):
    """Agent for generating a summary from conversation insights."""

    def __init__(self):
        """Initialize the conversation insights summary agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=ConversationInsightsSummaryInput,
            output_schema=ConversationInsightsSummaryOutput
        )

    @opik.track
    def get_limit(self, features: List[FeatureMap]) -> int:
        """Get the limit from the features."""
        limit = 5
        if features:
            for feature_map in features:
                if feature_map.feature_name == "limit":
                    limit = feature_map.feature_value
        return limit

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with limit from features."""
        limit = self.get_limit(request.features)
        return ConversationInsightsSummaryInput(
            user_id=request.user_id,
            limit=limit
        )

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        insights_tool = ConversationInsightsTool()
        return [FunctionTool(insights_tool.run)]
    
    # No need to override chat() - base class handles it!
    # No need to override _create_sub_agents() - defaults to empty list
