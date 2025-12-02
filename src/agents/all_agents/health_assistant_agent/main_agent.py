"""Medical conversation insights generation agent using Google ADK."""

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

class HealthAssistantInput(BaseModel):
    """Input for answering questions about user's health data, conversations, action items, etc."""
    message: str = Field(description="The message to answer.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")

class HealthAssistantOutput(BaseModel):
    """Output for answering questions about user's health data, conversations, action items, etc."""
    answer: str = Field(description="The answer to the question.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")

class HealthAssistantAgent(BaseAgent):
    """Agent for answering questions about user's health data, conversations, action items, etc."""

    def __init__(self):
        """Initialize the medical conversation insights agent."""
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/health_assistant_agent/main_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=HealthAssistantInput,
            output_schema=HealthAssistantOutput
        )
        
        logger.info(f"Medical Conversation Insights Agent initialized: {self.agent_config}")

    @opik.track
    def get_message(self, features: List[FeatureMap]) -> int:
        """Get the length of the summary from the features."""
        summary_length = 200

        if features:
            for feature_map in features:
                if feature_map.feature_name == "summary_length":
                    summary_length = feature_map.feature_value
        logger.debug(f"Summary length: {summary_length}")
        return summary_length

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                HealthAssistantInput(
                    message=request.query,
                    session_id=request.session_id,
                    user_id=request.user_id
                )
            )

            logger.info(f"Result from health assistant agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in health assistant agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the health assistant agent."""
        logger.info("Creating health assistant sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = HealthAssistantAgent()
        
        # Generate a fresh session ID to avoid corrupted sessions
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}-fresh-{__import__('time').time()}".encode()).hexdigest()[:8]
        print(f"Generated fresh session ID: {session_id}")
        
        query = "I am feeling tired and have a headache. What should I do to feel better?"

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            features=[]
        )
        
        result = await agent.chat(request=request)

        logger.info(f"Result: {result}")
    
    asyncio.run(main())