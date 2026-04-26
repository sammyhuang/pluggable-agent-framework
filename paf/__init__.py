"""Pluggable Agent Framework (PAF).

Convenience re-exports from paf.assembler so callers can write:
    from paf import assemble_system_md
"""

from .assembler import (
    assemble_system_md,
    assemble_agent_workspace,
    load_agent, list_agents, get_agent_dir,
    load_expert, list_experts, get_expert_dir,
    load_platform, list_platforms, get_platform_data_path,
    load_team, list_teams, get_team_agents_dict,
)

__all__ = [
    "assemble_system_md",
    "assemble_agent_workspace",
    "load_agent", "list_agents", "get_agent_dir",
    "load_expert", "list_experts", "get_expert_dir",
    "load_platform", "list_platforms", "get_platform_data_path",
    "load_team", "list_teams", "get_team_agents_dict",
]
