# CategoricalDomain — Semantic Specification

## 1. Definition

A **CategoricalDomain** is a ValueDomain whose admissible values are drawn from a finite, explicitly enumerated set of symbols.

It defines admissibility by exact membership, without ordering, arithmetic meaning, or implicit hierarchy.

---

## 2. Declaration

A CategoricalDomain exists as a semantic specialization that:

* Declares a finite set of admissible values
* Performs exact membership validation
* Preserves value identity without transformation

Minimal declaration requirements:

* A non-empty finite set of admissible values
* A deterministic equality predicate

No ordering, distance, or numeric interpretation is implied.

---

## 3. Semantic Invariants

These invariants **extend** all ValueDomain invariants.

### **C1: Finite Membership**

Only values explicitly declared in the domain are admissible.

### **C2: Exact Equality**

Membership MUST be determined by exact equality, not similarity or coercion.

### **C3: Stable Enumeration**

The admissible set MUST NOT change after domain declaration.

### **C4: Non-Ordinality**

No ordering relation is defined between values.

---

## 4. Negative Definition

What CategoricalDomain is NOT.

* Not ordered
* Not numeric
* Not probabilistic
* Not hierarchical
* Not fuzzy or similarity-based
* Not extensible at runtime

---

## 5. Impossibilities

States or operations that cannot occur.

* A value not in the declared set cannot be admissible
* Partial matches cannot be accepted
* New categories cannot be introduced dynamically
* Categories cannot be merged or split implicitly

---

## 6. Boundary Conditions

Defined behavior at semantic limits.

* **Empty set:**
  A CategoricalDomain with no admissible values is invalid.

* **Single-element set:**
  Valid but degenerate.

* **Duplicate values:**
  Duplicates collapse to a single admissible symbol.

* **Mixed types:**
  Mixed-type categories are allowed but discouraged; equality semantics must be explicit.

---

## 7. Composition Rules

### **Allowed**

* CategoricalDomain ∘ Variable
* CompositeDomain(CategoricalDomain, …)

### **Forbidden**

* CategoricalDomain ∘ NumericDomain
* CategoricalDomain ∘ BooleanDomain

Categorical meaning must remain discrete and uninterpreted.

---

## 8. Example (Non-Normative)

```text
Domain = {"red", "green", "blue"}

validate("red")   → admissible
validate("yellow") → inadmissible
```

---

## 9. Validation Rules

* **Static:**
  Domain must declare at least one admissible value.

* **Runtime:**
  Values not exactly matching an admissible symbol are invalid.

* **Structural:**
  Any transformation of values violates semantics.

---

## 10. Semantic Notes (Non-Binding)

* Designed for symbolic states, labels, and modes
* Avoids hidden hierarchies or ordering assumptions
* Enables strict categorical reasoning

---
