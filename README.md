# Pluggable Agent Framework (PAF)

A framework for defining, assembling, and deploying multi-agent teams on container-based AI agent platforms.

PAF separates **what an agent is** from **how it runs**. Agent authors define personas — identity, personality, memory — without touching infrastructure. Platform maintainers define system instructions, tool rules, and runtime configuration independently. The framework assembles both layers into ready-to-deploy agent workspaces.

## Why

Building multi-agent systems today means coupling agent definitions to a specific platform's plumbing. An agent's identity gets mixed with tool instructions, file path conventions, and collaboration protocols. This makes agents non-portable and forces contributors to understand platform internals just to define a new role.

PAF solves this by introducing a clear boundary:

- **Agent layer** — who the agent is (portable across platforms)
- **Platform layer** — how the agent runs (specific to each runtime)
- **Extension layer** — how the host application augments agents (collaboration, messaging, custom protocols)

## Installation

**From PyPI:**

```bash
pip install pluggable-agent-framework
```

**From GitHub (pinned to a release tag):**

```bash
pip install "pluggable-agent-framework @ git+https://github.com/sammyhuang/pluggable-agent-framework.git@v1.1.0"
```

**From a local clone (editable / development mode):**

```bash
git clone https://github.com/sammyhuang/pluggable-agent-framework.git
cd pluggable-agent-framework
pip install -e .
```

**Verify:**

```bash
python -c "from paf import assemble_system_md; print('OK')"
```

Requires Python 3.11+.

## Architecture

```
pluggable-agent-framework/
├── paf/                              Installable Python package
│   ├── __init__.py                   Re-exports public API
│   ├── assembler/                    Core library
│   │   ├── assemble.py              Glob partials → render → concatenate
│   │   ├── expert_loader.py         Load agent definitions with override fallback
│   │   ├── platform.py              Discover and load platform configs
│   │   └── team_loader.py           Load team templates
│   └── platforms/                    Bundled platform definitions (shipped with package)
│       └── openclaw/
│           ├── runtime.json          Image, ports, volumes, env, reload strategy
│           └── system/
│               ├── partials/         Numbered system instruction fragments
│               │   ├── 10-agent-header.md.tmpl
│               │   ├── 20-team-directory.md.tmpl
│               │   ├── 30-shared-dirs.md.tmpl
│               │   ├── 60-tool-recovery.md.tmpl
│               │   └── 70-edit-rules.md.tmpl
│               └── USER.md.tmpl      Template for agent-maintained user notes
│
├── agents/                           Sample agent definitions (not shipped with package)
│   ├── _skeleton/                    ← Copy this to create a new agent
│   │   ├── agent.json               Metadata: name, role, description, version
│   │   ├── IDENTITY.md              Who I am, what I do
│   │   ├── SOUL.md                  Values, communication style
│   │   └── MEMORY.md                Initial memory scaffold
│   └── sample/                       Example agents for reference
│       ├── coordinator/
│       ├── developer/
│       ├── designer/
│       └── tester/
│
├── teams/                            Sample team templates (not shipped with package)
│   ├── _skeleton/                    ← Copy this to create a new team
│   │   ├── template.json            Agent roster, platform reference
│   │   └── PURPOSE.md               Team mission and workflow
│   └── sample/                       Example teams for reference
│       └── ace/                      4-role development team
│
└── pyproject.toml                    Package build configuration
```

## How It Works

### 1. Define an Agent

Copy `agents/_skeleton/` and fill in the files (see `agents/sample/` for examples):

```
agents/my-group/security-auditor/
├── agent.json        Metadata: id, version, name, role, description
├── IDENTITY.md        "I am a security auditor. I review code for vulnerabilities..."
├── SOUL.md            "I am thorough but pragmatic. I prioritise impact over volume..."
└── MEMORY.md          ""
```

That's it. No infrastructure knowledge required. No tool configurations, no file paths, no protocol definitions. Agents can be nested in subdirectories — the framework discovers them recursively.

### 2. Compose a Team

Reference agents by ID in a team template:

```json
{
  "id": "security-team",
  "runtime": "openclaw",
  "agents": [
    { "id_suffix": "lead", "agent_id": "coordinator", "name": "Alex", "role": "Security Lead" },
    { "id_suffix": "auditor", "agent_id": "security-auditor", "name": "Sam", "role": "Security Auditor" }
  ]
}
```

