# Network and tooling lock

Novation's final deployment target is intentionally fixed.

- network: **Studionet**
- chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- GenLayer CLI: **0.39.1**

`scripts/deploy_studionet.py` verifies the CLI version and queries `eth_chainId` from the explicit RPC before it asks the CLI to deploy. It refuses to continue when either check does not match this file.

The deploy helper uses an already-configured CLI signer and never reads a private key from this repository.

A local CLI installation may be kept outside the repository and selected with `GENLAYER_BIN`. This avoids changing another project's global CLI and keeps Novation free of npm/product/frontend files.
