<!-- mcp-name: io.github.bjorngluck/piherder-mcp -->

# PiHerder MCP

[![Release](https://img.shields.io/badge/adapter-v0.1.1-green.svg)](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.1.1)
[![PyPI](https://img.shields.io/pypi/v/piherder-mcp)](https://pypi.org/project/piherder-mcp/)
[![PiHerder](https://img.shields.io/badge/PiHerder-v1.7.0-blue.svg)](https://github.com/bjorngluck/piherder/releases/tag/v1.7.0)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange.svg)](https://github.com/bjorngluck/piherder-mcp)
[![Install guide](https://img.shields.io/badge/wiki-install%20steps-red.svg)](https://piherder-docs.hacknow.info/operations/mcp/)
[![Sponsor](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=flat)](https://github.com/sponsors/bjorngluck)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?logo=buymeacoffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/bjorngluck)

stdio process that lets Cursor, Claude, Codex, Windsurf, Continue, Goose, and other MCP clients call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image. PiHerder **[v1.7.0](https://github.com/bjorngluck/piherder/releases/tag/v1.7.0)** also serves `POST /mcp` on the herder. This adapter is the air-gapped fallback for a machine that cannot reach that URL. The public demo is not a target.

**Adapter 0.1.1** talks to the same bearer token API as PiHerder **1.7.0**. MCP registry name: `io.github.bjorngluck/piherder-mcp` (see [`server.json`](server.json)). Release notes: [PiHerder v1.7.0](https://github.com/bjorngluck/piherder/blob/v1.7.0/docs/RELEASE_v1.7.0.md).

## Install

Full steps and scope notes: **[Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/)**.

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx piherder-mcp
```

Requires [uv](https://docs.astral.sh/uv/) (`uvx`). The package is on [PyPI](https://pypi.org/project/piherder-mcp/) (`piherder-mcp` 0.1.1).

Git fallback (pin a branch or commit):

```bash
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

### Auth and tokens

1. In PiHerder **1.7.0**: **Settings → API management → Create new token → MCP agent**. Details: [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/).
2. `read` is required. `jobs`, `edit`, and `files` add the write tools. A token without `read` exits on stderr.
3. Set `PIHERDER_URL` and `PIHERDER_TOKEN` for the MCP process.

**`${PIHERDER_TOKEN}` often does not expand** inside client JSON `env` blocks. Many clients pass that string literally. Prefer one of:

- Export `PIHERDER_TOKEN` in the host environment and omit it from the client `env` object (if the client inherits the parent env), or
- Use the client's secret / env UI when it has one, or
- Paste the token once into the client config and keep that file out of git.

Samples in `clients/` use a `ph_…` placeholder — replace it, or remove the key and rely on the host env. Do not commit real tokens.

## Clients

Samples: [`clients/`](clients/) (Cursor, Claude Desktop, Codex, Grok, Windsurf, Continue, Goose, Windows `cmd /c`). Path notes: [`clients/README.md`](clients/README.md).

Claude Desktop config locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Minimal Cursor / Claude-shaped entry:

```json
{
  "mcpServers": {
    "piherder": {
      "command": "uvx",
      "args": ["piherder-mcp"],
      "env": {
        "PIHERDER_URL": "https://piherder.example.com",
        "PIHERDER_TOKEN": "ph_…"
      }
    }
  }
}
```

The same operating note is in `skills/piherder/SKILL.md` (Grok), `clients/cursor/piherder.mdc` (Cursor), `CLAUDE.md`, and `AGENTS.md`.

## Tools

| Tool | Scope |
|------|--------|
| `health`, `summary`, `list_servers`, `get_server`, `inventory`, `services`, `list_jobs`, `get_job` | `read` |
| `trigger_job` | `jobs` |
| `set_features` | `edit` |
| `list_files`, `read_file`, `write_file`, `mkdir`, `rename_file`, `delete_file` | `files` |

`trigger_job` accepts `backup`, `retention`, `os_patch`, `container_patch`, `os_update_check`, `container_update_check`, `host_reboot`, `docker_stack_check`, `docker_stack_deploy`, `docker_stack_stop`, `docker_stack_start`, `docker_stack_restart`, `template_deploy`, and `template_redeploy`. For a `docker_stack_*` job, `source_filter` is the compose project path. A **409** is the job already running. Poll `get_job`. File bodies are capped at 256 KiB.

SSH, the console, Move, undo, nmap, and token admin are not tools. `docker_stack_down`, `docker_stack_remove`, and `template_drift_check` are not in this list.

## Wiki

| Topic | Page |
|-------|------|
| PiHerder v1.7.0 | [Release](https://github.com/bjorngluck/piherder/releases/tag/v1.7.0) · [notes](https://github.com/bjorngluck/piherder/blob/v1.7.0/docs/RELEASE_v1.7.0.md) |
| Install, clients, scopes | [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/) |
| Token scopes and allowlist | [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/) |
| Jobs the token can start | [Jobs](https://piherder-docs.hacknow.info/day-to-day/jobs-audit-notifications/) |
| Fleet-jail files | [Host Files](https://piherder-docs.hacknow.info/day-to-day/host-files/) |

Do not vendor this tree inside the PiHerder Docker image.

## Publishing (maintainers)

[piherder-mcp 0.1.1](https://pypi.org/project/piherder-mcp/) is the first PyPI release. The PyPI badge links to that project page. The Release badge links to the [v0.1.1 GitHub Release](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.1.1).

Trusted Publisher is already set: GitHub Environment `pypi`, workflow `release.yml`, owner `bjorngluck`, repository `piherder-mcp`. Later versions reuse it. `github-release` and `publish-pypi` still run independently after the build, so a green GitHub Release is not proof the package is on PyPI.

1. Package version is `piherder_mcp.__version__`. `pyproject.toml` reads it. CI checks `server.json`, the Continue sample, the changelog heading, and the README adapter line.
2. Tag the release commit and push the tag: `git tag -a vX.Y.Z <sha> -m "piherder-mcp X.Y.Z" && git push origin vX.Y.Z`.
3. Confirm the Release has wheel and sdist assets **and** the `publish-pypi` job succeeded, then check [pypi.org/project/piherder-mcp](https://pypi.org/project/piherder-mcp/).
4. Optional: publish [`server.json`](server.json) to the MCP registry; keep the README `<!-- mcp-name: … -->` marker in sync with `server.json` `name` (the version test checks the marker).
5. Suggested GitHub topics: `mcp`, `model-context-protocol`, `piherder`, `python`, `stdio`, `uvx`.

See [CHANGELOG.md](CHANGELOG.md). Workflow comments in [`.github/workflows/release.yml`](.github/workflows/release.yml) repeat the Trusted Publisher fields.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

Tests mock HTTP. They do not call a live herder. CI runs Python 3.10–3.12.

## Support

Optional. Nothing here is required to install the adapter.

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=for-the-badge)](https://github.com/sponsors/bjorngluck)
&nbsp;
[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=%E2%98%95&slug=bjorngluck&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/bjorngluck)

[github.com/sponsors/bjorngluck](https://github.com/sponsors/bjorngluck) · [buymeacoffee.com/bjorngluck](https://www.buymeacoffee.com/bjorngluck) · [Support the project](https://piherder-docs.hacknow.info/support/)
