"""Medical conversation followup generation agent using Google ADK."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src.configs.agent_config import AgentConfig
from src.agents.base_agent import BaseAgent
from src.agent_models.base_models import ChatInput, FeatureMap, ConversationTurn
import logging

logger = logging.getLogger(__name__)


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
        agent_config = AgentConfig.from_yaml("src/agents/followups_generation/main_agent.yaml")
        super().__init__(
            agent_config=agent_config,
            input_schema=FollowupQuestionsInput,
            output_schema=FollowupQuestionsOutput
        )
        self._setup_agent() # Setup the Google ADK agent with tools
        logger.info(f"Medical Followup Agent initialized: {self.agent_config}")
    
    async def chat(self, user_id: str, session_id: str, input: ChatInput) -> BaseModel:
        """Chat with the agent."""
        logger.info(f"Chatting with the agent: {self._get_agent_name()}")

        max_followups = 3
        if input.features:
            for feature_map in input.features:
                if feature_map.feature_name == "max_followups":
                    max_followups = feature_map.feature_value

        logger.info(f"Max followups: {max_followups}")

        result = await self.run(
            user_id,
            session_id,
            FollowupQuestionsInput(
                conversation_turns=input.conversation_turns,
                max_followups=max_followups
            )
        )

        logger.info(f"Result from followup questions agent: {result}")
        return result
    
    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = MedicalFollowupAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        query = "Patient: I have chest pain. Doctor: Can you describe it?"
        session_id = hashlib.md5(f"{user_id}_{query}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        # Create proper input using the schema
        input_data = ChatInput(
            conversation_turns=[
                ConversationTurn(speaker="Patient", text=query),
                ConversationTurn(speaker="Doctor", text="Can you describe it?"),
                ConversationTurn(speaker="Patient", text="It's a sharp, stabbing pain. It started after I lifted some heavy boxes at work."),
                ConversationTurn(speaker="Doctor", text="Have you had any shortness of breath or difficulty breathing?"),
                ConversationTurn(speaker="Patient", text="Yes, I feel a bit short of breath, especially when I walk up stairs."),
                ConversationTurn(speaker="Doctor", text="Any fever or cough?"),
                ConversationTurn(speaker="Patient", text="No fever, but I do have a dry cough that started yesterday."),
            ],
            features=[
                FeatureMap(feature_name="max_followups", feature_value=5)
            ]
        )
        
        result = await agent.chat(
            user_id=user_id,
            session_id=session_id,
            input=input_data
        )
        logger.info(f"Followup questions: {result.followup_questions}")
        logger.info(f"Number of questions: {result.count}")
    
    asyncio.run(main())