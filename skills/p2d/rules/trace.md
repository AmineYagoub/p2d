---
title: Trace and Impact Analysis via code-review-graph
impact: HIGH
impactDescription: Prevents regressions by mapping blast radius before edits
tags: trace, dependency analysis, impact, blast radius, code-review-graph, MCP
---

## Trace and Impact Analysis

Before suggesting any code edit, map the dependency graph to understand
the "blast radius" of the proposed change. This phase prevents regressions
by identifying every module, function, or import that depends on the target.

### Prerequisites

Before using code-review-graph MCP tools, check if it's installed and the
graph is built. If not, offer to install or fall back to ast-grep/grep.

```bash
code-review-graph --version 2>/dev/null || echo "code-review-graph not found"
code-review-graph status 2>/dev/null || echo "graph not built"
```

If missing, explain that code-review-graph requires Python 3.10+ and suggest:

```bash
pip install code-review-graph
# or: pipx install code-review-graph

code-review-graph install --platform codex
# or: code-review-graph install --platform claude-code

code-review-graph build
```

Restart the editor/tool after `code-review-graph install`. `uv` is recommended;
code-review-graph will use `uvx` in MCP configuration when available.

If the user declines, use the fallback methods documented later in this rule.

### When to Use This Rule

- Before renaming a symbol
- Before changing a function signature
- Before removing or moving a module
- Before modifying shared types or interfaces
- Any time the user asks "what will this affect?"

---

## Primary Method: code-review-graph MCP Tools

code-review-graph builds a persistent structural map of the codebase using
Tree-sitter, stored as a SQLite graph. It provides 28 MCP tools for
dependency analysis, blast radius, and risk scoring.

### Prerequisites

1. code-review-graph must be installed with Python 3.10+:
   `pip install code-review-graph` or `pipx install code-review-graph`
2. The target AI tool must be configured:
   ```bash
   code-review-graph install --platform codex
   code-review-graph install --platform claude-code
   ```
   Use only the platform command relevant to the user's tool.
3. The graph must be built for the current repo:
   ```bash
   code-review-graph build
   ```
   Or via MCP tool: `build_or_update_graph_tool`
4. Initial build takes ~10s for 500 files. Subsequent updates are incremental (<2s).

### Key MCP Tools for Trace Phase

**`get_impact_radius_tool`** — Blast radius of changed files.
Returns every caller, dependent, and test that could be affected.
Use this when you know which files will change.

**`detect_changes_tool`** — Risk-scored change impact analysis.
Maps diffs to affected functions, execution flows, and test coverage gaps.
Use this for code review scenarios.

**`query_graph_tool`** — Direct graph queries.
Supports: callers, callees, tests, imports, inheritance queries for any symbol.
Use this for targeted dependency lookups.

**`get_review_context_tool`** — Token-optimized review context.
Returns the minimal set of files the AI needs to read, with structural summary.

### How to Execute

1. **Ensure the graph is current:**
   Call `build_or_update_graph_tool` to verify the graph is built and up-to-date.

2. **Query the blast radius:**
   For a known symbol or file, call `get_impact_radius_tool` with the target.
   For a diff/change set, call `detect_changes_tool`.

3. **For specific dependency queries:**
   Call `query_graph_tool` with the symbol name and query type
   (callers, callees, tests, imports, inheritance).

4. **Report to the user BEFORE making changes:**

```
Blast radius for [Symbol]:
  Direct dependents (3):
    - src/auth.ts: function validateToken (line 42) — imports Symbol
    - src/api.ts: class AuthMiddleware (line 15) — calls Symbol
    - src/utils.ts: function helper (line 88) — references Symbol
  Transitive dependents (2):
    - src/routes.ts — via api.ts:AuthMiddleware
    - tests/auth.test.ts — test file
  Risk assessment: MEDIUM (5 files affected, 1 test file)
  Proceed with surgical update? [y/n]
```

5. **Only proceed after the user confirms** the blast radius is acceptable.

---

## Architecture-Level Analysis

When code-review-graph is available, go beyond simple blast radius.
Use these tools to understand the *architectural significance* of the change,
not just which files are affected.

### Hub Node Detection

**Tool:** `get_hub_nodes_tool`

Hub nodes are the most-connected symbols in the codebase. If the target
symbol is a hub, changes cascade widely and should be incremental.

**How to use:**
1. Call `get_hub_nodes_tool` to get the list of hubs
2. Check if the target symbol appears in the results
3. If yes, report the connection count and which communities it touches

**Report format:**
"Symbol [X] is a hub node with [N] connections spanning [M] communities.
Changes here have wide blast radius. Consider incremental edits."

### Bridge Node Detection

**Tool:** `get_bridge_nodes_tool`

Bridge nodes connect otherwise separate code communities. They represent
cross-cutting dependencies that should be minimal. Changing a bridge node
risks breaking the boundary between communities.

