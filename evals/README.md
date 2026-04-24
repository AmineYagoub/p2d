# P2D Evals

These files are development-only evaluation assets for P2D. They are not part
of the installed-user runtime skill.

## Files

- `evals.json`: realistic task prompts and objective assertions.
- `trigger-evals.json`: should-trigger / should-not-trigger description evals.
- `agents/comparator.md`: blind A/B comparison guidance for with-skill vs
  without-skill outputs.

## Intended Workflow

1. Pick an eval from `evals.json`.
2. Run the prompt once with P2D available and once without P2D, or against an
   old skill snapshot.
3. Save outputs in an iteration workspace:
   - `p2d-workspace/iteration-N/<eval-id>/with_skill/outputs/`
   - `p2d-workspace/iteration-N/<eval-id>/without_skill/outputs/`
4. Grade objective assertions.
5. Use `agents/comparator.md` for blind A/B comparison.
6. Record timing and token usage when available.

The existing P2D benchmark harness remains the fallback quantitative path:

```bash
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-run-all-benchmarks
PYTHONDONTWRITEBYTECODE=1 skills/p2d/scripts/p2d-benchmark-summary
```

## Trigger Evals

Use `trigger-evals.json` to tune the `description` field in
`skills/p2d/SKILL.md`. Keep should-not-trigger examples near the boundary so
the description does not become a broad keyword trap.
