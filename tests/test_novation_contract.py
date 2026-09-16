from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "novation.py"


class UInt(int):
    def __new__(cls, value=0):
        return int.__new__(cls, int(value))


class Address(str):
    def __new__(cls, value="0x0000000000000000000000000000000000000000"):
        return str.__new__(cls, str(value).lower())


class Event:
    emitted = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def emit(self):
        Event.emitted.append(self.__class__.__name__)
        return None


class Contract:
    pass


class UserError(Exception):
    pass


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


class Decorator:
    def __call__(self, fn):
        return fn

    @property
    def payable(self):
        return self


class FakeMessage:
    def __init__(self):
        self.sender_address = Address("0x1000000000000000000000000000000000000001")
        self.raw = types.SimpleNamespace(datetime="2026-09-15T16:00:00Z")


class Keccak256:
    def __init__(self, data: bytes):
        self._hash = hashlib.sha3_256(data)

    def hexdigest(self):
        return self._hash.hexdigest()


def install_fake_genlayer():
    module = types.ModuleType("genlayer")
    gl = types.SimpleNamespace()
    gl.Contract = Contract
    gl.Event = Event
    gl.public = types.SimpleNamespace(write=Decorator(), view=Decorator())
    gl.contract_interface = lambda cls: cls
    gl.message = FakeMessage()
    gl.message_raw = {"datetime": "2026-09-15T16:00:00Z"}

    def run_nondet_unsafe(leader_fn, validator_fn):
        value = leader_fn()
        if not validator_fn(Return(value)):
            raise UserError("fake consensus disagree")
        return value

    gl.vm = types.SimpleNamespace(UserError=UserError, Return=Return, run_nondet_unsafe=run_nondet_unsafe)
    gl.nondet = types.SimpleNamespace(
        web=types.SimpleNamespace(get=lambda _url: (_ for _ in ()).throw(RuntimeError("web unavailable in unit test"))),
        exec_prompt=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("llm unavailable in unit test")),
    )

    module.gl = gl
    module.Address = Address
    module.u8 = UInt
    module.u32 = UInt
    module.u256 = UInt
    module.TreeMap = dict
    module.DynArray = list
    module.Keccak256 = Keccak256
    module.allow_storage = lambda cls: cls
    module.__all__ = [
        "gl", "Address", "u8", "u32", "u256", "TreeMap", "DynArray",
        "Keccak256", "allow_storage",
    ]
    sys.modules["genlayer"] = module
    return module


FAKE = install_fake_genlayer()
spec = importlib.util.spec_from_file_location("novation_contract", CONTRACT)
novation = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["novation_contract"] = novation
spec.loader.exec_module(novation)


PRINCIPAL = Address("0x1000000000000000000000000000000000000001")
INCUMBENT = Address("0x2000000000000000000000000000000000000002")
SUCCESSOR = Address("0x3000000000000000000000000000000000000003")
SUCCESSOR_2 = Address("0x4000000000000000000000000000000000000004")
OUTSIDER = Address("0x5000000000000000000000000000000000000005")
DIGEST = "0x" + "ab" * 32
URL = "https://example.com/evidence"


def pass_observation():
    return {
        "subject": novation.DIM_PASS,
        "capability": novation.DIM_PASS,
        "criteria": novation.DIM_PASS,
        "continuity": novation.DIM_PASS,
        "evidence": novation.DIM_PASS,
        "reason_code": "ALL_REQUIREMENTS_SUPPORTED",
        "source_index": 1,
        "evidence_excerpt": "qualified evidence",
    }


def fail_observation():
    return {
        "subject": novation.DIM_PASS,
        "capability": novation.DIM_FAIL,
        "criteria": novation.DIM_FAIL,
        "continuity": novation.DIM_PASS,
        "evidence": novation.DIM_PASS,
        "reason_code": "MANDATORY_CAPABILITY_MISSING",
        "source_index": 1,
        "evidence_excerpt": "does not hold required capability",
    }


def inconclusive_observation():
    return {
        "subject": novation.DIM_UNKNOWN,
        "capability": novation.DIM_UNKNOWN,
        "criteria": novation.DIM_UNKNOWN,
        "continuity": novation.DIM_UNKNOWN,
        "evidence": novation.DIM_UNKNOWN,
        "reason_code": "EVIDENCE_INSUFFICIENT",
        "source_index": 0,
        "evidence_excerpt": "",
    }


