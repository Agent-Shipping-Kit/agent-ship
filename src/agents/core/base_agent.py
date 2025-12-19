"""Core implementation of `BaseAgent`.

This is the primary class that agent authors build on, but the heavy
lifting is delegated to small helper modules in this `core` package so
that the code is easier to read and extend.
"""

import abc
import logging
from typing import Any, List, Optional, Type

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel

from src.agents.configs.agent_config import AgentConfig
from src.agents.core.config import load_agent_config
from src.agents.core.io import create_input_from_request, parse_agent_response
from src.agents.core.observability import create_observer
from src.agents.core.tools import build_tools_from_config
from src.agents.core.types import AgentType
from src.agents.modules import (
    AgentConfigurator,
    ResponseParser,
    SessionManager,
    SessionServiceFactory,
)
from src.models.base_models import AgentChatRequest, AgentChatResponse, TextInput, TextOutput


load_dotenv()
logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Base class for all agents.

    Responsibilities (high-level):
    - Load `AgentConfig` from YAML (via `load_agent_config`).
    - Wire up session services and the Google ADK `Runner`.
    - Build tools from YAML configuration.
    - Provide a default `chat()` implementation.

    Subclasses typically only need to:
    - Provide `input_schema` / `output_schema` via `super().__init__`.
    - Optionally override `_create_input_from_request` for custom input
      mapping.
    """

    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        agent_type: Optional[AgentType] = None,
        config_path: Optional[str] = None,
        _caller_file: Optional[str] = None,
    ) -> None:
        # 1) Load configuration
        self.agent_config: AgentConfig = load_agent_config(
            agent_config=agent_config,
            config_path=config_path,
            caller_file=_caller_file,
        )
        logger.info("Agent config: %s", self.agent_config)

        # 2) Basic properties
        self.agent_type: Optional[AgentType] = agent_type
        self.input_schema: Type[BaseModel] = input_schema or TextInput
        self.output_schema: Type[BaseModel] = output_schema or TextOutput

        # 3) Modular components for configuration & sessions
        self.agent_configurator = AgentConfigurator(self.agent_config)
        self.session_service, self._use_database_sessions = SessionServiceFactory.create_session_service(
            self.agent_configurator.get_agent_name()
        )
        self.session_manager = SessionManager(
            self.session_service,
            self.agent_configurator.get_agent_name(),
            self._use_database_sessions,
        )
        self.response_parser = ResponseParser(self.agent_configurator.get_model())

        # 4) Observability (Opik)
        self.observer = create_observer(self.agent_config)

        # 5) Create underlying ADK agent and runner
        self._setup_agent()
        self._setup_runner()

    # ------------------------------------------------------------------
    # Small helper accessors
    # ------------------------------------------------------------------

    def _get_agent_name(self) -> str:
        return self.agent_configurator.get_agent_name()

    def _get_agent_description(self) -> str:
        return self.agent_configurator.get_agent_description()

    def _get_instruction_template(self) -> str:
        return self.agent_configurator.get_instruction_template()

    def _get_model(self) -> LiteLlm:
        return self.agent_configurator.get_model()

    def _get_agent_config(self) -> AgentConfig:
        return self.agent_configurator.get_agent_config()

    # ------------------------------------------------------------------
    # Agent + runner construction
    # ------------------------------------------------------------------

    def _setup_agent(self) -> None:
        """Setup the Google ADK agent with tools."""

        logger.info("Setting up agent: %s", self.agent_config)

        tools = self._create_tools()
        logger.info("Created %d tools for agent: %s", len(tools), self._get_agent_name())

        sub_agents = self._create_sub_agents()
        logger.info("Created %d sub-agents for agent: %s", len(sub_agents), self._get_agent_name())

        agent_kwargs: dict[str, Any] = {
            "model": self._get_model(),
            "name": self._get_agent_name(),
            "description": self._get_agent_description(),
            "instruction": self._get_instruction_template(),
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tools": tools,
            "sub_agents": sub_agents,
        }

        # Attach observability callbacks if available
        if self.observer:
            agent_kwargs.update(
                {
                    "before_agent_callback": self.observer.before_agent_callback,
                    "after_agent_callback": self.observer.after_agent_callback,
                    "before_model_callback": self.observer.before_model_callback,
                    "after_model_callback": self.observer.after_model_callback,
                    "before_tool_callback": self.observer.before_tool_callback,
                    "after_tool_callback": self.observer.after_tool_callback,
                }
            )
        else:
            logger.warning("No observability observer available - tracing will be disabled")

        self.agent: Agent = self._create_agent_from_type(agent_kwargs)

    def _create_agent_from_type(self, agent_kwargs: dict[str, Any]) -> Agent:
        """Instantiate the concrete ADK agent based on `agent_type`."""

        if self._get_agent_type() == AgentType.LLM_AGENT:
            return LlmAgent(**agent_kwargs)
        if self._get_agent_type() == AgentType.PARALLEL_AGENT:
            return ParallelAgent(**agent_kwargs)
        if self._get_agent_type() == AgentType.SEQUENTIAL_AGENT:
            return SequentialAgent(**agent_kwargs)
        return Agent(**agent_kwargs)

    def _get_agent_type(self) -> Optional[AgentType]:
        return self.agent_type

    def _setup_runner(self) -> None:
        """Setup the Google ADK runner."""

        logger.info("Setting up runner for agent: %s", self._get_agent_name())
        self.runner = Runner(
            agent=self.agent,
            app_name=self._get_agent_name(),
            session_service=self.session_service,
        )

    # ------------------------------------------------------------------
    # Public run + chat API
    # ------------------------------------------------------------------

    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent with schema validation handled by ADK."""

        logger.info("Running agent: %s", self._get_agent_name())
        logger.debug("Using session ID: %s", session_id)

        await self.session_manager.ensure_session_exists(user_id, session_id)

        input_text = input_data.model_dump_json()
        content = types.Content(role="user", parts=[types.Part(text=input_text)])

        result_generator = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        )

        result = None
        for response in result_generator:
            if (
                hasattr(response, "content")
                and response.content
                and response.content.parts
                and response.content.parts[0].text
            ):
                result = response

        logger.debug("Result: %s", result)
        return self._parse_agent_response(result)

    def _parse_agent_response(self, result) -> BaseModel:
        """Parse the agent response according to the output schema."""

        return parse_agent_response(self.output_schema, result)

    # ------------------------------------------------------------------
    # Overridable hooks
    # ------------------------------------------------------------------

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema instance from `AgentChatRequest`.

        Subclasses may override this for custom input transformation. The
        default implementation delegates to `core.io.create_input_from_request`.
        """

        return create_input_from_request(self.input_schema, request)

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Default chat implementation.

        Steps:
        1. Build input schema from the request.
        2. Run the agent.
        3. Wrap the result in `AgentChatResponse` with basic error handling.
        """

        logger.debug("Chatting with the agent: %s", self._get_agent_name())

        try:
            input_data = self._create_input_from_request(request)

            result = await self.run(
                request.user_id,
                request.session_id,
                input_data,
            )

            logger.info("Result from %s: %s", self._get_agent_name(), result)

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Error in %s: %s", self._get_agent_name(), exc, exc_info=True)
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(exc)}",
            )

    def _create_tools(self) -> List[Any]:
        """Create tools for the agent.

        By default this reads from the agent's YAML configuration via
        `build_tools_from_config`. Subclasses can override this for very
        custom behaviour.
        """

        return build_tools_from_config(self.agent_config)

    def _create_sub_agents(self) -> List[Agent]:
        """Create sub-agents for the agent.

        The default implementation returns an empty list; subclasses can
        override this to supply explicit sub-agents if needed.
        """

        return []
