# Deployment evidence

**Status: not yet populated with live evidence.**

This source package was prepared without access to Lola's funded signer. Do not replace placeholders with guesses. The final operator must update this file only after finalised Studionet transactions/readbacks are observed.

## Final deployment

| Field | Observed value |
|---|---|
| Network | Studionet |
| Chain ID | 61999 |
| RPC | `https://studio.genlayer.com/api` |
| CLI | 0.39.1 |
| Source commit | PENDING |
| Contract address | PENDING |
| Deployment transaction | PENDING |
| Deployment finalised at | PENDING |
| Source hash / artefact hash | PENDING |

## Tooling evidence

| Check | Observed result |
|---|---|
| `python scripts/preflight.py` | PENDING FINAL OPERATOR RUN |
| `python -m unittest discover -s tests -v` | PENDING FINAL OPERATOR RUN |
| GenVM lint/version | PENDING / record only if actually run |
| CLI `--version` | PENDING FINAL OPERATOR RUN |
| RPC `eth_chainId` | PENDING FINAL OPERATOR RUN |

## Live lifecycle evidence

### Qualified succession

- agreement creation tx: PENDING
- agreement ID: PENDING
- pre-activation definition hash: PENDING
- pre-activation terms digest: PENDING
- successor proposal tx / ID: PENDING
- qualification tx: PENDING
- qualification readback: PENDING
- early activation refusal evidence: PENDING
- principal ratification tx: PENDING
- incumbent ratification tx: PENDING
- successor ratification tx: PENDING
- activation tx / record ID: PENDING
- post-activation agreement readback: PENDING
- revision-1 lineage readback: PENDING
- old-incumbent consumer result: PENDING
- new-incumbent consumer result: PENDING

### Unqualified case

- proposal / qualification refs: PENDING
- final readback proving no responsibility transfer: PENDING

### Ambiguous / fail-closed case

- proposal / qualification refs: PENDING
- final readback: PENDING

### Optional ContinuityGate integration

- example contract address: PENDING / OMIT IF NOT DEPLOYED
- old-incumbent result: PENDING
- new-incumbent result: PENDING

## Final assertion

Do not mark the repository live until the final deployed source matches the repository commit and the evidence above has been reconciled against finalized chain state.
