"""Models for the agents."""
from pydantic import BaseModel, Field

# Base input/output models
class TextInput(BaseModel):
    """Simple text input."""
    text: str

class TextOutput(BaseModel):
    """Simple text output."""
    response: str

class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label, e.g., Patient or Doctor")
    text: str = Field(description="What the speaker said")