# P2D: Probabilistic-to-Deterministic Code Intelligence

An AI agent skill that orchestrates structural tools to navigate and edit code by AST structure instead of raw text. P2D moves AI behavior from **probabilistic** (guessing via grep/read) to **deterministic** (navigating via structure), reducing token consumption by 70-95%.

---

## Features

### Why should I use this skill instead of letting the AI grep and read files?

AI agents waste tokens reading entire files to find a single function, then re-reading them after edits. P2D teaches the agent to use structural tools (ast-grep, code-review-graph) that locate and modify code at the AST level — matching the exact node you need without ever reading the full file.

**Without P2D:**
```
Agent: "I'll find UserService"
→ grep -r "UserService" .              (reads all matches)
→ Read src/auth.ts                      (reads 800 lines for 1 class)
→ Read src/api.ts                       (reads 600 lines for 1 import)
→ Read src/models.ts                    (reads 400 lines for 1 reference)
→ Edit src/auth.ts                      (rewrites all 800 lines to change 3)
Token cost: ~4,500 tokens
```

**With P2D:**
```
Agent: "I'll find UserService"
→ sg -p 'class UserService { $$$ }' -l ts
→ "Found 1 match: src/auth.ts:42"
Token cost: ~50 tokens
```

### What makes P2D different from just telling the AI to use ast-grep?

P2D encodes judgment that a default agent doesn't have:

- **Decision trees** — automatically skips unnecessary analysis for private symbols, runs full blast radius for shared interfaces. The agent doesn't waste time on simple changes or skip analysis on risky ones.
- **Pattern catalog** — 50+ tested ast-grep patterns for React hooks, Python decorators, Go interfaces, Rust traits, import statements, and type assertions, including non-obvious gotchas (quote sensitivity, decorator matching, TSX conflicts).
- **Code smell detection** — automatically flags `as any` casts, untested callers, and architectural chokepoints near your change site before you edit.
- **Architecture-level reasoning** — uses code-review-graph to detect hub nodes (highly connected symbols), bridge nodes (cross-community dependencies), and execution flow impact. The agent understands *architectural risk*, not just file-level impact.
- **Multi-tool strategies** — combines tools in sequences an agent wouldn't naturally compose: semantic search → refactor preview → blast radius → test gap analysis.
- **Failure recovery** — when a structural search returns 0 matches unexpectedly, P2D has a recovery strategy (switch to `kind` matching, relax strictness, try different pattern forms).

### Does it work without installing anything?

Yes. P2D gracefully degrades:

| Tool installed | Capability |
|:---------------|:-----------|
| All three tools | Full P2D: structural discovery, architecture-aware blast radius, surgical AST edits |
| ast-grep only | Discovery + surgical edits via ast-grep. Trace phase uses targeted grep. |
| code-review-graph only | Blast radius + architecture analysis. Discovery uses targeted grep. |
| Nothing | Targeted grep with file-type filtering, git grep, line-range reads. Still minimizes tokens vs naive read-everything. |

The skill auto-detects available tools at session start and offers to install missing ones.

### What languages are supported?

**ast-grep** (25 languages): TypeScript, TSX, JavaScript, JSX, Python, Rust, Go, Java, C#, Ruby, Kotlin, Swift, Scala, PHP, C, C++, Bash, CSS, HTML, Elixir, Haskell, Lua, Solidity, Dart, YAML.

**code-review-graph** (23 languages): Python, TypeScript, JavaScript, Vue, Svelte, Go, Rust, Java, Scala, C#, Ruby, Kotlin, Swift, PHP, Solidity, C/C++, Dart, R, Perl, Lua, Zig, PowerShell, Julia, plus Jupyter notebooks.

### What kind of tasks does P2D handle?

| Task | How P2D handles it |
|:-----|:-------------------|
| "Find all usages of UserService" | ast-grep structural search. Reports file + line + context. ~50 tokens vs thousands. |
| "Rename OldService to NewService" | ast-grep replacement. Scans for string references too. Verifies with type checker. |
| "What depends on the Auth module?" | code-review-graph blast radius. Reports direct + transitive dependents, test coverage gaps. |
| "Is it safe to change this interface?" | Architecture analysis. Checks hub/bridge status, test gaps, execution flow impact. |
| "Refactor the payment module" | Community detection → incremental plan → surgical edits → verification. |
| "Add a parameter to processOrder()" | Finds all callers, updates signatures, verifies nothing breaks. |
| "What's the architecture of this codebase?" | code-review-graph community detection + hub/bridge analysis + coupling warnings. |
| "Any code smells near this change?" | Scans for `as any`, `@ts-ignore`, empty catches, untested callers, large functions. |

