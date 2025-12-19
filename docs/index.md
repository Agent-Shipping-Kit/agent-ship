# AgentShip

**An Agent Shipping Kit - Production-ready framework for building, deploying, and operating AI agents**

## Introduction

AgentShip is an Agent Shipping Kit—a complete foundation for building AI agents using Google's Agent Development Kit (ADK). It eliminates infrastructure complexity so you can focus on building intelligent solutions. The framework handles agent discovery, configuration management, session persistence, observability, and deployment—everything needed to go from development to production.

Built on FastAPI and Google ADK, AgentShip supports multiple LLM providers (OpenAI, Google, Anthropic) and provides three proven agent patterns: orchestrator, single-agent, and tool-based architectures.

## Key Features

**Declarative Configuration**: Define agents in YAML files with automatic discovery and registration. No boilerplate code required.

**Modular Architecture**: Core functionality is separated into focused modules (`core/`, `configs/`, `observability/`), making the framework easy to understand, maintain, and extend.

**Production-Ready**: FastAPI backend with OpenAPI documentation, PostgreSQL session management, Opik observability integration, and comprehensive test suite.

**Multiple Agent Patterns**: Orchestrator pattern for coordinating sub-agents, single-agent pattern for focused tasks, and tool pattern for comprehensive tooling capabilities.

## Quick Links

- [Installation](getting-started/installation.md) - Get started in minutes
- [Quick Start](getting-started/quickstart.md) - Build your first agent
- [Building Agents](building-agents/overview.md) - Learn agent patterns
- [API Reference](api/base-agent.md) - Complete API documentation
- [Deployment](deployment/overview.md) - Deploy to production

## Installation

```bash
pipenv install
```

See the [Installation Guide](getting-started/installation.md) for detailed setup instructions.

## Quick Example

```python
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import TextInput, TextOutput
from src.agents.utils.path_utils import resolve_config_path

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

That's it! Your agent is automatically discovered and registered.

## Documentation Structure

- **Getting Started**: Installation, configuration, and your first agent
- **Building Agents**: Agent patterns, configuration, and tools
- **API Reference**: Complete API documentation for all classes and modules
- **Deployment**: Production deployment guides
- **Testing**: Writing and running tests
