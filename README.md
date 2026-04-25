# P2D

**P2D helps AI coding agents stop guessing, map the system before they edit,
and save tokens, time, and money.**

P2D moves agents from vibe coding to system-aware engineering. It teaches them
to find symbols structurally, map blast radius, preview risky edits, detect
state ownership, and report benchmark savings with recall and precision.

## Install

```bash
npx skills add AmineYagoub/p2d
```

Or from a local clone:

```bash
npx skills add ./p2d
```

## What It Handles

- Find definitions, imports, callers, and references without reading every file.
- Preview renames and signature changes before editing.
- Map dependency impact and blast radius.
- Simulate module deletion.
- Detect state ownership and split-brain state.
- Benchmark token savings with recall and precision.

## How To Use

After installing, ask your agent:

- `Run P2D doctor on this codebase and tell me what mode it will use.` — check available tools and fallback mode.
- `Find all usages of UserService without reading every file.` — discover definitions, imports, callers, and references.
- `Preview a safe rename from OldService to NewService.` — inspect the rename match set before editing.
- `Can I delete this module safely?` — simulate deletion risk and likely breakage.
- `Where does auth state live?` — map state ownership and split-brain risks.
- `Benchmark P2D on this codebase and show token savings with recall and precision.` — measure discovery savings honestly.

P2D also includes helper scripts under `skills/p2d/scripts/`, but most users
should invoke them through their agent.

## Current Benchmarks

Pinned public benchmark profiles currently show:

| Profile                       | Targets | Latest Local Result                         |
| :---------------------------- | ------: | :------------------------------------------ |
| `nestjs-typescript-starter`   |       4 | 100% recall, 100% precision, 51-61% savings |
| `react-redux-realworld`       |       5 | 100% recall, 100% precision, 85-94% savings |
| `full-stack-fastapi-template` |       4 | 100% recall, 100% precision, 85-95% savings |
| `golang-gin-realworld`        |       3 | 100% recall, 100% precision, 90-98% savings |
| `mini-redis`                  |       3 | 100% recall, 100% precision, 92-96% savings |
| `spring-petclinic`            |       4 | 100% recall, 100% precision, 89-96% savings |

These results prove broad coverage across 23 targets and 6 ecosystems. They are
still benchmark evidence, not a claim that every language/framework edge case is
solved.

P2D reduced token usage by 51.07% to 97.95% when finding symbol-related files
and reading the relevant context, compared with reading every matched file in
full.

It does not mean every coding task becomes 51.07% to 97.95% cheaper overall.
Total agent cost also includes reasoning, planning, editing, test output, error
recovery, explanations, and unrelated file reads. P2D mainly saves tokens in the
expensive part where agents usually waste context: find the symbol, read files,
understand impact.

## Development

Run the commit-ready checks:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-run-all-benchmarks
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-benchmark-summary
git status --short
```

Dev-only fixtures live in `test/fixtures/p2d/`:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-fixture-check
```

## Structure

```text
skills/p2d/
├── SKILL.md
├── agents/openai.yaml
├── benchmarks/repos.json
├── metadata.json
├── references/
├── rules/
└── scripts/
```

## License

MIT
