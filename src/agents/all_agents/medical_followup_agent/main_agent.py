"""Medical conversation followup generation agent using Google ADK."""

from typing import List, Dict
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, FeatureMap
from google.adk.tools import FunctionTool
import opik


class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label, e.g., Patient or Doctor")
    text: str = Field(description="What the speaker said")


class FollowupQuestionsInput(BaseModel):
    """Input for followup questions generation."""
    conversation_turns: List[ConversationTurn] = Field(description="The medical conversation to generate followup questions for.")
    max_followups: int = Field(description="The maximum number of followup questions to generate.", default=5)


class FollowupQuestionsOutput(BaseModel):
    """Output for followup questions generation."""
    followup_questions: List[str] = Field(description="The list of followup questions generated.")
    count: int = Field(description="The number of followup questions generated.")


class MedicalFollowupAgent(BaseAgent):
    """Agent for generating medical conversation followup questions."""

    def __init__(self):
        """Initialize the medical followup agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=FollowupQuestionsInput,
            output_schema=FollowupQuestionsOutput
        )

    @opik.track
    def get_num_followups(self, features: List[FeatureMap]) -> int:
        """Get the number of followups from the features."""
        max_followups = 3
        if features:
            for feature_map in features:
                if feature_map.feature_name == "max_followups":
                    max_followups = feature_map.feature_value
        return max_followups

    def parse_conversation_turns(self, query: List[Dict]) -> List[ConversationTurn]:
        """Parse the query into ConversationTurn objects."""
        try:
            return [ConversationTurn(**turn) for turn in query]
        except (TypeError, ValueError, KeyError):
            # Fallback: treat as a single conversation turn
            return [ConversationTurn(speaker="Patient", text=str(query))]

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with features processing."""
        max_followups = self.get_num_followups(request.features)
        conversation_turns = self.parse_conversation_turns(request.query if isinstance(request.query, list) else [])
        
        return FollowupQuestionsInput(
            conversation_turns=conversation_turns,
            max_followups=max_followups
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list
