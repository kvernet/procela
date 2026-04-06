# ValueDomain — Semantic Specification

## 1. Definition

A **ValueDomain** defines the set of admissible values for a Variable.

It establishes **semantic validity constraints** over values without imposing representation, storage, sampling, or reasoning behavior.

A ValueDomain answers exactly one question:

> *Is this value admissible within this domain?*

---

## 2. Declaration

A ValueDomain exists as an abstract semantic construct that:

* Defines admissibility conditions for values
* Can validate candidate values against those conditions
* May expose domain metadata for introspection

Minimal declaration requirements:

* A validation predicate over values
* Deterministic behavior for identical inputs

No assumptions are made about value type, cardinality, or structure.

---

## 3. Semantic Invariants

Properties that MUST hold for all valid ValueDomain instances.

### **D1: Deterministic Validation**

Validation of a given value MUST always yield the same result.

### **D2: Purity**

Validation MUST NOT modify the value, the domain, or any external state.

### **D3: Total Decision**

For any input value, validation MUST return either:

* admissible, or
* inadmissible

Undefined or partial results are not permitted.

### **D4: Non-Transformative**

A ValueDomain MUST NOT transform, coerce, normalize, or generate values.

### **D5: Context Independence**

Validation MUST NOT depend on time, external systems, or mutable global state.

---

## 4. Negative Definition

What ValueDomain is NOT.

* Not a type system
* Not a sampler or generator
* Not a probability distribution
* Not a storage schema
* Not a reasoning engine
* Not responsible for uncertainty quantification

---

## 5. Impossibilities

States or operations that cannot occur.

* A ValueDomain cannot generate values
* A ValueDomain cannot infer missing values
* A ValueDomain cannot rank admissible values
* A ValueDomain cannot resolve conflicts between values
* A ValueDomain cannot change after validation begins

Any such behavior constitutes a semantic violation.

---

## 6. Boundary Conditions

Defined behavior at semantic limits.

### **Empty domain**

A domain that admits no values is valid but degenerate.

### **Universal domain**

A domain that admits all values is valid.

### **Invalid input**

All inputs, including `None`, malformed, or unexpected types, MUST be handled deterministically.

### **Resource exhaustion**

Behavior is undefined if validation cannot complete due to external constraints.

If undefined behavior exists, it MUST be explicitly stated.

---

## 7. Composition Rules

Semantic combination constraints.

### **Allowed**

* Variable ∘ ValueDomain → constrained Variable
* CompositeDomain(ValueDomain₁, …, ValueDomainₙ)

### **Forbidden**

* ValueDomain ∘ Variable (domains do not depend on variables)
* ValueDomain ∘ ReasoningResult
* ValueDomain ∘ History

Domains constrain values; they do not observe outcomes.

---

## 8. Example (Non-Normative)

Examples do not define semantics.

```text
domain admits values between 0 and 100 inclusive
validate(42)  → admissible
validate(-1)  → inadmissible
```

No assumptions are made about numeric representation.

---

## 9. Validation Rules

How violations are detected.

* **Static:**
  Domains with non-deterministic validation are invalid.

* **Runtime:**
  Supplying values that cannot be decisively validated is a semantic violation.

* **Structural:**
  Any component that mutates values during validation violates domain semantics.

Validation enforces semantics; it does not define them.

---

## 10. Semantic Notes (Non-Binding)

Rationale and intent.

* Separates value admissibility from reasoning
* Enables clear validation boundaries for Variables
* Prevents implicit coercion and hidden transformations
* Allows multiple concrete domain specializations without semantic drift
* Serves as a foundation for numeric, categorical, temporal, and composite domains

---
