"""Core assembly logic — builds agent workspace files from agent definitions + system partials.

The assembler:
1. Globs numbered partials from all partials_dirs (framework + extensions)
2. Sorts globally by filename (numeric prefix determines order)
3. Renders template variables ({agent_name}, {agent_role}, {team_table})
4. Concatenates into a single SYSTEM.md
5. Writes agent files (IDENTITY.md, SOUL.md, MEMORY.md) untouched

Extension partials (e.g. notification protocol) are picked up automatically
when their directory is listed in runtime.json extensions.partials_dirs.
"""

import glob
import os
from typing import Optional

from .expert_loader import load_agent
from .platform import load_platform


def _glob_partials(partials_dirs: list[str]) -> list[str]:
    """Glob all .md.tmpl files from all partials directories, sorted by filename.

    Files are sorted by basename (e.g. 10-agent-header.md.tmpl sorts before
    40-notification-bus.md.tmpl) so numeric prefixes control order globally
    across framework and extension directories.
    """
    paths = []
    for d in partials_dirs:
        if os.path.isdir(d):
            paths.extend(glob.glob(os.path.join(d, "*.md.tmpl")))
    # Sort by filename (basename), not full path — ensures global ordering
    paths.sort(key=lambda p: os.path.basename(p))
    return paths


def _build_team_table(agent_name: str, team_agents: dict) -> str:
    """Build Markdown table rows for team directory.

    Args:
        agent_name: Current agent's display name (gets "(me)" marker).
        team_agents: Dict of agent_id -> {"name": ..., "role": ...}.

    Returns:
        Pipe-delimited table rows, one per line.
    """
    rows = []
    for agent in team_agents.values():
        name = agent["name"]
        role = agent["role"]
        marker = " (me)" if name == agent_name else ""
        rows.append(f"| {name}{marker} | {role} |")
    return "\n".join(rows)


def assemble_system_md(
    platform_id: str,
    agent_name: str,
    agent_role: str,
    team_agents: Optional[dict] = None,
    extra_partials_dirs: Optional[list[str]] = None,
    extra_vars: Optional[dict] = None,
) -> str:
    """Assemble SYSTEM.md from platform partials.

    Globs all numbered partials from the platform's partials directories
    (including any extension dirs), renders template variables, and
    concatenates into a single string.

    Args:
        platform_id: Platform identifier (e.g. "openclaw").
        agent_name: Agent display name.
        agent_role: Agent role description.
        team_agents: Dict of agent_id -> {"name": ..., "role": ...} for
                     team directory. If None, team directory partial is
                     rendered with an empty table.
        extra_partials_dirs: Additional partials directories to include
                             (appended to runtime.json's dirs).
        extra_vars: Additional template variables to substitute.

    Returns:
        Assembled SYSTEM.md content string.
    """
    rt = load_platform(platform_id)
    partials_dirs = rt["_partials_dirs"]
    if extra_partials_dirs:
        partials_dirs = partials_dirs + extra_partials_dirs

    # Build template variables — include volume paths from runtime.json
    # so partials can reference {agent_workspace}, {team_shared}, etc.
    volumes = rt.get("volumes", {})
    team_table = _build_team_table(agent_name, team_agents) if team_agents else ""
    template_vars = {
        "agent_name": agent_name,
        "agent_role": agent_role,
        "team_table": team_table,
        "agent_workspace": volumes.get("agent_workspace", ""),
        "team_shared": volumes.get("team_shared", ""),
    }
    if extra_vars:
        template_vars.update(extra_vars)

    # Glob, render, concatenate
    partial_paths = _glob_partials(partials_dirs)
    sections = []
    for path in partial_paths:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        # Templates use {var} for substitutions and {{ / }} for literal braces.
        # format_map raises KeyError on unrecognised placeholders (e.g. bash
        # ${VAR}), so the try/except falls back to raw content on failure.
        try:
            rendered = content.format_map(template_vars)
        except (KeyError, ValueError):
            rendered = content
        sections.append(rendered.strip())

    return "\n\n".join(sections) + "\n"


def assemble_agent_workspace(
    platform_id: str,
    agent_id: str,
    agent_name: str,
    agent_role: str,
    output_dir: str,
    agents_dirs: list[str],
    team_agents: Optional[dict] = None,
    extra_partials_dirs: Optional[list[str]] = None,
    extra_vars: Optional[dict] = None,
) -> dict:
    """Assemble a complete agent workspace directory.

    Writes agent files (IDENTITY.md, SOUL.md, MEMORY.md) and the assembled
    SYSTEM.md into output_dir.

    Args:
        platform_id: Platform identifier.
        agent_id: Agent identifier (references a directory under agents_dirs).
        agent_name: Agent display name.
        agent_role: Agent role description.
        output_dir: Absolute path to the agent workspace directory.
        agents_dirs: Directories to search for agent definitions.
        team_agents: Team roster for team directory partial.
        extra_partials_dirs: Additional partials directories.
        extra_vars: Additional template variables.

    Returns:
        Dict with keys: identity, soul, memory, system (file contents written).
    """
    rt = load_platform(platform_id)
    platform_dir = rt["_platform_dir"]
    files_cfg = rt.get("files", {})

    # Load agent files (with platform override fallback)
    agent = load_agent(agent_id, agents_dirs=agents_dirs, platform_dir=platform_dir)

    os.makedirs(output_dir, exist_ok=True)

    # Write agent files — only if not already present (preserves agent edits)
    agent_files = {
        files_cfg.get("identity", "IDENTITY.md"): agent["identity"],
        files_cfg.get("soul", "SOUL.md"): agent["soul"],
        files_cfg.get("memory", "MEMORY.md"): agent["memory"],
    }
    for filename, content in agent_files.items():
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

    # Write USER.md template if not present
    user_tmpl = os.path.join(platform_dir, "system", "USER.md.tmpl")
    user_filename = files_cfg.get("user", "USER.md")
    user_path = os.path.join(output_dir, user_filename)
    if not os.path.exists(user_path) and os.path.isfile(user_tmpl):
        with open(user_tmpl, encoding="utf-8") as f:
            user_content = f.read()
        with open(user_path, "w", encoding="utf-8") as f:
            f.write(user_content)

    # Assemble and write SYSTEM.md — always overwritten (protocol updates)
    system_content = assemble_system_md(
        platform_id=platform_id,
        agent_name=agent_name,
        agent_role=agent_role,
        team_agents=team_agents,
        extra_partials_dirs=extra_partials_dirs,
        extra_vars=extra_vars,
    )
    system_filename = files_cfg.get("system", "SYSTEM.md")
    with open(os.path.join(output_dir, system_filename), "w", encoding="utf-8") as f:
        f.write(system_content)

    return {
        "identity": agent["identity"],
        "soul": agent["soul"],
        "memory": agent["memory"],
        "system": system_content,
    }
