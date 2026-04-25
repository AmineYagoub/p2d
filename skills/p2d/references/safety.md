---
title: P2D Safety Reference
---

# P2D Safety Reference

Use this reference when a P2D edit fails, a worktree is dirty, or a user asks
how to recover safely.

## Dirty Worktree Recovery

1. Inspect `git status --short`.
2. Inspect `git diff` for files touched during the current task.
3. Identify agent-owned hunks separately from pre-existing user work.
4. Revert only agent-owned hunks or ask the user before reverting a whole file.
5. Never use broad rollback that discards unrelated user changes.

## Rename And Signature Safety

- Preview the match set before mutation.
- Confirm definitions, imports, exports, calls, tests, strings, and config.
- Treat ast-grep replacements as sketches until the match set is reviewed.
- For signature changes, map all callers first and verify with type/tests.

## Reporting

When safety is uncertain, say what is known, what is unknown, and what should be
checked next. Do not present fallback text search as full structural proof.
