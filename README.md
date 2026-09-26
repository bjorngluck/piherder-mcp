# PiHerder MCP

stdio process that lets Cursor, Grok Build, Claude, and Codex call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image, and the herder does not open an MCP port. The public demo is not a target.

Operator page: [Agents (MCP)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md). Contract: [PLAN_v1.7.0.md](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/docs/PLAN_v1.7.0.md).

## Install

The package is not on PyPI yet. Launch it from git:

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

After a PyPI release the same program is `uvx piherder-mcp`.

Create the token in PiHerder under Settings → API management. `read` is required. `jobs`, `edit`, and `files` add the write tools. A token without `read` exits on stderr.

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

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

Tests mock HTTP. They do not call a live herder.
