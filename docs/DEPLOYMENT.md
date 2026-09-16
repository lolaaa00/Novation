# Deployment evidence

**Status: live on Studionet.** Every value below was read back from finalized Studionet transactions during this deployment session. No value is invented.

## Final deployment

| Field | Observed value |
|---|---|
| Network | Studionet |
| Chain ID | `61999` (confirmed via `eth_chainId` before deploy) |
| RPC | `https://studio.genlayer.com/api` |
| CLI | `0.39.1` (pinned local install, verified with `--version`) |
| Deployer account | `probe` / `0xaa18eCD158AEC67c75A51768b747cb3247A21689` |
| Source commit | `2548a962cafac53817ab2122900b311b26e05868` |
| Contract address | `0x271e7156fdD830Ff4361D339Ed48d6e91d8f46aB` |
| Deployment transaction | `0x3c58fd655870b82faf479360ed6ad218cd07ef8be3777c859feccc27eff1565e` |
| Deployment result | `FINALIZED`, consensus `MAJORITY_AGREE` |
| Source hash (sha256 of `contracts/novation.py`) | `62fc3e8296666f319b6c3907e964771bd760b97af8fda99091486a98f73a4798` (matches `MANIFEST.sha256`; file unchanged since deployment) |

GenVM linter: no standalone `genvm-lint`/lint subcommand was found in GenLayer CLI `0.39.1` (only `init/up/stop/account/deploy/call/write/schema/code/config/update/localnet/new/network/receipt/appeal/appeal-bond/trace/finalize/finalize-batch/staking`). No separate lint pass is claimed. The contract's own on-chain deployment and 6 live write transactions across 5 lifecycle cases constitute the observed GenVM runtime validation.

## Tooling evidence

| Check | Observed result |
|---|---|
| `python scripts/preflight.py` (Python 3.13.14) | `Novation preflight PASS: 47 checks` |
| `python -m unittest discover -s tests -v` (Python 3.13.14) | `Ran 27 tests ... OK` |
| `python -m py_compile contracts/novation.py examples/continuity_gate.py` | passed, no errors |
| CLI `--version` | `0.39.1` |
| RPC `eth_chainId` | `0xf22f` = `61999` |
| GenVM lint | not available as a separate tool in this CLI release; not claimed |

## Live lifecycle evidence

Fixture evidence used the raw GitHub URLs from this repository's own initial push (commit `2548a96...`), made public before qualification was resolved:

- `https://raw.githubusercontent.com/lolaaa00/Novation/main/fixtures/candidate_qualified.md`
- `https://raw.githubusercontent.com/lolaaa00/Novation/main/fixtures/candidate_unqualified.md`
- `https://raw.githubusercontent.com/lolaaa00/Novation/main/fixtures/candidate_ambiguous.md`

Actors (all local GenLayer CLI accounts, no private keys committed):

- `P` = `caveat_principal` / `0x19Fbc43de9F8dbcE33FBa7ad34e9F4eE49E565E1`
- `A` (initial incumbent, agreement 1) = `integration-test` / `0x7099f2F0d13A9e0C208A9E140f681334cc3D6B89`
- `B` (first successor, agreement 1) = `probe` / `0xaa18eCD158AEC67c75A51768b747cb3247A21689`
- `C` (second successor, agreement 1) = `vertex-fresh-test` / `0xA6cb6287A808e40561fB7FE3E058074617e417C4`
- unqualified/ambiguous candidate address (never signs; these proposals never reach ratification) = `watchtower-deployer` / `0x2d24de590f1f5bb2ff7838b06ccaf5a4c91cef2f`

### Case 1 — qualified three-party succession (agreement 1)

