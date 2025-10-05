# HealthLogue AI Agents Platform

A cookie-cutter AI agents template you can fork, customize, and deploy. It provides a complete ecosystem for building, observing, and operating AI agents using Google ADK.

## 🏗️ Architecture (The End Game)

![AI Agents Architecture](AgenticAI.jpg)

Our platform provides a complete AI agent ecosystem with:

#### ✨ Features
- **FastAPI Layer**: HTTP/chat, SSE/chat-streaming, WebSocket support with guardrails, observability, and PII security
- **AI Backend**: Google ADK framework (only) with multiple LLM provider integration like Google Gemini, OpenAI Chatgpt, Claude etc.
- **Memory Management**: Short/long-term memory with Postgres, RAG with Opensearch, and caching with DiceDB and flat file interaction with S3.
- **Observability**: Native Opik integration for tracing and metric
- **Operations**: Prompt versioning, evals, and evals tracing via Opik SDK integration
- **Tools & MCP**: Comprehensive tool registry and Model Control Plane for agent capabilities

## 🏗️ Platform Architecture

The platform is built with a modular, scalable architecture:

```
src/
├── service/                   # FastAPI service layer
│   ├── main.py               # FastAPI application
│   └── routers/              # API endpoints
├── agents/                   # Agent implementations and related code
│   ├── base_agent.py         # Base agent class
│   ├── configs/              # Configuration management
│   │   ├── agent_config.py   # Agent configuration
│   │   └── llm_provider_config.py # LLM provider configs
│   ├── all_agents/           # All agent implementations
│   │   ├── medical_followup/ # Medical followup agent
│   │   └── [other_agents]/   # Additional domain agents
│   ├── registry/             # Agent discovery and management
│   │   ├── core.py          # Core registry functionality
│   │   ├── discovery.py     # Auto-discovery system
│   │   └── __init__.py      # Registry API
│   ├── tools/               # Agent tools and capabilities
│   │   └── [tool_modules]/  # Various tool implementations
│   └── modules/             # Modular components (for future use)
├── models/                   # Data models
│   └── base_models.py       # Base input/output models
└── observability/           # Monitoring and observability
    ├── base.py              # Base observability
    └── opik.py              # Opik integration
```

## 🍪 Using this template

1. Fork this repository
2. Clone locally and copy `env.example` to `.env`
3. Start the service and open `/docs` for APIs
4. Customize agents in `src/agents/` (YAML/Python) and routes in `src/service/routers/`
5. Configure Opik for observability and iterate
6. Deploy to Heroku when ready

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

## 🚀 Quick Links

- **Local Development**: See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Heroku Deployment**: See [service_cloud_deploy/heroku/README.md](service_cloud_deploy/heroku/README.md)
- **Database Setup**: See [agent_store_deploy/README.md](agent_store_deploy/README.md)
- **API Testing**: See [postman/README.md](postman/README.md)

## 📋 Requirements

- Python 3.13+
- pipenv (recommended) or pip
- `GOOGLE_API_KEY`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
