# Local validation evidence

This file records checks actually executed while preparing the source package. It is **not** live-chain deployment evidence.

## Observed source checks

Environment used for these checks:

- Python: `3.13.5`
- GenLayer CLI: not installed in this execution environment
- funded deployment signer: unavailable

Observed results:

```text
python scripts/preflight.py
Novation preflight PASS: 47 checks
network: Studionet / chain 61999 / https://studio.genlayer.com/api
CLI: 0.39.1
frontend: absent
```

```text
python -m unittest discover -s tests -v
Ran 27 tests
OK
```

```text
python -m compileall -q contracts examples scripts tests
PASS (no compile errors)
```

The deployment helper was also invoked without a CLI installed. It ran preflight and then stopped safely before any RPC or signing step with the expected `GenLayer CLI not found` guard. No deployment transaction occurred.

## Not claimed

The preparation environment did not have the official GenLayer CLI, GenVM linter, Lola's funded signer, or reliable outbound DNS to the Studionet RPC. Therefore this package does not claim:

- a GenVM lint pass;
- a Direct Mode/runtime pass under the official GenLayer tooling;
- a successful RPC chain-ID readback from this environment;
- a live deployment;
- finalized lifecycle transactions.

Those items are intentionally left to the final operator and must be recorded in `docs/DEPLOYMENT.md` only after they are actually observed.
