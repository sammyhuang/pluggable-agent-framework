"""Pluggable Agent Framework — assembler.

Assembles expert definitions + platform system partials into agent workspace files.
"""

from .assemble import assemble_system_md, assemble_agent_workspace
from .expert_loader import load_expert, list_experts
from .platform import load_platform, list_platforms
from .team_loader import load_team, list_teams, get_team_agents_dict

__all__ = [
    "assemble_system_md",
    "assemble_agent_workspace",
    "load_expert",
    "list_experts",
    "load_platform",
    "list_platforms",
    "load_team",
    "list_teams",
    "get_team_agents_dict",
]
