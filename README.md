# P2D: Probabilistic-to-Deterministic Code Intelligence

An AI agent skill that orchestrates structural tools and bundled fallback scripts
to navigate and edit code by structure instead of raw text. P2D moves AI
behavior from **probabilistic** (guessing via grep/read) to **deterministic and
measurable** (categorized discovery, impact analysis, and recall-aware
benchmarks).

---

## Features

### Why should I use this skill instead of letting the AI grep and read files?

AI agents waste tokens reading entire files to find a single function, then re-reading them after edits. P2D teaches the agent to use structural tools (ast-grep, code-review-graph) that locate and modify code at the AST level — matching the exact node you need without ever reading the full file.

**Real-world test** — task: "Which services inject PrismaService in a NestJS monorepo (1,772 source files, 36 files reference PrismaService)?"

Standard agent approach:

```
→ grep -rn "PrismaService" --include="*.ts" .     (72 matches across 36 files)
→ Read order.service.ts                            (740 lines — needed 1 line)
→ Read sales.service.ts                            (200 lines — needed 1 line)
→ Read otp.service.ts                              (312 lines — needed 1 line)
→ ... 33 more files to read to get the full picture
Token cost: ~20,000+ tokens to read all 36 files
```

P2D approach:

```
→ grep -rn "private.*PrismaService" --include="*.ts" .    (constructor injections)
→ grep -rn "PrismaService" --include="*.module.ts" .      (module registrations)
→ grep -rln "import.*PrismaService" --include="*.ts" .    (import statements)
→ Summarize: "18 services inject PrismaService. 20 modules register it. 36 files total."
Token cost: ~150 tokens — and a MORE complete answer than reading every file
```

Result: large token savings are possible, but P2D now treats savings as valid
only when recall is reported too. The categorized summary (injections vs modules
vs imports) is useful because it can be checked against explicit expected
references instead of relying on a lower token count alone.

### What makes P2D different from just telling the AI to use ast-grep?

P2D encodes judgment that a default agent doesn't have:

- **Decision trees** — the agent doesn't run all phases blindly. It skips Phase 2 for private functions and always runs it for shared interfaces. That's judgment.
- **Encoded expertise** — the heuristics (quote sensitivity in ast-grep, decorator matching gotchas, Go receiver matching, TSX angle bracket conflicts) are things most agents would only learn after multiple failed attempts. They're now baked in.
- **Architecture reasoning** — hub nodes, bridge nodes, community detection, execution flows. The agent understands architectural risk, not just file-level impact. No agent does this on its own.
- **Code smell detection** — the agent doesn't just find what you asked for, it warns you about nearby risks (`as any` casts, untested callers) before you edit.
- **Failure recovery** — when a pattern returns 0 matches, the skill has a recovery strategy. Most agents just give up.
- **State ownership mapper** — before creating new state (provider, context, store), P2D scans for existing state owners in the same domain. Prevents split-brain bugs where two separate sources of truth diverge.
- **Deletion test** — simulate removing a module and see exactly what would break, before touching any code. No more "simple cleanup" turning into a multi-day rescue.
- **Runnable harness** — scripts for prerequisite checks, symbol discovery,
  rename previews, deletion simulation, state mapping, and recall-aware
  benchmarking.

### Does it work without installing anything?

Yes. P2D gracefully degrades:

| Tool installed         | Capability                                                                                                           |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------- |
| All three tools        | Full P2D: structural discovery, architecture-aware blast radius, surgical AST edits                                  |
| ast-grep only          | Discovery + surgical edits via ast-grep. Trace phase uses targeted grep.                                             |
| code-review-graph only | Blast radius + architecture analysis. Discovery uses targeted grep.                                                  |
| Nothing                | Targeted grep with file-type filtering, git grep, line-range reads. Still minimizes tokens vs naive read-everything. |

The skill auto-detects available tools at session start and offers to install missing ones.

### What languages are supported?

**ast-grep** (25 languages): TypeScript, TSX, JavaScript, JSX, Python, Rust, Go, Java, C#, Ruby, Kotlin, Swift, Scala, PHP, C, C++, Bash, CSS, HTML, Elixir, Haskell, Lua, Solidity, Dart, YAML.

**code-review-graph** (23 languages): Python, TypeScript, JavaScript, Vue, Svelte, Go, Rust, Java, Scala, C#, Ruby, Kotlin, Swift, PHP, Solidity, C/C++, Dart, R, Perl, Lua, Zig, PowerShell, Julia, plus Jupyter notebooks.

### What kind of tasks does P2D handle?

