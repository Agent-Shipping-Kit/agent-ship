# Medical Followup Generation Agent

A simple, configurable AI agent that generates followup questions for medical conversations using Google ADK and LiteLLM.

## Features

- 🤖 **Google ADK Integration**: Built with Google's Agent Development Kit
- 🔄 **Multi-Model Support**: Works with OpenAI (GPT), Claude, and Google Gemini models via LiteLLM
- ⚙️ **Environment Configuration**: Easy configuration via environment variables
- 🏥 **Medical Focus**: Specialized prompts for medical conversation analysis
- 📝 **Simple API**: Clean, straightforward interface for generating followups

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run the agent**:
   ```bash
   # Run example
   uv run python src.main
   
   # Or use CLI
   uv run python cli.py "Patient: I have chest pain. Doctor: Can you describe it?"
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
uv run python cli.py "Patient: I have chest pain. Doctor: Can you describe it?"

# With context
uv run python cli.py "conversation.txt" --context '{"patient_age": "45", "chief_complaint": "Chest pain"}'

# Using Claude model
uv run python cli.py "conversation.txt" --model claude --model-name claude-3-5-sonnet-20241022

# Using Gemini model
uv run python cli.py "conversation.txt" --model gemini --model-name gemini-1.5-pro

# JSON output
uv run python cli.py "conversation.txt" --output json

# Custom parameters
uv run python cli.py "conversation.txt" --max-followups 3 --temperature 0.5
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
uv run python test_agent.py

# Test specifically with Gemini
uv run python test_gemini.py
```

## Architecture

The agent is built with a simple, clean architecture:

```
src/
├── agents/
│   └── followups_generation/
│       ├── __init__.py
│       └── agent.py          # Main agent implementation
├── shared/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         # Configuration management
│   └── infrastructure/
│       ├── __init__.py
│       └── llm_service.py    # LiteLLM wrapper
└── main.py                   # Example usage
```

## Development

The codebase follows a staff engineer approach:
- **Simple**: Minimal complexity, easy to understand
- **Configurable**: Environment-based configuration
- **Maintainable**: Clear separation of concerns
- **Testable**: Clean interfaces and dependency injection

## Requirements

- Python 3.13+
- Google ADK 1.14.1+
- LiteLLM 1.77.1+
- OpenAI or Anthropic API key
