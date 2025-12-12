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
from src.agents.tools.conversation_insights_tool import ConversationInsightsTool


logger = logging.getLogger(__name__)

class ConversationInsightsSummaryInput(BaseModel):
    """Input for generating a summary from conversation insights."""
    user_id: str = Field(description="The user id to fetch the conversation insights for.")
    limit: int = Field(description="The number of conversation insights to fetch. Default is 5.")

class ConversationInsightsSummaryOutput(BaseModel):
    """Output for generating a summary from conversation insights."""
    summary: str = Field(description="The summary of the conversation insights.")

class ConversationInsightsSummaryAgent(BaseAgent):
    """Agent for generating a summary from conversation insights."""

    def __init__(self):
        """Initialize the conversation insights summary agent."""
        agent_config = AgentConfig.from_yaml(
            "src/agents/all_agents/health_assistant_agent/sub_agents/conversation_insights_summary_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=ConversationInsightsSummaryInput,
            output_schema=ConversationInsightsSummaryOutput
        )
        
        logger.info(f"Conversation Insights Summary Agent initialized: {self.agent_config}")


    @opik.track
    def get_limit(self, features: List[FeatureMap]) -> int:
        """Get the limit from the features."""
        limit = 5
        if features:
            for feature_map in features:
                if feature_map.feature_name == "limit":
                    limit = feature_map.feature_value
        return limit

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        limit = self.get_limit(request.features)

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                input_data=ConversationInsightsSummaryInput(
                    user_id=request.user_id,
                    limit=limit
                )
            )

            logger.info(f"Result from conversation insights summary agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in conversation insights summary agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the conversation insights summary agent."""
        logger.info("Creating conversation insights summary sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        
        tools = []
        
        # Add conversation insights tool
        insights_tool = ConversationInsightsTool()
        tools.append(FunctionTool(insights_tool.run))
        logger.info("Added conversation insights tool to health assistant agent")
        
        return tools


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = ConversationInsightsSummaryAgent()
        
        # Generate a fresh session ID to avoid corrupted sessions
        user_id = "e1470068-9772-41fa-8458-614074f33295"
        session_id = hashlib.md5(f"{user_id}-fresh-{__import__('time').time()}".encode()).hexdigest()[:8]
        print(f"Generated fresh session ID: {session_id}")
        

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query='',
            features=[FeatureMap(feature_name="limit", feature_value=5)]
        )
        
        result = await agent.chat(request=request)

        logger.info(f"Result: {result}")
    
    asyncio.run(main())