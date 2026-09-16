# Requirement traceability

| Requirement | Contract mechanism | Deterministic/source proof |
|---|---|---|
| Freeze obligation definition | `Agreement` + `canonical_agreement_hash` | activation never assigns `definition_hash` or `terms_digest` |
| Only current state may be novated | proposal snapshots revision + `from_party` | resolve/ratify/activate stale-state checks |
| Semantic successor qualification | `_assess_candidate` | custom validator independently re-fetches/re-reasons |
| No ungrounded conclusive result | `grounded_observation` | conclusive excerpt must occur in fetched body |
| Ambiguity cannot grant permission | `derive_qualification_status` | `INCONCLUSIVE` fails `can_activate` |
| Consent separate from AI | `ratify`, `_required_ratifications_met` | activation enforces configured booleans |
| Exact proposal ratification context | `canonical_proposal_hash` | binds revision/from-party/candidate/evidence/statement |
| Immutable succession history | `NovationRecord` | append-only record IDs + revision index |
| Downstream reuse | `is_current_obligor` | optional `examples/continuity_gate.py` |
| Closed agreement disables authority | agreement status gate | deterministic unit test |
| No frontend | repository/preflight constraint | preflight rejects common frontend paths |
| Final network lock | deployment/preflight constants | chain `61999` + explicit RPC |
| Final CLI lock | deploy helper | exact `0.39.1` version check |
