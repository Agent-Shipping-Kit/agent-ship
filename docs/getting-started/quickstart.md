# Quick Start

Create your first agent in minutes.

## Step 1: Create Agent Directory

```bash
mkdir -p src/agents/all_agents/my_agent
cd src/agents/all_agents/my_agent
```

## Step 2: Define Configuration

Create `main_agent.yaml`:

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: My custom agent
instruction_template: |
  You are a helpful assistant that answers questions clearly and concisely.
```

## Step 3: Implement Agent Class

Create `main_agent.py`:

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

## Step 4: Use Your Agent

```python
from src.models.base_models import AgentChatRequest
from src.agents.all_agents.my_agent.main_agent import MyAgent

agent = MyAgent()

request = AgentChatRequest(
    agent_name="my_agent",
    user_id="user-123",
    session_id="session-456",
    query="Hello, how are you?",
    features=[]
)

response = await agent.chat(request)
print(response.agent_response.text)
```

That's it! Your agent is automatically discovered and registered. No manual registration needed.

## Next Steps

- Learn about [Agent Patterns](../building-agents/patterns/single-agent.md)
- Add [Tools](../building-agents/tools.md) to your agent
- Configure [Advanced Settings](../getting-started/configuration.md)
