"""Voice notes summary agent using Google ADK."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, FeatureMap
from src.agents.tools.voice_notes_tool import VoiceNotesTool
from google.adk.tools import FunctionTool
import opik


class VoiceNotesSummaryInput(BaseModel):
    """Input for generating a summary from voice notes."""
    user_id: str = Field(description="The user id to fetch the voice notes for.")
    limit: int = Field(description="The number of voice notes to fetch. Default is 10.")


class VoiceNotesSummaryOutput(BaseModel):
    """Output for generating a summary from voice notes."""
    summary: str = Field(description="The summary of the voice notes.")


class VoiceNotesSummaryAgent(BaseAgent):
    """Agent for generating a summary from voice notes."""

    def __init__(self):
        """Initialize the voice notes summary agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=VoiceNotesSummaryInput,
            output_schema=VoiceNotesSummaryOutput
        )

    @opik.track
    def get_limit(self, features: List[FeatureMap]) -> int:
        """Get the limit from the features."""
        limit = 10
        if features:
            for feature_map in features:
                if feature_map.feature_name == "limit":
                    limit = feature_map.feature_value
        return limit

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with limit from features."""
        limit = self.get_limit(request.features)
        return VoiceNotesSummaryInput(
            user_id=request.user_id,
            limit=limit,
        )

    # Tools are now configured via YAML (`tools` section in voice_notes_summary_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().

