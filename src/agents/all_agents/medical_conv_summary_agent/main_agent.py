"""Medical conversation followup generation agent using Google ADK."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src.agents.configs.agent_config import AgentConfig
from src.agents.all_agents.base_agent import BaseAgent
from google.adk import Agent
from src.models.base_models import FeatureMap, AgentChatRequest, AgentChatResponse
import logging
import opik

logger = logging.getLogger(__name__)

class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label, e.g., Patient or Doctor")
    text: str = Field(description="What the speaker said")

class ConversationSummaryInput(BaseModel):
    """Input for conversation summary generation."""
    conversation_turns: List[ConversationTurn] = Field(description="The medical conversation to generate summary for.")
    summary_length: int = Field(description="The length of the summary to generate.", default=200)
    
class ConversationSummaryOutput(BaseModel):
    """Output for conversation summary generation."""
    summary: str = Field(description="The summary of the conversation.")
    key_findings: List[str] = Field(description="The key findings of the conversation.")
    action_items: List[str] = Field(description="The action items for the conversation.")

class MedicalConversationSummaryAgent(BaseAgent):
    """Agent for generating medical conversation summary."""

    def __init__(self):
        """Initialize the medical conversation summary agent."""
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/medical_conv_summary_agent/main_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=ConversationSummaryInput,
            output_schema=ConversationSummaryOutput
        )
        
        logger.info(f"Medical Followup Agent initialized: {self.agent_config}")

    @opik.track
    def get_summary_length(self, features: List[FeatureMap]) -> int:
        """Get the length of the summary from the features."""
        summary_length = 200

        if features:
            for feature_map in features:
                if feature_map.feature_name == "summary_length":
                    summary_length = feature_map.feature_value
        logger.debug(f"Summary length: {summary_length}")
        return summary_length

    def parse_conversation_turns(self, query: List[Dict]) -> List[ConversationTurn]:
        """Parse the query into ConversationTurn objects."""
        try:
            conversation_turns = [ConversationTurn(**turn) for turn in query]
            logger.debug(f"Conversation turns: {conversation_turns}")
            return conversation_turns
        except (TypeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse conversation query: {e}")
            # Fallback: treat as a single conversation turn
            conversation_turns = [ConversationTurn(speaker="Patient", text=str(query))]
            return conversation_turns
        except Exception as e:
            logger.error(f"Failed to parse conversation query: {e}")
            return []

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")
        summary_length = self.get_summary_length(request.features)
        conversation_turns = self.parse_conversation_turns(request.query)
        logger.debug(f"Conversation turns: {conversation_turns}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                ConversationSummaryInput(
                    conversation_turns=conversation_turns,
                    summary_length=summary_length
                )
            )

            logger.info(f"Result from conversation summary agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in conversation summary agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the medical conversation summary agent."""
        logger.info("Creating medical conversation summary sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = MedicalConversationSummaryAgent()
        
        # Generate a fresh session ID to avoid corrupted sessions
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}-fresh-{__import__('time').time()}".encode()).hexdigest()[:8]
        print(f"Generated fresh session ID: {session_id}")
        
        query = [
            {"speaker": "Patient", "text": "Patient: I have chest pain. Doctor: Can you describe it?"},
            {"speaker": "Doctor", "text": "Can you describe it?"},
            {"speaker": "Patient", "text": "It's a sharp, stabbing pain. It started after I lifted some heavy boxes at work."},
            {"speaker": "Doctor", "text": "Have you had any shortness of breath or difficulty breathing?"},
            {"speaker": "Patient", "text": "Yes, I feel a bit short of breath, especially when I walk up stairs."},
            {"speaker": "Doctor", "text": "Any fever or cough?"},
            {"speaker": "Patient", "text": "No fever, but I do have a dry cough that started yesterday."},
        ]

        features = [
            FeatureMap(feature_name="summary_length", feature_value=200)
        ]

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            features=features
        )
        
        result = await agent.chat(request=request)

        logger.info(f"Result: {result}")
    
    asyncio.run(main())