---
title: Multi-Tool Strategies & Code Smell Detection
impact: HIGH
impactDescription: Combines tools in non-obvious ways that encode architectural judgment
tags: strategies, orchestration, code smell, architecture, cross-tool, decision
---

## Multi-Tool Strategies & Code Smell Detection

This rule contains two types of encoded expertise:

1. **Multi-tool strategies** — sequences combining tools in ways an agent
   wouldn't naturally compose. Each strategy produces insight that no single
   tool can provide alone.

2. **Code smell detection** — structural patterns that indicate risk near
   a change site. Flag these to the user before proceeding with edits.

---

## Multi-Tool Strategies

### Strategy: Safe Rename Across Codebase

When the user asks to rename a symbol that might exist in multiple forms.

1. **Discover all forms:** Use ast-grep to find the symbol in different
   syntactic positions (declaration, reference, import, string literal).
   ```bash
   sg -p 'oldName' -l ts --json
   sg -p '"oldName"' -l ts          # string references
   sg -p "import { oldName } from '$SRC'" -l ts  # imports
   ```

2. **Preview the rename:** Use code-review-graph's refactor tool.
   Call `refactor_tool` with rename preview. This shows exactly what changes
   without applying anything.

3. **Check blast radius:** Call `get_impact_radius_tool` on files that
   reference the old name. Identify any callers in untested code.

4. **Check for test gaps:** Call `get_knowledge_gaps_tool` to find
   untested hotspots among the affected files.

5. **Apply and verify:** If the user confirms, apply the rename.
   Run type checker and tests.

**Why multiple tools:** ast-grep finds syntactic matches but misses semantic
references (string-based lookups, reflection). code-review-graph finds
dependency edges but doesn't show the exact code. Together they give
complete coverage.

### Strategy: Interface Change Risk Assessment

Before changing a shared interface, type, or API contract.

1. **Find all implementors and consumers:**
   Call `query_graph_tool` with query types: `inheritance`, `callers`, `imports`.
   This finds every class that implements the interface and every function
   that calls methods on it.

2. **Is this a bridge node?**
   Call `get_bridge_nodes_tool`. If the symbol appears in the results,
   it connects two or more code communities. Changing it has outsized risk.
   Report: "This symbol is a bridge node connecting [Community A] and
   [Community B]. Changes here affect cross-cutting concerns."

3. **Is this a hub node?**
   Call `get_hub_nodes_tool`. If the symbol appears, it's one of the most
   connected nodes in the codebase. Changes cascade widely.
   Report: "This symbol is a hub with [N] connections. Changes here affect
   [N%] of the codebase."

4. **Find test coverage gaps:**
   Call `get_knowledge_gaps_tool`. Check if any dependents lack test coverage.
   Report: "3 of 8 dependents have no test coverage. Changes to these are
   highest risk for silent breakage."

5. **Check affected execution flows:**
   Call `get_affected_flows_tool` with the files containing the interface.
   This traces how the change propagates through actual execution paths.

**Risk report template:**
```
Interface Change Risk Assessment for [Symbol]:
  Risk level: HIGH
  Implementors: 4 classes across 2 communities
  Direct callers: 12 functions in 8 files
  Bridge node: YES (connects auth and API communities)
  Hub node: no
  Test coverage: 5/12 callers tested (58%)
  Affected execution flows: 3 (login, token-refresh, api-middleware)
  Untested critical paths: token-refresh
  Recommendation: Add tests for token-refresh before modifying this interface.
```

### Strategy: Architecture-Aware Refactoring

Before a significant refactoring, understand the architectural landscape.

1. **Get architecture overview:**
   Call `get_architecture_overview_tool`. This shows code communities,
   coupling warnings, and structural weaknesses.

2. **Identify affected communities:**
   Determine which communities contain the code being refactored.
   Changes within a community are lower risk than cross-community changes.

3. **Find surprising connections:**
   Call `get_surprising_connections_tool`. These are unexpected dependencies
   that the refactoring might accidentally break.

4. **Check hub and bridge nodes:**
   If the refactoring touches hub or bridge nodes, flag it.
   Hub nodes are architectural hotspots — changes here should be incremental.
   Bridge nodes connect communities — changes here need careful coordination.

5. **Plan incrementally:**
   If the refactoring spans multiple communities, split it into phases:
   - Phase A: Refactor within Community 1 (low risk)
   - Phase B: Update bridge between Community 1 and 2 (medium risk)
   - Phase C: Refactor within Community 2 (low risk)

### Strategy: Monorepo Cross-Package Change

When a change spans multiple packages in a monorepo.

1. **Register repos and search across them:**
   If using code-review-graph multi-repo, call `cross_repo_search_tool`
   to find the symbol across all packages.

