# Teams

Team composition templates — define which agents work together and how.

## Structure

```
teams/
├── _skeleton/           ← Copy this to create a new team
│   ├── template.json    Team metadata + agent roster
│   └── PURPOSE.md       Team mission and workflow
└── sample/              ← Example teams for reference
    └── ace/             4-role development team
```

## Creating a New Team

1. Copy `_skeleton/` to a new directory: `cp -r _skeleton/ my-group/my-team/`
2. Edit `template.json`:
   - Set a unique `id`, `display_name`, and `description`
   - Set `runtime` to your target platform (e.g., `"openclaw"`)
   - Define the `agents` array — each entry references an `agent_id` from `agents/`
   - Mark exactly one agent as `"is_master": true` (receives user messages)
3. Write `PURPOSE.md` — describe the team's mission and workflow

Teams can be organized in subdirectories (e.g., `sample/ace/`, `enterprise/security-team/`).
The framework discovers teams recursively — directory depth doesn't matter, only the
presence of `template.json`.

## Agent Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id_suffix` | yes | Unique suffix for the agent's container ID |
| `agent_id` | yes | References an agent definition from `agents/` |
| `name` | yes | Display name (used in team directory and prompts) |
| `role` | yes | Role description |
| `description` | no | What this agent does in the team |
| `is_master` | yes | `true` for exactly one agent — the team coordinator |

## Rules

- **`id` must be unique** across all teams regardless of directory
- **Exactly one `is_master: true` agent** per team
- All `agent_id` values must resolve to an existing agent definition
- Directories starting with `_` are ignored by the framework
