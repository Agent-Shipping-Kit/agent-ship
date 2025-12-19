# AgentShip - Agent Shipping Kit

**An Agent Shipping Kit - Production-ready framework for building, deploying, and operating AI agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)

---

## Introduction

AgentShip is an Agent Shipping Kit—a complete foundation for building AI agents using Google's Agent Development Kit (ADK). It eliminates infrastructure complexity so you can focus on building intelligent solutions. The framework handles agent discovery, configuration management, session persistence, observability, and deployment—everything needed to go from development to production.

Built on FastAPI and Google ADK, AgentShip supports multiple LLM providers (OpenAI, Google, Anthropic) and provides three proven agent patterns: orchestrator, single-agent, and tool-based architectures.

## Key Features

**Declarative Configuration**: Define agents in YAML files with automatic discovery and registration. No boilerplate code required.

**Modular Architecture**: Core functionality is separated into focused modules (`core/`, `configs/`, `observability/`), making the framework easy to understand, maintain, and extend.

**Production-Ready**: FastAPI backend with OpenAPI documentation, PostgreSQL session management, Opik observability integration, and comprehensive test suite.

**Multiple Agent Patterns**: Orchestrator pattern for coordinating sub-agents, single-agent pattern for focused tasks, and tool pattern for comprehensive tooling capabilities.

## Installation

```bash
git clone https://github.com/yourusername/agentship.git
cd agentship
pipenv install
```

## Quick Start

### 1. Configure Environment

```bash
cp env.example .env
# Edit .env with your API keys (OpenAI, Google, or Anthropic)
```

### 2. Set Up Database

```bash
cd agent_store_deploy
./setup_local_postgres.sh
```

### 3. Start the Service

```bash
pipenv run uvicorn src.service.main:app --reload --port 7001
```

Access the API documentation at http://localhost:7001/docs

### 4. Create Your First Agent

Create a new agent directory:

```bash
mkdir -p src/agents/all_agents/my_agent
cd src/agents/all_agents/my_agent
```

Define the agent configuration in `main_agent.yaml`:

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: My custom agent
instruction_template: |
  You are a helpful assistant that...
```

Implement the agent class in `main_agent.py`:

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

Agents are automatically discovered and registered. No manual registration needed.

## Usage

### Python API

```python
from src.models.base_models import AgentChatRequest
from src.agents.all_agents.single_agent_pattern.main_agent import TranslationAgent

agent = TranslationAgent()

request = AgentChatRequest(
    agent_name="translation_agent",
    user_id="user-123",
    session_id="session-456",
    query={"text": "Hello", "from_language": "en", "to_language": "es"},
    features=[]
)

response = await agent.chat(request)
print(response.agent_response.translated_text)
```

### REST API

```bash
curl -X POST "http://localhost:7001/api/agents/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "translation_agent",
    "user_id": "test-user",
    "session_id": "test-session",
    "query": {"text": "Hello", "from_language": "en", "to_language": "es"},
    "features": []
  }'
```

## Agent Configuration

Agents are configured through YAML files. The YAML filename must match the Python filename (e.g., `main_agent.yaml` for `main_agent.py`).

```yaml
agent_name: translation_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Translates text between languages
instruction_template: |
  You are a translation expert...
tools:
  - type: function
    id: custom_tool
    import: src.agents.tools.my_tool.MyTool
    method: run
  - type: agent
    id: sub_agent
    agent_class: src.agents.all_agents.sub_agent.SubAgent
```

Tools can be function tools (import any Python class and method) or agent tools (use other agents as tools). Tool order is preserved from the YAML configuration.

## Architecture

The framework follows a modular architecture:

**Agent Discovery**: Agents are automatically discovered from the filesystem based on `AGENT_DIRECTORIES` configuration and registered with the `AgentRegistry` on startup.

**Configuration Management**: Agent configuration is loaded from YAML files with automatic path resolution. The `BaseAgent` class handles LLM setup, tool creation, and observability initialization.

**Session Management**: Sessions are created automatically on first request and persisted in PostgreSQL. Conversation history is maintained across requests.

**Observability**: Built-in Opik integration provides request/response tracing, performance metrics, token usage tracking, and structured logging.

## Testing

The framework includes a comprehensive test suite with mocked LLM calls for fast, reliable testing:

```bash
# Run all tests
pipenv run pytest tests/ -v

# Run agent-specific tests
pipenv run pytest tests/unit/agents/all_agents/ -v

# Run with coverage
pipenv run pytest tests/ --cov=src/agents
```

## Deployment

### Heroku

```bash
cd service_cloud_deploy/heroku
./deploy_heroku.sh
```

The deployment script handles database setup, environment variable configuration, application deployment, and health check verification.

## Environment Variables

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Required: Database for session management
SESSION_STORE_URI=postgresql://user:password@host:port/database

# Optional: Observability
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace

# Optional: Agent discovery (defaults to all agents)
AGENT_DIRECTORIES=src/agents/all_agents

# Optional: Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Documentation

**Framework Documentation**: [View Full Documentation](https://yourusername.github.io/ai-agent-framework/) | [Serve Locally](docs/index.md)

**API Documentation**: Available at `/swagger` (Swagger UI) and `/redoc` (ReDoc) when running the service

**Framework Docs**: Available at `/docs` when running the service (serves MkDocs site)

**Additional Guides**:
* [Local Development Guide](LOCAL_DEVELOPMENT.md)
* [Database Setup Guide](agent_store_deploy/README.md)
* [Heroku Deployment Guide](service_cloud_deploy/heroku/README.md)
* [API Testing Guide](postman/README.md)

### Serving Documentation Locally

```bash
pipenv run mkdocs serve
```

Access documentation at http://localhost:8000

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
