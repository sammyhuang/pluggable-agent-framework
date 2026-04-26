"""Agent definition loading with platform-specific override support.

Agent definitions are NOT auto-discovered from the PAF repo.
The host application provides search directories at runtime via the
agents_dirs parameter. The repo's agents/ folder contains only
skeletons (_skeleton/) and samples (sample/) for reference.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_AGENT_META = "agent.json"


def _read_text(path: str) -> str:
    """Read a text file, return empty string if missing."""
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _walk_agent_dirs(agents_dirs: list[str]) -> list[tuple[str, str]]:
    """Recursively find all agent directories containing agent.json.

    Skips directories whose name starts with '_' (skeletons/templates).
    Returns list of (agent_id, absolute_path) tuples.
    Warns on duplicate IDs — first occurrence wins.
    """
    results = []
    seen: dict[str, str] = {}
    for base_dir in agents_dirs:
        if not os.path.isdir(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = sorted(d for d in dirs if not d.startswith("_"))
            if _AGENT_META in files:
                agent_id = os.path.basename(root)
                if agent_id in seen:
                    logger.warning(
                        "Duplicate agent id '%s': %s (keeping %s)",
                        agent_id, root, seen[agent_id],
                    )
                    continue
                seen[agent_id] = root
                results.append((agent_id, root))
    return sorted(results, key=lambda x: x[0])


def list_agents(agents_dirs: list[str]) -> list[dict]:
    """Return list of agent metadata dicts from given directories.

    Args:
        agents_dirs: List of directory paths to search for agent definitions.
    """
    agents = []
    for _, path in _walk_agent_dirs(agents_dirs):
        meta_path = os.path.join(path, _AGENT_META)
        with open(meta_path, encoding="utf-8") as f:
            agents.append(json.load(f))
    return agents


def get_agent_dir(agent_id: str, agents_dirs: list[str]) -> Optional[str]:
    """Return absolute path to an agent directory, or None if not found.

    Args:
        agent_id: Agent identifier (directory name).
        agents_dirs: List of directory paths to search.
    """
    for aid, path in _walk_agent_dirs(agents_dirs):
        if aid == agent_id:
            return path
    return None


def load_agent(agent_id: str, agents_dirs: list[str],
               platform_dir: Optional[str] = None) -> dict:
    """Load agent files with platform-specific override support.

    Resolution order for each file (IDENTITY.md, SOUL.md, MEMORY.md):
      1. platform_dir/agents/{agent_id}/{file}  (platform-specific override)
      2. agents/{agent_id}/{file}                (shared default)

    Args:
        agent_id: Agent identifier (directory name).
        agents_dirs: List of directory paths to search for agent definitions.
        platform_dir: Optional absolute path to a platform directory.
                      If provided, platform-specific overrides are checked first.

    Returns:
        Dict with keys: id, identity, soul, memory, metadata.
    """
    shared_dir = get_agent_dir(agent_id, agents_dirs)
    if not shared_dir:
        raise FileNotFoundError(
            f"Agent '{agent_id}' not found in: {agents_dirs}"
        )

    # Load metadata from shared agent dir (always authoritative)
    meta_path = os.path.join(shared_dir, _AGENT_META)
    metadata = {}
    if os.path.isfile(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            metadata = json.load(f)

    # Resolve each file with platform override fallback
    def _resolve(filename: str) -> str:
        if platform_dir:
            override = os.path.join(platform_dir, "agents", agent_id, filename)
            if os.path.isfile(override):
                return _read_text(override)
        return _read_text(os.path.join(shared_dir, filename))

    return {
        "id": agent_id,
        "identity": _resolve("IDENTITY.md"),
        "soul": _resolve("SOUL.md"),
        "memory": _resolve("MEMORY.md"),
        "metadata": metadata,
    }


# ── Backward-compatible aliases ──
# Host apps written against the earlier "expert" naming still work.
list_experts = list_agents
get_expert_dir = get_agent_dir
load_expert = load_agent
