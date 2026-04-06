# RangeDomain — Semantic Specification

## 1. Definition

A **RangeDomain** is a ValueDomain whose admissible values are numeric quantities.

It defines admissibility in terms of numeric constraints such as bounds, discreteness, and finiteness, without imposing units, distributions, or probabilistic meaning.

---

## 2. Declaration

A RangeDomain exists as a semantic specialization that:

* Admits only numeric values
* Applies numeric constraints deterministically
* Rejects all non-numeric inputs

Minimal declaration requirements:

* A numeric admissibility predicate
* Explicit handling of numeric edge cases

No assumptions are made about physical interpretation or measurement units.

---

## 3. Semantic Invariants

These invariants **extend** all ValueDomain invariants.

### **N1: Numeric Exclusivity**

Only numeric values are admissible.

Non-numeric inputs MUST be rejected.

### **N2: Finiteness**

Admissible values MUST be finite.

NaN, +∞, and −∞ are inadmissible.

### **N3: Deterministic Comparison**

Numeric comparisons MUST be deterministic and order-preserving.

### **N4: Stable Precision**

Validation MUST NOT depend on machine-specific floating-point behavior beyond standard numeric comparison semantics.

### **N5: Explicit Bound Semantics**

If bounds are defined, inclusivity or exclusivity MUST be explicit and stable.

---

## 4. Numeric Constraints

A RangeDomain MAY define zero or more of the following constraints.

All declared constraints MUST be enforced.

### **Range Constraints**

* Lower bound
* Upper bound
* Open or closed interval semantics

### **Discreteness**

* Continuous (ℝ-like)
* Discrete (ℤ-like)
* Explicit step size

### **Cardinality Constraints**

* Finite numeric sets
* Enumerated numeric values

### **Sign Constraints**

* Non-negative
* Positive
* Non-positive
* Negative

Absence of a constraint implies no restriction of that type.

---

## 5. Negative Definition

What RangeDomain is NOT.

* Not a probability distribution
* Not a sampler
* Not a statistical model
* Not a unit system
* Not responsible for rounding or coercion
* Not a validator of semantic correctness beyond numeric admissibility

---

## 6. Impossibilities

States or operations that cannot occur.

* A RangeDomain cannot accept non-numeric values
* A RangeDomain cannot coerce strings or booleans into numbers
* A RangeDomain cannot normalize or clip values
* A RangeDomain cannot change constraints after validation begins
* A RangeDomain cannot depend on execution context

Any occurrence constitutes a semantic violation.

---

## 7. Boundary Conditions

Defined behavior at semantic limits.

### **Integer vs float**

Integers and floats are both numeric but MUST be evaluated consistently.

### **Floating-point edge cases**

NaN and infinities are always invalid.

### **Exact boundaries**

Values exactly equal to bounds MUST follow declared inclusivity rules.

### **Degenerate ranges**

Lower bound > upper bound is invalid by construction.

### **Empty numeric domain**

A RangeDomain that admits no values is valid but degenerate.

---

## 8. Composition Rules

Semantic combination constraints.

### **Allowed**

* RangeDomain ∘ Variable
* CompositeDomain(RangeDomain₁, RangeDomain₂)

### **Forbidden**

* RangeDomain ∘ CategoricalDomain
* RangeDomain ∘ ProbabilityDistribution
* RangeDomain ∘ History

Numeric domains constrain values; they do not interpret outcomes.

---

## 9. Example (Non-Normative)

Examples do not define semantics.

```text
Domain: finite real numbers in [0, 1]

validate(0.0)   → admissible
validate(1.0)   → admissible
validate(-0.1)  → inadmissible
validate(NaN)   → inadmissible
```

---

## 10. Validation Rules

How violations are detected.

* **Static:**
  Domains with undefined bounds or contradictory constraints are invalid.

* **Runtime:**
  Supplying NaN, infinities, or non-numeric types is invalid.

* **Structural:**
  Any RangeDomain that alters values during validation violates semantics.

---

## 11. Semantic Notes (Non-Binding)

Rationale and intent.

* Establishes a clean numeric admissibility contract
* Prevents implicit coercion and hidden rounding
* Enables reliable numeric reasoning upstream
* Provides a base for bounded, discrete, and real-valued domains
* Avoids conflating admissibility with probabilistic modeling

---
