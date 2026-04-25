"""Team template loading."""

import json
import os

_FRAMEWORK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEAMS_DIR = os.path.join(_FRAMEWORK_ROOT, "teams")


def list_teams() -> list[dict]:
    """Return list of team metadata from all team directories."""
    if not os.path.isdir(_TEAMS_DIR):
        return []
    teams = []
    for d in sorted(os.listdir(_TEAMS_DIR)):
        tmpl_path = os.path.join(_TEAMS_DIR, d, "template.json")
        if os.path.isfile(tmpl_path):
            with open(tmpl_path, encoding="utf-8") as f:
                teams.append(json.load(f))
    return teams


def load_team(team_template_id: str) -> dict:
    """Load a team template definition.

    Returns:
        Parsed template.json with agents list, runtime reference, etc.
    """
    tmpl_path = os.path.join(_TEAMS_DIR, team_template_id, "template.json")
    if not os.path.isfile(tmpl_path):
        raise FileNotFoundError(f"Team template '{team_template_id}' not found: {tmpl_path}")
    with open(tmpl_path, encoding="utf-8") as f:
        return json.load(f)


def get_team_agents_dict(team_template: dict) -> dict:
    """Build the team_agents dict from a team template for assembly.

    Returns:
        Dict of id_suffix -> {"name": ..., "role": ...}.
    """
    return {
        a["id_suffix"]: {"name": a["name"], "role": a["role"]}
        for a in team_template.get("agents", [])
    }
