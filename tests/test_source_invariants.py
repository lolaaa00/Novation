from __future__ import annotations

import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "novation.py"
SOURCE = CONTRACT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def dotted(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def function(name: str) -> ast.FunctionDef:
    return next(node for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef) and node.name == name)


class SourceInvariantTests(unittest.TestCase):
    def test_exact_dependency_header_present(self):
        self.assertIn('py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6', SOURCE)

    def test_only_one_primary_contract_file(self):
        deployables = sorted(path.name for path in (ROOT / "contracts").glob("*.py"))
        self.assertEqual(deployables, ["novation.py"])

    def test_exactly_one_contract_class(self):
        classes = [
            node for node in TREE.body
            if isinstance(node, ast.ClassDef) and any(dotted(base) == "gl.Contract" for base in node.bases)
        ]
        self.assertEqual([node.name for node in classes], ["Novation"])

    def test_custom_consensus_boundary_is_single(self):
        calls = [node for node in ast.walk(TREE) if isinstance(node, ast.Call) and dotted(node.func) == "gl.vm.run_nondet_unsafe"]
        self.assertEqual(len(calls), 1)

    def test_semantic_boundary_refetches_and_reruns(self):
        text = ast.unparse(function("_assess_candidate"))
        self.assertIn("gl.nondet.web.get", text)
        self.assertIn("gl.nondet.exec_prompt", text)
        self.assertIn("collect_and_judge()", text)
        self.assertIn("derive_qualification_status(follower)", text)

    def test_conclusive_result_is_source_grounded(self):
        text = ast.unparse(function("grounded_observation"))
        self.assertIn("excerpt in body", text)
        self.assertIn("INCONCLUSIVE", text)

    def test_activation_is_not_nondeterministic(self):
        text = ast.unparse(function("activate"))
        self.assertNotIn("gl.nondet", text)
        self.assertNotIn("exec_prompt", text)
        self.assertIn("_required_ratifications_met", text)

    def test_activation_does_not_rewrite_frozen_identity(self):
        text = ast.unparse(function("activate"))
        self.assertNotIn("agreement.definition_hash =", text)
        self.assertNotIn("agreement.terms_digest =", text)
        self.assertIn("agreement.incumbent = proposal.candidate", text)

    def test_proposal_hash_binds_state_and_evidence(self):
        text = ast.unparse(function("canonical_proposal_hash"))
        for marker in ("agreement_revision", "from_party", "candidate", "evidence_url_1", "candidate_statement"):
            self.assertIn(marker, text)

    def test_current_obligor_pins_definition_hash(self):
        text = ast.unparse(function("is_current_obligor"))
        self.assertIn("a.definition_hash == str(expected_definition_hash)", text)
        self.assertIn("a.incumbent == party", text)
        self.assertIn("a.status == AGREEMENT_ACTIVE", text)

    def test_consumer_example_uses_typed_view(self):
        text = (ROOT / "examples" / "continuity_gate.py").read_text(encoding="utf-8")
        self.assertIn("@gl.contract_interface", text)
        self.assertIn("is_current_obligor", text)
        self.assertIn(".view()", text)

    def test_network_and_cli_locks_are_committed(self):
        network = (ROOT / "docs" / "NETWORK.md").read_text(encoding="utf-8")
        deploy = (ROOT / "scripts" / "deploy_studionet.py").read_text(encoding="utf-8")
        self.assertIn("61999", network)
        self.assertIn("https://studio.genlayer.com/api", network)
        self.assertIn("0.39.1", network)
        self.assertIn("EXPECTED_CHAIN_ID = 61999", deploy)
        self.assertIn('EXPECTED_CLI_VERSION = "0.39.1"', deploy)

    def test_repository_has_no_product_frontend(self):
        for relative in ("frontend", "web", "app", "pages", "package.json"):
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_readme_live_claim_matches_deployment_evidence(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        deployment = (ROOT / "docs" / "DEPLOYMENT.md").read_text(encoding="utf-8")
        self.assertIn("docs/DEPLOYMENT.md", readme)
        # If the README claims a specific live contract address, that exact
        # address must also appear in the deployment evidence document, so the
        # README can never drift from or fabricate ahead of observed evidence.
        address_matches = re.findall(r"0x[0-9a-fA-F]{40}", readme)
        for address in address_matches:
            self.assertIn(address, deployment)

    def test_fixture_cases_are_distinct(self):
        q = (ROOT / "fixtures" / "candidate_qualified.md").read_text(encoding="utf-8")
        n = (ROOT / "fixtures" / "candidate_unqualified.md").read_text(encoding="utf-8")
        a = (ROOT / "fixtures" / "candidate_ambiguous.md").read_text(encoding="utf-8")
        self.assertIn("can assume responsibility", q)
        self.assertIn("cannot assume", n)
        self.assertIn("leaves subject linkage", a)
        self.assertNotEqual(q, n)
        self.assertNotEqual(n, a)

    def test_docs_cover_security_and_consensus(self):
        for name in ("ARCHITECTURE.md", "CONSENSUS.md", "SECURITY_MODEL.md", "LIVE_TEST_PLAN.md", "REVIEWER_GUIDE.md"):
            path = ROOT / "docs" / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 500, name)


if __name__ == "__main__":
    unittest.main()
