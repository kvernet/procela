# BooleanDomain — Semantic Specification

## 1. Definition

A **BooleanDomain** is a ValueDomain whose admissible values represent binary truth values.

It defines admissibility strictly as logical truth or falsity.

---

## 2. Declaration

A BooleanDomain exists as a specialization that:

* Admits exactly two logical values
* Applies strict boolean semantics
* Rejects all non-boolean inputs

Minimal declaration requirements:

* Explicit definition of truth and falsity values

No numeric, probabilistic, or categorical interpretation is implied.

---

## 3. Semantic Invariants

### **B1: Binary Exclusivity**

Exactly two values are admissible.

### **B2: Boolean Identity**

Admissible values MUST be logically true or false.

### **B3: No Coercion**

Non-boolean values MUST NOT be coerced.

### **B4: Stability**

Truth semantics MUST remain invariant.

---

## 4. Negative Definition

What BooleanDomain is NOT.

* Not numeric
* Not categorical
* Not probabilistic
* Not ternary or fuzzy logic
* Not extensible

---

## 5. Impossibilities

* A third truth value cannot exist
* Numeric or string equivalents cannot be accepted
* Boolean semantics cannot change

---

## 6. Boundary Conditions

* **Truth constants:**
  Only canonical boolean values are admissible.

* **Degenerate cases:**
  None permitted.

---

## 7. Composition Rules

### **Allowed**

* BooleanDomain ∘ Variable
* CompositeDomain(BooleanDomain, …)

### **Forbidden**

* BooleanDomain ∘ NumericDomain
* BooleanDomain ∘ CategoricalDomain

---

## 8. Example (Non-Normative)

```text
validate(True)  → admissible
validate(False) → admissible
validate(1)     → inadmissible
```

---

## 9. Validation Rules

* **Static:**
  BooleanDomain is valid by construction.

* **Runtime:**
  Any non-boolean value is invalid.

---

## 10. Semantic Notes (Non-Binding)

* Preserves strict logical reasoning
* Prevents implicit truthiness bugs
* Serves as a base for logical variables

---
