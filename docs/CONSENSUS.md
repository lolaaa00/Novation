# Consensus design

## Why semantic consensus is needed

A deterministic program can verify addresses, hashes, ratifications and revisions. It cannot reliably decide whether public evidence actually establishes that a proposed successor satisfies a natural-language operational role and qualification standard.

Novation therefore puts only that bounded judgement inside GenLayer consensus.

## Frozen inputs

`resolve_qualification(proposal_id)` copies only immutable proposal/agreement fields into `_assess_candidate`:

- agreement name;
- role description;
- qualification criteria;
- candidate subject;
- candidate statement;
- three already-frozen evidence URLs.

The model cannot edit any of them.

## Five-dimension observation

Each validator derives exactly five semantic dimensions:

```text
subject
capability
criteria
continuity
evidence
```

Each is one of:

```text
PASS
FAIL
UNKNOWN
```

The derived state-affecting result is deterministic:

- if subject or evidence is not `PASS` -> `INCONCLUSIVE`;
- if capability, criteria or continuity contains a `FAIL` -> `NOT_QUALIFIED`;
- if capability, criteria and continuity are all `PASS` -> `QUALIFIED`;
- otherwise -> `INCONCLUSIVE`.

The model returns no activation instruction.

## Evidence handling

Evidence pages are treated as untrusted data. The prompt explicitly instructs the model not to follow instructions from the pages.

A conclusive observation must identify a source index and supply a short verbatim excerpt. `grounded_observation` verifies that the excerpt actually occurs in the fetched body. If it does not, the leader path downgrades the result to `INCONCLUSIVE`.

## Leader path

The leader:

1. independently fetches each non-empty frozen HTTPS URL;
2. caps the total body volume;
3. asks the model for the bounded observation;
4. canonicalises the response;
5. rejects ungrounded conclusiveness;
6. returns the observation.

## Validator path

Each validator:

1. rejects malformed leader output;
2. independently fetches the same public URLs;
3. independently re-runs the same semantic task;
4. derives its own state-affecting qualification class;
5. requires leader and validator derived class to match;
6. for a conclusive leader result, requires the leader's quoted evidence to exist in the validator-fetched source copy.

The validator does not simply approve formatting or restate the leader answer.

## Why rich prose is not compared

Exact natural-language rationales can differ while representing the same bounded decision. State therefore depends on the derived qualification class and stored bounded vector, not prose similarity.

## Fail-closed behaviour

Unavailability, malformed model output, missing source grounding, insufficient subject linkage or unresolved ambiguity become `INCONCLUSIVE`.

`INCONCLUSIVE` does not transfer responsibility and never satisfies `can_activate`.
