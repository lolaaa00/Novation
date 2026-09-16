# Security model

## Assets protected

Novation protects four protocol properties:

1. **obligation identity** — the frozen definition and terms digest must survive succession;
2. **responsibility continuity** — there must be exactly one current incumbent in contract state;
3. **consent integrity** — qualification cannot replace configured ratification;
4. **lineage integrity** — activated substitutions must remain auditable by revision.

## Threats and mitigations

### Malicious or mistaken proposal author

Threat: proposer swaps evidence or candidate context after approvals begin.

Mitigation: evidence URLs, candidate, current revision/from-party and candidate statement are bound into an immutable proposal hash. Proposal fields are not mutable.

### Stale proposal replay

Threat: a proposal created under an old incumbent/revision activates after responsibility has already changed.

Mitigation: qualification, ratification and activation all check the active proposal, snapshotted revision and `from_party` against current agreement state.

### LLM grants authority

Threat: semantic output directly changes who is responsible.

Mitigation: impossible by architecture. Consensus only writes a bounded qualification result. Separate deterministic ratification and activation gates are required.

### Malicious leader

Threat: leader fabricates qualification or invents supporting evidence.

Mitigation: validators re-fetch and re-run the semantic task. State-affecting derived classes must agree. Conclusive leader evidence must be present in a validator-fetched public source.

### Prompt injection in evidence

Threat: an evidence page instructs validators to approve the candidate or reveal hidden context.

Mitigation: evidence is explicitly delimited as untrusted data and the model task is bounded. The validator independently repeats the assessment. The contract still requires deterministic consent after semantic qualification.

### Source unavailable or ambiguous

Threat: temporary failure is treated as permission.

Mitigation: fail closed to `INCONCLUSIVE`. Responsibility cannot move.

### Qualification criteria rewritten midstream

Threat: creator loosens criteria after an incumbent or consumer relies on them.

Mitigation: no update method exists. Criteria are part of the immutable agreement definition hash.

### Consent bypass

Threat: a qualified candidate activates without all required parties.

Mitigation: `_required_ratifications_met` is deterministic and enforced by both `can_activate` and `activate`.

### Old incumbent remains privileged

Threat: after activation, downstream systems still accept the previous address.

Mitigation: `is_current_obligor` compares against the single current incumbent and exact expected definition hash. The old address immediately returns false.

### Revision-history rewrite

Threat: lineage is edited after activation.

Mitigation: records are append-only under new IDs and indexed by new revision. There is no record update/delete method.

## Explicit non-goals

Novation does not prove:

- legal identity;
- legal enforceability;
- ownership of a real-world organisation;
- that public evidence is universally true;
- performance after succession;
- absence of undisclosed barriers.

A consumer must choose qualification criteria and evidence surfaces appropriate to its own risk model.