### 3. Assemble

The assembler combines agent definitions with platform system instructions:

```python
from paf import assemble_agent_workspace, load_team, get_team_agents_dict

AGENTS_DIRS = ["/app/agents"]   # host app provides search paths
TEAMS_DIRS  = ["/app/teams"]

team = load_team("security-team", teams_dirs=TEAMS_DIRS)
team_agents = get_team_agents_dict(team)

for agent_def in team["agents"]:
    assemble_agent_workspace(
        platform_id="openclaw",
        agent_id=agent_def["agent_id"],
        agent_name=agent_def["name"],
        agent_role=agent_def["role"],
        output_dir=f"/data/teams/my-team/agents/{agent_def['id_suffix']}",
        agents_dirs=AGENTS_DIRS,
        team_agents=team_agents,
    )
```

Each agent workspace gets:
- `IDENTITY.md` — pure agent persona (from `agents/`)
- `SOUL.md` — agent personality (from `agents/`)
- `MEMORY.md` — initial memory (from `agents/`)
- `SYSTEM.md` — assembled platform instructions (from `platforms/`)
- `USER.md` — template for runtime user notes

## System Partials

Platform instructions are split into numbered partial files under `platforms/{id}/system/partials/`. The assembler globs all `*.md.tmpl` files, sorts by filename, renders template variables, and concatenates into a single `SYSTEM.md`.

Numbering controls order:

| Range | Purpose |
|-------|---------|
| 10-19 | Agent identity header |
| 20-29 | Team awareness |
| 30-39 | Workspace and file system |
| 40-49 | *Reserved for extensions* |
| 50-59 | *Reserved for extensions* |
| 60-69 | Tool policies |
| 70-79 | Tool-specific rules |

### Template Variables

Partials can use `{variable}` placeholders. The assembler provides:

| Variable | Source |
|----------|--------|
| `{agent_name}` | Agent's display name |
| `{agent_role}` | Agent's role description |
| `{team_table}` | Rendered Markdown team roster |
| `{agent_workspace}` | Container path from `runtime.json` volumes |
| `{team_shared}` | Shared directory path from `runtime.json` volumes |

Host applications can pass additional variables via `extra_vars`.

## Extension Points

Host applications extend PAF without modifying the framework:

### Additional Partials

Add partials directories via `runtime.json`:

```json
{
  "extensions": {
    "partials_dirs": ["/app/extensions/partials"]
  }
}
```

Or pass them at assembly time:

```python
assemble_agent_workspace(
    ...,
    extra_partials_dirs=["/app/extensions/partials"],
)
```

Extension partials use the same numbering scheme. Drop a `40-messaging.md.tmpl` into the extension directory and it slots between shared-dirs (30) and tool-recovery (60) automatically.

### Additional Environment Variables

```json
{
  "extensions": {
    "env_extra": {
      "MY_API_URL": "{MY_API_URL}",
      "MY_API_TOKEN": "{MY_API_TOKEN}"
    }
  }
}
```

### Platform-Specific Agent Overrides

If an agent needs different content on a specific platform, place override files at:

```
platforms/{platform_id}/agents/{agent_id}/IDENTITY.md
```

The assembler checks for platform-specific overrides before falling back to the shared definition.

## Adding a New Platform

Create a directory under `platforms/` with a `runtime.json` and system partials:

```
platforms/my-platform/
├── runtime.json
└── system/
    └── partials/
        ├── 10-agent-header.md.tmpl
        └── ...
```

The `runtime.json` defines container image, port mappings, volume paths, environment variable mappings, and reload strategy. See `platforms/openclaw/runtime.json` for a complete example.

Reference the platform in team templates:

```json
{ "runtime": "my-platform" }
```

## Design Principles

- **Agent definitions are portable.** An agent written for one platform works on another. Platform-specific adaptation happens in the platform layer, not the agent layer.
- **System instructions are the platform's concern.** Tool rules, file paths, and operational protocols live in system partials — agent authors never see them.
- **Extensions are additive.** Host applications add capabilities (messaging, monitoring, custom protocols) by dropping partials into an extension directory. No framework code changes needed.
- **Convention over configuration.** Numbered partials, standard file names, directory-based discovery. Minimal boilerplate.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
