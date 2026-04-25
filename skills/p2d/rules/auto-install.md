---
title: Auto-Install & Prerequisites
impact: MEDIUM
impactDescription: Removes setup friction by detecting and offering to install missing tools
tags: setup, install, prerequisites, onboarding
---

## Auto-Install & Prerequisites

Run these checks once at the start of a P2D session, not on every invocation.
If a tool is missing, offer to install it. If the user declines, note which
phases will run in fallback mode.

If the user asks for "P2D doctor", "doctor mode", or "what mode will P2D use",
this is the rule to execute. Prefer the bundled helper when available:

```bash
skills/p2d/scripts/p2d-doctor --root .
```

### How to Check

Run each check via bash. Report a summary to the user before proceeding.

```bash
# Check ast-grep
sg --version 2>/dev/null

# Check code-review-graph (MCP server)
code-review-graph --version 2>/dev/null

# Check codemod
npx codemod --version 2>/dev/null
```

### Install Commands by Platform

**ast-grep** (required for Phase 1 & 3):

| Platform | Command |
|:---------|:--------|
| macOS | `brew install ast-grep` |
| npm (any) | `npm install --global @ast-grep/cli` |

**code-review-graph** (required for Phase 2 MCP integration):

Requires Python 3.10+. `uv` is recommended; code-review-graph uses `uvx` in MCP
configuration when available and falls back to the installed command otherwise.

| Platform | Command |
|:---------|:--------|
| pip (any) | `pip install code-review-graph` |
| pipx (any) | `pipx install code-review-graph` |

After installing, run `code-review-graph install` to auto-configure your
AI coding tool. To target one platform:

```bash
code-review-graph install --platform codex
code-review-graph install --platform claude-code
```

Restart the editor/tool after install. Then run `code-review-graph build` in
the project to parse the codebase.

**Codemod** (optional, for Phase 3 complex transforms):

| Platform | Command |
|:---------|:--------|
| npm (any) | `npm install -g codemod` |

### Startup Report Template

Present this to the user on first activation:

```
P2D Prerequisites Check:
  ast-grep:           ✓ v0.x.x  (Phase 1 & 3)
  code-review-graph:  ✓ v0.x.x  (Phase 2 MCP)
  codemod:            ✗ not found (Phase 3 optional, ast-grep covers most cases)

All critical tools available. P2D ready.
```

or:

```
P2D Prerequisites Check:
  ast-grep:           ✗ not found
  code-review-graph:  ✓ v0.x.x

ast-grep is missing. P2D will run in degraded mode:
  Phase 1 (Discovery): fallback to targeted grep
  Phase 3 (Surgeon):   fallback to native Edit tool

Install ast-grep for full capability:
  brew install ast-grep       (macOS)
  npm install --global @ast-grep/cli (any)

Proceed in degraded mode? [y/n]
```

### Principles

- Never silently skip a tool check — always report what's available
- Never auto-install without user confirmation
- If all tools are missing, P2D still works in pure fallback mode
  (see `rules/fallback.md`), but the user should know the limitations
