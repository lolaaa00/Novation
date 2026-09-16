# v0.2.18
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


@gl.contract_interface
class INovation:
    class View:
        def is_current_obligor(
            self,
            agreement_id: u256,
            party: Address,
            expected_definition_hash: str,
        ) -> bool: ...

    class Write:
        pass


class ContinuityGate(gl.Contract):
    """Minimal consumer proving that Novation state can gate another IC.

    This is intentionally an example, not a second submission. A consumer pins
    one Novation agreement definition hash. Only the party currently recorded as
    the obligor for that exact frozen agreement can acknowledge service.
    """

    novation_address: Address
    agreement_id: u256
    expected_definition_hash: str
    acknowledgement_count: u256
    last_acknowledger: Address
    last_note: str

    def __init__(
        self,
        novation_address: Address,
        agreement_id: u256,
        expected_definition_hash: str,
    ):
        self.novation_address = novation_address
        self.agreement_id = agreement_id
        self.expected_definition_hash = expected_definition_hash
        self.acknowledgement_count = u256(0)
        self.last_acknowledger = Address("0x0000000000000000000000000000000000000000")
        self.last_note = ""

    @gl.public.write
    def acknowledge_service(self, note: str) -> None:
        actor = gl.message.sender_address
        novation = INovation(self.novation_address)
        if not novation.view().is_current_obligor(
            self.agreement_id,
            actor,
            self.expected_definition_hash,
        ):
            raise gl.vm.UserError("caller is not the current obligor for the pinned agreement")
        text = " ".join(str(note).strip().split())[:240]
        if text == "":
            raise gl.vm.UserError("note required")
        self.acknowledgement_count = u256(int(self.acknowledgement_count) + 1)
        self.last_acknowledger = actor
        self.last_note = text

    @gl.public.view
    def get_state(self) -> dict:
        return {
            "novation_address": str(self.novation_address),
            "agreement_id": int(self.agreement_id),
            "expected_definition_hash": self.expected_definition_hash,
            "acknowledgement_count": int(self.acknowledgement_count),
            "last_acknowledger": str(self.last_acknowledger),
            "last_note": self.last_note,
        }
