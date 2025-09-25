"""Models for the agents."""
from pydantic import BaseModel, Field
from typing import List, Optional, Any

# Base input/output models
class TextInput(BaseModel):
    """Simple text input."""
    text: str

class TextOutput(BaseModel):
    """Simple text output."""
    response: str

class FeatureMap(BaseModel):
    """Feature map for the agent."""
    feature_name: str = Field(description="Feature name")
    feature_value: Any = Field(description="Feature value")

class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label, e.g., Patient or Doctor")
    text: str = Field(description="What the speaker said")

class ChatInput(BaseModel):
    """List of conversation turns."""
    conversation_turns: List[ConversationTurn] = Field(description="List of conversation turns")
    features: Optional[List[FeatureMap]] = Field(description="List of features")

