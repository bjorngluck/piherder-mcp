# PiHerder MCP 0.3.0

**2 October 2026.** Tag **[v0.3.0](https://github.com/bjorngluck/piherder-mcp/releases/tag/v0.3.0)**. Package **[0.3.0](https://pypi.org/project/piherder-mcp/0.3.0/)** on PyPI. Prior package: [0.2.0](https://pypi.org/project/piherder-mcp/0.2.0/).

`trigger_job` accepts the same eighteen job types as hosted `POST /mcp` on PiHerder **[v1.8.1](https://github.com/bjorngluck/piherder/blob/v1.8.1/docs/RELEASE_v1.8.1.md)**. That adds `container_start`, `container_stop`, `container_restart`, and `container_redeploy` on top of the **0.2.0** list. Each of those four needs `service` (compose service name) and `source_filter` (compose project directory). This package is the air-gapped stdio client. A Cursor or Grok connector that already points at hosted `/mcp` does not install it.

Install after the tag: `uvx piherder-mcp`.

Operator page: [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/).

---

## What’s new

**0.2.0** exposed fourteen job types and refused the four one-service jobs. **0.3.0** sends those four as well. The tool count is unchanged: a token with `read`, `jobs`, `edit`, and `files` still has 16 tools. Refresh the client and open `trigger_job` to see the new `job_type` values.

## Tools

A missing scope hides that group. A token without `read` lists nothing.

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

## Job types

`trigger_job` takes `server_id` and `job_type`. `source_filter`, `service`, and `os_steps` are optional except where the table says they are required. HTTP 202 means accepted. HTTP 409 means that job is already active: poll `get_job` and do not start another. The host feature flag and any `feature:*` scope still apply.

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

Not accepted: `docker_stack_down`, `docker_stack_remove`, `template_drift_check`, Move (`service_migrate`), undo (`service_migrate_undo`), and dest-up recover (`service_migrate_dest_recover`). SSH, the console, nmap, and token admin are not tools.
