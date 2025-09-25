from src.configs.llm_provider_config import (
    LLMModel, 
    LLMProviderName,
    LLMProviderConfig
)
import yaml


class AgentConfig:
    """
    Agent configuration for all agents.
    This configuration is used to configure the agent.
    It is used to configure the model provider, model, max followups, temperature, agent name, description, and instruction template.
    It is also used to validate that the model belongs to the correct provider.
    It is also used to load the agent configuration from a YAML file.
    It is also used to print the agent configuration.
    It is also used to get the agent configuration from a YAML file.
    """

    def __init__(self, llm_provider_name: LLMProviderName, llm_model: LLMModel = LLMModel.GPT_4O_MINI, 
                temperature: float = 0.4, agent_name: str='', description: str='', instruction_template: str=''):
        self.model_provider = LLMProviderConfig.get_llm_provider(llm_provider_name)
        self.model = llm_model
        self.temperature = temperature
        self.agent_name = agent_name
        self.description = description
        self.instruction_template = instruction_template

        # Validate that the model belongs to the correct provider
        if self.model not in self.model_provider.models:
            available_models = [llm_model.value for llm_model in self.model_provider.models]
            raise ValueError(
                f"Model '{self.model.value}' is not compatible with provider '{self.model_provider.name.value}'. "
                f"Available models for {self.model_provider.name.value}: {available_models}"
            )

    @classmethod
    def from_yaml(cls, file_path: str) -> 'AgentConfig':
        """Load agent configuration from a YAML file."""
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)

        return cls(
            llm_provider_name=LLMProviderName(config['llm_provider_name']),
            llm_model=LLMModel(config['llm_model']),
            temperature=config['temperature'],
            agent_name=config['agent_name'  ],
            description=config['description'],
            instruction_template=config['instruction_template']
        )

    def __str__(self):
        return f"AgentConfig(model_provider={self.model_provider.name.value}, model={self.model.value}, \
            temperature={self.temperature}, agent_name={self.agent_name}, description={self.description}, instruction_template={self.instruction_template})"

if __name__ == "__main__":
    agent_config = AgentConfig.from_yaml("src/agents/followups_generation/main_agent.yaml")
    print(agent_config)