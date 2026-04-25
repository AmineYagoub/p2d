# P2D

Version: `v1.5.2` | Repository: [AmineYagoub/p2d](https://github.com/AmineYagoub/p2d)

**P2D helps AI coding agents stop guessing, map the system before they edit,
and save tokens, time, and money.**

P2D moves agents from vibe coding to system-aware engineering. It teaches an
agent to find the right code, map what depends on it, preview risky changes,
and report savings with recall and precision instead of vibes.

If you are asking an agent, "Should I use this skill here?", the answer is
usually **yes** when the task involves finding code, changing shared behavior,
removing code, renaming things, tracing impact, or avoiding accidental breakage.

## Why Use P2D

Most agents are tempted to solve codebase tasks by opening files, searching
loosely, guessing what matters, and editing once the local context feels good
enough. That works in small files, but it gets expensive and risky in real
projects.

P2D changes the default behavior: map first, edit second, and report evidence.

The practical result: less context waste, fewer missed call sites, clearer
blast-radius reports, and safer edits.

## When To Use It

Use P2D for codebase navigation:

- "Find all usages of `UserService`."
- "Where is this defined?"
- "Find the files I need to edit."
- "I don't know where this logic lives."

Use P2D before risky edits:

- "Rename this safely."
- "Change this API without breaking callers."
- "Update all related files."
- "Fix this without breaking anything else."

Use P2D for architecture and impact:

- "What depends on this?"
- "What is the blast radius?"
- "Why did changing this break other parts of the app?"
- "Is this dead code?"

Use P2D for state and deletion:

- "Where does auth state live?"
- "Who owns this data?"
- "Can I delete this module safely?"
- "What breaks if I remove this?"

## When Not To Use It

P2D is not meant for every task. Skip it for:

- Writing a brand-new feature with no existing codebase context.
- Styling or copy edits that touch one obvious file.
- Explaining a small function.
- Formatting, typos, or API design from scratch.

If a task starts simple but becomes "where else is this used?", switch to P2D.

## What It Handles

P2D is organized around three phases:

- **Structural discovery:** find definitions, imports, callers, references,
  tests, exports, and config mentions before reading full files.
- **Trace and impact analysis:** map the blast radius before editing shared
  symbols, modules, APIs, routes, or state.
- **Surgical execution:** preview and apply targeted edits instead of rewriting
  whole files for small changes.

It also includes doctor mode, safe rename preview, deletion simulation, state
ownership mapping, recall-aware benchmarks, and fallback mode when advanced
tools are unavailable.

## Install

General install:

```bash
npx skills add AmineYagoub/p2d
```

Install for Codex:

```bash
npx skills add AmineYagoub/p2d -g -a codex -y
```

Install for Claude Code:

```bash
npx skills add AmineYagoub/p2d -g -a claude-code -y
```

Or from a local clone:

```bash
npx skills add ./p2d -g -a codex -y
```

Then ask your agent to use it. You do not need to manually run scripts for most
workflows.

## How To Ask Your Agent

Use these prompts as-is:

- `Run P2D doctor on this codebase and tell me what mode it will use.` - check tools and fallback mode.
- `Find all usages of UserService without reading every file.` - discover definitions, imports, callers, and references.
- `Find the files I need to edit for this payment change.` - turn vague intent into a targeted file map.
- `Preview a safe rename from OldService to NewService.` - inspect the rename match set before editing.
- `What depends on this module before I change it?` - map blast radius.
- `Can I delete this module safely?` - simulate deletion risk and likely breakage.
- `Where does auth state live?` - map state ownership and split-brain risks.
- `Update all related files without breaking callers.` - combine discovery, impact, and targeted edits.
- `Benchmark P2D on this codebase and show token savings with recall and precision.` - measure discovery savings honestly.

For casual coding, this is enough:

```text
Use P2D. Find what this touches before changing it.
```

## Operating Modes

P2D adapts to the tools available in the project:

| Mode | Available tools | What happens |
| :--- | :-------------- | :----------- |
| Full | [ast-grep](https://github.com/ast-grep/ast-grep), [code-review-graph](https://github.com/tirth8205/code-review-graph), [Codemod](https://github.com/codemod/codemod) | Best structural discovery, graph tracing, and surgical edit previews. |
| Structural | [ast-grep](https://github.com/ast-grep/ast-grep), [Codemod](https://github.com/codemod/codemod) | Strong AST search and targeted edits, fallback dependency tracing. |
| Graph | [code-review-graph](https://github.com/tirth8205/code-review-graph), [Codemod](https://github.com/codemod/codemod) | Strong impact mapping, fallback text discovery. |
| Fallback | no structural tools | Targeted grep/git grep, line-range reads, and bundled scripts. |

Even fallback mode is useful. It is not "no P2D"; it is P2D with fewer
structural guarantees and more explicit reporting.

## Benchmarks

Pinned public benchmark profiles currently show:

| Profile | Targets | Latest Local Result |
| :------ | ------: | :------------------ |
| `nestjs-typescript-starter` | 4 | 100% recall, 100% precision, 51-61% savings |
| `react-redux-realworld` | 5 | 100% recall, 100% precision, 85-94% savings |
| `full-stack-fastapi-template` | 4 | 100% recall, 100% precision, 85-95% savings |
| `golang-gin-realworld` | 3 | 100% recall, 100% precision, 90-98% savings |
| `mini-redis` | 3 | 100% recall, 100% precision, 92-96% savings |
| `spring-petclinic` | 4 | 100% recall, 100% precision, 89-96% savings |

These results cover 23 targets across 6 ecosystems: TypeScript/NestJS, React,
FastAPI/Python, Go/Gin, Rust/Tokio, and Java/Spring.

Savings vary by target size and symbol spread: smaller or tightly clustered
symbols have less irrelevant context to skip, while larger cross-file symbols
leave more room for P2D to save tokens.

P2D reduced token usage by 50.84% to 97.95% when finding symbol-related files
and reading the relevant context, compared with reading every matched file in
full.

That does not mean every coding task becomes 50.84% to 97.95% cheaper overall.
Total agent cost also includes reasoning, planning, editing, test output, error
recovery, explanations, and unrelated file reads. P2D mainly saves tokens in the
expensive part where agents usually waste context: find the symbol, read files,
understand impact.

## Included Helpers

P2D works as an agent skill first. It also ships lightweight scripts under
`skills/p2d/scripts/` for repeatable workflows:

`p2d-doctor`, `p2d-find-symbol`, `p2d-safe-rename-preview`,
`p2d-deletion-sim`, `p2d-state-map`, `p2d-benchmark`,
`p2d-run-all-benchmarks`, and `p2d-benchmark-summary`.

Most users should invoke these through their agent. Contributors can run them
directly.

## Development

Run commit-ready checks:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-fixture-check
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-run-all-benchmarks
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-benchmark-summary
git diff --check
git status --short
```

Dev-only fixtures live in `test/fixtures/p2d/`. External benchmark repos are
cloned into `.p2d-bench/`, which is ignored by git.

## License

MIT
