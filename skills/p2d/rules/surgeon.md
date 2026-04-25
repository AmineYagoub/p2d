---
title: Surgical Execution via Tree-sitter and Codemod
impact: HIGH
impactDescription: Reduces output tokens by up to 95% vs full-file rewrites
tags: surgeon, codemod, tree-sitter, AST edit, surgical, node swap
---

## Surgical Execution via Tree-sitter and Codemod

For changes involving less than 20% of a file's code, perform targeted
AST node swaps instead of full file rewrites.

### Prerequisites

Before using ast-grep replacement or Codemod, check availability:

```bash
sg --version 2>/dev/null || echo "ast-grep not found"
npx codemod --version 2>/dev/null || echo "codemod not found"
```

If ast-grep is missing, suggest: `npm install --global @ast-grep/cli` or `brew install ast-grep`.
If both are missing, fall back to the native Edit tool with line-specific edits.

### When to Use This Rule

- Renaming a symbol across multiple files
- Changing a function signature
- Adding/removing a parameter
- Replacing a decorator or annotation
- Updating import paths
- Any targeted edit that does not restructure the entire file

### When NOT to Use This Rule

- The change affects more than 20% of the file (use standard edit)
- The file is very small (< 20 lines — just rewrite it)
- You need to restructure control flow significantly

---

## Method 1: ast-grep Replacement (Preferred)

ast-grep supports inline replacement with the `-r` flag. Treat every command in
this section as a pattern sketch until the previewed match set proves it is
complete and safe.

### Symbol Rename Preview

```bash
# First preview the complete match set. Do not mutate files yet.
skills/p2d/scripts/p2d-safe-rename-preview oldFunctionName newFunctionName --root .
```

Only apply replacements after the preview includes every required bucket:
definitions, imports, exports, calls, strings/config references, and tests. A
single pattern rarely covers all buckets.

```bash
# Example sketch after preview, scoped to function calls only
sg -p 'oldFunctionName($$$ARGS)' -r 'newFunctionName($$$ARGS)' -l ts
```

### Signature Change

Treat these as sketches, not complete recipes. Signature changes require Phase
2 caller discovery, a match-count preview, and type/test verification.

```bash
# Add a parameter to known call sites only after caller review
sg -p 'myFunc($$$ARGS)' -r 'myFunc($$$ARGS, newParam)' -l ts

# Remove a parameter only after confirming argument position and semantics
sg -p 'myFunc($$$A, $REMOVED, $$$B)' -r 'myFunc($$$A, $$$B)' -l ts
```

### Import Path Update

```bash
sg -p 'import { $$$NAMES } from "old/path"' -r 'import { $$$NAMES } from "new/path"' -l ts
```

### Decorator Modification

```bash
# Replace a decorator
sg -p '@oldDecorator' -r '@newDecorator' -l py
```

### Complex Transforms via YAML Rule File

When inline patterns can't express the transform, use a YAML rule file:

```yaml
# rename.yml
id: rename-user-service
language: ts
rule:
  pattern: "UserService"
fix: "AccountService"
```

```bash
sg run --rule rename.yml
```

Use rule files when:
- The pattern has multiple conditions (`any`, `not`, `inside`)
- You need to combine `pattern` with `kind` matching
- The replacement depends on captured metavariables

---

## Method 2: Codemod (for supported languages)

Codemod provides a registry of pre-built transforms and a local JS/TS
ast-grep engine for custom transforms.

### Running a registry transform

```bash
npx codemod workflow run <codemod-name> --target src/
```

Browse available codemods at codemod.com/registry.

### Running a local custom transform

```bash
npx codemod jssg run ./transforms/rename-symbol.ts --target src/
```

The transform file is a TypeScript module using Codemod's jssg engine
(JS/TS ast-grep syntax).

### When to use Codemod vs ast-grep

| Situation | Use |
|:----------|:----|
| Simple rename/replacement | ast-grep (`sg -p ... -r ...`) |
| Pre-built transform from registry | Codemod (`npx codemod workflow run`) |
| Custom JS/TS transform with logic | Codemod jssg |
| Non-JS/TS language | ast-grep (broader language support) |

---

## Method 3: Native Edit Tool

When neither ast-grep nor Codemod is available, use the agent's native
Edit tool with line-specific edits. Target only the lines that change.

**Approach:**
1. Use Phase 1 (discovery) to identify exact line numbers
2. Use Phase 2 (trace) to confirm all locations that need updating
3. Apply edits one at a time using the Edit tool with exact line ranges

---

## Verification

After any surgical edit, verify correctness:

1. **Type checking** (if available):
   ```bash
   tsc --noEmit       # TypeScript
   mypy src/          # Python
   cargo check        # Rust
   go vet ./...       # Go
   ```

2. **Run affected tests:**
   ```bash
   npm test -- --related path/to/changed/file.ts
   pytest tests/test_changed_module.py
   ```

3. **Syntax validation:**
   ```bash
   node --check file.js        # JavaScript
   python -m py_compile file.py # Python
   ```

---

## Failure Recovery

### Replacement produced syntax errors

**Cause:** Pattern captured different nodes than expected.
**Fix:**
1. Inspect the specific lines with errors using `Read` on the affected range
2. Check if metavariables captured multi-line constructs that broke the replacement
3. Use a more specific pattern with `kind` instead of `pattern`
4. Use a YAML rule file with `selector` to target the exact node type

### Replacement changed too many locations

**Cause:** Pattern was too broad, matching unintended nodes.
**Fix:**
1. Add `not` conditions to exclude false positives
2. Use `inside` to narrow the scope (e.g., only within a specific class)
3. Use `--strictness smart` to control matching precision
4. Always run Phase 2 (trace) before Phase 3 to confirm the exact match set

### Verification fails (type errors, test failures)

**Cause:** The rename/replacement created inconsistencies.
**Fix:**
1. List all locations that were changed
2. Check if the replacement missed any references (run discovery again)
3. If tests fail, read the test file to understand expected behavior
4. Consider using `git diff` to review all changes at once
5. If the change is too invasive, stop and review `git diff`. Revert only the
   hunks created by this agent. Never use broad rollback commands that discard
   unrelated user work. See `references/safety.md` for dirty-worktree recovery.

### Token Savings

- Full file rewrite: outputs entire file = file_size tokens
- Surgical edit: outputs only changed lines = ~5-20% of file tokens
- Savings: 80-95%

### Anti-Patterns

- NEVER rewrite an entire 500-line file to change 3 lines
- NEVER use full-file output when a targeted edit suffices
- NEVER use broad destructive rollback that discards unrelated user work
- Do NOT skip verification after surgical edits
- Do NOT apply replacements without running Phase 2 first — always confirm
  the match set matches expectations
