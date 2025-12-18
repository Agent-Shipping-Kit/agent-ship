import abc
import logging
import json
import opik
import inspect
from enum import Enum
from typing import Any, List, Optional, Type, Dict, Union
from pydantic import BaseModel
from src.agents.configs.agent_config import AgentConfig
from src.models.base_models import TextInput, TextOutput, AgentChatRequest, AgentChatResponse
from src.agents.modules import SessionManager, AgentConfigurator, SessionServiceFactory, ResponseParser
from src.agents.utils.path_utils import resolve_config_path
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv
from src.agents.observability.opik import OpikObserver


load_dotenv()
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enum for the type of agent."""
    LLM_AGENT = "llm_agent"
    PARALLEL_AGENT = "parallel_agent"
    SEQUENTIAL_AGENT = "sequential_agent"


class BaseAgent(abc.ABC):
    """Base class for all agents."""

    def __init__(self, 
                 agent_config: Optional[AgentConfig] = None,
                 input_schema: Optional[Type[BaseModel]] = None,
                 output_schema: Optional[Type[BaseModel]] = None,
                 agent_type: Optional[AgentType] = None,
                 config_path: Optional[str] = None,
                 _caller_file: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            agent_config: Agent configuration. If None, will auto-load from YAML file.
            input_schema: Input schema class. Defaults to TextInput.
            output_schema: Output schema class. Defaults to TextOutput.
            agent_type: Type of agent (LLM_AGENT, PARALLEL_AGENT, etc.). Defaults to None.
            config_path: Path to config YAML file. If None, auto-detects from _caller_file.
                        Only used if agent_config is None.
            _caller_file: Internal parameter - pass __file__ here for auto-detection.
                         Recommended: super().__init__(_caller_file=__file__, ...)
        """
        # Auto-load config if not provided
        if agent_config is None:
            if config_path is None:
                if _caller_file:
                    config_path = resolve_config_path(relative_to=_caller_file)
                else:
                    # Try to auto-detect from stack (fallback)
                    try:
                        frame = inspect.currentframe()
                        caller_frame = frame.f_back
                        if caller_frame:
                            caller_file = caller_frame.f_globals.get('__file__')
                            if caller_file:
                                config_path = resolve_config_path(relative_to=caller_file)
                            else:
                                raise ValueError(
                                    "Cannot auto-detect config file. Please provide one of: "
                                    "agent_config, config_path, or _caller_file=__file__"
                                )
                        del frame
                    except Exception as e:
                        raise ValueError(
                            f"Cannot auto-detect config file: {e}. "
                            "Please provide one of: agent_config, config_path, or _caller_file=__file__"
                        )
            
            agent_config = AgentConfig.from_yaml(config_path)
        
        self.agent_config = agent_config
        self.agent_type = agent_type
        self.input_schema = input_schema or TextInput
        self.output_schema = output_schema or TextOutput
        logger.info(f"Agent config: {self.agent_config}")
        
        # Initialize modular components
        self.agent_configurator = AgentConfigurator(agent_config)
        self.session_service, self._use_database_sessions = SessionServiceFactory.create_session_service(
            self.agent_configurator.get_agent_name()
        )
        self.session_manager = SessionManager(
            self.session_service, 
            self.agent_configurator.get_agent_name(),
            self._use_database_sessions
        )
        self.response_parser = ResponseParser(self.agent_configurator.get_model())
        # Observability
        self._setup_observability()

        self._setup_agent()
        self._setup_runner()

    def _get_agent_name(self) -> str:
        """Get the name of the agent."""
        return self.agent_configurator.get_agent_name()
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent."""
        return self.agent_configurator.get_agent_description()

    def _get_instruction_template(self) -> str:
        """Get the instruction template of the agent."""
        return self.agent_configurator.get_instruction_template()

    def _get_model(self) -> LiteLlm:
        """Get the model of the agent."""
        return self.agent_configurator.get_model()
    
    def _get_agent_config(self) -> AgentConfig:
        """Get the configuration of the agent."""
        return self.agent_configurator.get_agent_config()

    def _setup_agent(self) -> None:
        """Setup the Google ADK agent with tools."""
        logger.info(f"Setting up agent: {self.agent_config}")
        
        # Get tools from the agent implementation
        tools = self._create_tools()
        logger.info(f"Created {len(tools)} tools for agent: {self._get_agent_name()}")

        sub_agents = self._create_sub_agents()
        logger.info(f"Created {len(sub_agents)} sub-agents for agent: {self._get_agent_name()}")
        
        # Create agent configuration with input/output schemas and tools
        agent_kwargs = {
            "model": self._get_model(),
            "name": self._get_agent_name(),
            "description": self._get_agent_description(),
            "instruction": self._get_instruction_template(),
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tools": tools,
            "sub_agents": sub_agents,
        }
        
        # Add observability callbacks only if observer is available
        if self.observer:
            agent_kwargs.update({
                "before_agent_callback": self.observer.before_agent_callback,
                "after_agent_callback": self.observer.after_agent_callback,
                "before_model_callback": self.observer.before_model_callback,
                "after_model_callback": self.observer.after_model_callback,
                "before_tool_callback": self.observer.before_tool_callback,
                "after_tool_callback": self.observer.after_tool_callback
            })
        else:
            logger.warning("No observability observer available - tracing will be disabled")
        
        self.agent = self._create_agent_from_type(agent_kwargs)

    def _create_agent_from_type(self, agent_kwargs: dict) -> Agent:
        """Create the agent."""
        if self._get_agent_type() == AgentType.LLM_AGENT:
            return LlmAgent(**agent_kwargs)
        elif self._get_agent_type() == AgentType.PARALLEL_AGENT:
            return ParallelAgent(**agent_kwargs)
        elif self._get_agent_type() == AgentType.SEQUENTIAL_AGENT:
            return SequentialAgent(**agent_kwargs)

        return Agent(**agent_kwargs)
    
    def _get_agent_type(self) -> AgentType:
        """Get the type of the agent."""
        return self.agent_type
    
    def _setup_observability(self) -> None:
        """Setup the observability for the agent."""
        logger.info(f"Setting up observer for agent: {self._get_agent_name()}")
        try:
            self.observer = OpikObserver(
                agent_config=self.agent_config
            )
        except Exception as e:
            logger.error(f"Failed to setup observability: {e}")
            # Create a no-op observer to prevent errors
            self.observer = None

    def _setup_runner(self) -> None:
        """Setup the Google ADK runner."""
        logger.info(f"Setting up runner for agent: {self._get_agent_name()}")
        self.runner = Runner(
            agent=self.agent,
            app_name=self._get_agent_name(),
            session_service=self.session_service,
        )


    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent with schema validation handled by ADK."""
        logger.info(f"Running agent: {self._get_agent_name()}")
        logger.debug(f"Using session ID: {session_id}")
        
        # Handle session management based on session service type
        await self.session_manager.ensure_session_exists(user_id, session_id)
        
        # Serialize structured input for the model
        input_text = input_data.model_dump_json()
        
        # Create the proper Google ADK message format
        content = types.Content(
            role='user',
            parts=[types.Part(text=input_text)]
        )
        
        # Run the agent - ADK handles schema validation, output formatting, and session management
        # The runner.run() returns a generator, so we need to consume it
        result_generator = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )

        # Consume the generator to get the final result
        # The generator yields multiple events: function calls, tool results, final response
        result = None
        for response in result_generator:
            # Look for the final text response (not function calls)
            if (hasattr(response, 'content') and 
                response.content and 
                response.content.parts and 
                response.content.parts[0].text):
                result = response
        
        logger.debug(f"Result: {result}")
        # Parse the result according to output_schema
        return self._parse_agent_response(result)
    
    def _parse_agent_response(self, result) -> BaseModel:
        """Parse the agent response according to the output schema."""
        # Extract the content from the Event object and parse it according to output_schema
        logger.debug(f"Parsing agent response: {result}")
        if result and hasattr(result, 'content') and result.content and result.content.parts:
            # Extract the text content from the event
            content_text = result.content.parts[0].text
            
            # Parse the JSON content according to our output schema
            try:
                logger.debug(f"Parsing agent response: {content_text}")
                parsed_data = json.loads(content_text)
                # Create the output schema instance
                logger.debug(f"Parsed data: {parsed_data}")
                output_instance = self.output_schema(**parsed_data)
                logger.debug(f"Output instance: {output_instance}")
                return output_instance
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.error(f"Failed to parse output: {e}")
                # Fallback: return the raw content
                return content_text
        else:
            logger.error("No valid content found in the response")
            return None
    
    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """
        Create input schema instance from AgentChatRequest.
        
        Override this method if you need custom input transformation.
        Default behavior: If query is a dict, use it as kwargs. Otherwise, pass as 'text' or first field.
        
        Args:
            request: The chat request
            
        Returns:
            Instance of input_schema
        """
        query = request.query
        
        # If query is a dict, try to use it as kwargs
        if isinstance(query, dict):
            try:
                return self.input_schema(**query)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to create input from dict, trying with 'text' field: {e}")
                # Fallback: try with 'text' field
                if hasattr(self.input_schema, 'model_fields') and 'text' in self.input_schema.model_fields:
                    return self.input_schema(text=str(query))
        
        # If query is a string or other type, try 'text' field first
        if hasattr(self.input_schema, 'model_fields'):
            # Check if schema has a 'text' field
            if 'text' in self.input_schema.model_fields:
                return self.input_schema(text=str(query))
            # Otherwise, try to pass as first field
            fields = list(self.input_schema.model_fields.keys())
            if fields:
                return self.input_schema(**{fields[0]: query})
        
        # Last resort: try to pass query directly
        return self.input_schema(query) if query else self.input_schema()
    
    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """
        Default chat implementation.
        
        Override this method for custom behavior. Default implementation:
        1. Creates input schema from request
        2. Runs the agent
        3. Returns AgentChatResponse with success/error handling
        
        Args:
            request: The chat request
            
        Returns:
            AgentChatResponse with result or error
        """
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")
        
        try:
            # Create input schema instance from request
            input_data = self._create_input_from_request(request)
            
            # Run the agent
            result = await self.run(
                request.user_id,
                request.session_id,
                input_data
            )
            
            logger.info(f"Result from {self._get_agent_name()}: {result}")
            
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in {self._get_agent_name()}: {e}", exc_info=True)
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_tools(self) -> List[FunctionTool]:
        """
        Create the tools for the agent.
        
        Override this method to provide tools. Default returns empty list.
        
        Returns:
            List of FunctionTool instances
        """
        return []
    
    def _create_sub_agents(self) -> List[Agent]:
        """
        Create the sub-agents for the agent.
        
        Override this method to provide sub-agents. Default returns empty list.
        
        Returns:
            List of Agent instances
        """
        return []
