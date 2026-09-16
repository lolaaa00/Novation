# Novation final-runtime handoff for Lola's agent

Finish Novation completely from the repository folder Lola opens for you.

Do not just review it, return a checklist, redesign it, or add product features. Inspect the existing implementation and documentation, run the actual checks, fix only genuine runtime/tooling incompatibilities, deploy the final contract, execute the live lifecycle, collect real evidence, update the evidence documents, and push the finished repository to:

`https://github.com/lolaaa00/Novation`

## Non-negotiable scope

Novation is a **standalone GenLayer Intelligent Contract primitive**.

Do **not** add a frontend.

Do not add React, Next.js, Vite, Vue, a dashboard, landing page, wallet UI or product application. `examples/continuity_gate.py` is an optional contract consumer example, not a frontend.

Preserve the core primitive:

> a successor may replace the current obligor only after consensus-backed qualification against frozen public evidence and all configured parties ratify the exact frozen proposal; activation changes the incumbent and lineage but not the frozen obligation definition.

Do not broaden this into legal advice or claim that the protocol performs legal novation.

## Immutable final network/tooling target

- network: **Studionet**
- chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- GenLayer CLI: **0.39.1 exactly**

Do not change the final network. Do not upgrade the CLI beyond the pinned release for this build.

The committed deployment helper checks both the RPC chain identity and CLI version before it can submit a deployment.

## Read first

Read these in full before changing code:

1. `README.md`
2. `SUBMISSION.md`
3. `BUILD_STATUS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/CONSENSUS.md`
6. `docs/SECURITY_MODEL.md`
7. `docs/LIVE_TEST_PLAN.md`
8. `contracts/novation.py`
9. `tests/test_novation_contract.py`
10. `tests/test_source_invariants.py`
11. `scripts/preflight.py`
12. `scripts/deploy_studionet.py`

## Phase 1 — verify the package before touching runtime

From the repository root run:

```bash
python scripts/preflight.py
python -m unittest discover -s tests -v
python -m py_compile contracts/novation.py examples/continuity_gate.py
```

All must pass.

If the official GenVM linter is available, run it against `contracts/novation.py`. Record the exact tool version and actual output in `docs/DEPLOYMENT.md`; never claim a lint/runtime pass that was not observed.

If an actual GenVM/runtime incompatibility is found, make the smallest compatible fix that preserves every invariant documented in `docs/ARCHITECTURE.md` and `docs/SECURITY_MODEL.md`. Add a regression test for every fix.

## Phase 2 — use CLI 0.39.1 without polluting the repo

A local CLI is allowed and is preferred if replacing a global installation would disturb other projects. Keep the npm install **outside this repository**, because this submission must remain frontend-free and has no package manifest.

### Windows PowerShell local install

From the parent directory of the Novation repository:

```powershell
mkdir novation-cli -Force
Push-Location novation-cli
npm init -y
npm install genlayer@0.39.1
$env:GENLAYER_BIN = (Resolve-Path .\node_modules\.bin\genlayer.cmd).Path
Pop-Location
```

Keep that PowerShell session open, enter the Novation repository, and verify:

```powershell
& $env:GENLAYER_BIN --version
```

It must report `0.39.1`.

### macOS/Linux local install

From the parent directory:

```bash
mkdir -p novation-cli
cd novation-cli
npm init -y
npm install genlayer@0.39.1
export GENLAYER_BIN="$PWD/node_modules/.bin/genlayer"
cd ../Novation
"$GENLAYER_BIN" --version
```

It must report `0.39.1`.

A global install of the exact pinned release is also acceptable if Lola deliberately wants that. Do not install an unspecified/latest CLI.

## Phase 3 — signer and final deploy

1. Confirm the selected CLI can see the intended funded signer.
2. Do not write a private key or mnemonic into this repository.
3. From the repository root run:

```bash
python scripts/deploy_studionet.py
```

The helper will:

- run preflight;
- verify CLI `0.39.1`;
- query `eth_chainId` from the explicit Studionet RPC;
- refuse unless it is `61999`;
- show the configured CLI account;
- deploy `contracts/novation.py` using the explicit RPC.

Wait for successful finalisation. Capture the contract address, deployment transaction hash, source/commit hash, CLI version and timestamp.

Do not invent any value if a readback is unavailable.

## Phase 4 — make the synthetic fixtures public

The repository contains:

- `fixtures/candidate_qualified.md`
- `fixtures/candidate_unqualified.md`
- `fixtures/candidate_ambiguous.md`

Once the repo has been pushed publicly, use the raw GitHub URLs for these files as synthetic HTTPS evidence. They contain no secrets or real-person claims.

If you need the fixtures public before the final evidence commit, an initial push of the source package is acceptable. Do not change the contract after deployment unless a genuine runtime fix is necessary; if it changes, redeploy and make the deployment document reflect the final source only.

## Phase 5 — execute the live lifecycle

Follow `docs/LIVE_TEST_PLAN.md` exactly. At minimum prove on chain:

1. create a three-party agreement with a synthetic terms digest, role and criteria;
2. propose a successor using `candidate_qualified.md` evidence;
3. resolve qualification and read back `QUALIFIED` plus the semantic vector/evidence excerpt;
4. prove activation fails before all required ratifications;
5. ratify as principal, current incumbent and candidate;
6. activate and prove:
   - current incumbent changed to the candidate;
   - revision advanced exactly once;
   - an immutable lineage record was created;
   - terms digest is unchanged;
   - definition hash is unchanged;
   - old incumbent fails `is_current_obligor`;
   - new incumbent passes with the exact expected definition hash;
7. create a second proposal from the new incumbent and show the former incumbent is no longer a valid three-party ratifier;
8. use `candidate_unqualified.md` in a fresh agreement/proposal and prove it cannot activate or transfer responsibility;
9. use `candidate_ambiguous.md` and prove the contract fails closed as `INCONCLUSIVE`; if the same immutable evidence is retried, responsibility still must not move unless consensus becomes conclusive;
10. close an agreement and prove its consumer gate returns false.

If practical, deploy `examples/continuity_gate.py` as an additional **example contract**, configure it with the Novation address/agreement/hash, and prove the old incumbent is blocked while the newly activated successor can acknowledge. Do not present the example as a second primary submission.

## Phase 6 — evidence and final audit

Fill `docs/DEPLOYMENT.md` only with observed facts:

- final contract address;
- final deployment transaction;
- source commit hash;
- CLI version;
- network/chain readback;
- qualification/ratification/activation transaction references;
- key view readbacks;
- optional consumer address/evidence;
- lint/runtime/test outputs.

Then run again:

```bash
python scripts/preflight.py
python -m unittest discover -s tests -v
```

The repository must remain frontend-free and the preflight must remain green.

## Phase 7 — push

Commit the final evidence and push to:

`https://github.com/lolaaa00/Novation`

Before declaring completion, inspect the actual GitHub default branch and verify it contains the final source, tests, docs and deployment evidence.

## Do not weaken these invariants to make a test pass

- validators independently re-fetch and re-evaluate the frozen evidence;
- conclusive results remain source-grounded;
- `INCONCLUSIVE` remains a fail-closed first-class result;
- the qualification model cannot alter agreement state directly;
- proposal hashes remain revision/from-party/evidence/candidate bound;
- configured ratifications cannot be bypassed;
- stale proposals cannot activate;
- terms digest and agreement definition hash never mutate on activation;
- lineage is immutable and revision-indexed;
- only the current obligor passes the consumer view;
- no frontend is added;
- final deploy uses Studionet chain `61999` and CLI `0.39.1`.
