---
title: "Project Status"
requires:
  - api_token
apis:
  items:
    url: https://api.example.com/projects/${PROJECT_ID}/items?state=open&per_page=30
    auth: ${API_TOKEN}
    refresh: 120
  releases:
    url: https://api.example.com/projects/${PROJECT_ID}/releases?per_page=10
    auth: ${API_TOKEN}
    refresh: 300
---

<!--
================================================================================
SAMPLE — generic project status dashboard for a master/coordinator agent
================================================================================
This is a working sample, not a production template. Adapt it to your data:

  • Replace `api.example.com` with your actual API host.
  • Add the magic tokens your host platform supports to `requires:` (e.g.
    `git_pat` on Clawborate, or any custom variable name your runtime
    resolves). See your host's documentation.
  • Use `${VAR}` in URLs and `auth:` references; the proxy substitutes
    them server-side so credentials never reach the browser.

This sample uses two API definitions (`items`, `releases`) and three body
sections (open items table, releases bullet list, an inline progress demo).
The optional 4th positional arg of {{apitable}} / {{apilist}} becomes the
section heading and gets "(N)" appended once data lands.

For the full token + frontmatter spec, see:
  agents/UI_EXTENSIONS.md
================================================================================
-->

{{apitable:items:title,owner,status,due_on:Open Items}}

{{apilist:releases:tag_name:Recent Releases}}

---

## Manual Progress Snippet

For static progress visualisation that doesn't come from an API, use the
inline `{{progress:open:closed}}` token:

{{progress:3:21}}

(3 open / 21 closed → 87% complete.)
