---
title: Whole-Agent Cost Discipline
impact: MEDIUM
impactDescription: Keeps planning, editing, testing, recovery, and reporting proportional after P2D activates
tags: cost, discipline, testing, recovery, reporting, token savings
---

## Whole-Agent Cost Discipline

Apply this rule only after P2D has activated. It does not broaden P2D's trigger
surface and it is not generic coding-agent guidance. Its job is to keep the
rest of the agent loop as disciplined as discovery.

### How To Execute

1. **Reason compactly.** Report findings, uncertainty, and next action. Avoid
   long architecture essays unless the user asks for one.
2. **Plan to the task size.** Tiny tasks need no formal plan. Medium tasks need
   a short 3-5 step plan. Large refactors need a checklist.
3. **Edit surgically.** Do not rewrite whole files for small changes. Prefer
   previewed match sets and line-specific edits.
4. **Test narrowly first.** Run the most related test, type check, or syntax
   check before escalating to package or full-suite tests.
5. **Recover deliberately.** Inspect the exact failure, fix the smallest likely
   cause, and rerun targeted verification. Avoid noisy trial-and-error loops.
6. **Report briefly.** Default final answer: what changed, what was verified,
   and any residual risk.
7. **Stop unrelated reads.** Once the recall target is satisfied, do not open
   extra files "just in case".

### Anti-Patterns

- Turning a small edit into a full architecture review.
- Running the full test suite before a targeted check would answer the question.
- Pasting large logs instead of summarizing the failing lines.
- Re-planning after every command when no new evidence changed the path.
- Using this rule to trigger P2D for generic styling, copy, typo, or greenfield
  implementation tasks.
