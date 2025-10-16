"""Azure artifact reading agent for PDF files from Azure Blob Storage."""

import logging
import re
import opik
from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from google.adk import Agent
from src.agents.configs.agent_config import AgentConfig
from src.agents.tools.azure_artifact_reading_tool import AzureArtifactTool
from src.models.base_models import AgentChatRequest, AgentChatResponse
from google.adk.tools import FunctionTool



logger = logging.getLogger(__name__)

class MedicalReportsAnalysisInput(BaseModel):
    """Input for medical reports analysis."""
    medical_report_path: str = Field(description="The azure blob path to the medical report. Format: container/blob_name.")

class MedicalReportsAnalysisOutput(BaseModel):
    """Output for medical reports analysis."""
    summary: str = Field(description="The summary of the medical report.")
    key_findings: List[str] = Field(description="The key findings of the medical report.")
    recommendations: List[str] = Field(description="The recommendations of the medical report.")

class MedicalReportsAnalysisAgent(BaseAgent):
    """Agent for analyzing medical reports."""

    def __init__(self):
        """Initialize the medical reports analysis agent."""
        # Load agent config from YAML file
        agent_config = AgentConfig.from_yaml(
            "src/agents/all_agents/medical_reports_analysis_agent/main_agent.yaml")
        
        super().__init__(
            agent_config=agent_config,
            input_schema=MedicalReportsAnalysisInput,
            output_schema=MedicalReportsAnalysisOutput
        )

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the Azure artifact agent."""
        logger.info(f"Medical reports analysis agent chat request: {request}")
        
        if not request.artifacts:
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response="No artifacts provided"
            )

        medical_report_path = request.artifacts[0].artifact_path

        # Run the agent with the input
        result = await self.run(
            user_id=request.user_id,
            session_id=request.session_id,
            input_data=MedicalReportsAnalysisInput(
                medical_report_path=medical_report_path
            )
        )
        
        # Return the response
        return AgentChatResponse(
            agent_name=self._get_agent_name(),
            user_id=request.user_id,
            session_id=request.session_id,
            success=True,
            agent_response=result
        )

    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the Azure artifact agent."""
        logger.info("Creating Azure artifact sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the Azure artifact agent."""
        logger.info("Creating Azure artifact tools")
        # Create the Azure artifact reading tool
        azure_tool = AzureArtifactTool()
        logger.info(f"Azure artifact tool: {azure_tool}")
        
        return [FunctionTool(azure_tool.run)]

if __name__ == "__main__":
    import asyncio
    import hashlib
    from src.models.base_models import Artifact

    async def main():
        agent = MedicalReportsAnalysisAgent()

        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id="123",
            session_id=hashlib.md5(f"123".encode()).hexdigest()[:8],
            query='',
            artifacts=[Artifact(
                artifact_name="fb02add5-7127-496f-af15-9791795f0912.pdf",
                artifact_path="medical-reports/fb02add5-7127-496f-af15-9791795f0912.pdf")]
        )

        result = await agent.chat(request)

        print(result)

    asyncio.run(main())