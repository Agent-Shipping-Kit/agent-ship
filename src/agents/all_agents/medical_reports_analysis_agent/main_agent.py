"""Azure artifact reading agent for PDF files from Azure Blob Storage."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, AgentChatResponse
from src.agents.tools.azure_artifact_reading_tool import AzureArtifactTool
from google.adk.tools import FunctionTool


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
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=MedicalReportsAnalysisInput,
            output_schema=MedicalReportsAnalysisOutput
        )

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent - custom implementation for artifact handling."""
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
            input_data=MedicalReportsAnalysisInput(medical_report_path=medical_report_path)
        )
        
        return AgentChatResponse(
            agent_name=self._get_agent_name(),
            user_id=request.user_id,
            session_id=request.session_id,
            success=True,
            agent_response=result
        )

    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the agent."""
        azure_tool = AzureArtifactTool()
        return [FunctionTool(azure_tool.run)]
    
    # No need to override _create_sub_agents() - defaults to empty list