### How does P2D decide what to run?

Not every task needs all three phases. P2D uses decision trees to skip unnecessary work:

- **"Find X"** → Phase 1 only. Report. Stop.
- **"Rename private function X"** → Phase 1 → Phase 3 (skip trace, low risk).
- **"Change interface X"** → Phase 1 → Phase 2 (full blast radius) → Phase 3.
- **"What depends on X?"** → Phase 1 → Phase 2. Report blast radius. Stop.

The agent classifies the symbol type (private, exported, shared interface, framework entry point) and edit type (rename, signature change, move, refactor) to choose the right strategy automatically.

---

## How It Works

P2D runs up to three phases based on the task:

| Phase | Tool | Purpose |
|:------|:-----|:--------|
| **1. Discovery** | ast-grep | Find exact AST nodes without reading files |
| **2. Trace** | code-review-graph (MCP) | Map blast radius + architectural risk before editing |
| **3. Surgeon** | Tree-sitter / Codemod | Swap AST nodes instead of rewriting files |

When structural tools are unavailable, P2D falls back to targeted text-based search (git grep, line-range reads) with heuristics to minimize token waste.

---

## Installation

```bash
npx skills add AmineYagoub/p2d
```

Or from a local clone:

```bash
npx skills add ./p2d
```

## Prerequisites

P2D works best with these tools installed, but gracefully degrades when absent:

- **[ast-grep](https://ast-grep.github.io)** — Structural pattern matching across 25 languages. Install: `npm install -g @ast-grep/cli` or `brew install ast-grep`
- **[code-review-graph](https://github.com/tirth8205/code-review-graph)** — Persistent codebase graph with 28 MCP tools for dependency analysis, blast radius, community detection, and risk scoring. Install: `pip install code-review-graph && code-review-graph install && code-review-graph build`
- **[Codemod](https://codemod.com)** — Large-scale AST transformations and pre-built refactoring recipes. Install: `npm install -g codemod`

## Usage

After installing the skill, P2D activates automatically when your AI agent encounters matching requests. No configuration needed.

**Example prompts that trigger P2D:**

```
"Find all usages of UserService across the codebase"
"Rename OldService to NewService"
"What depends on the auth module?"
"Is it safe to change the PaymentInterface?"
"Refactor the notification module"
"What's the blast radius of changing this function signature?"
"Any code smells near the User model?"
```

On first activation, P2D checks which structural tools are available and reports capabilities:

```
P2D Prerequisites Check:
  ast-grep:           ✓ v0.37  (Phase 1 & 3)
  code-review-graph:  ✓ v2.1   (Phase 2 MCP)
  codemod:            ✗ not found (Phase 3 optional)

All critical tools available. P2D ready.
```

## Repository Structure

```
p2d/
├── skills/p2d/
│   ├── SKILL.md              # The skill definition (frontmatter + orchestration)
│   ├── metadata.json         # Registry metadata
│   └── rules/
│       ├── _sections.md      # Rule category index
│       ├── discovery.md      # Phase 1: ast-grep patterns, heuristics, failure recovery
│       ├── trace.md          # Phase 2: blast radius + architecture-level analysis via MCP
│       ├── surgeon.md        # Phase 3: AST node replacement + failure recovery
│       ├── fallback.md       # Graceful degradation with heuristics + caching
│       ├── auto-install.md   # Tool detection and platform-specific install
│       └── strategies.md     # Multi-tool orchestration + code smell detection
├── benchmark/                # Token comparison tooling
├── docs/                     # Design documentation
├── AGENTS.md                 # Contributor guide
└── README.md                 # This file
```

## Benchmarking

The `benchmark/` directory contains a tool that compares token usage between a standard agent workflow and a P2D-guided workflow. See [benchmark/README.md](benchmark/README.md) for details.

```bash
cd benchmark
python3 benchmark_tool.py --repo /path/to/target/repo --task tasks/find-usages.json
```

## License

MIT
