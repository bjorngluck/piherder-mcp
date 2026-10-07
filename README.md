<!-- mcp-name: io.github.bjorngluck/piherder-mcp -->

# PiHerder MCP

[![Release](https://img.shields.io/badge/adapter-v0.4.1-blue.svg)](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.4.1)
[![PyPI](https://img.shields.io/badge/pypi-v0.4.1-blue.svg)](https://pypi.org/project/piherder-mcp/0.4.1/)
[![PiHerder](https://img.shields.io/badge/PiHerder-v1.10.0-blue.svg)](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange.svg)](https://github.com/bjorngluck/piherder-mcp)
[![Install guide](https://img.shields.io/badge/wiki-install%20steps-red.svg)](https://piherder-docs.hacknow.info/operations/mcp/)
[![Sponsor](https://img.shields.io/badge/Sponsor-%231EAEDB?logo=githubsponsors&logoColor=fff&style=flat)](https://github.com/sponsors/bjorngluck)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?logo=buymeacoffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/bjorngluck)

stdio process that lets Cursor, Claude, Codex, Windsurf, Continue, Goose, and other MCP clients call a [PiHerder](https://github.com/bjorngluck/piherder) instance through the existing bearer API.

It runs on the computer that runs the agent. It is not part of the PiHerder image. PiHerder **[v1.10.0](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md)** also serves `POST /mcp` on the herder, including browser sign-in. This adapter does not use that sign-in. It is the air-gapped fallback for a machine that cannot reach that URL. The public demo is not a target.

**Adapter 0.4.1** calls the PiHerder bearer API. `trigger_job` accepts the same list as hosted `/mcp` on PiHerder **v1.10.0**, including `container_start`, `container_stop`, `container_restart`, and `container_redeploy`. `start_move`, `read_discovery`, and `start_discovery` match the hosted tools on the v1.11 train. `list_discovery_devices`, `rename_discovery_device`, `set_discovery_device_state`, `link_discovery_device`, `unlink_discovery_device`, `purge_discovery_device`, `purge_stale_discovery_devices`, and `scan_discovery_device` tidy LAN Discovery devices. MCP registry name: `io.github.bjorngluck/piherder-mcp` (see [`server.json`](server.json)). Herder notes: [PiHerder v1.10.0](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md). Adapter notes: [v0.4.1](docs/RELEASE_v0.4.1.md) · [CHANGELOG.md](CHANGELOG.md). PyPI package: **[0.4.1](https://pypi.org/project/piherder-mcp/0.4.1/)**.

## Install

Full steps and scope notes: **[Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/)**.

```bash
export PIHERDER_URL='https://piherder.example.com'
export PIHERDER_TOKEN='ph_…'
uvx piherder-mcp
```

Requires [uv](https://docs.astral.sh/uv/) (`uvx`). The package is on [PyPI](https://pypi.org/project/piherder-mcp/). `uvx piherder-mcp` installs the latest published release, **[0.4.1](https://pypi.org/project/piherder-mcp/0.4.1/)**.

Git fallback (pin a branch or commit):

```bash
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

### Auth and tokens

1. In PiHerder **1.9.0**: **Settings → API management → Create new token → MCP agent**. Details: [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/).
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

A token with `read`, `jobs`, `edit`, and `files` has these 27 tools. A missing scope hides that group. A token without `read` exits on stderr and lists nothing.

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
| `read_discovery` | `read` | Read saved LAN Discovery ranges and recent scans. |
| `list_discovery_devices` | `read` | Page devices. Optional `state`, `limit`, and `offset`. |
| `trigger_job` | `jobs` | Start one job type from the table below. |
| `start_move` | `jobs` | Start a stop-first Move. `confirm` must be true. The source stack is left stopped. There is no undo. |
| `start_discovery` | `jobs` | Start a scan of the saved LAN Discovery ranges. `confirm` must be true. |
| `scan_discovery_device` | `jobs` | Scan one device inside those ranges. `confirm` must be true. |
| `set_features` | `edit` | Toggle `backup`, `os_patch`, or `docker`. Omit a field to leave it unchanged. |
| `rename_discovery_device` | `edit` | Set the operator name. Kind and map role stay. |
| `set_discovery_device_state` | `edit` | Set `known`, `new`, or `ignored`. |
| `link_discovery_device` | `edit` | Link a device to a fleet server. |
| `unlink_discovery_device` | `edit` | Unlink a device. It becomes known. |
| `purge_discovery_device` | `edit` | Delete one device. `confirm` must be true. A linked device is refused. |
| `purge_stale_discovery_devices` | `edit` | Delete offline devices. `confirm` must be true. Linked devices stay. |
| `list_files` | `files` | List a fleet-jail directory. `p` is jail-relative. `""` is the jail root. |
| `read_file` | `files` | Download one fleet-jail file. Capped around 256 KiB. The result says when it was cut. |
| `write_file` | `files` | Upload text. `p` is the directory, `name` is the basename. Cap 256 KiB. |
| `mkdir` | `files` | Create a directory. `p` is the parent, `name` is the new directory. |
| `rename_file` | `files` | Rename inside the current directory. `p`, `src`, `dest`. |
| `delete_file` | `files` | Delete one file or an empty directory. Not recursive. |

Read tools set `readOnlyHint`. `set_features`, `trigger_job`, `start_move`, `start_discovery`, `scan_discovery_device`, `rename_discovery_device`, `set_discovery_device_state`, `link_discovery_device`, `unlink_discovery_device`, `purge_discovery_device`, `purge_stale_discovery_devices`, `write_file`, `mkdir`, `rename_file`, and `delete_file` set `destructiveHint`.

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

Not accepted on `trigger_job`: `docker_stack_down`, `docker_stack_remove`, `template_drift_check`, Move (`service_migrate`), undo (`service_migrate_undo`), and dest-up recover (`service_migrate_dest_recover`). SSH, the console, and token admin are not tools. A Move is `start_move`. A LAN Discovery scan is `read_discovery` and `start_discovery`. A device scan is `scan_discovery_device`. Adapter **0.3.1** did not send `start_move`, `read_discovery`, or `start_discovery`. Adapter **0.4.0** did not send the device tools. This package does.

### Move

`start_move` takes `server_id` (the source), `dest_server_id`, `project` (the compose project name, not a directory), and `confirm: true`. It calls `POST /api/v1/servers/{id}/moves`. The source stack is left stopped. There is no undo. **409** means a stack, Move, or backup is already running. Poll `get_job`. That route is on PiHerder **1.10.0**.

### LAN Discovery

`read_discovery` lists saved ranges and the latest scan. Pass `integration_id` for recent scans, or `integration_id` and `run_id` for one scan.

`start_discovery` takes `integration_id` and `confirm: true`. Optional `intensity` is `discovery`, `inventory`, `detailed`, or `deep`. The body is `confirm` and `intensity` only. The scan uses the ranges saved on that integration. The agent does not choose the ranges. Vulnerability scripts stay off.

`list_discovery_devices` pages devices. `state` is `new`, `known`, `linked`, `ignored`, or `stale`. `rename_discovery_device` sets the operator name and leaves kind and map role alone. `set_discovery_device_state` sets `known`, `new`, or `ignored`. A linked device cannot be marked new. `link_discovery_device` and `unlink_discovery_device` tie a device to a fleet server. `purge_discovery_device` and `purge_stale_discovery_devices` need `confirm: true`. A linked device cannot be purged. Offline purge removes only `stale` rows. There is no undo. `scan_discovery_device` scans one device whose address sits inside the saved ranges. Default intensity is `deep`. Vulnerability scripts stay off.

These tools call `/api/v1/discovery`. A herder without that route returns **404**. Device routes need the v1.11 herder that exposes them.

## Wiki

| Topic | Page |
|-------|------|
| PiHerder v1.10.0 | [Notes](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md). Package **1.10.0**. Prior tag: [v1.9.0](https://github.com/bjorngluck/piherder/releases/tag/v1.9.0) |
| PiHerder v1.9.0 | [Notes](https://github.com/bjorngluck/piherder/blob/v1.9.0/docs/RELEASE_v1.9.0.md). Tag [v1.9.0](https://github.com/bjorngluck/piherder/releases/tag/v1.9.0). Prior: [v1.8.1](https://github.com/bjorngluck/piherder/releases/tag/v1.8.1) |
| Adapter 0.4.1 | [Notes](docs/RELEASE_v0.4.1.md) · [changelog](CHANGELOG.md). Prior package: [0.4.0](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.4.0) |
| Install, clients, scopes | [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/) |
| Token scopes and allowlist | [API tokens](https://piherder-docs.hacknow.info/operations/api-tokens/) |
| Jobs the token can start | [Jobs](https://piherder-docs.hacknow.info/day-to-day/jobs-audit-notifications/) |
| Fleet-jail files | [Host Files](https://piherder-docs.hacknow.info/day-to-day/host-files/) |

Do not vendor this tree inside the PiHerder Docker image.

## Publishing (maintainers)

[piherder-mcp 0.1.1](https://pypi.org/project/piherder-mcp/0.1.1/) was the first PyPI release. **[0.4.1](https://pypi.org/project/piherder-mcp/0.4.1/)** is the current package. Prior package: [0.4.0](https://pypi.org/project/piherder-mcp/0.4.0/). Notes: [docs/RELEASE_v0.4.1.md](docs/RELEASE_v0.4.1.md). The adapter badge reads the latest GitHub Release. The PyPI badge reads the latest package. The PiHerder badge is hand-typed **v1.10.0** and links to the [v1.10.0 notes](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md).

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
