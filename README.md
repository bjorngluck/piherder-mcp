<!-- mcp-name: io.github.bjorngluck/piherder-mcp -->

# PiHerder MCP

[![Release](https://img.shields.io/github/v/release/bjorngluck/piherder-mcp?label=adapter)](https://github.com/bjorngluck/piherder-mcp/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/piherder-mcp)](https://pypi.org/project/piherder-mcp/)
[![PiHerder](https://img.shields.io/badge/PiHerder-v1.8.1-blue.svg)](https://github.com/bjorngluck/piherder/blob/v1.8.1/docs/RELEASE_v1.8.1.md)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange.svg)](https://github.com/bjorngluck/piherder-mcp)
[![Install guide](https://img.shields.io/badge/wiki-install%20steps-red.svg)](https://piherder-docs.hacknow.info/operations/mcp/)
[![Sponsor](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=flat)](https://github.com/sponsors/bjorngluck)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?logo=buymeacoffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/bjorngluck)

stdio process that lets Cursor, Claude, Codex, Windsurf, Continue, Goose, and other MCP clients call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image. PiHerder **[v1.8.1](https://github.com/bjorngluck/piherder/blob/v1.8.1/docs/RELEASE_v1.8.1.md)** also serves `POST /mcp` on the herder. This adapter is the air-gapped fallback for a machine that cannot reach that URL. The public demo is not a target.

**Adapter 0.3.0** calls the PiHerder bearer API. `trigger_job` accepts the same list as hosted `/mcp` on PiHerder **v1.8.1**, including `container_start`, `container_stop`, `container_restart`, and `container_redeploy`. MCP registry name: `io.github.bjorngluck/piherder-mcp` (see [`server.json`](server.json)). Herder notes: [PiHerder v1.8.1](https://github.com/bjorngluck/piherder/blob/v1.8.1/docs/RELEASE_v1.8.1.md). Adapter notes: [v0.3.0](docs/RELEASE_v0.3.0.md) · [CHANGELOG.md](CHANGELOG.md). PyPI still serves **[0.2.0](https://pypi.org/project/piherder-mcp/0.2.0/)** until tag `v0.3.0` is pushed.

## Install

Full steps and scope notes: **[Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/)**.

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx piherder-mcp
```

Requires [uv](https://docs.astral.sh/uv/) (`uvx`). The package is on [PyPI](https://pypi.org/project/piherder-mcp/). `uvx piherder-mcp` installs the latest published release, **[0.2.0](https://pypi.org/project/piherder-mcp/0.2.0/)**.

Git fallback (pin a branch or commit):

```bash
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

### Auth and tokens

1. In PiHerder **1.8.1**: **Settings → API management → Create new token → MCP agent**. Details: [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/).
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

A token with `read`, `jobs`, `edit`, and `files` has these 16 tools. A missing scope hides that group. A token without `read` exits on stderr and lists nothing.

| Tool | Scope | What it does |
|------|--------|----------------|
| `health` | `read` | Token health, scopes, and allowed features. |
| `summary` | `read` | Fleet heartbeat from the database. Does not SSH. Call this before a change. |
| `list_servers` | `read` | Servers. `q` filters. `limit` defaults to 100 and caps at 100. `offset` pages. |
| `get_server` | `read` | One server, including its feature flags. |
| `inventory` | `read` | Stored Docker inventory. Omit `server_id` for the fleet. Does not SSH. |
| `services` | `read` | Stored service up/down chips. Does not poll Uptime Kuma or Nginx Proxy Manager. |
| `list_jobs` | `read` | Jobs. Optional `server_id`, `status_filter`, `job_type`, `active_only`, `limit`, `offset`. |
| `get_job` | `read` | One job. `detail` true includes a longer log tail. |
| `trigger_job` | `jobs` | Start one job type from the table below. |
| `set_features` | `edit` | Toggle `backup`, `os_patch`, or `docker`. Omit a field to leave it unchanged. |
| `list_files` | `files` | List a fleet-jail directory. `p` is jail-relative. `""` is the jail root. |
| `read_file` | `files` | Download one fleet-jail file. Capped around 256 KiB. The result says when it was cut. |
| `write_file` | `files` | Upload text. `p` is the directory, `name` is the basename. Cap 256 KiB. |
| `mkdir` | `files` | Create a directory. `p` is the parent, `name` is the new directory. |
| `rename_file` | `files` | Rename inside the current directory. `p`, `src`, `dest`. |
| `delete_file` | `files` | Delete one file or an empty directory. Not recursive. |

Read tools set `readOnlyHint`. `set_features`, `trigger_job`, `write_file`, `mkdir`, `rename_file`, and `delete_file` set `destructiveHint`.

### `trigger_job` types

`server_id` and `job_type` are required. `source_filter`, `service`, and `os_steps` are optional on the tool. For `container_start`, `container_stop`, `container_restart`, and `container_redeploy`, `service` (compose service name) and `source_filter` (compose project directory) are both required and are sent on `POST /api/v1/servers/{id}/jobs`. HTTP 202 means accepted. HTTP 409 means that job is already active: poll `get_job` and do not start another. The host feature flag and any `feature:*` scope still apply. The `jobs` scope is still required. Docker stays behind the server docker flag and `feature:docker` when the token is feature-restricted.

| `job_type` | Host feature | Arguments |
|------------|----------------|-----------|
| `backup` | backup | `source_filter` is the backup source name. |
| `retention` | backup | Prune backups. |
| `os_patch` | os_patch | `os_steps` is the optional step list. |
| `os_update_check` | os_patch | Check for OS package updates. |
| `host_reboot` | os_patch | Reboot the host. |
| `container_patch` | docker | Update containers. |
| `container_update_check` | docker | Check for container image updates. |
| `docker_stack_check` | docker | `source_filter` is the compose project path. |
| `docker_stack_deploy` | docker | `source_filter` is the compose project path. |
| `docker_stack_stop` | docker | `source_filter` is the compose project path. |
| `docker_stack_start` | docker | `source_filter` is the compose project path. |
| `docker_stack_restart` | docker | `source_filter` is the compose project path. |
| `template_deploy` | docker | On this list because the jobs POST accepts it. This call has no template slug or variable values, so a catalog deploy still starts from the template UI. |
| `template_redeploy` | docker | Same as `template_deploy`. |
| `container_start` | docker | `service` and `source_filter` are required. `service` is the compose service name. `source_filter` is the compose project directory. |
| `container_stop` | docker | Same required `service` and `source_filter` as `container_start`. |
| `container_restart` | docker | Same required `service` and `source_filter` as `container_start`. |
| `container_redeploy` | docker | Same required `service` and `source_filter` as `container_start`. One service, not the whole project. |

Not accepted: `docker_stack_down`, `docker_stack_remove`, `template_drift_check`, Move (`service_migrate`), undo (`service_migrate_undo`), and dest-up recover (`service_migrate_dest_recover`). SSH, the console, nmap, and token admin are not tools. Adapter **0.2.0** did not send the four one-service jobs. This package does.

## Wiki

| Topic | Page |
|-------|------|
| PiHerder v1.8.1 | [Notes](https://github.com/bjorngluck/piherder/blob/v1.8.1/docs/RELEASE_v1.8.1.md). Tag [v1.8.1](https://github.com/bjorngluck/piherder/releases/tag/v1.8.1). Prior: [v1.8.0](https://github.com/bjorngluck/piherder/releases/tag/v1.8.0) |
| Adapter 0.3.0 | [Notes](docs/RELEASE_v0.3.0.md) · [changelog](CHANGELOG.md). Prior package: [0.2.0](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.2.0) |
| Install, clients, scopes | [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/) |
| Token scopes and allowlist | [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/) |
| Jobs the token can start | [Jobs](https://piherder-docs.hacknow.info/day-to-day/jobs-audit-notifications/) |
| Fleet-jail files | [Host Files](https://piherder-docs.hacknow.info/day-to-day/host-files/) |

Do not vendor this tree inside the PiHerder Docker image.

## Publishing (maintainers)

[piherder-mcp 0.1.1](https://pypi.org/project/piherder-mcp/0.1.1/) was the first PyPI release. **[0.2.0](https://pypi.org/project/piherder-mcp/0.2.0/)** is still the package on PyPI. This commit is **0.3.0**. Notes: [docs/RELEASE_v0.3.0.md](docs/RELEASE_v0.3.0.md). The adapter badge reads the latest GitHub Release. The PyPI badge reads the latest package. The PiHerder badge is hand-typed **v1.8.1** and links to tag [v1.8.1](https://github.com/bjorngluck/piherder/releases/tag/v1.8.1).

Trusted Publisher is already set: GitHub Environment `pypi`, workflow `release.yml`, owner `bjorngluck`, repository `piherder-mcp`. Later versions reuse it. `github-release` and `publish-pypi` still run independently after the build, so a green GitHub Release is not proof the package is on PyPI.

1. Package version is `piherder_mcp.__version__`. `pyproject.toml` reads it. CI checks `server.json`, the Continue sample, the changelog heading, and the README adapter line.
2. Write `docs/RELEASE_vX.Y.Z.md` on that commit. The release workflow uses it as the GitHub Release body. Tag and push: `git tag -a vX.Y.Z <sha> -m "piherder-mcp X.Y.Z" && git push origin vX.Y.Z`.
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
