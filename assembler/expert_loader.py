"""Expert definition loading with platform-specific override support."""

import json
import os
from typing import Optional

_FRAMEWORK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AGENTS_DIR = os.path.join(_FRAMEWORK_ROOT, "agents")


def _read_text(path: str) -> str:
    """Read a text file, return empty string if missing."""
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def list_experts() -> list[dict]:
    """Return list of expert metadata dicts from all agent directories."""
    if not os.path.isdir(_AGENTS_DIR):
        return []
    experts = []
    for d in sorted(os.listdir(_AGENTS_DIR)):
        meta_path = os.path.join(_AGENTS_DIR, d, "expert.json")
        if os.path.isfile(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                experts.append(json.load(f))
    return experts


def get_expert_dir(expert_id: str) -> Optional[str]:
    """Return absolute path to an expert directory, or None if not found."""
    path = os.path.join(_AGENTS_DIR, expert_id)
    if os.path.isdir(path):
        return path
    return None


def load_expert(expert_id: str, platform_dir: Optional[str] = None) -> dict:
    """Load expert files with platform-specific override support.

    Resolution order for each file (IDENTITY.md, SOUL.md, MEMORY.md):
      1. platform_dir/agents/{expert_id}/{file}  (platform-specific override)
      2. agents/{expert_id}/{file}                (shared default)

    Args:
        expert_id: Expert identifier (directory name under agents/).
        platform_dir: Optional absolute path to a platform directory.
                      If provided, platform-specific overrides are checked first.

    Returns:
        Dict with keys: id, identity, soul, memory, metadata.
    """
    shared_dir = os.path.join(_AGENTS_DIR, expert_id)
    if not os.path.isdir(shared_dir):
        raise FileNotFoundError(f"Expert '{expert_id}' not found: {shared_dir}")

    # Load metadata from shared expert dir (always authoritative)
    meta_path = os.path.join(shared_dir, "expert.json")
    metadata = {}
    if os.path.isfile(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            metadata = json.load(f)

    # Resolve each file with platform override fallback
    def _resolve(filename: str) -> str:
        if platform_dir:
            override = os.path.join(platform_dir, "agents", expert_id, filename)
            if os.path.isfile(override):
                return _read_text(override)
        return _read_text(os.path.join(shared_dir, filename))

    return {
        "id": expert_id,
        "identity": _resolve("IDENTITY.md"),
        "soul": _resolve("SOUL.md"),
        "memory": _resolve("MEMORY.md"),
        "metadata": metadata,
    }
