# HealthLogue AI Agents Platform

A comprehensive AI agent development platform that provides a complete ecosystem for building, deploying, and managing AI agents with integrated tools, observability, and memory management.

## Architecture

![AI Agents Architecture](architecture.jpg)

Our platform provides a complete AI agent ecosystem with:

- **FastAPI Layer**: HTTP/chat, SSE/chat-streaming, WebSocket support with guardrails, observability, and PII security
- **AI Backend**: Multi-framework support (Crew AI, Strands SDK, Google ADK) with LLM provider integration
- **Observability**: Integrated with Datadog, AWS, and Azure for comprehensive monitoring
- **Memory Management**: Short/long-term memory, RAG, and caching with DiceDB, PostgreSQL, S3, and OpenSearch
- **Operations**: Prompt versioning, evaluation management, and tracing via Opik integration
- **Tools & MCP**: Comprehensive tool registry and Model Control Plane for agent capabilities

## Features

- 🤖 **Multi-Framework Support**: Google ADK, Crew AI, and Strands SDK integration
- 🔄 **Multi-Model Support**: OpenAI (GPT), Claude, and Google Gemini models via LiteLLM
- 🛠️ **Tool Integration**: Comprehensive tool registry and MCP (Model Control Plane) support
- 📊 **Observability**: Built-in monitoring with Datadog, AWS, and Azure integration
- 🧠 **Memory Management**: Short/long-term memory, RAG, and intelligent caching
- ⚙️ **Configuration Management**: Environment-based and YAML configuration support
- 🔒 **Security**: PII protection and guardrails layer
- 📝 **API-First**: RESTful APIs with streaming and WebSocket support
- 🏥 **Domain-Specific**: Specialized agents for medical, healthcare, and other domains

## Quick Start

1. **Install dependencies**:
   ```bash
   # Install production dependencies
   pipenv install
   
   # Or install with development dependencies
   pipenv install --dev
   ```

2. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start the AI Agents Platform**:
   ```bash
   # Start the FastAPI service
   pipenv run uvicorn src.service.main:app --reload --port 8000
   
   # Or run individual agents
   pipenv run python src.agents.followups_generation.main_agent
   ```

4. **Test the API**:
   ```bash
   # Test the chat endpoint
   curl -X POST "http://localhost:8000/api/agents/chat" \
        -H "Content-Type: application/json" \
        -d '{
          "agent_name": "medical_followup",
          "user_id": "user-123",
          "chat_input": {
            "conversation_turns": [
              {"speaker": "Patient", "text": "I have chest pain"},
              {"speaker": "Doctor", "text": "Can you describe it?"}
            ]
          }
        }'
   ```

## Configuration

The system uses a super clean configuration structure: API keys in environment variables, model selection directly in code.

### Environment Variables (API Keys Only)

Only API keys need to be set in environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude models |
| `GOOGLE_API_KEY` | Google API key | For Gemini models |
| `TEMPERATURE` | Global temperature | `0.7` | 0.0 to 1.0 |

### Agent Configuration (Direct in Code)

Each agent specifies its model directly in the code - no environment variables needed!

```python
# Medical Followup Agent - uses Claude
agent_config = MedicalFollowupConfig(
    model_provider="claude",
    model_name="claude-3-5-sonnet-20241022",
    max_followups=5
)

# Base config with API keys from environment
base_config = BaseAgentConfig.from_env()

agent = MedicalFollowupAgent(agent_config, base_config)
```

### Example Environment Setup
```bash
# Only API keys needed in environment
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key
GOOGLE_API_KEY=your-gemini-key
TEMPERATURE=0.7
```

### Supported Models

**OpenAI Models:**
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-3.5-turbo`

**Claude Models:**
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

**Google Gemini Models:**
- `gemini-1.5-pro`
- `gemini-1.5-flash`

## Usage

### Basic Usage

```python
from src.agents.followups_generation import MedicalFollowupAgent

# Initialize agent (uses environment variables)
agent = MedicalFollowupAgent()

# Generate followups
conversation = "Patient: I have chest pain. Doctor: Can you describe it?"
followups = await agent.generate_followups(conversation)
print(followups)
```

### With Context

```python
context = {
    "patient_age": "45",
    "chief_complaint": "Chest pain",
    "medical_history": "Hypertension"
}

result = await agent.process_conversation(conversation, context)
print(result["followup_questions"])
```

### Custom Configuration

```python
from src.shared.core.config import MedicalFollowupConfig, BaseAgentConfig

# Agent-specific config (only 3 variables!)
agent_config = MedicalFollowupConfig(
    model_provider="gemini",
    model_name="gemini-1.5-pro",
    max_followups=3
)

# Base config with API keys
base_config = BaseAgentConfig(
    google_api_key="your-key",
    temperature=0.5
)

agent = MedicalFollowupAgent(agent_config, base_config)
```

## Creating New Agents

The system is designed to easily support multiple agents with different configurations:

### 1. Create Agent-Specific Config (Super Simple!)

```python
# src/agents/my_agent/config.py
from dataclasses import dataclass

