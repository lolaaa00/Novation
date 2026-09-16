# Architecture

## Primitive boundary

Novation answers one protocol question:

> Which address is currently responsible for an immutable obligation after a consensus-qualified and consent-ratified succession?

It deliberately does not custody funds, execute the underlying service, adjudicate breach, rewrite contract terms, prove legal identity or provide a product UI.

## State model

### Agreement

An `Agreement` freezes the identity of the obligation:

- `principal`
- `initial_incumbent`
- `name`
- `terms_digest`
- `role_description`
- `qualification_criteria`
- `consent_mode`
- `definition_hash`

Mutable continuity state is kept separate:

- `incumbent`
- `revision`
- `history_count`
- `pending_proposal_id`
- `last_record_id`
- lifecycle status.

`definition_hash` canonically binds the creator, original incumbent, human-readable obligation definition and consent rule. It does not change when a successor is activated.

### Proposal

A proposal snapshots the current agreement state:

- agreement ID and revision;
- current incumbent as `from_party`;
- proposed successor address and public subject label;
- up to three immutable HTTPS evidence URLs;
- optional candidate statement;
- `proposal_hash` over the frozen proposal context.

This makes a proposal stale if another continuity transition moves the agreement before it activates.

### NovationRecord

Each successful activation creates an append-only record containing:

- old party;
- new party;
- previous and new revision;
- activation timestamp;
- immutable agreement definition hash;
- immutable terms digest;
- exact proposal hash.

Records are also indexed by `(agreement_id, new_revision)`.

## State machine

```text
AGREEMENT ACTIVE
    │
    └── one active proposal at a time
             │
             ▼
      PENDING_QUALIFICATION
          │       │
          │       ├── NOT_QUALIFIED -> terminal proposal, slot released
          │       └── INCONCLUSIVE -> active/fail-closed/retryable
          ▼
      AWAITING_RATIFICATION
          │       │
          │       ├── DECLINED  -> terminal, slot released
          │       └── CANCELLED -> terminal, slot released
          ▼
      ACTIVATED
          │
          ├── immutable lineage record
          ├── incumbent changes
          └── revision + 1
```

## Consent modes

`THREE_PARTY`

- principal must approve;
- current incumbent must approve;
- successor must approve.

`PRINCIPAL_SUCCESSOR`

- principal must approve;
- successor must approve;
- incumbent approval is intentionally not required because that exception was frozen in the agreement at creation.

The semantic model does not participate in consent.

## Deterministic activation invariant

Activation is possible only when all of the following are simultaneously true:

1. proposal status is awaiting ratification;
2. semantic qualification verdict is `QUALIFIED`;
3. agreement is active;
4. proposal is still the agreement's active proposal;
5. agreement revision equals the proposal snapshot revision;
6. current incumbent equals proposal `from_party`;
7. every configured ratification is present.

Then and only then code writes the lineage record and updates `incumbent` + revision counters. It does not assign new `terms_digest` or `definition_hash` values.

## Consumer interface

The minimal stable reuse hook is:

```python
is_current_obligor(agreement_id, party, expected_definition_hash) -> bool
```

A downstream contract pins the expected agreement definition hash. This prevents an address from becoming acceptable merely because a caller references the wrong agreement or altered definition.

See `examples/continuity_gate.py`.
