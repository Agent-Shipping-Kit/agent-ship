"""Agent Registry - Backward compatibility module."""

# Import from the modular structure
from src.agent_registry import (
    registry,
    AgentRegistry,
    discover_agents,
    get_agent_instance,
    has_agent_instance,
    clear_agent_instance,
    clear_cache,
    register_agent,
    get_agent_class,
    list_agents,
    get_agent_info
)
import logging

logger = logging.getLogger(__name__)

# Maintain backward compatibility
__all__ = [
    'registry',
    'AgentRegistry',
    'discover_agents',
    'get_agent_instance', 
    'has_agent_instance',
    'clear_agent_instance',
    'clear_cache',
    'register_agent',
    'get_agent_class',
    'list_agents',
    'get_agent_info'
]


if __name__ == "__main__":
    
    # Use the global registry instance directly
    # Discover agents
    discover_agents()
    
    # List discovered agents
    logger.info("Discovered agents:")
    for agent_name in list_agents():
        info = get_agent_info(agent_name)
        logger.info(f"  {agent_name}: {info['class']} - {info['description']}")
    
    # Example of using an agent
    try:
        # Use the first available agent
        available_agents = list_agents()
        if available_agents:
            agent_name = available_agents[0]
            agent = get_agent_instance(agent_name)
            logger.info(f"agent instance: {type(agent).__name__}")
        else:
            logger.info("No agents available")
    except Exception as e:
        logger.error(f"Error creating agent: {e}")