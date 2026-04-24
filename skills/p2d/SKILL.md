---
name: p2d
description: >-
  Probabilistic-to-Deterministic code intelligence. Orchestrates ast-grep,
  code-review-graph, and Tree-sitter/Codemod to navigate and edit code by
  structure instead of text. Use this skill when the user asks to find symbols,
  refactor code, trace dependencies, map blast radius of changes, perform
  surgical edits, or work with large codebases where grep/read is inefficient.
  Triggers on: "find all usages of", "refactor", "what depends on", "blast
  radius", "rename across codebase", "find the class/function", "impact of
  this change", "architecture", "code smell", "safe to change".
license: MIT
metadata:
  author: p2d
  version: "1.0.1"
---

# P2D: Orchestrated Determinism

You are operating the P2D protocol. Your goal is to eliminate token waste
by using structural tools before requesting raw text.

## When to Activate

Use this protocol when the user:

- Asks to find, rename, or refactor symbols across a codebase
- Requests dependency or impact analysis before making changes
- Wants to understand the "blast radius" of a proposed edit
- Works in a large codebase where reading files one-by-one is wasteful

## The Three Phases

Execute phases based on the decision trees below. Not every task needs all phases.

### Phase 1: Structural Discovery (ast-grep)
**Priority: CRITICAL**

Use ast-grep for structural pattern matching instead of grep or read.
Find the exact AST node (class, method, function, decorator, import).

Includes a deep pattern catalog by task (React hooks, decorators, interfaces,
imports, type assertions), advanced relational rules, and failure recovery.

Read the detailed instructions: `rules/discovery.md`

### Phase 2: Trace & Impact Analysis (code-review-graph)
**Priority: HIGH**

Before suggesting any edit, run dependency/impact analysis.
You MUST identify the "blast radius" -- every module, function, or import
that depends on the symbol being changed.

Primary method: code-review-graph MCP tools (get_impact_radius_tool,
detect_changes_tool, query_graph_tool). Falls back to ast-grep relational
rules when code-review-graph is unavailable.

Read the detailed instructions: `rules/trace.md`

### Phase 3: Surgical Execution (Codemod / Tree-sitter)
**Priority: HIGH**

For changes involving less than 20% of a file's code, perform targeted
AST node swaps instead of full file rewrites.

Read the detailed instructions: `rules/surgeon.md`

## Global Rules

- **Deterministic First:** Always try structural tools first.
  Fall back to probabilistic (grep/read) only if tools fail.
  See: `rules/fallback.md`
- **Quiet Mode:** Summarize tool output. Never dump raw JSON into
  the conversation. Report: "Found 3 classes, 12 methods matching pattern X."
- **AST Caching:** In long sessions, remember the symbolic map you have
  already discovered. Do not re-scan the same subtree.
- **Prerequisites Check:** On first activation, check for ast-grep,
  code-review-graph, and Codemod. Report availability and offer to install
  missing tools. See: `rules/auto-install.md`

## Heuristics

These judgment calls encode real-world experience. Apply them automatically:

- **File size matters:** Files under 50 lines can be read whole. Files over
  500 lines should NEVER be read whole — always use targeted search.
- **ast-grep strictness:** Default `smart` strictness treats single and double
  quotes differently. Use `strictness: ast` when matching imports.
- **Pattern vs kind:** If a `pattern` search returns 0 matches but you know
  the symbol exists, switch to `kind` matching (e.g., `kind: function_definition`).
- **Quote sensitivity in Go:** `$TYPE` in Go matches both `MyType` and
  `*MyType` — no need for separate pointer/value receiver patterns.
- **Python decorator gotcha:** `@$DECORATOR` only matches bare decorators.
  For parameterized decorators like `@app.route("/path")`, use
  `kind: decorator` with `has`.
- **TSX angle brackets:** In `.tsx` files, always use `as` form for type
  assertions. Angle brackets conflict with JSX syntax.

## Workflow Execution

1. **Prerequisites check:** Verify tools are available (`rules/auto-install.md`)
2. **Classify the task:** Use the decision trees below to determine which phases to run
3. **Execute phases:** Run only the phases the decision tree requires
4. **Report:** What changed, what depends on it, and whether tests need updating

## Decision Trees

Use these decision trees to skip unnecessary phases and choose the right strategy.
Do NOT blindly run all three phases for every request.

### Is this an investigation or an edit?

```
User asks "find", "where", "list", "show", "count"
  → Phase 1 only. Report findings. Stop.

User asks "rename", "refactor", "change", "move", "remove"
  → Phase 1 → decision tree below.

User asks "what depends on", "blast radius", "impact of"
  → Phase 1 + Phase 2. Report blast radius. Stop unless user asks to proceed.
```

### What type of symbol is being changed?

```
Shared/public interface or type definition
  → ALWAYS run Phase 2 (trace). Risk is high.
  → Use code-review-graph get_impact_radius_tool for full blast radius.
  → Cross-reference with get_knowledge_gaps_tool for untested dependents.
  → Warn user about any bridge nodes (architectural chokepoints).

Exported function/class from a library module
  → Run Phase 2. Use query_graph_tool (callers, imports).
  → If callers span >3 files, use strategies.md multi-file strategy.

Private/internal function (used in 1-2 files)
  → Skip Phase 2. Apply Phase 3 directly after Phase 1.
  → Verify with type checker. No blast radius analysis needed.

React component, Flask route, or framework entry point
  → Run Phase 2 with get_affected_flows_tool.
  → These are execution flow entry points — changes cascade through flows.

Database model, API schema, or shared config
  → ALWAYS run Phase 2. These are high-risk changes.
  → Use architecture overview (get_architecture_overview_tool) to understand
    which code communities depend on this.
```

### What type of edit?

```
Simple rename (no signature change)
  → ast-grep -r directly. Verify with type checker.
  → Skip Phase 2 if private symbol. Run Phase 2 if public.

Signature change (add/remove params, change return type)
  → Phase 2 mandatory. Use query_graph_tool to find all callers.
  → Update callers systematically. Check strategies.md for the pattern.

Move/relocate module
  → Phase 2 mandatory. All importers must update.
  → Use semantic_search_nodes_tool for cross-repo impact.

Structural refactor (>20% of file)
  → Phase 2 recommended. Use standard Edit, not surgical.
  → The 20% rule: if the change is big, surgical AST edits are riskier
    than a clean rewrite of the affected region.
```

### Code smell signals

If Phase 1 discovery reveals any of these patterns near the target symbol,
flag them to the user before proceeding. See `rules/strategies.md` for detection
patterns and recommended actions.

- `as any` or double-assertion (`as unknown as X`) near changed interface
- Untested callers of a modified function
- Deprecated API usage in dependent code
- Hub node (highly connected symbol) being modified
- Bridge node (cross-community dependency) being changed

## Multi-Tool Strategies

For complex tasks, combine tools in ways an agent wouldn't naturally compose.
See `rules/strategies.md` for the full catalog:

- **Safe rename:** semantic search → refactor preview → blast radius → apply
- **Interface change risk:** impact radius → bridge detection → test gap analysis
- **Architecture-aware refactor:** community detection → hub/bridge analysis → targeted edit
