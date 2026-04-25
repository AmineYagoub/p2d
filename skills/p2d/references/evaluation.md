---
title: P2D Evaluation Criteria
---

# P2D Evaluation Criteria

P2D is excellent only when it reduces tokens without hiding missed references.
Measure accuracy and savings together.

## Required Metrics

- **Recall:** percentage of expected files or references found.
- **Precision:** percentage of found files or references that are expected.
- **Token estimate:** command output and file-read characters divided by 4.
- **Savings:** standard token estimate vs P2D token estimate.
- **Mode:** full tools, ast-grep only, code-review-graph only, or fallback.
- **Safety:** whether the workflow avoided destructive commands and broad rewrites.

## Release Targets

- Symbol discovery fixtures: 100% recall.
- State ownership fixtures: all expected owner files reported.
- Deletion simulation fixtures: all runtime break candidates reported.
- Average token reduction: 70% or better on medium/large fixtures.
- No instruction may recommend broad rollback that discards unrelated user work.

## Reporting Rule

Never report token savings alone. Report savings with recall and precision:

```text
P2D found 5/5 expected files, recall 100%, precision 100%, savings 82.4%.
```

If recall is below 100%, say so plainly and list false negatives.