@dataclass
class MyAgentConfig:
    # Model selection (only 3 variables needed!)
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str = None  # Optional: specific API key
    
    # Agent-specific settings
    my_setting: str = "default_value"
```

### 2. Create Agent Implementation

```python
# src/agents/my_agent/agent.py
from ...shared.infrastructure.llm_service import LLMService
from ...shared.core.config import BaseAgentConfig
from .config import MyAgentConfig

class MyAgent:
    def __init__(self, agent_config: MyAgentConfig = None, base_config: BaseAgentConfig = None):
        self.agent_config = agent_config or MyAgentConfig()
        self.base_config = base_config or BaseAgentConfig.from_env()
        self.llm_service = LLMService(self.agent_config, self.base_config)
```

### 3. Usage (No Environment Variables Needed!)

```python
# Create agent with specific model
agent_config = MyAgentConfig(
    model_provider="claude",
    model_name="claude-3-5-sonnet-20241022",
    my_setting="custom_value"
)

agent = MyAgent(agent_config)
```

### 4. Environment Variables (Only API Keys!)

```bash
# Only API keys needed in environment
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key
GOOGLE_API_KEY=your-gemini-key
TEMPERATURE=0.7
```

## CLI Usage

The agent includes a command-line interface for easy usage:

```bash
# Basic usage
pipenv run python cli.py "Patient: I have chest pain. Doctor: Can you describe it?"

# With context
pipenv run python cli.py "conversation.txt" --context '{"patient_age": "45", "chief_complaint": "Chest pain"}'

# Using Claude model
pipenv run python cli.py "conversation.txt" --model claude --model-name claude-3-5-sonnet-20241022

# Using Gemini model
pipenv run python cli.py "conversation.txt" --model gemini --model-name gemini-1.5-pro

# JSON output
pipenv run python cli.py "conversation.txt" --output json

# Custom parameters
pipenv run python cli.py "conversation.txt" --max-followups 3 --temperature 0.5
```

### CLI Options

- `conversation`: Medical conversation text or path to file
- `--context`: Additional context as JSON string
- `--model`: Model provider (`openai`, `claude`, or `gemini`)
- `--model-name`: Specific model name
- `--max-followups`: Maximum number of questions (default: 5)
- `--temperature`: LLM temperature 0.0-1.0 (default: 0.7)
- `--output`: Output format (`json`, `text`, `list`)

## Testing

Run the test suite to verify everything works:

```bash
# Test with any available model
pipenv run python test_agent.py

# Test specifically with Gemini
pipenv run python test_gemini.py
```

## Platform Architecture

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
├── agent_models/             # Data models
│   └── base_models.py       # Base input/output models
├── observability/           # Monitoring and observability
│   ├── base.py              # Base observability
│   ├── opik.py              # Opik integration
│   └── datadog.py           # Datadog integration
└── tools/                    # Agent tools and capabilities
    └── [tool_modules]/       # Various tool implementations
```

## Development

The platform follows enterprise-grade development practices:
- **Modular**: Clean separation of concerns with pluggable components
- **Scalable**: Built for high-throughput agent operations
- **Observable**: Comprehensive monitoring and tracing
- **Configurable**: Environment-based and YAML configuration
- **Testable**: Clean interfaces and dependency injection
- **Secure**: Built-in PII protection and guardrails

## API Endpoints

### Chat with Agents
```http
POST /api/agents/chat
Content-Type: application/json

{
  "agent_name": "medical_followup",
  "user_id": "user-123",
  "session_id": "optional-session-id",
  "chat_input": {
    "conversation_turns": [
      {"speaker": "Patient", "text": "I have chest pain"},
      {"speaker": "Doctor", "text": "Can you describe it?"}
    ],
    "features": [
      {"feature_name": "max_followups", "feature_value": 5}
    ]
  }
}
```

### Response Format
```json
{
  "success": true,
  "user_id": "user-123",
  "session_id": "session-id",
  "result": {
    "followup_questions": ["Question 1", "Question 2"],
    "count": 2
  }
}
```

## Requirements

- Python 3.13+
- pipenv (for dependency management)
- Google ADK 1.14.1+
- LiteLLM 1.77.1+
- FastAPI 0.116.2+
- Pydantic 2.11.9+
- OpenAI, Anthropic, or Google API key

## Dependency Management

The project supports multiple dependency management approaches:

### Using pipenv (Recommended)
```bash
# Install dependencies
pipenv install

# Install with development dependencies
pipenv install --dev

# Run commands in the virtual environment
pipenv run python src/service/main.py
```

### Using pip with requirements.txt
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Deployment

The platform supports multiple deployment options:

- **Local Development**: `pipenv run uvicorn src.service.main:app --reload`
- **Docker**: Containerized deployment with multi-stage builds
- **Cloud**: AWS, Azure, GCP with auto-scaling
- **Kubernetes**: Helm charts for production deployments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your agent implementation
4. Update tests and documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
