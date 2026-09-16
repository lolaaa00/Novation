# Novation

**Novation is a standalone GenLayer Intelligent Contract primitive for replacing the currently responsible party in a long-lived obligation without rewriting the obligation itself.**

It has **no frontend**. The contract is the submission.

## Why this primitive exists

Long-lived autonomous agreements outlive agents, service operators and organisations. A provider can disappear, reorganise or need to hand an obligation to a successor. A simple owner-controlled `set_provider(new_address)` destroys the distinction between:

- the frozen obligation,
- evidence that a proposed successor can actually assume the role,
- the parties whose consent is required,
- the historical lineage of responsibility.

Novation separates those concerns.

The original agreement freezes a terms digest, role description, successor qualification criteria and consent mode. A successor proposal then has to pass **independent GenLayer semantic qualification against public evidence** and collect the configured ratifications before deterministic code can replace the incumbent. Activation creates an immutable lineage record and preserves the original terms digest and agreement definition hash.

## Reviewer-facing invariant

> A successor can become the current obligor only after independent GenLayer validators agree that the frozen public evidence supports the frozen qualification criteria and every configured consent party ratifies the exact proposal hash; activation changes the incumbent and revision lineage but never rewrites the frozen obligation definition.

Novation does **not** claim legal enforceability, legal novation, real-world identity, or truth beyond the declared public evidence. It is a machine-level continuity primitive for contracts that need a stable answer to: **who currently carries this frozen obligation?**

## Core lifecycle

```text
create agreement
      │
      ▼
ACTIVE revision 0 / incumbent A
      │
      ├── propose successor B + immutable public evidence
      │
      ▼
PENDING_QUALIFICATION
      │
      ├── independent GenLayer re-fetch + semantic assessment
      │
      ├── NOT_QUALIFIED ──> proposal closes, A remains
      │
      ├── INCONCLUSIVE ───> fail closed, same evidence may be retried
      │
      ▼
AWAITING_RATIFICATION
      │
      ├── principal ratifies exact proposal hash
      ├── successor ratifies exact proposal hash
      └── incumbent ratifies when three-party mode requires it
      │
      ▼
ACTIVATE
      │
      ├── immutable NovationRecord A -> B
      ├── revision 0 -> 1
      ├── current obligor = B
      └── terms digest + definition hash unchanged
```

A later novation starts from B, not A. Historical records remain addressable by revision.

## What GenLayer consensus decides

Consensus is intentionally narrow. Validators independently fetch the same frozen HTTPS evidence and classify five dimensions:

1. **subject** — does the evidence actually refer to the declared candidate subject?
2. **capability** — does it support the capabilities required by the role?
3. **criteria** — are the frozen successor criteria supported rather than contradicted?
4. **continuity** — is there evidence that the candidate can assume this specific continuing role without a disclosed material barrier?
5. **evidence** — is the evidence sufficiently public and substantive for a conclusive result?

Each dimension is `PASS`, `FAIL`, or `UNKNOWN`.

The LLM never decides consent, activation, revision numbers, ownership, terms, or state transition rules. A conclusive leader result must include a verbatim excerpt grounded in a source that the validator independently fetched. Validators re-run the semantic task and must agree on the **derived state-affecting qualification class**.

See [`docs/CONSENSUS.md`](docs/CONSENSUS.md).

## Deterministic safety properties

- only the principal or current incumbent may propose a successor;
- only one proposal may be active per agreement;
- the proposal hash binds the agreement definition, revision, current incumbent, candidate, evidence URLs and candidate statement;
- a stale proposal cannot activate after agreement state changes;
- `INCONCLUSIVE` is first-class and fails closed;
- `NOT_QUALIFIED` never transfers the obligation;
- activation requires a `QUALIFIED` result plus every configured ratification;
- the original terms digest and definition hash are immutable across novations;
- every activated substitution creates a revision-indexed immutable lineage record;
- a consumer can gate work with `is_current_obligor(agreement_id, party, expected_definition_hash)`;
- closing the agreement disables that consumer gate.

## Reuse example

[`examples/continuity_gate.py`](examples/continuity_gate.py) shows a tiny independent Intelligent Contract consuming Novation through a typed cross-contract view. It accepts an acknowledgement only from the party Novation currently recognises as obligor under the expected immutable agreement definition hash.

The example is **not** a second submission and it is not required to use Novation.

## Repository layout

```text
contracts/novation.py              primary standalone Intelligent Contract
examples/continuity_gate.py        optional typed IC-to-IC consumer example
fixtures/                          synthetic public evidence for live testing
tests/                             deterministic and source-invariant tests
scripts/preflight.py               source/network/security drift guard
scripts/deploy_studionet.py        chain + CLI locked deploy helper
docs/                              reviewer and operator documentation
```

## Local checks

These checks require only Python 3.12+:

```bash
python scripts/preflight.py
python -m unittest discover -s tests -v
python -m py_compile contracts/novation.py examples/continuity_gate.py
```

If the official GenVM linter is available in the operator environment, also run it against `contracts/novation.py` and record the exact result.

## Final deployment target

The repository is locked to:

- **network:** Studionet
- **chain ID:** `61999`
- **RPC:** `https://studio.genlayer.com/api`
- **GenLayer CLI:** `0.39.1`

The deploy helper refuses to continue if the RPC does not report chain `61999` or the selected CLI does not report `0.39.1`.

```bash
python scripts/deploy_studionet.py
```

The script uses the account already configured in the CLI. It does not read a private key.

See [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md) for the exact final-runtime sequence.

## Status

Source implementation and deterministic tests are included. **No live address or transaction hash is claimed in this package.** The final operator must deploy with a funded signer, execute the live lifecycle, and replace the placeholders in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) only with observed results.
