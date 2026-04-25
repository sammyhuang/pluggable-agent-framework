"""Platform discovery and runtime.json loading."""

import json
import os
from typing import Optional

_FRAMEWORK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PLATFORMS_DIR = os.path.join(_FRAMEWORK_ROOT, "platforms")


def list_platforms() -> list[str]:
    """Return list of available platform IDs (directory names under platforms/)."""
    if not os.path.isdir(_PLATFORMS_DIR):
        return []
    return sorted(
        d for d in os.listdir(_PLATFORMS_DIR)
        if os.path.isfile(os.path.join(_PLATFORMS_DIR, d, "runtime.json"))
    )


def get_platform_dir(platform_id: str) -> str:
    """Return absolute path to a platform directory."""
    return os.path.join(_PLATFORMS_DIR, platform_id)


def load_platform(platform_id: str) -> dict:
    """Load runtime.json for a platform.

    Returns the parsed JSON with resolved internal paths:
      _platform_dir: absolute path to the platform directory
      _partials_dirs: list of absolute paths to partials directories
                      (framework partials + any extension dirs)
    """
    platform_dir = get_platform_dir(platform_id)
    runtime_path = os.path.join(platform_dir, "runtime.json")
    if not os.path.isfile(runtime_path):
        raise FileNotFoundError(f"Platform '{platform_id}' not found: {runtime_path}")
    with open(runtime_path, encoding="utf-8") as f:
        rt = json.load(f)

    # Resolve partials directories
    base_partials = os.path.join(platform_dir, "system", "partials")
    partials_dirs = [base_partials]

    # Add extension partials dirs (from runtime.json extensions.partials_dirs)
    for extra in rt.get("extensions", {}).get("partials_dirs", []):
        if os.path.isabs(extra):
            partials_dirs.append(extra)
        else:
            partials_dirs.append(os.path.join(platform_dir, extra))

    rt["_platform_dir"] = platform_dir
    rt["_partials_dirs"] = partials_dirs
    return rt
