"""Medical conversation insights generation agent using Google ADK."""

from typing import List, Dict
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, FeatureMap
from google.adk.tools import FunctionTool
import opik


class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label (0, 1, 2, etc.)")
    text: str = Field(description="What the speaker said")


class ConversationInsightsInput(BaseModel):
    """Input for conversation insights generation."""
    conversation_turns: List[ConversationTurn] = Field(description="The medical conversation to generate insights for.")
    summary_length: int = Field(description="The length of the summary to generate.", default=200)
    num_of_key_findings: int = Field(description="The number of key findings to generate.", default=5)
    num_of_action_items: int = Field(description="The number of action items to generate (should be 3-4, focusing on top priority patient actions).", default=3)


class ConversationInsightsOutput(BaseModel):
    """Output for conversation insights generation."""
    summary: str = Field(description="The summary of the conversation.")
    key_findings: List[str] = Field(description="The key findings of the conversation.")
    action_items: List[str] = Field(description="The action items for the conversation.")


class MedicalConversationInsightsAgent(BaseAgent):
    """Agent for generating medical conversation insights including summary, key findings, and action items."""

    def __init__(self):
        """Initialize the medical conversation insights agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=ConversationInsightsInput,
            output_schema=ConversationInsightsOutput
        )

    @opik.track
    def get_summary_length(self, features: List[FeatureMap]) -> int:
        """Get the length of the summary from the features."""
        summary_length = 200
        if features:
            for feature_map in features:
                if feature_map.feature_name == "summary_length":
                    summary_length = feature_map.feature_value
        return summary_length

    @opik.track
    def get_num_of_key_findings(self, features: List[FeatureMap]) -> int:
        """Get the number of key findings from the features."""
        num_of_key_findings = 5
        if features:
            for feature_map in features:
                if feature_map.feature_name == "num_of_key_findings":
                    num_of_key_findings = feature_map.feature_value
        return num_of_key_findings

    @opik.track 
    def get_num_of_action_items(self, features: List[FeatureMap]) -> int:
        """Get the number of action items from the features."""
        num_of_action_items = 3  # Default to 3, max 4 for focused, high-quality action items
        if features:
            for feature_map in features:
                if feature_map.feature_name == "num_of_action_items":
                    num_of_action_items = min(feature_map.feature_value, 4)  # Cap at 4
        return num_of_action_items

    def parse_conversation_turns(self, query: List[Dict]) -> List[ConversationTurn]:
        """Parse the query into ConversationTurn objects."""
        try:
            return [ConversationTurn(**turn) for turn in query]
        except (TypeError, ValueError, KeyError):
            # Fallback: treat as a single conversation turn
            return [ConversationTurn(speaker="Patient", text=str(query))]

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with features processing."""
        summary_length = self.get_summary_length(request.features)
        num_of_key_findings = self.get_num_of_key_findings(request.features)
        num_of_action_items = self.get_num_of_action_items(request.features)
        conversation_turns = self.parse_conversation_turns(request.query if isinstance(request.query, list) else [])
        
        return ConversationInsightsInput(
            conversation_turns=conversation_turns,
            summary_length=summary_length,
            num_of_key_findings=num_of_key_findings,
            num_of_action_items=num_of_action_items
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list
