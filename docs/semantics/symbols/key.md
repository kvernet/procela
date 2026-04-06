# Key Semantics

## 1. Definition
A **Key** is a pure, atomic, opaque identity token that uniquely and persistently identifies exactly one entity within a Procela Universe. A Key carries no semantic content beyond identity and supports only binary equality as its meaningful operation.

Formally:
For any entities E₁, E₂, and Keys K₁, K₂:

- K₁ = K₂ ⇔ E₁ and E₂ are the *same* entity
- K₁ ≠ K₂ ⇔ E₁ and E₂ are *distinct* entities

---

## 2. Declaration
A Key is declared as an immutable atomic value satisfying:

- Global uniqueness within a Procela Universe
- Opaqueness: no components that convey semantic information
- Equality and consistent hashing
- No ordering, extraction, or decomposition operations

A Key’s internal representation is unspecified and must not be relied on for semantics.

---

## 3. Semantic Invariants
For all valid Keys, the following must hold:

1. **Atomicity**
   A Key is indivisible and has no constituent parts.

2. **Non-Derivability**
   A Key cannot be computed from entity state or observable properties; no function `f(entity_state) → Key` exists.

3. **Flatness**
   A Key does not encode hierarchy, containment, scope, type, or any other structural property.

4. **Stability**
   A Key remains constant throughout the lifetime of the entity it identifies regardless of changes to that entity’s state, relationships, or properties.

5. **Opacity**
   Nothing about the entity is inferable from the Key’s structure or representation.

---

## 4. Negative Definition
A Key is *not*:

- A label, name, or human-readable identifier
- A pointer or memory address
- A hierarchical or scoped identifier
- A semantic descriptor of type, role, or behavior
- A composite constructed from other Keys or properties

---

## 5. Impossibilities
The following cannot occur:

- Inferring containment, ownership, type, or context solely from Keys.
- Computing similarity, ordering, or distance between Keys.
- Extracting internal values or meaning from a Key.
- Creating composite Keys from other Keys.

---

## 6. Boundary Conditions

1. **Empty Context**
   A Key remains valid in contexts where the referenced entity has no other relations.

2. **Entity Destruction**
   A Key may become a dangling reference if the entity is removed, but the Key syntactically remains valid; its referent is invalidated.

3. **Cross-Universe Isolation**
   A Key from Universe *U₁* cannot semantically reference an entity in Universe *U₂*; cross-universe comparisons are invalid.

4. **Serialization/Deserialization**
   A Key must preserve equality and consistency through persistence, transmission, and reconstruction.

5. **Temporal Invariance**
   A Key’s validity does not depend on time; it remains semantically valid at any temporal context.

---

## 7. Composition Rules
### 7.1 Key-Key Composition
No meaningful Key–Key compositions exist.
The following are invalid:

- Concatenation (e.g., `K1 + K2`)
- Union (e.g., `K1 | K2`)
- Intersection (e.g., `K1 & K2`)
- Nesting as a Key (e.g., `Key(K1)`)

### 7.2 Key-Entity Association
Keys may be associated with entities only via explicit relations.

### 7.3 Data Container Composition
Keys may participate in data structures for reference purpose only:

- Dictionaries (mapping Key → value)
- Sets of Keys
- Tuples combining Keys with other values

These do *not* produce new Keys.

---

## 8. Example
```python
from procela.symbols import Key

# Key creation (abstract, non-deterministic)
k1 = Key()
k2 = Key()

assert k1 != k2         # Distinct identities
assert k1 == k1         # Self-equality
assert hash(k1) == hash(k1)  # Hash consistency

# Valid usage
mapping = {k1: "entity_data", k2: "other_data"}
collection = {k1, k2}

# Invalid operations (semantic violations)
# k1 + k2        # SemanticViolation: Keys cannot be concatenated or composed
# k1 < k2        # SemanticViolation: Keys cannot be ordered
```

---

## 9. Semantic Notes

* Keys are designed to be minimal primitives of identity.
* Identity semantics are *explicitly separated* from other relationships and structural context.
* This ensures structural refactoring, context changes, and model evolution do not alter identity semantics.

---

## 10. Validation Rules

### Static Checks

* No ordering operators are permitted on Keys.
* No structural or value access on Keys.
* Key usage must be limited to equality, hashing, and relation linking.

### Dynamic Enforcement

* Unsupported operations on Keys must raise `SemanticViolation`.
* Serialization loops must preserve equality semantics.

### Test Requirements

* ∀ K1, K2: either (K1 == K2) or (K1 != K2) (law of excluded middle for identity).
* All prohibited operations must be covered by tests asserting failures.

---
