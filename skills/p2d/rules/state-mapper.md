---
title: State Ownership Mapper
impact: HIGH
impactDescription: Prevents split-brain state bugs by mapping who owns what state
tags: state, ownership, injectable, context, provider, architecture, split-brain
---

## State Ownership Mapper

Before creating a new state variable, provider, or context, the agent must
check if equivalent state already exists somewhere in the codebase. This
prevents "split-brain" bugs where two separate sources of truth diverge.

### When to Use This Rule

- Agent is about to add a new state variable, React context, or service
- Agent is about to create a new provider or store
- User asks "where does [state] live?" or "who owns [data]?"
- Agent needs to decide where to put new state

### Prerequisites

Check for ast-grep availability. If not installed, fall back to targeted grep.

```bash
sg --version 2>/dev/null || echo "ast-grep not found"
```

### NestJS: Map Injectable Providers

Find all injectable services and what they provide:

```bash
# Find all @Injectable() providers
sg -p '@Injectable() class $NAME { $$$ }' -l ts
```

Or with grep fallback:
```bash
grep -rn "@Injectable" --include="*.ts" .
```

**State ownership check:** Before creating a new service, pass the actual
domain terms to the bundled state mapper. Do not rely on the example terms.

```bash
skills/p2d/scripts/p2d-state-map user auth session --root .
```

**Report format:**
```
State ownership map for [domain]:
  Existing providers:
    - AuthService (auth.service.ts): handles user sessions, tokens
    - UserService (user.service.ts): handles user CRUD, profiles
    - WalletService (wallet.service.ts): handles balances, transactions
  No existing provider for: [new state you're adding]
  Recommendation: Add to [UserService] or create new [XyzService]
```

### React: Map Context Providers

Find all React context providers and their consumers:

```bash
# Find context definitions
sg -p 'const $NAME = createContext($$$)' -l tsx

# Find context providers
sg -p '<$NAME.Provider value={$$$}>' -l tsx

# Find useContext calls
sg -p 'useContext($$$)' -l tsx
```

Or with grep fallback:
```bash
grep -rn "createContext\|useContext" --include="*.tsx" --include="*.ts" .
```

**State ownership check:** Before creating a new context, scan for existing
owners using the user's domain terms:

```bash
skills/p2d/scripts/p2d-state-map user auth theme --root .
```

**Report format:**
```
State ownership map for [domain]:
  Existing contexts:
    - AuthContext (auth.context.tsx): user session, login state
    - CartContext (cart.context.tsx): cart items, totals
  Consumers of AuthContext: 12 components
  No existing context for: [new state you're adding]
  Recommendation: Extend [AuthContext] or create new [XyzContext]
```

### Valtio / Zustand / Jotai: Map State Stores

Find all state store definitions:

```bash
# Valtio stores
sg -p 'const $NAME = proxy($$$)' -l tsx

# Zustand stores
sg -p 'const use$NAME = create($$$)' -l ts

# Jotai atoms
sg -p 'const $NAME = atom($$$)' -l ts
```

Or with grep fallback:
```bash
grep -rn "proxy(\|create(\|atom(" --include="*.ts" --include="*.tsx" .
```

**State ownership check:** Before creating a new store, scan existing stores
and other state owners:

```bash
skills/p2d/scripts/p2d-state-map user cart auth theme --root .
```

### Angular: Map Services and Providers

Angular services are the primary state container. DI providers define ownership.

```bash
# Find all Angular services
sg -p '@Injectable({ $$$ }) class $NAME { $$$ }' -l ts

# Find providedIn declarations (tree-shakable providers)
sg -p 'providedIn: $SCOPE' -l ts
```

Or with grep fallback:
```bash
grep -rn "@Injectable" --include="*.ts" .
grep -rn "providedIn" --include="*.ts" .
```

**State ownership check:**
```bash
# Check if a service already handles this domain
grep -rn "@Injectable" --include="*.service.ts" . -l | xargs grep -l "user\|auth\|cart"
```

### Vue: Map Pinia Stores and Provide/Inject

```bash
# Pinia stores
sg -p 'const use$NAME = defineStore($$$)' -l ts

# Vue provide/inject
sg -p 'provide($KEY, $$$)' -l ts
sg -p 'inject($KEY)' -l ts
```

Or with grep fallback:
```bash
grep -rn "defineStore\|provide(\|inject(" --include="*.ts" --include="*.vue" .
```

