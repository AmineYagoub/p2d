---
title: Agent-Run Benchmarks
impact: MEDIUM
impactDescription: Measures token savings without hiding recall loss
tags: benchmark, measurement, token savings, recall, precision
---

## Agent-Run Benchmarks

When the user asks to run benchmarks, use the bundled harness instead of
improvising a token-only comparison. P2D is successful only when it reduces
tokens while preserving recall.

Benchmark claims are valid only for the discovery/context-reading workflow being
measured. Do not imply that the same percentage applies to total agent cost,
which also includes reasoning, planning, editing, tests, recovery, and
explanations.

### Prerequisites

Run the doctor first:

```bash
skills/p2d/scripts/p2d-doctor --root .
```

The benchmark works even when structural tools are missing, but the report must
label the mode as degraded/fallback.

### Trigger Phrases

- "run P2D benchmarks"
- "show me the token savings"
- "how much does P2D save?"
- "benchmark P2D on this codebase"
- "prove P2D works"

### Fixture Benchmark

Use the bundled fixture as a smoke test:

```bash
skills/p2d/scripts/p2d-benchmark UserService \
  --root test/fixtures/p2d/typescript-nest \
  --expected test/fixtures/p2d/expected/typescript-nest-UserService.json
```

This development benchmark fails if P2D misses an expected file. Installed
users do not need the `test/fixtures` directory unless they are validating
changes to the P2D skill itself.

### External Public Repo Benchmark

Public repos belong in `.p2d-bench/`, not in committed fixtures. Use pinned
profiles from `skills/p2d/benchmarks/repos.json`:

```bash
skills/p2d/scripts/p2d-fetch-benchmark-repo --list
skills/p2d/scripts/p2d-fetch-benchmark-repo nestjs-typescript-starter
```

Each profile must pin a commit SHA. Targets should include expected files so
recall is measured instead of inferred from the same search that P2D is testing.

### Run All Benchmarks

Before release or commit, run the aggregate command:

```bash
skills/p2d/scripts/p2d-run-all-benchmarks
```

This runs fixture checks and every external profile with configured targets.
It saves a timestamped JSON report under `benchmark/results/`, which is ignored
by git.

Render a Markdown summary from the latest saved result:

```bash
skills/p2d/scripts/p2d-benchmark-summary
```

### Real Codebase Benchmark

For a real repository:

1. Pick a symbol with a clear expected surface.
2. Build or approximate ground truth with exhaustive search and manual
   classification.
   Do not compare P2D output against a narrower search and claim equivalence.
3. Save expected files in JSON:

```json
{
  "symbol": "UserService",
  "files": [
    "src/auth.service.ts",
    "src/user.service.ts"
  ]
}
```

4. Run:

```bash
skills/p2d/scripts/p2d-benchmark UserService \
  --root . \
  --expected /tmp/p2d-expected-UserService.json
```

### Metrics To Report

Always report:

- Standard token estimate
- P2D token estimate
- Savings percentage
- Recall percentage
- Precision percentage
- False negatives
- False positives
- Tool availability from `p2d-doctor`

Never report savings without recall and precision. If recall is below the
configured threshold, the benchmark must fail and list the missing files.

### Report Template

```markdown
## P2D Benchmark Results

Codebase: [repo]
Mode: [full tools | ast-grep only | fallback]

| Symbol | Standard Tokens | P2D Tokens | Savings | Recall | Precision |
|:-------|----------------:|-----------:|--------:|-------:|----------:|
| UserService | 1420 | 248 | 82.54% | 100% | 100% |

False negatives: none
False positives: none
```

### What Makes This Honest

- Token savings are never reported without recall.
- Expected files are explicit and reviewable.
- The command exits non-zero when expected files are missed.
- Fallback mode is labeled instead of presented as full structural analysis.
- Savings mean "tokens avoided while finding symbol-related files and relevant
  context", not "total task cost reduction".

See `references/evaluation.md` for release targets.
