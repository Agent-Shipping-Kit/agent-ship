"""Action items creation agent for health assistant."""

import opik
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, FeatureMap
from typing import List

class ActionItemCreationInput(BaseModel):
    user_id: str = Field(description="The user id to create the action item for.")
    action_item_text: str = Field(description="The text of the action item to create. Should be specific, actionable, and patient-focused.")
    source_id: str = Field(description="The source ID for the action item (e.g., conversation_id, 'manual' for user-created items).")
    source_type: str = Field(description="The source type for the action item (e.g., 'CONVERSATION', 'GENERAL').", default="GENERAL")

class ActionItemCreationOutput(BaseModel):
    success: bool = Field(description="Whether the action item was created successfully.")
    message: str = Field(description="A message describing the result of the action item creation.")
    action_item_id: str = Field(description="The ID of the created action item, if successful.", default="")

class ActionItemsCreationAgent(BaseAgent):
    """Agent for creating action items for users."""
    
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=ActionItemCreationInput,
            output_schema=ActionItemCreationOutput
        )

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request."""
        # Parse the query to extract action item details
        # The query should be a dict or JSON string with action_item_text, source_id, and optionally source_type
        query = request.query
        
        if isinstance(query, str):
            import json
            try:
                query = json.loads(query)
            except json.JSONDecodeError:
                # If it's not JSON, treat it as the action item text
                query = {"action_item_text": query}
        
        if isinstance(query, dict):
            action_item_text = query.get("action_item_text", "")
            source_id = query.get("source_id", "manual")
            source_type = query.get("source_type", "GENERAL")
        else:
            # Fallback: treat query as action item text
            action_item_text = str(query) if query else ""
            source_id = "manual"
            source_type = "GENERAL"
        
        return ActionItemCreationInput(
            user_id=request.user_id,
            action_item_text=action_item_text,
            source_id=source_id,
            source_type=source_type
        )

