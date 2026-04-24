# AGENTS.md — Contributing to P2D

This guide is for contributors (human and AI) working on the P2D skill.

## Repository Conventions

- Skills live under `skills/{name}/SKILL.md`
- Rules live under `skills/p2d/rules/{category}.md`
- Rule filenames use lowercase, hyphenated names matching the section ID in `_sections.md`
- All files use LF line endings

## Adding a New Rule

1. Add an entry to `skills/p2d/rules/_sections.md` with the section name, impact level, and description
2. Create the rule file at `skills/p2d/rules/{name}.md`
3. Reference the new rule from `skills/p2d/SKILL.md` in the appropriate phase or global rules section

### Rule File Template

```markdown
---
title: [Rule Title]
impact: [CRITICAL | HIGH | MEDIUM | LOW]
impactDescription: One-line explanation of what this rule saves/prevents
tags: tag1, tag2, tag3
---

## [Rule Title]

[One-paragraph summary of what this rule does and why]

### When to Use This Rule

- [Condition 1]
- [Condition 2]

### How to Execute

1. [Step 1]
2. [Step 2]

### Token Savings

- Standard approach: [description] = [tokens]
- P2D approach: [description] = [tokens]

### Anti-Patterns

- [Pattern to avoid]
```

## Testing Changes

Install the skill locally to test:

```bash
npx skills add /path/to/p2d -g -a claude-code -y
```

Verify it was discovered:

```bash
npx skills add /path/to/p2d --list
```

## Release Process

1. Update `version` in both `skills/p2d/SKILL.md` frontmatter and `skills/p2d/metadata.json`
2. Commit with message: `chore: release v1.x.x`
3. Tag: `git tag v1.x.x`

## Running Benchmarks

Ask the agent to run benchmarks against the current codebase:

```
"run P2D benchmarks"
"show me the token savings"
```

The benchmark procedure is defined in `skills/p2d/rules/benchmark.md`.
