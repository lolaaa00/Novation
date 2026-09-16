# Live Studionet test plan

This plan must be executed against the **final deployed source** on Studionet chain `61999` using the pinned CLI `0.39.1` for deployment.

Do not fill `docs/DEPLOYMENT.md` from this plan. Fill it only from actual finalized transactions and readbacks.

## Actors

Use synthetic test wallets only:

- `P` — principal
- `A` — initial incumbent
- `B` — qualified successor
- `C` — later successor / unqualified test candidate as appropriate

Never publish private keys.

## Evidence

After this repository is public, raw versions of the files in `fixtures/` can provide stable synthetic HTTPS evidence.

- `candidate_qualified.md`
- `candidate_unqualified.md`
- `candidate_ambiguous.md`

The exact URLs used must be recorded in deployment evidence.

## Case 1 — qualified three-party succession

1. As `P`, create an agreement using:
   - a synthetic 32-byte terms digest;
   - role: operate a public API continuously and provide incident response;
   - criteria matching the qualified fixture;
   - three-party consent mode.
2. Read the agreement and record `definition_hash`, `terms_digest`, revision `0`, and incumbent `A`.
3. As `P` or `A`, propose `B` using the qualified fixture URL.
4. Read the proposal and record its `proposal_hash`.
5. Call `resolve_qualification` and wait for finalization.
6. Confirm proposal is `AWAITING_RATIFICATION`, qualification is `QUALIFIED`, and the stored excerpt is grounded in the fixture.
7. Attempt `activate` before ratification and record that it is refused.
8. Ratify from `P` and `B`. Confirm `can_activate` remains false until `A` also ratifies.
9. Ratify from `A`.
10. Confirm `can_activate == true`.
11. Activate.
12. Read back:
    - current incumbent is `B`;
    - revision is `1`;
    - history count is `1`;
    - pending proposal is cleared;
    - terms digest equals the pre-novation value;
    - definition hash equals the pre-novation value.
13. Read revision-1 record and confirm `A -> B`, proposal hash binding, definition hash and terms digest.
14. Confirm `is_current_obligor(agreement, A, expected_hash) == false`.
15. Confirm `is_current_obligor(agreement, B, expected_hash) == true`.
16. Confirm the same `B` check with an intentionally wrong definition hash returns false.

## Case 2 — lineage authority moves with the incumbent

1. From the case-1 agreement, have `B` propose `C`.
2. Resolve the proposal to a state where ratification is possible using suitable synthetic qualified evidence.
3. Demonstrate that former incumbent `A` cannot satisfy the incumbent ratification role.
4. Demonstrate that current incumbent `B` can.
5. If completing the second activation, confirm revision becomes `2` and both revision records remain readable.

## Case 3 — explicit unqualified successor

Use a fresh agreement so this case cannot disturb case 1.

1. Propose a candidate using `candidate_unqualified.md`.
2. Resolve qualification.
3. Confirm `NOT_QUALIFIED`.
4. Confirm the pending slot is released.
5. Confirm incumbent and revision are unchanged.
6. Confirm `can_activate == false` and activation cannot transfer responsibility.

## Case 4 — ambiguity fails closed

Use a fresh agreement/proposal with `candidate_ambiguous.md`.

1. Resolve qualification.
2. Confirm `INCONCLUSIVE` or another non-permissive outcome if validators cannot ground a conclusive class.
3. Confirm the incumbent remains unchanged.
4. If `INCONCLUSIVE`, retry the **same immutable proposal** once to show retry does not itself create permission.
5. Confirm activation is impossible until the result is genuinely `QUALIFIED` and required ratifications exist.

## Case 5 — closure

1. On an agreement with no pending proposal, have the principal call `close_agreement`.
2. Confirm status is `CLOSED`.
3. Confirm `is_current_obligor` returns false even for the last incumbent.

## Optional consumer proof

Deploy `examples/continuity_gate.py` only as an example integration.

Configure it with:

- deployed Novation address;
- case-1 agreement ID;
- exact case-1 definition hash.

Before case-1 activation, show `A` can acknowledge and `B` cannot. After activation, show `A` is rejected and `B` succeeds. Record all finalized transaction/readback references if this optional proof is used.