- agreement creation tx: `0x650c69691ff4fc68451a2028e19b1b60222728a9ff2225d18ac4ac1d639c7749` (FINALIZED) — returned agreement ID `1`
- agreement ID: `1`
- pre-activation definition hash: `f78f502d787ecabd369fd510e617e9a17a1b1f35d7d4e730274bc1488cf21ebd`
- pre-activation terms digest: `0xabababababababababababababababababababababababababababababababab`
- successor proposal tx: `0x4fd59eb3e0763de779e1929c9c74f2259a2955b7ae10458bf0251577de9501d8` (FINALIZED) — proposal ID `1`, `proposal_hash = 187cff8925ab25d300a4eca2522bea96985b7b3c994c91c2e8852cde8c839c91`
- qualification tx: `0x5deebf5cd122ecf2b9d2f7938c06a4e4139ad62743ddbabb316077c4f904093c` (FINALIZED, consensus `MAJORITY_AGREE`)
- qualification readback: `QUALIFIED`, `semantic_vector = PPPPP`, `reason_code = ALL_CRITERIA_MET_WITH_PUBLIC_EVIDENCE`, `evidence_source_index = 1`, grounded excerpt: *"Successor Operations Ltd operates public HTTP API services continuously and maintains an on-call incident response function covering service availability, production incidents and customer-impacting outages."* (verbatim substring of the fetched qualified fixture)
- early activation refusal: tx `0x3c12719d36cc253480003ba5d5f7c7ea9a5bf8086e37f922c853e06760d10606` rolled back with payload `EXPECTED: required ratifications are incomplete`; `can_activate(1)` read `false` beforehand
- principal (`P`) ratification tx: `0xd718c2783e046b98e34f1b8e3d945b30deb2766f1504ae315342bdc7f055141e`
- successor (`B`) ratification tx: `0xb7384ec2f188de5d075cb2e7e777904a2e862cbd422fa4a2da809b041382ad2c`
- `can_activate(1)` after P+B only: `false` (incumbent ratification still outstanding)
- incumbent (`A`) ratification tx: `0x8baae6baf1acd00bd2be67da00027ab4de1f02fe127dca67cb9fdb9b581d8945`
- `can_activate(1)` after all three: `true`
- activation tx: `0x630758f18e6922c9f579c429ccbb4a5e8133e7edc4863c5b8871a5cc6fc8f304` (FINALIZED) — record ID `1`
- post-activation agreement readback: `incumbent = 0xaa18eCD158AEC67c75A51768b747cb3247A21689 (B)`, `revision = 1`, `history_count = 1`, `terms_digest` and `definition_hash` unchanged from pre-activation values
- revision-1 lineage readback (`get_record_for_revision(1,1)`): `from_party = A`, `to_party = B`, `previous_revision = 0`, `new_revision = 1`, `agreement_definition_hash` and `terms_digest` match the frozen values, `proposal_hash` matches proposal 1
- old-incumbent consumer result: `is_current_obligor(1, A, f78f502d...) = false`
- new-incumbent consumer result: `is_current_obligor(1, B, f78f502d...) = true`
- wrong-hash consumer result: `is_current_obligor(1, B, <wrong hash>) = false`

### Case 2 — lineage authority moves with the incumbent (agreement 1, second novation)

- second proposal tx (proposer `B`, candidate `C`): `0x808593aaefe2425e116ff169eeb737ea4cd4e344c33a954b471cae6d7d5dc0ef` (FINALIZED) — proposal ID `2`, `proposal_hash = 997a887ab0a9c8335602b61d918d3c0ba35f3a366c87b3ccded223bb272fcb8b`
- qualification tx: `0x5fbdc64cf503b1ca5e4fd54783c38308139dd4a7f5b29af7e7407f0cdd185079` (FINALIZED) — `QUALIFIED`, `semantic_vector = PPPPP`, `reason_code = ALL_CRITERIA_MET`
- former incumbent `A` ratification attempt (rejected): tx `0x9cc188814d1fd3fdcc784595ad6cf507cac7dd692c2d44a2bea0628d1cba1329` rolled back with payload `EXPECTED: caller is not a required ratifying party`
- current incumbent `B` ratification (accepted, recorded as `INCUMBENT` role): tx `0x47d4fd0afd797e78dfe8f8dd18f17c815058d8b21b61c9f9411af334df6daf6d`; readback confirmed `incumbent_approved = true`
- principal `P` ratification tx: `0x60cad40383d79b94759c40e684e16708c62eb5eba6358def2916fbfd50082efc`
- successor `C` ratification tx: `0x008ffe3f1a797815c2e656ff905f72699cf6eb2e66f4061f381522e1b99975e7`
- `can_activate(2)` before activation: `true`
- second activation tx: `0xc2377ebe071a85f07a6d2ba2ef892d2e87308e64f6bd59b06055b7cf49ddfbb6` (FINALIZED) — record ID `2`
- post-second-activation agreement readback: `incumbent = 0xA6cb6287A808e40561fB7FE3E058074617e417C4 (C)`, `revision = 2`, `history_count = 2`, `terms_digest` and `definition_hash` still unchanged
- revision-2 lineage readback (`get_record_for_revision(1,2)`): `from_party = B`, `to_party = C`, `previous_revision = 1`, `new_revision = 2`
- revision-1 lineage record remains independently readable and unmodified (`get_record_for_revision(1,1)` still returns the original `A -> B` record)

### Case 3 — explicit unqualified successor (fresh agreement 2)

- agreement creation tx: `0x4988026ae3cd412083a3332bce827bc4b3aebbebf203c9e8109b4c6e15e8d769` (FINALIZED) — agreement ID `2`, `definition_hash = 79c145ad02aef8a74a01d746916e5bca8693e8bf1c377907e663a163121270f5`
- proposal tx (unqualified fixture): `0xc9329f70a1f8dea335e4928b56bcf25291e417e097d0d8647d96317ea3b3b913` (FINALIZED) — proposal ID `3`
- qualification tx: `0x71c74e38621ecae149f34d5f426074352bf68a3def56999dca49cd6c0ec85d22` (FINALIZED) — `NOT_QUALIFIED`, `semantic_vector = PFFFP`, `reason_code = NO_API_IR_AND_MATERIAL_BARRIER`, grounded excerpt from the unqualified fixture
- final readback proving no responsibility transfer: proposal `status_name = NOT_QUALIFIED`, agreement `pending_proposal_id = 0`, `incumbent` and `revision` unchanged from creation, `can_activate(3) = false`