**State ownership check:**
```bash
grep -rn "defineStore" --include="*.ts" . -l | xargs grep -l "user\|auth\|cart"
```

### Svelte: Map Stores

```bash
# Svelte writable/readable stores
sg -p 'const $NAME = writable($$$)' -l ts
sg -p 'const $NAME = readable($$$)' -l ts
sg -p 'const $NAME = derived($$$)' -l ts
```

Or with grep fallback:
```bash
grep -rn "writable(\|readable(\|derived(" --include="*.ts" --include="*.svelte" .
```

### Django: Map Models and Managers

Django models are the source of truth. Model managers define data access patterns.

```bash
# Find all Django models
sg -p 'class $NAME(models.Model): $$$' -l py

# Find model managers
sg -p 'class $NAME(models.Manager): $$$' -l py
```

Or with grep fallback:
```bash
grep -rn "models.Model\|models.Manager" --include="*.py" .
```

**State ownership check:**
```bash
# Check which app/model owns a domain
grep -rn "class.*models.Model" --include="*.py" . | grep -i "user\|order\|product"
```

### FastAPI: Map Dependencies and State

FastAPI uses Depends() for dependency injection and app.state for shared state.

```bash
# Find dependency injection
sg -p 'Depends($FUNC)' -l py

# Find app state
sg -p 'app.state.$NAME = $$$' -l py
```

Or with grep fallback:
```bash
grep -rn "Depends(\|app.state" --include="*.py" .
```

### Spring Boot (Java): Map Beans and Components

```bash
# Find Spring components
sg -p '@Service class $NAME { $$$ }' -l java
sg -p '@Repository class $NAME { $$$ }' -l java
sg -p '@Component class $NAME { $$$ }' -l java
sg -p '@Configuration class $NAME { $$$ }' -l java
```

Or with grep fallback:
```bash
grep -rn "@Service\|@Repository\|@Component\|@Configuration" --include="*.java" .
```

### Go: Map Structs and Interfaces

Go doesn't have DI decorators, but state ownership follows struct patterns.

```bash
# Find service-like structs (accept interfaces)
sg -p 'type $NAME struct { $$$ }' -l go

# Find interface definitions
sg -p 'type $NAME interface { $$$ }' -l go
```

Or with grep fallback:
```bash
# Find structs that look like service owners
grep -rn "type.*struct" --include="*.go" . | grep -i "service\|handler\|repository\|store"
```

### Rust: Map Structs with State

```bash
# Find structs holding state
sg -p 'struct $NAME { $$$ }' -l rust

# Find traits that define state contracts
sg -p 'trait $NAME { $$$ }' -l rust
```

Or with grep fallback:
```bash
grep -rn "^pub struct\|^struct" --include="*.rs" . | grep -i "state\|store\|repo\|service"
```

### Decision Rule

When the agent is about to create new state:

```
1. Search for existing state owners in the same domain
2. If found:
   → Report: "State already exists in [X]. Reuse it instead of creating duplicate."
   → Show the file and line where the existing state is defined
   → Suggest importing/extending the existing provider
3. If not found:
   → Report: "No existing state owner for this domain."
   → Proceed with creation, noting the ownership in the codebase map
4. If ambiguous (2+ overlapping state owners):
   → Report: "WARNING: Multiple state owners for this domain."
   → List each owner and what it covers
   → Flag as potential split-brain bug
   → Ask user which to consolidate into
```

### Split-Brain Detection

A split-brain bug occurs when two separate sources of truth manage the
same conceptual data. Detect this by:

1. Finding all state definitions (providers, contexts, stores) for a domain
2. Checking if any two store overlapping fields
3. Reporting conflicts

```bash
# Example: find all stores that reference "user"
grep -rn "user" --include="*.valtio.ts" --include="*.store.ts" . | grep "proxy\|create\|atom"
```

**Report format:**
```
Split-brain warning for "user" state:
  - user.valtio.ts: stores { id, name, email, role }
  - auth.context.tsx: stores { id, name, email, token }
  Overlap: id, name, email are in both stores
  Risk: updates to user profile in one store won't reflect in the other
  Recommendation: consolidate into a single source of truth
```

### Anti-Patterns

- NEVER create a new provider/context/store without checking for existing ones
- NEVER duplicate state because "it's easier" — this is the root cause of
  the hardest bugs to debug
- Do NOT skip this rule when adding state "temporarily" — temporary state
  becomes permanent
