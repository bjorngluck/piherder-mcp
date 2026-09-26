# PiHerder MCP

[![Release](https://img.shields.io/badge/adapter-v0.1.0-green.svg)](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.1.0)
[![PiHerder](https://img.shields.io/badge/PiHerder-v1.7%20train-blue.svg)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/docs/PLAN_v1.7.0.md)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange.svg)](https://github.com/bjorngluck/piherder-mcp)
[![Install guide](https://img.shields.io/badge/wiki-install%20steps-red.svg)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=flat)](https://github.com/sponsors/bjorngluck)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?logo=buymeacoffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/bjorngluck)

stdio process that lets Cursor, Grok Build, Claude, and Codex call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image, and the herder does not open an MCP port. The public demo is not a target.

**Adapter 0.1.0** (GitHub Release [`v0.1.0`](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.1.0)). It talks to the token API that shipped with PiHerder **1.6.0**. The contract for this cut is the **v1.7** train.

## Install

Full steps, client samples, and what each scope can do: **[Agents (MCP)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md)**.

The public docs site ([piherder-docs.hacknow.info](https://piherder-docs.hacknow.info/)) is built from PiHerder `main`. That site’s Agents page is published when v1.7 merges. Until then, use the wiki file on `v1.7.0-dev` linked above.

The package is not on PyPI yet. Launch it from git:

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

After a PyPI release the same program is `uvx piherder-mcp`.

1. In PiHerder: Settings → **API management**. Token page: [API tokens](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/api-tokens.md).
2. `read` is required. `jobs`, `edit`, and `files` add the write tools. A token without `read` exits on stderr.
3. Put `PIHERDER_URL` and `PIHERDER_TOKEN` in the client config. Samples are in `clients/`. Do not commit the token.

## Tools

| Tool | Scope |
|------|--------|
| `health`, `summary`, `list_servers`, `get_server`, `inventory`, `services`, `list_jobs`, `get_job` | `read` |
| `trigger_job` | `jobs` |
| `set_features` | `edit` |
| `list_files`, `read_file`, `write_file`, `mkdir`, `rename_file`, `delete_file` | `files` |

`trigger_job` accepts `backup`, `retention`, `os_patch`, `container_patch`, `os_update_check`, and `container_update_check`. A **409** is the job already running. Poll `get_job`. File bodies are capped at 256 KiB.

SSH, the console, Move, undo, compose stack actions, and token admin are not tools.

## Clients

Samples live in `clients/`. They use `${PIHERDER_TOKEN}` so the secret stays out of git. Grok Build also loads a Cursor `.cursor/mcp.json` when Cursor MCP import is on. Codex needs `clients/codex/config.toml`.

The same operating note is in `skills/piherder/SKILL.md` (Grok), `clients/cursor/piherder.mdc` (Cursor), `CLAUDE.md`, and `AGENTS.md`.

## Wiki

| Topic | Page |
|-------|------|
| Install, clients, scopes | [Agents (MCP)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md) |
| Token scopes and allowlist | [API tokens](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/api-tokens.md) |
| Jobs the token can start | [Jobs](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/day-to-day/jobs-audit-notifications.md) |
| Fleet-jail files | [Host Files](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/day-to-day/host-files.md) |
| Train contract | [PLAN v1.7.0](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/docs/PLAN_v1.7.0.md) |

Do not vendor this tree inside the PiHerder Docker image.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

Tests mock HTTP. They do not call a live herder.

## Support

Optional. Nothing here is required to install the adapter.

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=for-the-badge)](https://github.com/sponsors/bjorngluck)
&nbsp;
[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=%E2%98%95&slug=bjorngluck&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bjorngluck)

[github.com/sponsors/bjorngluck](https://github.com/sponsors/bjorngluck) · [buymeacoffee.com/bjorngluck](https://www.buymeacoffee.com/bjorngluck) · [Support the project](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/support.md)
