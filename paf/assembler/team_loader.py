"""Team template loading.

Team definitions are NOT auto-discovered from the PAF repo.
The host application provides search directories at runtime via the
teams_dirs parameter. The repo's teams/ folder contains only
skeletons (_skeleton/) and samples (sample/) for reference.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def _walk_team_dirs(teams_dirs: list[str]) -> list[tuple[str, str]]:
    """Recursively find all team directories containing template.json.

    Skips directories whose name starts with '_' (skeletons/templates).
    Returns list of (team_id, absolute_path) tuples.
    Warns on duplicate IDs — first occurrence wins.
    """
    results = []
    seen: dict[str, str] = {}
    for base_dir in teams_dirs:
        if not os.path.isdir(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = sorted(d for d in dirs if not d.startswith("_"))
            if "template.json" in files:
                team_id = os.path.basename(root)
                if team_id in seen:
                    logger.warning(
                        "Duplicate team id '%s': %s (keeping %s)",
                        team_id, root, seen[team_id],
                    )
                    continue
                seen[team_id] = root
                results.append((team_id, root))
    return sorted(results, key=lambda x: x[0])


def list_teams(teams_dirs: list[str]) -> list[dict]:
    """Return list of team metadata from given team directories.

    Args:
        teams_dirs: List of directory paths to search for team definitions.
    """
    teams = []
    for _, path in _walk_team_dirs(teams_dirs):
        tmpl_path = os.path.join(path, "template.json")
        with open(tmpl_path, encoding="utf-8") as f:
            teams.append(json.load(f))
    return teams


def load_team(team_template_id: str, teams_dirs: list[str]) -> dict:
    """Load a team template definition.

    Args:
        team_template_id: Team identifier (directory name).
        teams_dirs: List of directory paths to search for team definitions.

    Returns:
        Parsed template.json with agents list, runtime reference, etc.
    """
    for tid, path in _walk_team_dirs(teams_dirs):
        if tid == team_template_id:
            tmpl_path = os.path.join(path, "template.json")
            with open(tmpl_path, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        f"Team template '{team_template_id}' not found in: {teams_dirs}"
    )


def get_team_agents_dict(team_template: dict) -> dict:
    """Build the team_agents dict from a team template for assembly.

    Returns:
        Dict of id_suffix -> {"name": ..., "role": ...}.
    """
    return {
        a["id_suffix"]: {"name": a["name"], "role": a["role"]}
        for a in team_template.get("agents", [])
    }
