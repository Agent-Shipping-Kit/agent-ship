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
import json

logger = logging.getLogger(__name__)

class ConversationTurn(BaseModel):
    """One turn in a conversation."""
    speaker: str = Field(description="Speaker label, e.g., Patient or Doctor")
    text: str = Field(description="What the speaker said")

class FollowupQuestionsInput(BaseModel):
    """Input for followup questions generation."""
    conversation_turns: List[ConversationTurn] = Field(description="The medical conversation to generate followup questions for.")
    max_followups: Optional[int] = Field(description="The maximum number of followup questions to generate.", default=5)

class FollowupQuestionsOutput(BaseModel):
    """Output for followup questions generation."""
    followup_questions: List[str] = Field(description="The list of followup questions generated.")
    count: int = Field(description="The number of followup questions generated.")


class MedicalFollowupAgent(BaseAgent):
    """Agent for generating medical conversation followup questions."""

    def __init__(self):
        """Initialize the medical followup agent."""
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/medical_followup_agent/main_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=FollowupQuestionsInput,
            output_schema=FollowupQuestionsOutput
        )
        
        logger.info(f"Medical Followup Agent initialized: {self.agent_config}")

    @opik.track
    def get_num_followups(self, features: List[FeatureMap]) -> int:
        """Get the number of followups from the features."""
        max_followups = 3
        if features:
            for feature_map in features:
                if feature_map.feature_name == "max_followups":
                    max_followups = feature_map.feature_value
        logger.debug(f"Max followups: {max_followups}")
        return max_followups

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
        max_followups = self.get_num_followups(request.features)
        conversation_turns = self.parse_conversation_turns(request.query)
        logger.debug(f"Conversation turns: {conversation_turns}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                FollowupQuestionsInput(
                    conversation_turns=conversation_turns,
                    max_followups=max_followups
                )
            )

            logger.info(f"Result from followup questions agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in followup questions agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the medical followup agent."""
        logger.info("Creating medical followup sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = MedicalFollowupAgent()
        
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
            FeatureMap(feature_name="max_followups", feature_value=5)
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