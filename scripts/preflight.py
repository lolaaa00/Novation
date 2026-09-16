#!/usr/bin/env python3
"""Zero-dependency Novation source/network/security preflight.

This deliberately does not import GenLayer. It catches repository drift before
runtime testing or deployment: wrong network/tooling, accidental frontend files,
missing independent validator replay, weak qualification grounding, mutable
agreement identity, incomplete consent gates, and missing lineage checks.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "novation.py"
STABLE_RPC = "https://studio.genlayer.com/api"
STABLE_CHAIN = "61999"
PINNED_CLI = "0.39.1"
FORBIDDEN_RPC_TOKEN = "studio" + "-dev"
FORBIDDEN_CHAIN_TOKEN = "619" + "97"
FORBIDDEN_CLI_TOKEN = "0." + "40.0"


class Fail(RuntimeError):
    pass


def check(ok: bool, message: str) -> None:
    if not ok:
        raise Fail(message)


def dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def function_parents(tree: ast.AST) -> dict[int, tuple[str, ...]]:
    result: dict[int, tuple[str, ...]] = {}

    class Visitor(ast.NodeVisitor):
        stack: list[str] = []

        def generic_visit(self, node: ast.AST) -> None:
            result[id(node)] = tuple(self.stack)
            super().generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

    Visitor().visit(tree)
    return result


def text_files() -> list[pathlib.Path]:
    ignored = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "artifacts"}
    result: list[pathlib.Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() in {".py", ".md", ".yaml", ".yml", ".toml", ".txt", ".example"} or path.name in {".gitignore"}:
            result.append(path)
    return result


def fn(tree: ast.AST, name: str) -> ast.FunctionDef:
    return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)


def main() -> int:
    checks = 0
    source = CONTRACT.read_text(encoding="utf-8")
    compile(source, str(CONTRACT), "exec")
    tree = ast.parse(source)
    checks += 2

    deployables = sorted(p.name for p in (ROOT / "contracts").glob("*.py") if p.name != "__init__.py")
    check(deployables == ["novation.py"], f"unexpected primary deployables: {deployables}")
    checks += 1

    contract_classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(dotted(base) == "gl.Contract" for base in node.bases)
    ]
    check(len(contract_classes) == 1 and contract_classes[0].name == "Novation", "expected one Novation(gl.Contract)")
    checks += 1

    expected_methods = {
        "create_agreement", "propose_successor", "resolve_qualification", "ratify",
        "decline", "cancel_proposal", "activate", "close_agreement", "get_agreement",
        "get_proposal", "get_record", "get_record_for_revision", "can_activate",
        "is_current_obligor", "get_status_dictionary",
    }
    method_names = {n.name for n in contract_classes[0].body if isinstance(n, ast.FunctionDef)}
    check(not (expected_methods - method_names), f"missing methods: {sorted(expected_methods - method_names)}")
    checks += 1

    # Custom consensus must independently refetch evidence and rerun the semantic task.
    parents = function_parents(tree)
    unsafe_calls = []
    web_calls = []
    prompt_calls = []
    nondet_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = dotted(node.func)
        if name == "gl.vm.run_nondet_unsafe":
            unsafe_calls.append(node)
        if name == "gl.nondet.web.get":
            web_calls.append(node)
        if name == "gl.nondet.exec_prompt":
            prompt_calls.append(node)
        if name.startswith("gl.nondet."):
            nondet_calls.append((name, node.lineno, parents.get(id(node), ())))
    check(len(unsafe_calls) == 1, f"expected one custom consensus host, got {len(unsafe_calls)}")
    check(bool(web_calls), "qualification path must fetch public evidence")
    check(bool(prompt_calls), "qualification path must use semantic reasoning")
    for name, line, hosts in nondet_calls:
        check("_assess_candidate" in hosts, f"{name} escaped _assess_candidate at line {line}")
    checks += 4

    assess_text = ast.unparse(fn(tree, "_assess_candidate")).replace('"', "'")
    for marker in (
        "collect_and_judge()",
        "gl.vm.run_nondet_unsafe",
        "derive_qualification_status(leader)",
        "derive_qualification_status(follower)",
        "grounded_observation(leader, follower_bodies)",
    ):
        check(marker in assess_text, f"consensus invariant missing: {marker}")
        checks += 1

    # Conclusive semantic results must be source-grounded and inconclusive is first-class.
    grounded_text = ast.unparse(fn(tree, "grounded_observation"))
    derive_text = ast.unparse(fn(tree, "derive_qualification_status"))
    check("excerpt in body" in grounded_text, "conclusive result is not quote-grounded")
    check("INCONCLUSIVE" in derive_text and "DIM_UNKNOWN" not in derive_text, "qualification derivation drifted")
    check("subject" in derive_text and "evidence" in derive_text and "capability" in derive_text, "bounded dimension gate missing")
    checks += 3

    # Activation must be entirely deterministic and preserve the frozen agreement identity.
    activate_text = ast.unparse(fn(tree, "activate")).replace('"', "'")
    for marker in (
        "_required_ratifications_met",
        "qualification_verdict != QUALIFIED",
        "pending_proposal_id",
        "agreement.revision",
        "proposal.agreement_revision",
        "agreement.incumbent != proposal.from_party",
        "agreement.incumbent = proposal.candidate",
        "agreement.definition_hash",
        "agreement.terms_digest",
        "record_by_revision",
    ):
        check(marker in activate_text, f"activation invariant missing: {marker}")
        checks += 1
    check("agreement.definition_hash =" not in activate_text, "activation mutates frozen definition hash")
    check("agreement.terms_digest =" not in activate_text, "activation mutates frozen terms digest")
    checks += 2

    ratify_text = ast.unparse(fn(tree, "ratify")).replace('"', "'")
    check("principal_approved" in ratify_text and "candidate_approved" in ratify_text, "required consent roles missing")
    check("CONSENT_THREE_PARTY" in ratify_text and "incumbent_approved" in ratify_text, "three-party consent path missing")
    checks += 2

    # Proposal hash must bind current incumbent + revision so approvals cannot be replayed after state changes.
    proposal_hash_text = ast.unparse(fn(tree, "canonical_proposal_hash"))
    for marker in ("agreement_revision", "from_party", "candidate", "evidence_url_1", "candidate_statement"):
        check(marker in proposal_hash_text, f"proposal hash omits {marker}")
        checks += 1

    # Stable network and exact CLI lock across committed text/config.
    for path in text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        check(FORBIDDEN_RPC_TOKEN not in lower, f"preview RPC token present in {path.relative_to(ROOT)}")
        check(FORBIDDEN_CHAIN_TOKEN not in text, f"preview chain id present in {path.relative_to(ROOT)}")
        check(FORBIDDEN_CLI_TOKEN not in text, f"unapproved CLI release present in {path.relative_to(ROOT)}")
    checks += 3

    network_doc = (ROOT / "docs" / "NETWORK.md").read_text(encoding="utf-8")
    deploy_script = (ROOT / "scripts" / "deploy_studionet.py").read_text(encoding="utf-8")
    gltest = (ROOT / "gltest.config.yaml").read_text(encoding="utf-8")
    for text, label in ((network_doc, "NETWORK.md"), (deploy_script, "deploy script"), (gltest, "gltest.config.yaml")):
        check(STABLE_RPC in text, f"stable RPC absent from {label}")
    check(STABLE_CHAIN in network_doc and STABLE_CHAIN in deploy_script, "chain lock missing")
    check(PINNED_CLI in network_doc and PINNED_CLI in deploy_script, "CLI lock missing")
    checks += 5

    # Standalone Intelligent Contract: examples/docs/tests are fine; product frontend is not.
    forbidden_frontend_paths = [
        ROOT / "frontend", ROOT / "web", ROOT / "app", ROOT / "pages",
        ROOT / "src" / "app", ROOT / "package.json",
    ]
    check(not any(path.exists() for path in forbidden_frontend_paths), "frontend/product surface detected")
    checks += 1

    # No private keys or mnemonic phrases should be committed.
    secret_pattern = re.compile(
        r"(?i)(private[_-]?key|mnemonic)\s*[=:]\s*['\"]?(0x[a-f0-9]{64}|[a-z]+(?:\s+[a-z]+){11,23})"
    )
    for path in text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        check(secret_pattern.search(text) is None, f"possible secret committed in {path.relative_to(ROOT)}")
    checks += 1

    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    checks += 1

    print(f"Novation preflight PASS: {checks} checks")
    print(f"network: Studionet / chain {STABLE_CHAIN} / {STABLE_RPC}")
    print(f"CLI: {PINNED_CLI}")
    print("frontend: absent")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Fail as exc:
        print(f"Novation preflight FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
