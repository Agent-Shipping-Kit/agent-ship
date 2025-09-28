# HealthLogue AI Agents Platform

A comprehensive AI agent development platform that provides a complete ecosystem for building, deploying, and managing AI agents with integrated tools, observability, and memory management.

## 🏗️ Architecture

![AI Agents Architecture](architecture.jpg)

Our platform provides a complete AI agent ecosystem with:

- **FastAPI Layer**: HTTP/chat, SSE/chat-streaming, WebSocket support with guardrails, observability, and PII security
- **AI Backend**: Multi-framework support (Crew AI, Strands SDK, Google ADK) with LLM provider integration
- **Observability**: Integrated with Datadog, AWS, and Azure for comprehensive monitoring
- **Memory Management**: Short/long-term memory, RAG, and caching with DiceDB, PostgreSQL, S3, and OpenSearch
- **Operations**: Prompt versioning, evaluation management, and tracing via Opik integration
- **Tools & MCP**: Comprehensive tool registry and Model Control Plane for agent capabilities

## ✨ Features

- 🤖 **Multi-Framework Support**: Google ADK, Crew AI, and Strands SDK integration
- 🔄 **Multi-Model Support**: OpenAI (GPT), Claude, and Google Gemini models via LiteLLM
- 🛠️ **Tool Integration**: Comprehensive tool registry and MCP (Model Control Plane) support
- 📊 **Observability**: Built-in monitoring with Datadog, AWS, and Azure integration
- 🧠 **Memory Management**: Short/long-term memory, RAG, and intelligent caching
- ⚙️ **Configuration Management**: Environment-based and YAML configuration support
- 🔒 **Security**: PII protection and guardrails layer
- 📝 **API-First**: RESTful APIs with streaming and WebSocket support
- 🏥 **Domain-Specific**: Specialized agents for medical, healthcare, and other domains

## 🚀 Quick Start

```bash
# Install dependencies
pipenv install

# Set up environment
cp env.example .env
# Edit .env with your API keys

# Start the service
pipenv run uvicorn src.service.main:app --reload --port 7001
```

**Service URL**: http://localhost:7001  
**API Docs**: http://localhost:7001/docs

## 📚 Documentation

This repository contains comprehensive documentation organized by purpose:

### 🏠 Main Documentation
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Complete local setup and development guide
- **[service_cloud_deploy/heroku/README.md](service_cloud_deploy/heroku/README.md)** - Heroku deployment and debugging
- **[agent_store_deploy/README.md](agent_store_deploy/README.md)** - PostgreSQL database setup
- **[postman/README.md](postman/README.md)** - API testing with Postman

### 🔧 Configuration

The system uses a clean configuration structure: API keys in environment variables, model selection in code.

**Required Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key  
- `GOOGLE_API_KEY` - Google API key

**Supported Models:**
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Claude**: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- **Google**: `gemini-1.5-pro`, `gemini-1.5-flash`

## 🏗️ Platform Architecture

The platform is built with a modular, scalable architecture:

```
src/
├── service/                   # FastAPI service layer
│   ├── main.py               # FastAPI application
│   └── routers/              # API endpoints
├── agents/                   # Agent implementations
│   ├── base_agent.py         # Base agent class
│   ├── followups_generation/ # Medical followup agent
│   └── [other_agents]/       # Additional domain agents
├── agent_registry/           # Agent discovery and management
│   ├── core.py              # Core registry functionality
│   ├── discovery.py         # Auto-discovery system
│   └── __init__.py          # Registry API
├── configs/                  # Configuration management
│   ├── agent_config.py      # Agent configuration
│   └── llm_provider_config.py # LLM provider configs
├── models/                   # Data models
│   └── base_models.py       # Base input/output models
├── observability/           # Monitoring and observability
│   ├── base.py              # Base observability
│   ├── opik.py              # Opik integration
│   └── datadog.py           # Datadog integration
└── agent_tools/             # Agent tools and capabilities
    └── [tool_modules]/       # Various tool implementations
```

## 🚀 Quick Links

- **Local Development**: See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Heroku Deployment**: See [service_cloud_deploy/heroku/README.md](service_cloud_deploy/heroku/README.md)
- **Database Setup**: See [agent_store_deploy/README.md](agent_store_deploy/README.md)
- **API Testing**: See [postman/README.md](postman/README.md)

## 📋 Requirements

- Python 3.13+
- pipenv (recommended) or pip
- At least one API key: OpenAI, Anthropic, or Google

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
