<!-- mcp-name: io.github.bjorngluck/piherder-mcp -->

# PiHerder MCP

[![Release](https://img.shields.io/badge/adapter-v0.1.1-green.svg)](https://github.com/bjorngluck/piherder-mcp/releases)
[![PyPI](https://img.shields.io/badge/PyPI-pending%20v0.1.1-lightgrey.svg)](#publishing-maintainers)
[![PiHerder](https://img.shields.io/badge/PiHerder-v1.7%20train-blue.svg)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/docs/PLAN_v1.7.0.md)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange.svg)](https://github.com/bjorngluck/piherder-mcp)
[![Install guide](https://img.shields.io/badge/wiki-install%20steps-red.svg)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=flat)](https://github.com/sponsors/bjorngluck)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?logo=buymeacoffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/bjorngluck)

stdio process that lets Cursor, Claude, Codex, Windsurf, Continue, Goose, and other MCP clients call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image, and the herder does not open an MCP port. The public demo is not a target.

**Adapter 0.1.1** talks to the token API that shipped with PiHerder **1.6.0**. The contract for this cut is the **v1.7** train. MCP registry name: `io.github.bjorngluck/piherder-mcp` (see [`server.json`](server.json)).

## Install

Full steps and scope notes: **[Agents (MCP)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md)**.

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx piherder-mcp
```

Requires [uv](https://docs.astral.sh/uv/) (`uvx`). After the first PyPI release, that is the whole install story.

Git fallback (pre-PyPI, or to pin a branch/commit):

```bash
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

### Auth and tokens

1. In PiHerder: **Settings → API management** (mint a token). Prefer an **MCP preset** when that lands on the token page. Details: [API tokens](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/api-tokens.md).
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

`trigger_job` accepts `backup`, `retention`, `os_patch`, `container_patch`, `os_update_check`, and `container_update_check`. A **409** is the job already running. Poll `get_job`. File bodies are capped at 256 KiB.

SSH, the console, Move, undo, compose stack actions, and token admin are not tools.

## Wiki

| Topic | Page |
|-------|------|
| Install, clients, scopes | [Agents (MCP)](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/mcp.md) |
| Token scopes and allowlist | [API tokens](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/operations/api-tokens.md) |
| Jobs the token can start | [Jobs](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/day-to-day/jobs-audit-notifications.md) |
| Fleet-jail files | [Host Files](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/day-to-day/host-files.md) |
| Train contract | [PLAN v1.7.0](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/docs/PLAN_v1.7.0.md) |

Do not vendor this tree inside the PiHerder Docker image.

## Publishing (maintainers)

First PyPI upload needs a one-time Trusted Publisher click — automation cannot finish that alone.

The Release badge links to the [releases index](https://github.com/bjorngluck/piherder-mcp/releases) so it does not 404 before the `v0.1.1` tag exists. The PyPI badge stays **pending** and links to this section until the project page exists. After the first upload, point that badge at `https://pypi.org/project/piherder-mcp/`.

`github-release` and `publish-pypi` run independently after the build. A green GitHub Release is not proof the package is on PyPI — if Trusted Publisher is not set up yet, the PyPI job fails and the Release assets can still appear.

1. Package version is `piherder_mcp.__version__`. `pyproject.toml` reads it. CI checks `server.json`, the Continue sample, the changelog heading, and the README adapter line.
2. Create a GitHub Environment named **`pypi`** (Settings → Environments). Optional: require a reviewer.
3. On [PyPI publishing](https://pypi.org/manage/account/publishing/), add a **pending** trusted publisher:
   - Project name: `piherder-mcp`
   - Owner: `bjorngluck`
   - Repository: `piherder-mcp`
   - Workflow filename: `release.yml`
   - Environment name: `pypi`
4. Tag and push: `git tag v0.1.1 && git push origin v0.1.1`.
5. Confirm the Release has wheel/sdist assets **and** the `publish-pypi` job succeeded. Then open `https://pypi.org/project/piherder-mcp/` and retarget the README PyPI badge.
6. Optional: publish [`server.json`](server.json) to the MCP registry; keep the README `<!-- mcp-name: … -->` marker in sync with `server.json` `name` (the version test checks the marker).
7. Suggested GitHub topics: `mcp`, `model-context-protocol`, `piherder`, `python`, `stdio`, `uvx`.

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

[github.com/sponsors/bjorngluck](https://github.com/sponsors/bjorngluck) · [buymeacoffee.com/bjorngluck](https://www.buymeacoffee.com/bjorngluck) · [Support the project](https://github.com/bjorngluck/piherder/blob/v1.7.0-dev/wiki/support.md)
