# UI Extensions — `ui-extensions.md`

Optional **per-agent template file** that declares an interactive UI tab on
the host platform's dashboard. This is a *spec*; the file format is portable
across platforms, but the runtime that watches the file and renders the tab
is provided by the host (e.g. Clawborate, but any PAF host can implement it).

> **Optional and master-only.** Only the team's master/coordinator agent's
> `ui-extensions.md` is read by the runtime. Sub-agents may have one in their
> template directory, but it is ignored — the master owns the tab.

---

## File location

After a team is materialised on a host, each agent has its own workspace
directory. The runtime reads:

```
<agent-workspace>/ui-extensions.md
```

The file is shipped as part of the agent's template (alongside
`IDENTITY.md` / `SOUL.md` / `MEMORY.md`), copied into the workspace at team
creation time, and is freely editable by the agent at runtime.

## File format

YAML frontmatter + Markdown body. The body uses standard Markdown plus a
small set of `{{token}}` substitutions.

### Frontmatter

```yaml
---
title: "Project Status"        # tab label in the dashboard navbar
requires:                      # tab is hidden until every entry resolves
  - api_token                  # — list of ${VAR} names (case-insensitive)
apis:                          # per-API definition for live external data
  items:
    url: https://api.example.com/projects/${PROJECT_ID}/items?state=open
    auth: ${API_TOKEN}         # resolved server-side as Bearer auth
    headers:                   # optional explicit headers
      X-Custom: value
    refresh: 120               # seconds between client re-fetches (default 60)
---
```

#### `title`

The label that appears in the host's tab bar. Falls back to "UI" when omitted.

#### `requires`

A list of `${VAR}` names that must resolve to a non-empty value for the tab
to be reported `active`. The tab is hidden in the navbar until every name
resolves. This is what gates "show the dashboard once the user has set up
their token". Variable names are matched case-insensitively against the
host's resolution order (see below).

#### `apis`

Per-API key, defines an outbound HTTP call the runtime will make on the
client's behalf. The proxy lives on the host and resolves `${VAR}`
references **server-side** so credentials never reach the browser. Both the
`url` and the `auth` field accept `${VAR}` substitution.

### Body tokens

Each token is substituted at render time. Tokens not on the line they appear
are passed through unchanged.

| Token | Renders |
|---|---|
| `{{progress:open:closed[:label]}}` | Thin green progress bar + stats line ("X% complete · N open · N closed"). `open` and `closed` are integers; optional 3rd arg overrides the "complete" suffix. |
| `{{apitable:api_key:col1,col2,...[:Heading]}}` | Renders the API JSON array as a table with the given columns. Optional `Heading` becomes "`Heading (N)`" above the table where N is the row count. |
| `{{apilist:api_key:field[:Heading]}}` | Renders the API JSON array as a bullet list, displaying `field` per row. Optional `Heading` becomes "`Heading (N)`" above the list. |

### Auto-features (when row data is shaped like a GitHub-style resource)

These apply uniformly to `{{apitable}}` and `{{apilist}}` rows; they activate
when the corresponding fields exist in the API response. No author config.

- **`#NNN` reference prefix** — when a row has a `number` field, it is
  rendered in muted monospace before the title (e.g. `#142 Fix login bug`).
- **External-link icon** — when a row has an `html_url` field, a small ↗
  link follows the title, opening the resource in a new tab.
- **Title-cell progress bar** (apitable only) — when a row has both
  `open_issues` and `closed_issues` numeric fields, a thin progress bar
  renders beneath the title cell using `closed / (open+closed)` as the
  percentage. Matches the GitHub milestones page convention.

## `${VAR}` resolution

The runtime resolves `${VAR}` references in three places — `requires:`
entries, `apis.*.url` (URL substitution), and `apis.*.auth` (credential
substitution). Resolution order:

1. **Magic tokens** — host-defined names that resolve from platform state
   (e.g. Clawborate provides `${GIT_PAT}`, `${GIT_REPO}`, `${GIT_REPO_URL}`
   from a per-agent stored credential). Documented per host.
2. **Server environment variable** — `os.getenv(VAR_NAME)`.
3. **`ui_secrets.json`** — a JSON file in the agent workspace, written by
   the agent or operator, never served to the browser. Read by the host
   only for proxy substitution.

If a `requires:` entry resolves at any layer, the tab is eligible to
activate. If a URL or `auth:` reference fails to resolve, the proxy returns
HTTP 502 and the cell shows an error.

## Runtime contract (what a host platform must provide)

The file format above is portable; the runtime that brings it to life is
the host's responsibility. To implement the spec, a host needs:

| Capability | Notes |
|---|---|
| **Coordinator resolution** | Find the team's master agent and locate its `ui-extensions.md`. |
| **Frontmatter parser** | Extract `title`, `requires`, and the `apis:` block. The grammar is "two-space indent for keys, four-space indent for fields, six-space indent for headers" — see `paf/platforms/openclaw/system/partials/45-git-access.md.tmpl` (Clawborate) for a reference parser. |
| **`requires:` gate** | `GET /<host>/ui/state` must return `active=true` only when every `requires:` entry resolves to a non-empty value. |
| **Proxy endpoint** | `GET /<host>/ui/proxy/{api_key}` reads the frontmatter `apis:` block, substitutes `${VAR}` in URL + `auth`, calls the upstream with `Authorization: Bearer <auth>`, and returns the JSON body. |
| **WebSocket / poll** | Push file-change events to the browser so layout edits propagate within ~10 s. |
| **Skeleton renderer** | Parse body tokens and render the components above. The renderer should add **no chrome of its own** (no card-wrap, no toolbar, no headers) — the agent's MD body owns the entire visual flow. |

## Lifecycle

| State | `ui-extensions.md` | `requires:` | Tab visible? |
|---|---|---|---|
| Inactive (default) | absent | n/a | no |
| Pending credentials | present | not all resolved | no |
| Active | present | all resolved | **yes** |

Editing the body propagates within the runtime's poll/push interval (e.g.
~10 s). No agent step or notification is required to reveal the tab — when
the user satisfies `requires:`, the tab appears systemically.

## Authoring tips

- Keep the file **minimal**. Markdown body + a few tokens is usually enough.
- Use the **HTML comment block at the top** of `_skeleton/ui-extensions.md.example`
  as a self-documenting reference for anyone editing the file.
- If you need data in a non-standard shape, the host's `${VAR}` and proxy
  features are open-ended — declare a new `apis:` entry pointing anywhere.
- The renderer is intentionally a skeleton. If you need a card layout or
  custom header, write it in Markdown directly. The host won't add its
  own chrome.

## See also

- `agents/sample/coordinator/ui-extensions.md` — a working generic example.
- `agents/_skeleton/ui-extensions.md.example` — minimal scaffold for a new
  master agent.
- Clawborate's GitHub-flavored implementation:
  https://github.com/sammyhuang/clawborate/blob/master/agent-arch/openclaw/agents/coordinator/ui-extensions.md
