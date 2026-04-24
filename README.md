# P2D: Probabilistic-to-Deterministic Code Intelligence

An AI agent skill that orchestrates structural tools to navigate and edit code by AST structure instead of raw text. P2D moves AI behavior from **probabilistic** (guessing via grep/read) to **deterministic** (navigating via structure), reducing token consumption by 70-95%.

## How It Works

P2D runs three phases in sequence:

| Phase | Tool | Purpose |
|:------|:-----|:--------|
| **1. Discovery** | ast-grep | Find exact AST nodes without reading files |
| **2. Trace** | code-review-graph (MCP) | Map blast radius before editing |
| **3. Surgeon** | Tree-sitter / Codemod | Swap AST nodes instead of rewriting files |

When structural tools are unavailable, P2D gracefully falls back to targeted text-based search.

## Installation

```bash
npx skills add <owner>/p2d
```

Or from a local clone:

```bash
npx skills add ./p2d
```

## Prerequisites

P2D works best with these tools installed, but gracefully degrades when they're absent:

- **[ast-grep](https://ast-grep.github.io)** — Structural pattern matching (Phase 1 & 3)
- **[code-review-graph](https://github.com/tirth8205/code-review-graph)** — Dependency graph analysis via MCP (Phase 2)
- **[Codemod](https://codemod.com)** — Large-scale AST transformations (Phase 3)

## Repository Structure

```
p2d/
├── skills/p2d/
│   ├── SKILL.md              # The skill definition
│   ├── metadata.json         # Registry metadata
│   └── rules/
│       ├── discovery.md      # Phase 1: ast-grep structural search + pattern catalog
│       ├── trace.md          # Phase 2: blast radius + architecture-level analysis via MCP
│       ├── surgeon.md        # Phase 3: AST node replacement + failure recovery
│       ├── fallback.md       # Graceful degradation with heuristics
│       ├── auto-install.md   # Tool detection and auto-install
│       └── strategies.md     # Multi-tool orchestration + code smell detection
├── benchmark/                # Token comparison tooling
├── docs/                     # Design documentation
├── AGENTS.md                 # Contributor guide
└── README.md                 # This file
```

## Benchmarking

The `benchmark/` directory contains a tool that compares token usage between a standard agent workflow and a P2D-guided workflow. See [benchmark/README.md](benchmark/README.md) for details.

## License

MIT
