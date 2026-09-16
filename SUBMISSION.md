# Novation — submission notes

## Category

Standalone GenLayer Intelligent Contract. No frontend.

## Primitive

Novation provides **successor substitution without obligation mutation**.

An agreement creator freezes:

- an immutable terms digest;
- a human-readable role description;
- bounded successor qualification criteria;
- a consent mode;
- the original incumbent.

A proposed successor is assessed from immutable public HTTPS evidence under GenLayer consensus. The result is deliberately bounded to `QUALIFIED`, `NOT_QUALIFIED`, or `INCONCLUSIVE`. Qualification alone cannot alter responsibility. The configured parties must independently ratify the exact proposal hash. Only deterministic activation then advances the revision and records the old-to-new responsibility edge while leaving the original terms and definition hashes unchanged.

## Why GenLayer is necessary

Whether public evidence actually establishes that a proposed successor meets a natural-language role and qualification standard is semantic and cannot be safely reduced to a deterministic parser. Novation therefore uses custom GenLayer validation:

- leader fetches frozen public evidence and derives a bounded five-dimension observation;
- every validator independently re-fetches the evidence and re-runs the same semantic task;
- validators compare the state-affecting derived qualification class, not prose;
- any conclusive leader result must remain grounded in a verbatim excerpt found in a validator-fetched source;
- malformed, unavailable, ambiguous, or ungrounded evidence becomes `INCONCLUSIVE` rather than permission.

Everything after qualification is deterministic.

## What the model cannot do

The model cannot:

- alter the frozen agreement;
- create or waive consent;
- choose a successor on its own;
- activate a proposal;
- alter revisions or lineage;
- declare a real-world legal novation;
- make an ungrounded conclusive decision.

## Reusability

Other Intelligent Contracts can call:

```python
is_current_obligor(agreement_id, party, expected_definition_hash)
```

and fail closed unless the address is the current obligor for the exact frozen agreement definition. This lets settlement, access, service, workflow or escrow contracts survive responsible-party replacement without rewriting their own agreement state.

`examples/continuity_gate.py` demonstrates this typed IC-to-IC pattern.

## Adversarial cases covered

The included source/deterministic suite exercises or checks:

- incomplete ratification;
- two supported consent modes;
- outsider ratification/cancellation attempts;
- successor decline;
- explicit `NOT_QUALIFIED` fail-close;
- `INCONCLUSIVE` retry without state transfer;
- stale incumbent protection on a second novation;
- immutable terms and agreement-definition hashes;
- revision-indexed lineage;
- agreement closure invalidating the consumer gate;
- proposal hash binding;
- single custom-consensus boundary;
- independent validator evidence replay;
- grounded conclusive evidence;
- network and CLI deployment locks;
- no product frontend.

## Final proof required before submission

A funded final operator should execute the live sequence in `docs/LIVE_TEST_PLAN.md`, record the contract address and finalized transaction/readback evidence in `docs/DEPLOYMENT.md`, and re-run the repository preflight/tests before pushing the final commit.