| Task                                        | How P2D handles it                                                                          |
| :------------------------------------------ | :------------------------------------------------------------------------------------------ |
| "Find all usages of UserService"            | ast-grep structural search. Reports file + line + context. ~50 tokens vs thousands.         |
| "Rename OldService to NewService"           | ast-grep replacement. Scans for string references too. Verifies with type checker.          |
| "What depends on the Auth module?"          | code-review-graph blast radius. Reports direct + transitive dependents, test coverage gaps. |
| "Is it safe to change this interface?"      | Architecture analysis. Checks hub/bridge status, test gaps, execution flow impact.          |
| "Refactor the payment module"               | Community detection → incremental plan → surgical edits → verification.                     |
| "Add a parameter to processOrder()"         | Finds all callers, updates signatures, verifies nothing breaks.                             |
| "What's the architecture of this codebase?" | code-review-graph community detection + hub/bridge analysis + coupling warnings.            |
| "Any code smells near this change?"         | Scans for `as any`, `@ts-ignore`, empty catches, untested callers, large functions.         |
| "Where does user state live?"               | State ownership mapper. Scans providers, contexts, stores. Detects split-brain bugs.        |
| "Can I delete this module?"                 | Deletion test. Simulates removal, reports runtime breaks, test failures, type-only imports. |

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

| Phase            | Tool                    | Purpose                                              |
| :--------------- | :---------------------- | :--------------------------------------------------- |
| **1. Discovery** | ast-grep                | Find exact AST nodes without reading files           |
| **2. Trace**     | code-review-graph (MCP) | Map blast radius + architectural risk before editing |
| **3. Surgeon**   | Tree-sitter / Codemod   | Swap AST nodes instead of rewriting files            |

When structural tools are unavailable, P2D falls back to targeted text-based search (git grep, line-range reads) with heuristics to minimize token waste.

## Runnable Harness

The skill includes dependency-light scripts under `skills/p2d/scripts/`:

```bash
skills/p2d/scripts/p2d-doctor --root .
skills/p2d/scripts/p2d-find-symbol UserService --root .
skills/p2d/scripts/p2d-safe-rename-preview OldService NewService --root .
skills/p2d/scripts/p2d-deletion-sim ./src/feature --root .
skills/p2d/scripts/p2d-state-map user auth session --root .
skills/p2d/scripts/p2d-fetch-benchmark-repo nestjs-typescript-starter
skills/p2d/scripts/p2d-run-all-benchmarks
skills/p2d/scripts/p2d-benchmark-summary
```

Benchmarks report token savings with recall and precision. If recall drops,
the benchmark fails instead of presenting the lower token count as success.
External benchmark repos are pinned in `skills/p2d/benchmarks/repos.json` and
cloned into `.p2d-bench/`, which is ignored by git.

Current pinned external profiles:

| Profile | Targets | Latest Local Result |
| :------ | ------: | :------------------ |
| `nestjs-typescript-starter` | 2 | 100% recall, 100% precision, 51-59% savings |
| `react-redux-realworld` | 3 | 100% recall, 100% precision, 89-94% savings |

Generated aggregate benchmark JSON is written to `benchmark/results/` and is
ignored by git. Use `p2d-benchmark-summary` to render the latest result as a
Markdown table for release notes or PR descriptions.

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
"Where does user state live?"
"Can I delete this module safely?"
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
│   ├── agents/openai.yaml    # UI metadata
│   ├── scripts/              # Runnable P2D harness
│   ├── references/           # Evaluation criteria
│   └── rules/
│       ├── _sections.md      # Rule category index
│       ├── discovery.md      # Phase 1: ast-grep patterns, heuristics, failure recovery
│       ├── trace.md          # Phase 2: blast radius + architecture-level analysis via MCP
│       ├── surgeon.md        # Phase 3: AST node replacement + failure recovery
│       ├── fallback.md       # Graceful degradation with heuristics + caching
│       ├── auto-install.md   # Tool detection and platform-specific install
│       ├── strategies.md     # Multi-tool orchestration + code smell detection + deletion test
│       ├── state-mapper.md   # State ownership + split-brain detection
│       └── benchmark.md      # Agent-run benchmark procedure
├── AGENTS.md                 # Contributor guide
├── test/fixtures/p2d/        # Dev-only benchmark and safety fixtures
└── README.md                 # This file
```

## Benchmarking

Ask your agent to measure P2D savings on your actual codebase:

```
run P2D benchmarks
```

The agent will run `p2d-doctor`, establish expected references, then compare
standard file-reading cost against P2D categorized output. Reports include
tokens, savings, recall, precision, false negatives, and false positives.

## Commit-Ready Verification

Before committing this version, run:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-run-all-benchmarks
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-benchmark-summary
git status --short
```

For local development of the skill itself, the fixture smoke test uses
dev-only fixtures from `test/fixtures/p2d/`:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-fixture-check
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-benchmark UserService \
  --root test/fixtures/p2d/typescript-nest \
  --expected test/fixtures/p2d/expected/typescript-nest-UserService.json
```

Expected benchmark result:

| Repo | Symbol | Recall | Precision |
| :--- | :----- | -----: | --------: |
| `nestjs-typescript-starter` | `AppService`, `AppController` | 100% | 100% |
| `react-redux-realworld` | `ArticleList`, `Header`, `articleList` | 100% | 100% |

Generated files under `benchmark/results/` and cloned repos under `.p2d-bench/`
should remain untracked.

## License

MIT
