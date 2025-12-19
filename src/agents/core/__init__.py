"""Core building blocks for Ship AI Agents.

This package contains the internal implementation of the BaseAgent and
related helpers. Most users should import `BaseAgent` and `AgentType`
from `src.agents.all_agents.base_agent` rather than from here directly.
"""

from .types import AgentType
from .base_agent import BaseAgent
