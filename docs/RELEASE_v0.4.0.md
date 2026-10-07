# PiHerder MCP 0.4.0

**7 October 2026.** Package **0.4.0**.

`start_move`, `read_discovery`, and `start_discovery` match hosted `/mcp` on the PiHerder v1.11 train. `trigger_job` keeps the same eighteen job types as PiHerder **[v1.10.0](https://github.com/bjorngluck/piherder/blob/v1.10.0/docs/RELEASE_v1.10.0.md)**. This package is the air-gapped stdio client. A Cursor or Grok connector that already points at hosted `/mcp` does not install it.

Install: `uvx piherder-mcp`.

Operator page: [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/).

---

## What’s new

**0.3.1** had 16 tools and refused Move and LAN Discovery. **0.4.0** adds three tools. A token with `read`, `jobs`, `edit`, and `files` has 19 tools.

`start_move` calls `POST /api/v1/servers/{id}/moves` with `confirm: true`. That route is on PiHerder **1.10.0**. The source stack is left stopped. There is no undo.

`read_discovery` and `start_discovery` call `/api/v1/discovery`. A herder without that route returns **404**. The scan uses the ranges saved on the integration. The agent does not choose the ranges. Vulnerability scripts stay off.

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
| `read_discovery` | `read` | Read saved LAN Discovery ranges and recent scans. |
| `trigger_job` | `jobs` | Start one job type from the table below. |
| `start_move` | `jobs` | Start a stop-first Move. `confirm` must be true. |
| `start_discovery` | `jobs` | Start a scan of the saved ranges. `confirm` must be true. |
| `set_features` | `edit` | Toggle `backup`, `os_patch`, or `docker`. Omit a field to leave it unchanged. |
| `list_files` | `files` | List a fleet-jail directory. `p` is jail-relative. `""` is the jail root. |
| `read_file` | `files` | Download one fleet-jail file. Capped around 256 KiB. The result says when it was cut. |
| `write_file` | `files` | Upload text. `p` is the directory, `name` is the basename. Cap 256 KiB. |
| `mkdir` | `files` | Create a directory. `p` is the parent, `name` is the new directory. |
| `rename_file` | `files` | Rename inside the current directory. `p`, `src`, `dest`. |
| `delete_file` | `files` | Delete one file or an empty directory. Not recursive. |

## Job types

`trigger_job` takes `server_id` and `job_type`. `source_filter`, `service`, and `os_steps` are optional except where the table says they are required. HTTP 202 means accepted. HTTP 409 means that job is already active: poll `get_job` and do not start another.

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
| `container_start` | docker | `service` and `source_filter` are required. |
| `container_stop` | docker | Same required `service` and `source_filter` as `container_start`. |
| `container_restart` | docker | Same required `service` and `source_filter` as `container_start`. |
| `container_redeploy` | docker | Same required `service` and `source_filter` as `container_start`. |

Not accepted on `trigger_job`: `docker_stack_down`, `docker_stack_remove`, `template_drift_check`, `service_migrate`, `service_migrate_undo`, and `service_migrate_dest_recover`. SSH, the console, and token admin are not tools.
