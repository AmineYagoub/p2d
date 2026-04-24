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

## Runtime Commands

The installed skill works as instructions, but also includes dependency-light
helpers:

```bash
skills/p2d/scripts/p2d-doctor --root .
skills/p2d/scripts/p2d-find-symbol UserService --root .
skills/p2d/scripts/p2d-safe-rename-preview OldService NewService --root .
skills/p2d/scripts/p2d-deletion-sim ./src/feature --root .
skills/p2d/scripts/p2d-state-map user auth session --root .
```

Optional benchmark commands:

```bash
skills/p2d/scripts/p2d-fetch-benchmark-repo nestjs-typescript-starter
skills/p2d/scripts/p2d-run-all-benchmarks
skills/p2d/scripts/p2d-benchmark-summary
```

External repos are cloned into `.p2d-bench/`, which is ignored by git.

## Current Benchmarks

Pinned public benchmark profiles currently show:

| Profile | Targets | Latest Local Result |
| :------ | ------: | :------------------ |
| `nestjs-typescript-starter` | 2 | 100% recall, 100% precision, 51-59% savings |
| `react-redux-realworld` | 3 | 100% recall, 100% precision, 89-94% savings |

These results prove the harness works for the current profiles. They do not yet
claim broad excellence across every language or framework.

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

Dev-only eval assets live in `evals/`. See:

- [docs/evaluation-process.md](docs/evaluation-process.md)
- [docs/description-optimization.md](docs/description-optimization.md)
- [docs/v1.3.0-excellence-plan.md](docs/v1.3.0-excellence-plan.md)

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
