"""Pluggable Agent Framework — assembler.

Assembles agent definitions + platform system partials into agent workspace files.
"""

from .assemble import assemble_system_md, assemble_agent_workspace
from .expert_loader import (
    load_agent, list_agents, get_agent_dir,
    load_expert, list_experts, get_expert_dir,  # backward-compatible aliases
)
from .platform import load_platform, list_platforms, get_platform_data_path
from .team_loader import load_team, list_teams, get_team_agents_dict

__all__ = [
    "assemble_system_md",
    "assemble_agent_workspace",
    "load_agent",
    "list_agents",
    "get_agent_dir",
    "load_expert",    # alias for load_agent
    "list_experts",   # alias for list_agents
    "get_expert_dir", # alias for get_agent_dir
    "load_platform",
    "list_platforms",
    "get_platform_data_path",
    "load_team",
    "list_teams",
    "get_team_agents_dict",
]
