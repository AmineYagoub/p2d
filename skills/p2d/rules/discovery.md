---
title: Structural Discovery via ast-grep
impact: CRITICAL
impactDescription: Eliminates 80-95% of token waste from file reading
tags: discovery, ast-grep, structural search, pattern matching, token optimization
---

## Structural Discovery via ast-grep

Use ast-grep to find exact AST nodes by structural pattern instead of
grepping for text. This is the single highest-impact rule in P2D.

### Prerequisites

Before using this rule, check if ast-grep is available. If not, offer to
install it or fall back to `rules/fallback.md`.

```bash
sg --version 2>/dev/null || echo "ast-grep not found"
```

If missing, suggest: `npm install --global @ast-grep/cli` or `brew install ast-grep`.

### When to Use This Rule

- User asks to find, locate, or list symbols (classes, functions, methods, variables)
- User asks "where is X imported" or "who uses Y"
- You need to understand the structure of a codebase region before editing
- You need to count or enumerate constructs (decorators, hooks, interfaces)

### Quick Reference

ast-grep supports 25 languages. CLI aliases: `ts` (TypeScript), `tsx` (TSX),
`js`/`jsx` (JavaScript), `py` (Python), `rust`/`rs` (Rust), `go`/`golang` (Go),
`java` (Java), `rb`/`ruby` (Ruby), `cs`/`csharp` (C#), `swift` (Swift),
`kotlin`/`kt` (Kotlin), `scala` (Scala), `php` (PHP), `c` (C), `cc`/`cpp` (C++).

```bash
# Basic pattern search
sg -p 'function $NAME($$$ARGS) { $$$ }' -l ts

# Pattern with replacement (used in Phase 3)
sg -p 'oldName($$$A)' -r 'newName($$$A)' -l ts

# JSON output for programmatic use
sg -p 'class $NAME { $$$ }' -l ts --json

# YAML rule file for complex patterns
sg run --rule my-rule.yml
```

### Metavariable Syntax

| Syntax | Matches | Example |
|:-------|:--------|:--------|
| `$NAME` | Single AST node (uppercase A-Z, `_`, digits after `$`) | `$FUNC` matches `handleClick` |
| `$$$NAME` | Zero or more AST nodes (spread) | `($$$ARGS)` matches any param list |
| `$$$` | Anonymous spread (unnamed) | `{ $$$ }` matches any body |
| `$_NAME` | Non-capturing (skips HashMap, faster) | `$_( $_ )` matches any call |
| `$$VAR` | Captures unnamed tree-sitter nodes | Rarely needed |

**Identity matching:** Reusing the same metavariable enforces structural equality.
`$A == $A` matches `x == x` but not `x == y`.

---

## Pattern Catalog by Task

### Finding React Hooks (TSX)

**useState:**
```bash
sg -p 'const [$VAR, $SETTER] = useState($INIT)' -l tsx
```

**useEffect with empty dependency array (potential bug):**
```bash
sg -p 'useEffect(() => { $$$ }, [])' -l tsx
```

**useEffect with no dependency array at all (runs every render):**
```yaml
# Use YAML rule — the `not` filter excludes effects that have a second arg
id: useEffect-no-deps
language: tsx
rule:
  any:
    - pattern: "useEffect(function $FUNC() { $$$ })"
    - pattern: "useEffect(() => { $$$ })"
```

**useCallback/useMemo with empty deps:**
```bash
sg -p 'useCallback(() => { $$$ }, [])' -l tsx
```

### Finding Python Decorators

**Any decorated function (most reliable method):**
```yaml
id: decorated-functions
language: python
rule:
  kind: decorated_definition
  has:
    kind: function_definition
```

> **Heuristic:** `@$DECORATOR` only matches bare decorators like `@staticmethod`.
> It will NOT match parameterized decorators like `@app.route("/path")` because
> `app.route("/path")` is a `call` node, not an `identifier`. Use `kind: decorator`
> with `has` to match both forms.

**Specific decorator (bare):**
```bash
sg -p '@staticmethod' -l py
sg -p '@property' -l py
```

**Parameterized decorator (e.g., Flask routes):**
```yaml
id: flask-routes
language: python
rule:
  kind: decorator
  has:
    pattern: "app.route($$$ARGS)"
```

**All decorators with arguments:**
```yaml
id: parameterized-decorators
language: python
rule:
  kind: decorator
  has:
    kind: call
```

### Finding Go Interface Implementations

**All struct declarations:**
```yaml
id: structs
language: go
rule:
  kind: type_declaration
  has:
    kind: type_spec
    has:
      kind: struct_type
```

**All methods on a specific type:**
```bash
sg -p 'func ($RECEIVER $TYPE) $METHOD($$$PARAMS) $$$RET { $$$ }' -l go
```

> **Heuristic:** `$TYPE` matches both `MyType` and `*MyType` — no need for
> separate pointer and value receiver patterns.

**Interface definitions:**
```yaml
id: interfaces
language: go
rule:
  kind: type_spec
  has:
    kind: interface_type
```

### Finding Rust Trait Implement

**All trait impl blocks:**
```yaml
id: trait-impls
language: rust
rule:
  kind: impl_item
  has:
    kind: trait
```

**Impl for a specific trait:**
```bash
sg -p 'impl $TRAIT for $TYPE { $$$ }' -l rust
```

**Inherent impl blocks only (no trait):**
```yaml
id: inherent-impls
language: rust
rule:
  pattern: "impl $TYPE { $$$ }"
  not:
    has:
      kind: trait
```

> **Heuristic:** The pattern `impl $TYPE { $$$ }` matches BOTH inherent and trait
> impls because `$TYPE` can capture `Trait for Type` as a single node. Use
> `not: has: kind: trait` to filter.

### Finding Import Statements

**TypeScript/JavaScript named imports:**
```bash
sg -p 'import { $$$NAMES } from "$SOURCE"' -l ts
```

> **Heuristic:** At `smart` strictness (default), single vs double quotes matter.
> `'$SOURCE'` won't match `"module"`. Use `--strictness ast` or match both:
> ```yaml
> rule:
>   any:
>     - pattern: "import { $$$ } from '$SOURCE'"
>     - pattern: "import { $$$ } from \"$SOURCE\""
> ```

**Python from-imports:**
```bash
sg -p 'from $MODULE import $NAME' -l py
sg -p 'from $MODULE import $$$NAMES' -l py
```

**Go imports (specific package):**
```yaml
id: go-import-fmt
language: go
rule:
  kind: import_declaration
  has:
    pattern: '"fmt"'
```

**Rust use statements:**
```bash
sg -p 'use $CRATE::$PATH;' -l rust
```

### Finding TypeScript Type Assertions

**`as` assertions:**
```bash
sg -p '$EXPR as $TYPE' -l ts
```

**`as any` anti-pattern:**
```bash
sg -p '$EXPR as any' -l ts
```

**Double assertion anti-pattern (`as unknown as X`):**
```bash
sg -p '$EXPR as unknown as $TYPE' -l ts
```

> **Heuristic:** In `.tsx` files, angle-bracket assertions `<Type>value` conflict
> with JSX syntax. Always use the `as` form in TSX files.

---

## Advanced Techniques

### Relational Rules

Search by position in the AST tree, not just pattern:

```yaml
# Find `await` inside any loop
rule:
  pattern: "await $PROMISE"
  inside:
    any:
      - kind: for_in_statement
      - kind: for_statement
      - kind: while_statement
    stopBy: end    # search to tree boundary, not just one level
```

```yaml
# Find object properties with key "prototype" (not values)
rule:
  kind: pair
  has:
    field: key     # only match the key, not the value
    regex: "prototype"
```

Available relational rules: `inside`, `has`, `follows`, `precedes`.
Modifiers: `stopBy: end` (search deeply), `field: name` (narrow to specific AST field).

### Pattern Objects for Ambiguity

When a pattern is syntactically ambiguous, wrap it with `selector` + `context`:

```yaml
# Match class fields (not assignment expressions)
pattern:
  selector: field_definition
  context: "class A { $FIELD = $INIT }"
```

### Excluding False Positives with `not`

```yaml
# Match console.log but NOT console.log('Hello World')
rule:
  pattern: console.log($GREETING)
  not:
    pattern: console.log('Hello World')
```

### Common Mistake with `has` + `all`

```yaml
# WRONG — a node can't be both number AND string
has:
  all: [kind: number, kind: string]

# RIGHT — two separate has checks
all:
  - has: {kind: number}
  - has: {kind: string}
```

---

## Failure Modes

### 0 matches but you know the symbol exists

1. Try `kind` instead of `pattern` — the parser may group nodes differently
   ```bash
   sg -k function_definition -l py
   ```
2. Try `--strictness relaxed` to ignore comments and whitespace differences
3. Try a broader pattern: `$NAME($$$ARGS)` instead of `function $NAME($$$ARGS) { $$$ }`
4. Verify the file extension matches the language flag (`.tsx` files need `-l tsx`, not `-l ts`)

### Ambiguous patterns in TSX

Angle brackets `<Type>value` parse as JSX in `.tsx` files.
Always use the `as` form: `$EXPR as $TYPE`.

### When to use CLI `-p` vs YAML rule files

| Situation | Use |
|:----------|:----|
| Simple pattern, single search | CLI: `sg -p '...' -l ts` |
| Multiple conditions (`any`, `not`, `inside`) | YAML rule file: `sg run --rule file.yml` |
| Need to combine `pattern` + `kind` + relational | YAML rule file |
| Quick one-off search | CLI |

### Report Format

Never dump raw JSON. Summarize:

"Found [N] matches for [pattern] across [M] files:
- path/to/file.ts: class FooBar (line 42)
- path/to/other.ts: class FooBar (line 108)"

### Token Savings

- Standard: read 50 files x ~200 tokens = ~10,000 tokens
- ast-grep: 1 command + summary = ~200 tokens
- Savings: 95%+

### Anti-Patterns

- Do NOT use `grep -r` when ast-grep is available
- Do NOT read entire files just to find one symbol
- Do NOT dump raw ast-grep JSON output into the conversation
- Do NOT assume a pattern is correct without testing — tree-sitter grammars
  have quirks that differ from regex expectations
