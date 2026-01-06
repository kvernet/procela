# VariableRecord — Semantic Specification

* Version: 0.1.0
* Status: **Draft**
* Date: 2026-01-06

---

## 1. Definition

A **VariableRecord** is an **immutable semantic fact** representing the value of a Variable at a specific moment, optionally attributed to a source and contextualized by metadata.

It is the **atomic unit of historical truth** for a Variable.

---

## 2. Declaration

A VariableRecord exists if and only if it satisfies the following minimal structure:

* A unique identity key issued by KeyAuthority
* A concrete value
* Optional temporal anchoring
* Optional source attribution
* Optional epistemic qualifiers (confidence, metadata, explanation)

Minimal declaration requirements:

* Exactly one identity Key
* Exactly one value
* All other fields are optional and non-identifying

A VariableRecord cannot exist without identity assignment by KeyAuthority.

---

## 3. Semantic Invariants

Properties that MUST hold for all valid VariableRecords.

* **I1: Identity Uniqueness**
  Each VariableRecord is uniquely identified by its Key.

* **I2: Identity Immutability**
  The identity Key of a VariableRecord MUST NOT change after creation.

* **I3: Value Fixity**
  The value of a VariableRecord MUST NOT change after creation.

* **I4: Semantic Atomicity**
  A VariableRecord represents exactly one factual assertion.

* **I5: Authority-Originated Identity**
  The identity Key MUST originate from KeyAuthority.

Any violation invalidates the record.

---

## 4. Negative Definition

A VariableRecord is NOT:

* a Variable
* a container for multiple values
* a mutable state
* a temporal process
* responsible for conflict resolution
* responsible for historical aggregation

---

## 5. Impossibilities

States or operations that cannot occur.

* A VariableRecord cannot change its value
* A VariableRecord cannot change its identity
* Two VariableRecords cannot share the same Key
* A VariableRecord cannot exist without KeyAuthority-issued identity
* A VariableRecord cannot represent multiple facts

---

## 6. Boundary Conditions

Defined behavior at semantic limits.

* **Empty / null:**
  A VariableRecord without optional fields (time, source, confidence, explanation, metadata) is valid.

* **Degenerate:**
  A VariableRecord with a null value is invalid.

* **Temporal boundary:**
  Absence of time implies the record is temporally unanchored.

* **Resource exhaustion:**
  Behavior is undefined if identity issuance fails.

If undefined, it MUST be stated explicitly.

---

## 7. Composition Rules

Semantic combination constraints.

**Allowed**

* Variable ∘ VariableRecord → VariableHistory
* VariableRecord ∘ TimePoint → Temporally anchored fact

**Forbidden**

* VariableRecord ∘ VariableRecord (records do not merge)
* VariableRecord ∘ Variable (records do not define variables)
* VariableRecord ∘ Key (identity cannot be reassigned)

---

## 8. Example (Non-Normative)

Examples do not define semantics.

```python
from procela.core.memory import VariableRecord
from procela.symbols import Key, TimePoint

record = VariableRecord(
    value=42.0,
    time=TimePoint(),
    source=Key()
)
record.describe()
```

---

## 9. Validation Rules

How violations are detected.

* **Static:**
  Identity field is not user-declarable.

* **Runtime:**
  Any attempt to mutate a record raises an error.

* **Structural:**
  Records with non-authority-issued Keys are invalid.

Validation enforces semantics; it does not define them.

---

## 10. Semantic Notes (Non-Binding)

* Records are intentionally minimal and immutable
* Identity is separated from content
* Records enable full historical traceability
* Higher-level reasoning (conflicts, anomalies, explanations) occurs at the Variable level
* This design favors semantic clarity over convenience

---
