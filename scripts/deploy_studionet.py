#!/usr/bin/env python3
"""Deploy Novation only to stable GenLayer Studionet with CLI 0.39.1.

The script never reads or stores a private key. It uses the account already
configured in the official GenLayer CLI and refuses to sign unless:
  1. source preflight passes,
  2. the selected CLI reports exactly the pinned release,
  3. the explicit RPC reports chain ID 61999.

Set GENLAYER_BIN to a local CLI executable when you do not want to replace a
global GenLayer installation.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "novation.py"
PREFLIGHT = ROOT / "scripts" / "preflight.py"
STUDIONET_RPC = "https://studio.genlayer.com/api"
EXPECTED_CHAIN_ID = 61999
EXPECTED_CLI_VERSION = "0.39.1"


def command_for(cli: str, *args: str) -> list[str]:
    # A local npm install on Windows exposes a .cmd shim. Execute it through
    # cmd.exe so the same script works with a local or global CLI.
    if os.name == "nt" and cli.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", cli, *args]
    return [cli, *args]


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=capture,
    )
    if completed.returncode != 0:
        if capture:
            if completed.stdout:
                print(completed.stdout, file=sys.stderr)
            if completed.stderr:
                print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)
    return completed


def rpc_chain_id() -> int:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_chainId",
        "params": [],
    }).encode("utf-8")
    request = urllib.request.Request(
        STUDIONET_RPC,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "novation-studionet-deployer/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))
    value = body.get("result")
    if not isinstance(value, str):
        raise RuntimeError(f"eth_chainId returned no hex result: {body!r}")
    return int(value, 16)


def find_cli() -> str | None:
    explicit = os.environ.get("GENLAYER_BIN", "").strip()
    if explicit:
        return explicit
    return shutil.which("genlayer")


def verify_cli_version(cli: str) -> None:
    completed = run(command_for(cli, "--version"), capture=True)
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    pattern = rf"(?<!\d){re.escape(EXPECTED_CLI_VERSION)}(?!\d)"
    if re.search(pattern, output) is None:
        print(
            f"ERROR: refusing deployment: expected GenLayer CLI {EXPECTED_CLI_VERSION}, got {output!r}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print(f"CLI LOCK OK: {EXPECTED_CLI_VERSION}")


def main() -> int:
    run([sys.executable, str(PREFLIGHT)])

    cli = find_cli()
    if cli is None:
        print(
            "ERROR: GenLayer CLI not found. Install/use the pinned release or set GENLAYER_BIN.",
            file=sys.stderr,
        )
        return 2
    verify_cli_version(cli)

    try:
        actual = rpc_chain_id()
    except Exception as exc:
        print(f"ERROR: unable to verify Studionet chain identity: {exc}", file=sys.stderr)
        return 2
    if actual != EXPECTED_CHAIN_ID:
        print(
            f"ERROR: refusing deployment: expected chain {EXPECTED_CHAIN_ID}, RPC returned {actual}",
            file=sys.stderr,
        )
        return 2
    print(f"CHAIN LOCK OK: {STUDIONET_RPC} -> {actual}")

    if not CONTRACT.is_file():
        print(f"ERROR: contract not found: {CONTRACT}", file=sys.stderr)
        return 2

    # Show the already-configured signer before any deployment transaction.
    run(command_for(cli, "account", "show"))
    # Explicit RPC avoids mutating or trusting a saved default network alias.
    run(command_for(cli, "deploy", "--contract", str(CONTRACT), "--rpc", STUDIONET_RPC))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
