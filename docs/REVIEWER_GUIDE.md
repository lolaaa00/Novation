# Reviewer guide

## Thirty-second summary

Novation preserves a frozen obligation while replacing only the party responsible for it. GenLayer validators decide a narrow semantic question—whether immutable public evidence supports the frozen successor criteria. Deterministic code then requires configured party consent, rejects stale state, writes immutable lineage and changes only the current incumbent/revision.

## Five things to inspect first

1. `Agreement.definition_hash` and `terms_digest` in `contracts/novation.py`.
2. `_assess_candidate` for independent validator evidence replay.
3. `derive_qualification_status` + `grounded_observation` for fail-closed semantic settlement.
4. `activate` for deterministic ratification/staleness/lineage checks and absence of definition/terms mutation.
5. `is_current_obligor` for the minimal reusable cross-contract interface.

## Why it is not a thin LLM wrapper

The semantic model controls only a bounded qualification observation. It cannot mutate the agreement or cause activation. The protocol still has:

- immutable definitions;
- revision-bound proposals;
- independent ratification roles;
- stale-state rejection;
- append-only responsibility lineage;
- a deterministic consumer gate;
- first-class inconclusive handling.

## Useful adversarial questions

- Can a leader invent evidence? Conclusive results must quote text independently present in a validator-fetched source.
- Can the criteria be changed after agreement creation? No update method exists and criteria are definition-hashed.
- Can the old incumbent approve a later successor after it has already been replaced? No; ratification uses the current incumbent and the proposal snapshot must match current state.
- Can a qualified successor self-activate? No; configured ratifications are separate deterministic state.
- Can a downstream consumer accidentally accept the right address under the wrong agreement definition? It should pin `expected_definition_hash`.
- What happens when evidence is unavailable? The design fails closed as inconclusive rather than transferring responsibility.

## Limits

This is a protocol continuity primitive, not a legal document, identity oracle or performance guarantee.