**How to use:**
1. Call `get_bridge_nodes_tool`
2. Check if the target symbol appears
3. If yes, report which communities it connects

**Report format:**
"Symbol [X] is a bridge node connecting [Community A] and [Community B].
This is a cross-community dependency. Changes need testing in both communities."

### Community Detection

**Tool:** `list_communities_tool`, `get_community_tool`

Communities are clusters of related code detected via the Leiden algorithm.
Understanding which communities are affected helps plan incremental changes.

**How to use:**
1. After blast radius analysis, identify which communities contain affected files
2. If the change spans communities, plan community-by-community
3. Changes within one community are lower risk than cross-community changes

**Decision rule:**
- Change within 1 community → low risk, proceed
- Change spans 2-3 communities → medium risk, use bridge node analysis
- Change spans 4+ communities → high risk, recommend splitting into phases

### Execution Flow Analysis

**Tools:** `list_flows_tool`, `get_flow_tool`, `get_affected_flows_tool`

Execution flows trace how data and control move through the codebase from
entry points (API handlers, CLI commands, event listeners).

**How to use:**
1. Call `get_affected_flows_tool` with the files being changed
2. This shows which user-facing flows pass through the changed code
3. Prioritize testing flows with highest criticality scores

**Report format:**
"Affected execution flows:
  1. POST /api/auth/login (criticality: HIGH) — passes through changed auth.ts
  2. GET /api/users/:id (criticality: MEDIUM) — indirectly affected via UserService
  3. Background job: email-sender (criticality: LOW) — uses unchanged code path"

### Knowledge Gap Analysis

**Tool:** `get_knowledge_gaps_tool`

Identifies structural weaknesses: untested hotspots, isolated nodes,
thin communities, and missing test coverage.

**How to use:**
1. After blast radius analysis, call `get_knowledge_gaps_tool`
2. Cross-reference: are any affected files flagged as untested hotspots?
3. If yes, recommend adding tests before making changes

**Decision rule:**
- All affected files have tests → proceed
- Some affected files lack tests → warn user, recommend adding tests first
- Critical path has no tests → strongly recommend adding tests, offer to write them

### Minimal Context Retrieval

**Tool:** `get_minimal_context_tool`

When the agent needs to understand a region of code but wants to minimize
token consumption, this tool returns ultra-compact context (~100 tokens)
covering the essential structure.

**When to use:**
- You need to understand what a file does but don't need to read it fully
- You want to verify the graph's understanding before querying further
- Quick sanity check before a more targeted query

### When to Use Architecture Analysis

| Situation | Use architecture tools? |
|:----------|:------------------------|
| Private function, 1-2 files affected | No — simple blast radius is sufficient |
| Shared interface, 5+ files affected | Yes — check hub/bridge status |
| Refactoring spanning multiple modules | Yes — community detection + flow analysis |
| User asks "is this safe to change?" | Yes — full architecture assessment |
| Entry point (API handler, CLI command) | Yes — execution flow analysis |

---

## Fallback: ast-grep Relational Rules

When code-review-graph is not installed or the graph has not been built,
use ast-grep relational rules for dependency tracing.

### Find all usages of a symbol

```bash
# Find any reference to SymbolName
sg -p '$NAME' -l ts --json
```

### Find imports of a module

```bash
# Find all files that import from a specific source
sg -p 'import { $$$ } from "$SOURCE"' -l ts
```

### Find callers of a function

```yaml
id: callers
language: ts
rule:
  pattern: "$FUNC($$$ARGS)"
  # Combine with known function name
```

### Find implementations of an interface

```yaml
id: interface-impls
language: ts
rule:
  pattern: "class $CLASS implements $INTERFACE { $$$ }"
```

### Find type references

```yaml
id: type-refs
language: ts
rule:
  pattern: "$TYPE"
  # Use kind: type_identifier for more precision
```

---

## Fallback: Targeted grep

When neither code-review-graph nor ast-grep is available:

```bash
# Find all references with surrounding context
grep -rn -B2 -A2 "SymbolName" --include="*.ts" --include="*.tsx" src/

# Find imports specifically
grep -rn "import.*SymbolName" --include="*.ts" src/

# Find test files referencing the symbol
grep -rn "SymbolName" --include="*.test.ts" --include="*.spec.ts" .
```

---

## Token Savings

- Standard approach: read every potentially-affected file = thousands of tokens
- code-review-graph: 1 MCP query + structured summary = ~100-300 tokens
- ast-grep fallback: 1 command + summary = ~200-400 tokens

## Anti-Patterns

- NEVER skip this phase, even if you think the change is "simple"
- NEVER assume a change is isolated without verification
- Do NOT proceed with edits until the user confirms the blast radius
- Do NOT use code-review-graph CLI commands like `crg analyze` — the tool
  operates via MCP, not CLI flags
