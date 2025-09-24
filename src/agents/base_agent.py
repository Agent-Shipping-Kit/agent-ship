import abc
import logging
import json
from typing import List, Optional, Type
from pydantic import BaseModel
from src.configs.agent_config import AgentConfig
from src.agents.models import TextInput, TextOutput
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types



logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Base class for all agents."""

    def __init__(self, agent_config: AgentConfig, 
                 input_schema: Optional[Type[BaseModel]] = None,
                 output_schema: Optional[Type[BaseModel]] = None):
        """Initialize the agent."""
        self.agent_config = agent_config
        self.input_schema = input_schema or TextInput
        self.output_schema = output_schema or TextOutput
        logger.info(f"Agent config: {self.agent_config}")
        self._setup_agent()
        self._setup_runner()

    def _get_agent_name(self) -> str:
        """Get the name of the agent."""
        logger.info(f"Getting agent name: {self.agent_config.agent_name}")
        return self.agent_config.agent_name
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent."""
        logger.info(f"Getting description: {self.agent_config.description}")
        return self.agent_config.description

    def _get_instruction_template(self) -> str:
        """Get the instruction template of the agent."""
        logger.info(f"Getting instruction template: {self.agent_config.instruction_template}")
        return self.agent_config.instruction_template

    def _get_model(self) -> str:
        """Get the model of the agent."""
        logger.info(f"Getting model: {self.agent_config.model.value}")
        return LiteLlm(self.agent_config.model.value)
    
    def _get_agent_config(self) -> AgentConfig:
        """Get the configuration of the agent."""
        logger.info(f"Getting agent config: {self.agent_config}")
        return self.agent_config

    def _setup_agent(self) -> None:
        """Setup the Google ADK agent with tools."""
        logger.info(f"Setting up agent: {self.agent_config}")
        
        # Create agent configuration with input/output schemas
        self.agent = Agent(
            model=self._get_model(),
            name=self._get_agent_name(),
            description=self._get_agent_description(),
            instruction=self._get_instruction_template(),
            input_schema=self.input_schema,
            output_schema=self.output_schema,
        )

    def _setup_runner(self) -> None:
        """Setup the Google ADK runner."""
        logger.info(f"Setting up session service for agent: {self._get_agent_name()}")
        session_service = InMemorySessionService()
        logger.info(f"Session service for agent: {self._get_agent_name()} created")

        logger.info(f"Setting up runner for agent: {self._get_agent_name()}")
        self.runner = Runner(
            agent=self.agent,
            app_name=self._get_agent_name(),
            session_service=session_service,
        )
        
    async def _get_or_create_session(self, user_id: str, session_id: str) -> None:
        # Create session if it doesn't exist
        try:
            session = self.runner.session_service.get_session(session_id)
            logger.info(f"Using existing session: {session_id}")
        except:
            logger.info(f"Creating new session: {session_id}")
            session = await self.runner.session_service.create_session(
                app_name=self._get_agent_name(),
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Created session: {session_id}")
        return session

    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent with schema validation handled by ADK."""
        logger.info(f"Running agent: {self._get_agent_name()}")
        logger.info(f"Using session ID: {session_id}")
        
        # ADK will validate input_data against input_schema automatically
        session = await self._get_or_create_session(user_id, session_id)
        
        # Serialize structured input for the model
        input_text = input_data.model_dump_json()
        
        # Create the proper Google ADK message format
        content = types.Content(
            role='user',
            parts=[types.Part(text=input_text)]
        )
        
        # Run the agent - ADK handles schema validation and output formatting
        # The runner.run() returns a generator, so we need to consume it
        result_generator = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )
        
        # Consume the generator to get the actual result
        result = None
        for response in result_generator:
            result = response
            break  # We only need the first (and typically only) response
        
        logger.info(f"Result: {result}")
        # Parse the result according to output_schema
        return self._parse_agent_response(result)
    
    def _parse_agent_response(self, result) -> BaseModel:
        """Parse the agent response according to the output schema."""
        # Extract the content from the Event object and parse it according to output_schema
        logger.info(f"Parsing agent response: {result}")
        if result and hasattr(result, 'content') and result.content and result.content.parts:
            # Extract the text content from the event
            content_text = result.content.parts[0].text
            
            # Parse the JSON content according to our output schema
            try:
                logger.info(f"Parsing agent response: {content_text}")
                parsed_data = json.loads(content_text)
                # Create the output schema instance
                logger.info(f"Parsed data: {parsed_data}")
                output_instance = self.output_schema(**parsed_data)
                logger.info(f"Output instance: {output_instance}")
                return output_instance
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.error(f"Failed to parse output: {e}")
                # Fallback: return the raw content
                return content_text
        else:
            logger.error("No valid content found in the response")
            return None
    
    @abc.abstractmethod
    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the agent."""
        pass