class NovationContractTests(unittest.TestCase):
    def setUp(self):
        Event.emitted.clear()
        FAKE.gl.message.sender_address = PRINCIPAL
        FAKE.gl.message.raw.datetime = "2026-09-15T16:00:00Z"
        FAKE.gl.message_raw["datetime"] = "2026-09-15T16:00:00Z"
        self.c = novation.Novation()
        # GenVM zero-initializes persistent mappings. Plain Python does not, so
        # the shim supplies the same empty state explicitly.
        self.c.agreements = {}
        self.c.proposals = {}
        self.c.records = {}
        self.c.record_by_revision = {}

    def create(self, mode=novation.CONSENT_THREE_PARTY):
        return self.c.create_agreement(
            "Critical API continuity",
            INCUMBENT,
            DIGEST,
            "Operate the public API and honour the frozen service obligation.",
            "Public evidence must show API operations experience, incident response capability, and ability to assume service without a disclosed material barrier.",
            mode,
        )

    def propose(self, agreement_id, candidate=SUCCESSOR):
        FAKE.gl.message.sender_address = PRINCIPAL
        return self.c.propose_successor(
            agreement_id,
            candidate,
            "Successor Operations Ltd",
            URL,
            "",
            "",
            "Candidate accepts the exact frozen terms if qualified and ratified.",
        )

    def qualify(self, proposal_id, observation=None):
        obs = observation or pass_observation()
        self.c._assess_candidate = lambda *_args: dict(obs)
        self.c.resolve_qualification(proposal_id)

    def test_three_party_happy_path_preserves_terms_and_hash(self):
        agreement_id = self.create()
        before = self.c.get_agreement(agreement_id)
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)

        FAKE.gl.message.sender_address = PRINCIPAL
        self.c.ratify(proposal_id)
        FAKE.gl.message.sender_address = INCUMBENT
        self.c.ratify(proposal_id)
        FAKE.gl.message.sender_address = SUCCESSOR
        self.c.ratify(proposal_id)

        self.assertTrue(self.c.can_activate(proposal_id))
        record_id = self.c.activate(proposal_id)
        after = self.c.get_agreement(agreement_id)
        record = self.c.get_record(record_id)

        self.assertEqual(after["incumbent"], str(SUCCESSOR))
        self.assertEqual(after["revision"], 1)
        self.assertEqual(after["history_count"], 1)
        self.assertEqual(after["terms_digest"], before["terms_digest"])
        self.assertEqual(after["definition_hash"], before["definition_hash"])
        self.assertEqual(record["from_party"], str(INCUMBENT))
        self.assertEqual(record["to_party"], str(SUCCESSOR))
        self.assertEqual(record["agreement_definition_hash"], before["definition_hash"])
        self.assertTrue(self.c.is_current_obligor(agreement_id, SUCCESSOR, before["definition_hash"]))
        self.assertFalse(self.c.is_current_obligor(agreement_id, INCUMBENT, before["definition_hash"]))

    def test_activation_requires_every_configured_ratification(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)

        FAKE.gl.message.sender_address = PRINCIPAL
        self.c.ratify(proposal_id)
        FAKE.gl.message.sender_address = SUCCESSOR
        self.c.ratify(proposal_id)
        self.assertFalse(self.c.can_activate(proposal_id))
        with self.assertRaises(UserError):
            self.c.activate(proposal_id)

        FAKE.gl.message.sender_address = INCUMBENT
        self.c.ratify(proposal_id)
        self.assertTrue(self.c.can_activate(proposal_id))

    def test_principal_successor_mode_does_not_require_incumbent(self):
        agreement_id = self.create(novation.CONSENT_PRINCIPAL_SUCCESSOR)
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)
        FAKE.gl.message.sender_address = PRINCIPAL
        self.c.ratify(proposal_id)
        FAKE.gl.message.sender_address = SUCCESSOR
        self.c.ratify(proposal_id)
        self.assertTrue(self.c.can_activate(proposal_id))
        self.c.activate(proposal_id)
        self.assertEqual(self.c.get_agreement(agreement_id)["incumbent"], str(SUCCESSOR))

    def test_unqualified_candidate_closes_slot_without_transfer(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id, fail_observation())
        p = self.c.get_proposal(proposal_id)
        a = self.c.get_agreement(agreement_id)
        self.assertEqual(p["status_name"], "NOT_QUALIFIED")
        self.assertEqual(a["pending_proposal_id"], 0)
        self.assertEqual(a["incumbent"], str(INCUMBENT))
        self.assertFalse(self.c.can_activate(proposal_id))

    def test_inconclusive_result_fails_closed_and_can_retry_same_evidence(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id, inconclusive_observation())
        self.assertEqual(self.c.get_proposal(proposal_id)["status_name"], "INCONCLUSIVE")
        self.assertEqual(self.c.get_agreement(agreement_id)["pending_proposal_id"], proposal_id)
        self.assertFalse(self.c.can_activate(proposal_id))

        self.qualify(proposal_id, pass_observation())
        self.assertEqual(self.c.get_proposal(proposal_id)["status_name"], "AWAITING_RATIFICATION")
        self.assertEqual(self.c.get_proposal(proposal_id)["qualification_attempts"], 2)

    def test_candidate_can_decline_and_release_pending_slot(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)
        FAKE.gl.message.sender_address = SUCCESSOR
        self.c.decline(proposal_id)
        self.assertEqual(self.c.get_proposal(proposal_id)["status_name"], "DECLINED")
        self.assertEqual(self.c.get_agreement(agreement_id)["pending_proposal_id"], 0)

    def test_outsider_cannot_ratify_or_cancel(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)
        FAKE.gl.message.sender_address = OUTSIDER
        with self.assertRaises(UserError):
            self.c.ratify(proposal_id)
        with self.assertRaises(UserError):
            self.c.cancel_proposal(proposal_id)

    def test_new_incumbent_is_required_for_next_three_party_novation(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)
        for actor in (PRINCIPAL, INCUMBENT, SUCCESSOR):
            FAKE.gl.message.sender_address = actor
            self.c.ratify(proposal_id)
        self.c.activate(proposal_id)

        FAKE.gl.message.sender_address = SUCCESSOR
        second = self.c.propose_successor(
            agreement_id,
            SUCCESSOR_2,
            "Second Successor Ltd",
            URL,
            "",
            "",
            "Ready to assume frozen obligations.",
        )
        self.qualify(second)
        FAKE.gl.message.sender_address = INCUMBENT
        with self.assertRaises(UserError):
            self.c.ratify(second)
        FAKE.gl.message.sender_address = SUCCESSOR
        self.c.ratify(second)
        self.assertTrue(self.c.get_proposal(second)["incumbent_approved"])

    def test_record_lookup_by_revision_is_immutable_lineage(self):
        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        self.qualify(proposal_id)
        for actor in (PRINCIPAL, INCUMBENT, SUCCESSOR):
            FAKE.gl.message.sender_address = actor
            self.c.ratify(proposal_id)
        self.c.activate(proposal_id)
        record = self.c.get_record_for_revision(agreement_id, 1)
        self.assertEqual(record["previous_revision"], 0)
        self.assertEqual(record["new_revision"], 1)

    def test_close_agreement_disables_consumer_gate(self):
        agreement_id = self.create()
        definition_hash = self.c.get_agreement(agreement_id)["definition_hash"]
        self.assertTrue(self.c.is_current_obligor(agreement_id, INCUMBENT, definition_hash))
        FAKE.gl.message.sender_address = PRINCIPAL
        self.c.close_agreement(agreement_id)
        self.assertFalse(self.c.is_current_obligor(agreement_id, INCUMBENT, definition_hash))

    def test_digest_validation_and_proposal_hash_binding(self):
        with self.assertRaises(UserError):
            self.c.create_agreement("x", INCUMBENT, "0x1234", "role", "criteria", novation.CONSENT_THREE_PARTY)

        agreement_id = self.create()
        proposal_id = self.propose(agreement_id)
        proposal_hash = self.c.get_proposal(proposal_id)["proposal_hash"]
        self.assertTrue(len(proposal_hash) >= 64)
        self.assertNotEqual(proposal_hash, self.c.get_agreement(agreement_id)["definition_hash"])


if __name__ == "__main__":
    unittest.main()
