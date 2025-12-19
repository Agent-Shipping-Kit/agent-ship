# Installation

## Prerequisites

- Python 3.13+
- PostgreSQL (for session management)
- At least one LLM API key (OpenAI, Google, or Anthropic)

## Install Dependencies

```bash
git clone https://github.com/yourusername/agentship.git
cd agentship
pipenv install
```

## Configure Environment

```bash
cp env.example .env
```

Edit `.env` with your API keys:

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
```

## Set Up Database

For local development:

```bash
cd agent_store_deploy
./setup_local_postgres.sh
```

For production deployment, see the [Deployment Guide](../deployment/overview.md).

## Verify Installation

Start the service:

```bash
pipenv run uvicorn src.service.main:app --reload --port 7001
```

Access the API documentation:
- Swagger UI: http://localhost:7001/swagger
- ReDoc: http://localhost:7001/redoc
- Framework Docs: http://localhost:7001/docs (after building with `mkdocs build`)
