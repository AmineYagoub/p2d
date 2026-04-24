---
title: Graceful Fallback to Probabilistic Search
impact: MEDIUM
impactDescription: Ensures progress is never blocked while minimizing waste
tags: fallback, probabilistic, grep, graceful degradation, heuristics
---

## Graceful Fallback to Probabilistic Search

When structural tools (ast-grep, code-review-graph, Codemod) are unavailable
or fail, fall back to traditional text-based methods — but do so efficiently.

### When to Use This Rule

- ast-grep is not installed on the system
- ast-grep does not support the target language
- code-review-graph is not installed or the graph is not built
- Any structural tool returns an error

### File Size Heuristics

The right fallback depends on file size. Always check size before choosing a strategy:

| File size | Strategy |
|:----------|:---------|
| < 50 lines | Read the whole file — overhead of targeted search isn't worth it |
| 50-500 lines | Use targeted grep to locate, then read only relevant line ranges |
| > 500 lines | NEVER read the whole file. Use targeted search exclusively |

```bash
# Check file size before reading
wc -l path/to/file.ts
```

### How to Fallback Efficiently

1. **Acknowledge the fallback:**
   "Structural tool [X] not available. Falling back to text-based search.
   Results may be less precise."

2. **Prefer `git grep` over `grep -r` in git repos:**
   ```bash
   # Fast — uses git index
   git grep -n "SymbolName" -- "*.ts" "*.tsx"

   # Slower — scans filesystem
   grep -rn "SymbolName" --include="*.ts" src/
   ```

3. **Use targeted grep with file-type filtering:**
   ```bash
   # Good: scoped to source directory, filtered by extension
   grep -rn "SymbolName" --include="*.ts" --include="*.tsx" src/

   # Bad: scanning everything including node_modules, build artifacts
   grep -rn "SymbolName" .
   ```

4. **Use `ctags` for symbol location when available:**
   ```bash
   # Find symbol definition
   ctags -R --fields=+ne -o - . | grep "SymbolName"

   # Or use readtags if available
   readtags -e -n SymbolName
   ```

5. **Read with line ranges, not full files:**
   ```bash
   # Good: read only the relevant lines (grep gives you line numbers)
   # After grep returns "file.ts:42:  export class UserService"
   # Read file.ts lines 38-55 to see the full class

   # Bad: read entire 800-line file
   ```

6. **Summarize results:**
   Even with grep, summarize rather than dumping raw output:
   "Found 5 occurrences of SymbolName in 3 files:
   - src/auth.ts: line 42 (class definition)
   - src/api.ts: line 15 (import statement)
   - tests/auth.test.ts: line 88 (test reference)"

### Caching Strategy

Remember what you discover in a session. Do not re-search the same patterns.

**Cache these in conversation memory:**
- File structure of directories you've explored (which files exist where)
- Symbol locations found in previous searches (file + line number)
- Which tools are available (don't re-check `sg --version` every time)
- Grep results for symbols that haven't changed since last search

**Don't cache:**
- File contents (may change between reads)
- Grep results after edits (content has changed)

### Fallback Strategy by Phase

**Phase 1 (Discovery) fallback:**
- Use `git grep` or targeted `grep` with `--include` filtering
- Use `ctags` if available for symbol definitions
- Fall back to `find` + file extension filtering for locating files

**Phase 2 (Trace) fallback:**
- Use `grep -rn` with context lines (`-B2 -A2`) to understand usage patterns
- Search for import statements first, then function calls
- Check test files specifically: `grep -rn "SymbolName" --include="*.test.*"`

**Phase 3 (Surgeon) fallback:**
- Use native Edit tool with exact line ranges
- Apply changes one file at a time
- Verify after each file rather than batching

### Principles

- Fallback is always temporary — recommend installing the structural tool
- Even in fallback mode, minimize tokens: targeted searches, summaries, line-range reads
- Never silently skip a phase. If Phase 2 cannot run, explicitly warn the user
  that impact analysis was skipped
- Always use `git grep` in git repos — it's 10-50x faster than `grep -r`
  because it uses the git index instead of walking the filesystem
