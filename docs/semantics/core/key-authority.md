# KeyAuthority — Semantic Specification

## 1. Definition

**KeyAuthority** is the **single, process-global semantic authority** responsible for issuing, registering, and validating identity keys within a Procela runtime.

It defines the **only valid source of identity** for all keyed entities.
KeyAuthority is **not an instantiable entity** and exists solely as a global semantic construct.

---

## 2. Declaration

A KeyAuthority exists as a **unique, implicit semantic context** that:

* Issues identity Keys
* Registers Key–entity associations
* Enforces global identity consistency

Minimal declaration requirements:

* A mechanism to issue a new unique Key
* A registry mapping Keys to at most one entity
* A mechanism to detect and reject identity violations
* Guaranteed global availability without instantiation

No persistence, storage strategy, lifecycle management, or instantiation semantics are implied.

---

## 3. Semantic Invariants

Properties that MUST hold for all valid Procela runtimes.

* **I1: Global Uniqueness**
  Every Key issued by KeyAuthority is unique within the process.

* **I2: Single Ownership**
  A Key MAY be associated with at most one semantic entity.

* **I3: Identity Stability**
  Once a Key is issued and associated, that association MUST NOT change.

* **I4: Authority Exclusivity**
  All valid Keys MUST originate from KeyAuthority.

* **I5: Non-Instantiability**
  KeyAuthority MUST NOT be instantiated. Any attempt to create an instance is invalid.

Any violation invalidates the semantic model.

---

## 4. Negative Definition

KeyAuthority is NOT:

* Not an entity
* Not a persistence layer
* Not a garbage collector
* Not responsible for entity lifecycle
* Not configurable or instantiable
* Not a security or cryptographic authority beyond identity issuance

---

## 5. Impossibilities

The following states or operations cannot occur.

* A Key cannot be issued twice
* Two distinct entities cannot share the same Key
* A Key cannot be reassigned
* Identity conflicts cannot be silently resolved
* KeyAuthority cannot be instantiated
* Multiple KeyAuthorities cannot exist within a process

---

## 6. Boundary Conditions

Defined behavior at semantic limits.

* **Empty / null:**
  A runtime with zero issued Keys is valid.

* **Degenerate:**
  Attempting to register an already-known Key is invalid.

* **Temporal boundary:**
  KeyAuthority defines no temporal semantics.

* **Resource exhaustion:**
  Behavior is undefined if no further Keys can be issued.

If undefined, it MUST be stated explicitly.

---

## 7. Composition Rules

Semantic combination constraints.

**Allowed**

* KeyAuthority ∘ Entity → Key
* KeyAuthority ∘ Key → Validation result

**Forbidden**

* KeyAuthority ∘ KeyAuthority
* Entity ∘ Key (self-assignment)
* User ∘ KeyAuthority (instantiation or configuration)

---

## 8. Example (Non-Normative)

Examples do not define semantics.

```python
from procela.core.key_authority import KeyAuthority

key = KeyAuthority.issue()
assert KeyAuthority.resolve(key) is None
```

---

## 9. Validation Rules

How violations are detected.

* **Static:**
  No Key constructor accepts identity parameters.

* **Runtime:**
  Duplicate issuance, reassignment, or foreign Keys raise a semantic violation.

* **Structural:**
  Any entity claiming a Key not issued by KeyAuthority is invalid.

Validation enforces semantics; it does not define them.

---

## 10. Semantic Notes (Non-Binding)

* Identity is centralized by design
* Enforces global reasoning and introspection
* Enables provenance, diagnostics, and consistency checks
* Prevents accidental or malicious identity forgery
* Rejects decentralized identity to eliminate ambiguity
* Mirrors the locked, process-global implementation exactly

---
