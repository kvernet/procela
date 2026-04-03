# TimePoint Semantics

### 1. Definition

A **TimePoint** is a pure, immutable identity token representing a **declared temporal position** within a system.
It **carries no information** about relationships, ordering, or duration. All temporal precedence relationships are managed externally by a **TemporalDAG**.

### 2. Declaration

```text
TimePoint()
```

* Each TimePoint has a unique `Key`.
* No temporal adjacency is stored inside the TimePoint itself.
* Creation is always immutable: once instantiated, the identity cannot change.

### 3. Semantic Invariants

1. **Identity purity:** Each TimePoint is uniquely identified by a Key.
2. **Immutability:** No internal state (adjacency, order, etc.) can change after creation.
3. **Opaqueness:** The Key reveals nothing about the temporal position.
4. **No hidden state:** Temporal relationships are never stored inside the TimePoint.
5. **Equality:** Two TimePoints are equal if and only if their Keys are equal.

### 4. Negative Definition

TimePoint is **not**:

* A container of temporal relationships
* A clock or timestamp
* Orderable or composable
* Derivable from entity properties or data

### 5. Impossibilities

* Cannot declare or store precedence internally.
* Cannot compute duration, interval, or difference.
* Cannot participate in arithmetic, union, intersection, or ordering operations.
* Cannot infer temporal density or infinity.

### 6. Boundary Conditions

* Each TimePoint is isolated until explicitly added to layers.
* Multiple TimePoints can share no relationship; all are independent identities.
* Creation of a TimePoint does not fail due to system time, resources, or adjacency.

### 7. Composition Rules

* **Valid compositions:** None at the TimePoint level.
* **Invalid compositions:** Any operation attempting to combine TimePoints (add, multiply, union, intersect) raises `SemanticViolation`.

### 8. Example

```python
from procela.symbols import Key, TimePoint

# Create new temporal identities
t0 = TimePoint()
t1 = TimePoint()

# Identity equality
assert t0 != t1
```

### 9. Semantic Notes

* Temporal relationships (precedes, is_before, transitivity) are **externalized** to layers.
* Separation of identity and adjacency ensures immutability, predictable equality, and alignment with Procela’s identity-first philosophy.
* Allows multiple DAG contexts to reuse the same TimePoints without conflict.

### 10. Validation Rules

* **Static checks:** TimePoint creation must always produce a Key; no mutable fields exist.
* **Dynamic checks:** Any operation on a TimePoint attempting ordering, arithmetic, or composition must raise `SemanticViolation`.

---
