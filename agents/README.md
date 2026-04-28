# Agents

Agent definitions — portable personas that work across any PAF-supported platform.

## Structure

```
agents/
├── _skeleton/                       ← Copy this to create a new agent
│   ├── agent.json                   Metadata: id, version, name, role, description
│   ├── IDENTITY.md                  Who the agent is, what it does
│   ├── SOUL.md                      Values, personality, boundaries
│   ├── MEMORY.md                    Initial memory (can be empty)
│   └── ui-extensions.md.example     Optional, master-agent only — see UI_EXTENSIONS.md
├── UI_EXTENSIONS.md                 Spec for the optional ui-extensions.md file
└── sample/                          ← Example agents for reference
    ├── coordinator/                 includes a working ui-extensions.md sample
    ├── designer/
    ├── developer/
    └── tester/
```

## Creating a New Agent

1. Copy `_skeleton/` to a new directory: `cp -r _skeleton/ my-group/my-agent/`
2. Edit `agent.json` — set a unique `id`, `name`, `role`, and `description`
3. Write `IDENTITY.md` — define who the agent is and its responsibilities
4. Write `SOUL.md` — define personality, values, and boundaries
5. Optionally populate `MEMORY.md` with domain knowledge
6. (Master/coordinator agents only, optional) Rename `ui-extensions.md.example`
   to `ui-extensions.md` and customise to declare a dashboard tab. See
   [`UI_EXTENSIONS.md`](UI_EXTENSIONS.md) for the format spec, and
   [`sample/coordinator/ui-extensions.md`](sample/coordinator/ui-extensions.md)
   for a working example.

Agents can be organized in subdirectories (e.g., `sample/coordinator/`, `security/auditor/`).
The framework discovers agents recursively — directory depth doesn't matter, only the
presence of `agent.json`.

## Rules

- **`id` must be unique** across all agents regardless of directory
- **No platform-specific content** — agents should not reference file paths, tools, or protocols specific to any runtime
- Directories starting with `_` are ignored by the framework (used for skeletons/templates)
