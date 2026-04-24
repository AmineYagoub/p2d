# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename used for each rule.

---

## 1. Structural Discovery (discovery)

**Impact:** CRITICAL
**Description:** The foundation of the P2D protocol. Use ast-grep structural pattern matching to locate exact AST nodes (classes, methods, decorators, imports) without reading entire files. Includes a deep pattern catalog organized by task (React hooks, decorators, interfaces, imports, type assertions), advanced relational rules, concrete heuristics, and failure recovery strategies.

## 2. Trace & Impact Analysis (trace)

**Impact:** HIGH
**Description:** Before any edit, map the dependency graph and calculate blast radius. Primary method uses code-review-graph MCP tools (get_impact_radius_tool, detect_changes_tool, query_graph_tool) for precise, persistent structural analysis. Falls back to ast-grep relational rules and targeted grep when unavailable.

## 3. Surgical Execution (surgeon)

**Impact:** HIGH
**Description:** For targeted changes (less than 20% of a file), perform AST node swaps using ast-grep replacement, Codemod, or native Edit tool instead of full-file rewrites. Includes real replacement patterns, verification steps, and failure recovery procedures.

## 4. Graceful Fallback (fallback)

**Impact:** MEDIUM
**Description:** When structural tools are unavailable or fail, fall back to probabilistic methods (git grep, targeted grep, ctags) in a controlled manner. Includes file size heuristics, caching strategy, and phase-specific fallback plans.

## 5. Auto-Install & Prerequisites (auto-install)

**Impact:** MEDIUM
**Description:** Detects missing structural tools (ast-grep, code-review-graph, Codemod) at the start of a P2D session and offers platform-specific install commands. Reports which phases will run in degraded mode if tools are unavailable.

## 6. Multi-Tool Strategies & Code Smell Detection (strategies)

**Impact:** HIGH
**Description:** Encodes architectural judgment through multi-tool orchestration strategies (safe rename, interface risk assessment, architecture-aware refactoring, monorepo cross-package changes) and code smell detection patterns (type safety bypasses, untested callers, hub/bridge nodes, empty catch blocks). Combines tools in non-obvious ways that no single tool can achieve alone.