2. **Map the dependency boundary:**
   Use `query_graph_tool` (imports) to find which packages import the
   symbol from another package.

3. **Check execution flows across packages:**
   Call `get_affected_flows_tool` to see if any user-facing flows
   traverse the package boundary.

4. **Apply changes package-by-package:**
   Start with the package that defines the symbol (upstream),
   then update consuming packages (downstream).

### Strategy: Validate Before Edit

Quick validation that an edit is safe before applying it.

1. **Check if the symbol is a hub or bridge** (1 call to get_hub_nodes_tool
   or get_bridge_nodes_tool). If yes → run full Phase 2.

2. **Check test coverage of direct dependents** (1 call to
   get_knowledge_gaps_tool). If dependents are untested → warn user.

3. **Run ast-grep to confirm the exact match set** for the planned edit.
   If match count differs from Phase 1 count → something is wrong.

4. **Apply the edit.** Run type checker immediately after.

---

## Code Smell Detection

When Phase 1 (discovery) finds the target symbol, also scan the surrounding
code for these risk indicators. Flag any findings to the user.

### Detection Patterns (ast-grep)

**TypeScript `as any` near changed code:**
```bash
sg -p '$EXPR as any' -l ts
```
Risk: An `as any` near the change site means the type system is already
bypassed there. The edit might silently break assumptions.

**Double assertion anti-pattern:**
```bash
sg -p '$EXPR as unknown as $TYPE' -l ts
```
Risk: Double assertions bypass TypeScript's safety net entirely.
Verify these still compile after the change.

**`@ts-ignore` / `@ts-expect-error` near change site:**
```bash
sg -p '// @ts-ignore' -l ts
sg -p '// @ts-expect-error' -l ts
```
Risk: These suppress type errors. After your edit, the suppressed error
may have changed or the suppression may now hide a new error.

**Non-null assertions on changed types:**
```yaml
id: non-null-assertion
language: ts
rule:
  kind: non_null_expression
```
Risk: `value!` asserts non-null. If the edit changes what `value` can be,
the assertion may now be invalid.

**Empty catch blocks near change site:**
```bash
sg -p 'catch ($ERR) { }' -l ts
```
Risk: Errors are silently swallowed. Your edit might introduce new error
paths that go unnoticed.

**Python bare `except`:**
```bash
sg -p 'except:' -l py
```
Risk: Catches all exceptions including KeyboardInterrupt. Changes to
code inside the try block may have unexpected failure modes.

**Python mutable default arguments:**
```bash
sg -p 'def $FUNC($$$ARGS, $PARAM=[])' -l py
sg -p 'def $FUNC($$$ARGS, $PARAM={})' -l py
```
Risk: Classic Python bug. If the edit involves a function with mutable
defaults, flag it regardless of what's being changed.

**Rust `unwrap()` on values that might change:**
```bash
sg -p '$EXPR.unwrap()' -l rust
```
Risk: If the edit changes what `EXPR` can produce, `.unwrap()` might panic.

### Detection Patterns (code-review-graph)

**Untested callers of modified function:**
Call `get_knowledge_gaps_tool` after Phase 2 (trace). If any direct callers
lack test coverage, report:
"Warning: 3 callers of [Function] have no test coverage. Changes here
cannot be validated by tests."

**Hub node being modified:**
Call `get_hub_nodes_tool`. If the target symbol appears, it's an architectural
hotspot. Report the connection count and affected communities.

**Bridge node being modified:**
Call `get_bridge_nodes_tool`. If the target appears, it connects code
communities that should be independently maintainable. Report the communities
and recommend testing the boundary.

**Large functions in blast radius:**
Call `find_large_functions_tool` with a threshold (e.g., 100 lines).
If functions in the blast radius exceed this, they're harder to reason about.
Recommend splitting before editing.

### How to Report Smells

Do NOT block the user. Present findings as risk indicators:

```
Pre-edit risk scan for [Symbol]:
  Code smells detected:
    - src/api.ts:42 — `as any` cast on modified type (type safety bypassed)
    - src/api.ts:108 — `@ts-ignore` within blast radius
    - src/utils.ts:15 — untested caller of modified function
  Architecture notes:
    - Symbol is a hub node (23 connections) — changes cascade widely
  Recommendation: Review `as any` and `@ts-ignore` locations after edit.
  Consider adding test for utils.ts:15 before proceeding.
```

### Anti-Patterns

- Do NOT treat every smell as a blocker — they are risk indicators
- Do NOT scan the entire codebase for smells — only scan within the blast radius
- Do NOT attempt to fix smells outside the scope of the user's request
