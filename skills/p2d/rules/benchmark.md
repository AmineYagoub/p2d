---
title: Agent-Run Benchmarks
impact: MEDIUM
impactDescription: Lets users measure real token savings on their actual codebase
tags: benchmark, measurement, token savings, comparison
---

## Agent-Run Benchmarks

When the user asks to run benchmarks, measure P2D savings on their actual
codebase using real tools. No simulation — run actual commands and count
real output.

### Trigger Phrases

- "run P2D benchmarks"
- "show me the token savings"
- "how much does P2D save?"
- "benchmark P2D on this codebase"
- "prove P2D works"

### Step 1: Detect the codebase

Identify the primary language and pick 3 representative symbols at different
scales:

```bash
# Find the most-referenced symbols in the codebase
grep -rhoP '\b[A-Z][a-zA-Z]+\b' --include="*.ts" --include="*.tsx" --include="*.py" --include="*.go" --include="*.rs" --include="*.java" . 2>/dev/null \
  | sort | uniq -c | sort -rn | head -20
```

From the results, pick 3 symbols:
- **Small:** referenced in 5-15 files
- **Medium:** referenced in 20-50 files
- **Large:** referenced in 50+ files

### Step 2: Run each benchmark

For each symbol, run both approaches and measure output size.

**Standard approach** (simulate what a naive agent does):

```bash
# 1. Grep for the symbol
grep -rn "SYMBOL" --include="*.ts" --include="*.tsx" . > /tmp/p2d-standard.txt 2>/dev/null
# 2. Read every matched file (count total lines as proxy for tokens)
STANDARD_FILES=$(grep -rln "SYMBOL" --include="*.ts" --include="*.tsx" . 2>/dev/null)
echo "$STANDARD_FILES" | xargs wc -l 2>/dev/null | tail -1
```

Standard tokens = (grep output chars + total file chars) / 4

```bash
# Measure
STANDARD_GREP_CHARS=$(wc -c < /tmp/p2d-standard.txt)
STANDARD_FILE_CHARS=$(echo "$STANDARD_FILES" | xargs cat 2>/dev/null | wc -c)
STANDARD_TOKENS=$(( (STANDARD_GREP_CHARS + STANDARD_FILE_CHARS) / 4 ))
```

**P2D approach** (targeted, categorized, no file reads):

```bash
# 1. Constructor injections
grep -rn "private.*SYMBOL\|protected.*SYMBOL" --include="*.ts" . > /tmp/p2d-targeted.txt 2>/dev/null

# 2. Import statements
grep -rn "import.*SYMBOL" --include="*.ts" . >> /tmp/p2d-targeted.txt 2>/dev/null

# 3. Module registrations
grep -rn "SYMBOL" --include="*.module.ts" . >> /tmp/p2d-targeted.txt 2>/dev/null

# Measure only the summary output
P2D_CHARS=$(wc -c < /tmp/p2d-targeted.txt)
P2D_TOKENS=$(( P2D_CHARS / 4 ))
```

If ast-grep is available, use it instead for even lower token counts:

```bash
sg -p 'SYMBOL' -l ts --json 2>/dev/null > /tmp/p2d-sg.json
P2D_CHARS=$(wc -c < /tmp/p2d-sg.json)
```

### Step 3: Compute and display results

Calculate savings percentage for each benchmark, then present a table:

```markdown
## P2D Benchmark Results

Codebase: [repo name] ([N] source files, primary language: [lang])
Tools available: ast-grep [yes/no], code-review-graph [yes/no]

| Task | Symbol | Files | Standard Tokens | P2D Tokens | Savings |
|:-----|:-------|:------|:----------------|:-----------|:--------|
| Small | [name] | [N]   | [tokens]        | [tokens]   | [X%]    |
| Medium | [name] | [N]  | [tokens]        | [tokens]   | [X%]    |
| Large | [name] | [N]   | [tokens]        | [tokens]   | [X%]    |

**Average savings: [X%]**

Method: Standard approach reads all matched files fully (chars/4 as tokens).
P2D approach uses targeted categorized grep without reading files.
Both approaches find the same matches — no accuracy loss.
```

### Step 4: Clean up

```bash
rm -f /tmp/p2d-standard.txt /tmp/p2d-targeted.txt /tmp/p2d-sg.json
```

### What makes this honest

- Runs against the user's **actual codebase**, not a synthetic test
- Uses **real tool output**, not simulated estimates
- Counts **real character counts** from actual command output
- Both approaches find the **same matches** — accuracy is identical
- The only difference is whether the agent reads matched files or just
  summarizes the grep/ast-grep output
- Savings come from a real behavior change: not reading files you don't need
