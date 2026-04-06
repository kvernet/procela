# CompositeDomain — Semantic Specification

## 1. Definition

A **CompositeDomain** is a ValueDomain that defines admissibility by combining multiple ValueDomains using explicit logical composition.

It enables multidimensional or constrained value spaces without redefining primitive domains.

---

## 2. Declaration

A CompositeDomain exists as a specialization that:

* Contains two or more ValueDomains
* Declares a composition operator
* Applies deterministic evaluation

Minimal declaration requirements:

* A finite set of component domains
* A declared composition rule

No implicit precedence or coercion is allowed.

---

## 3. Semantic Invariants

### **D1: Domain Closure**

All components MUST be valid ValueDomains.

### **D2: Deterministic Composition**

Given the same input, composition MUST yield the same admissibility result.

### **D3: No Value Transformation**

CompositeDomain MUST NOT alter values.

### **D4: Explicit Semantics**

Composition logic MUST be explicit and fixed.

---

## 4. Composition Operators

Allowed operators:

* **AND** — value must satisfy all domains
* **OR** — value must satisfy at least one domain
* **XOR** — value must satisfy exactly one domain
* **NOT** — negation of a single domain

---

## 5. Negative Definition

What CompositeDomain is NOT.

* Not a new primitive domain
* Not probabilistic
* Not fuzzy
* Not hierarchical
* Not order-dependent unless explicitly stated

---

## 6. Impossibilities

* Empty component sets are invalid
* Circular domain definitions are invalid
* Implicit coercion between domains is invalid
* Conflicting composition rules are invalid

---

## 7. Boundary Conditions

* **Single-domain composite:**
  Valid but redundant.

* **Contradictory domains:**
  CompositeDomain may admit no values.

* **Evaluation order:**
  Undefined unless explicitly stated.

---

## 8. Example (Non-Normative)

```text
Composite = NumericDomain(0 ≤ x ≤ 1) AND Not(IntegerDomain)

validate(0.5) → admissible
validate(1)   → inadmissible
```

---

## 9. Validation Rules

* **Static:**
  All component domains must be valid.

* **Runtime:**
  Value admissibility follows declared composition logic.

---

## 10. Semantic Notes (Non-Binding)

* Enables expressive constraint modeling
* Preserves domain orthogonality
* Avoids explosion of specialized domain types
* Supports future extensions (e.g., temporal domains)

---