### Case 4 — ambiguity fails closed (fresh agreement 3)

- agreement creation tx: `0x1fa2b8cfb1fa80410858a207d0e779cd49bb7fbbb2720831ba95b7ee66447501` (FINALIZED) — agreement ID `3`, `definition_hash = eb4af3f857244cf9616a6fbadcf507cf50fc1b9de8feb4d2e236474dd3627418`
- proposal tx (ambiguous fixture): `0x83830680f42315f2ed8ca61b825b2149dc9eb713d01392aa344e6f5d89fbbae3` (FINALIZED) — proposal ID `4`
- first qualification attempt tx: `0x356a65eef32ececf56b014bdfec411f180be6d03211fcdba6b0523141b8a9c6c` (FINALIZED) — `INCONCLUSIVE`, `semantic_vector = UUUUU`, `reason_code = EVIDENCE_INCONCLUSIVE`, `qualification_attempts = 1`; proposal stayed open (`status_name = INCONCLUSIVE`, not closed)
- retry of the same immutable proposal, tx: `0x1fc0e4db1205aff0789f0bb363e7cead7128161527fe358fda89ece736e580c9` (FINALIZED) — still `INCONCLUSIVE`, `qualification_attempts = 2`, `reason_code = INCONCLUSIVE_FIXTURE`
- final readback: agreement 3 `incumbent`/`revision` unchanged across both attempts, `can_activate(4) = false`; responsibility never moved despite retry on the same evidence

### Case 5 — closure (agreement 2)

- `close_agreement` tx: `0xa44285a646739ca858aa5fba4961817d23bb69b304f63ad09147723c7e0b0916` (FINALIZED)
- post-closure readback: agreement 2 `status_name = CLOSED`
- consumer gate result: `is_current_obligor(2, A, 79c145ad...) = false` even though `A` was the last (and only) recorded incumbent

### Optional ContinuityGate integration

- example contract address: `0xFED80ca90BbE324dc9Dd4e2aF8eB2D7ab8d20155`
- deployment tx: `0x978075d4abc0fa056e942c6a10648ceb3c7e3dba1bdf16d5e693af7db4cc5e96` (FINALIZED)
- configured with: Novation address `0x271e7156fdD830Ff4361D339Ed48d6e91d8f46aB`, agreement ID `1`, `expected_definition_hash = f78f502d787ecabd369fd510e617e9a17a1b1f35d7d4e730274bc1488cf21ebd` (the case-1 agreement, by then already twice-novated to incumbent `C`)
- old-incumbent (`A`) result: tx `0x9bebee186238265e89f99068575402a4fbef1fb166fe38606d757da1358a6012` rolled back — `caller is not the current obligor for the pinned agreement`
- old-incumbent (`B`, the first successor and now also stale) result: tx `0x8fd95c3fb9084e6fe7315a13c1b0cd4c82392d998ba3c8fbd25e6cdb6b8c50ef` rolled back — same rejection
- current-incumbent (`C`) result: tx `0x8fe8144ece381b5765de15e5f1f2db40fd63a47f5cf7c3c62b4df38222e6bc5f` (FINALIZED) succeeded; `get_state()` readback: `acknowledgement_count = 1`, `last_acknowledger = 0xA6cb6287A808e40561fB7FE3E058074617e417C4 (C)`, `last_note = "C acknowledges as current obligor"`

## Tooling note (CLI argument encoding)

GenLayer CLI `0.39.1`'s `--args` scalar parser (`parseScalar` in the shipped bundle) auto-converts any `0x`-prefixed token into a `BigInt`, and converts an empty string `""` into the number `0`. This is a CLI argument-encoding behaviour, not a contract defect, and required two accommodations during live testing, neither of which touched `contracts/novation.py`:

- `terms_digest` was passed to the CLI **without** its `0x` prefix (the contract's `normalise_digest` already accepts and canonicalises unprefixed 64-hex-character digests).
- Optional `evidence_url_2`/`evidence_url_3` were passed as the same valid `https://` URL as `evidence_url_1` instead of an empty string, since the CLI cannot encode a literal empty string as a `str` argument. This is evidentially equivalent (each URL is still independently fetched and re-verified by every validator) and does not relax `validate_evidence_url`, which still runs unchanged.

## Final assertion

The final deployed source at `0x271e7156fdD830Ff4361D339Ed48d6e91d8f46aB` matches repository commit `2548a962cafac53817ab2122900b311b26e05868` (`contracts/novation.py` sha256 `62fc3e82...`, unchanged since). All evidence above was read back from finalized Studionet transactions during this session; none of it is projected or assumed.
