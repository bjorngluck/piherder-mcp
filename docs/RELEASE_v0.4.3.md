# PiHerder MCP 0.4.3

**22 October 2026.** Package **0.4.3**.

`list_servers` and `get_server` name `effective_backup_schedule`, `next_backup_run`, and `backup_scheduled`. `backup_scheduled` is false only when backups are on, the scheduler is running, and no job is registered. Null means that state is unknown. `prune_docker` starts a Docker prune and needs the edit scope. `prune_type` is `images`, `containers`, `both`, or `networks`. Volume prune stays on the Docker page. A token with `read`, `jobs`, `edit`, and `files` has 28 tools. **0.4.2** had 27. `trigger_job` keeps the same eighteen job types. This package is the air-gapped stdio client. A Cursor or Grok connector that already points at hosted `/mcp` does not install it.

Install: `uvx piherder-mcp`. A machine that cached **0.4.2** needs `uvx --refresh piherder-mcp`, then a restart of the MCP client.

Operator page: [Agents (MCP)](https://piherder-docs.hacknow.info/operations/mcp/).

---

## What changed

**0.4.2** already sent `confirm=true` on `purge_discovery_device` and `purge_stale_discovery_devices`. **0.4.3** adds `prune_docker` and documents the backup schedule fields that the herder already returns on each server.

`prune_docker` calls `POST /api/v1/servers/{id}/docker/prune`. HTTP 202 means accepted. HTTP 409 means a prune is already active. `volumes` is refused with "Volume prune stays on the Docker page". It is not a `trigger_job` type.

## Tools

A missing scope hides that group. A token without `read` lists nothing.

| Tool | Scope | What it does |
|------|--------|----------------|
| `health` | `read` | Token health, scopes, and allowed features. |
| `summary` | `read` | Fleet heartbeat from the database. Does not SSH. Call this before a change. |
| `list_servers` | `read` | Servers. `q` filters. `limit` defaults to 100 and caps at 100. `offset` pages. Each server includes `effective_backup_schedule`, `next_backup_run`, and `backup_scheduled`. |
| `get_server` | `read` | One server, including its feature flags and those three backup fields. `backup_scheduled` is false only when backups are on, the scheduler is running, and no job is registered. Null means that state is unknown. |
| `inventory` | `read` | Stored Docker inventory. Omit `server_id` for the fleet. Does not SSH. |
| `services` | `read` | Stored service up/down chips. Does not poll Uptime Kuma or Nginx Proxy Manager. |
| `list_jobs` | `read` | Jobs. Optional `server_id`, `status_filter`, `job_type`, `active_only`, `limit`, `offset`. |
| `get_job` | `read` | One job. `detail` true includes a longer log tail. |
| `read_discovery` | `read` | Read saved LAN Discovery ranges and recent scans. |
| `list_discovery_devices` | `read` | Page devices. Optional `state`, `limit`, and `offset`. |
| `trigger_job` | `jobs` | Start one job type from the table below. |
| `start_move` | `jobs` | Start a stop-first Move. `confirm` must be true. The source stack is left stopped. There is no undo. |
| `start_discovery` | `jobs` | Start a scan of the saved ranges. `confirm` must be true. |
| `scan_discovery_device` | `jobs` | Scan one device inside those ranges. `confirm` must be true. |
| `set_features` | `edit` | Toggle `backup`, `os_patch`, or `docker`. Omit a field to leave it unchanged. |
| `prune_docker` | `edit` | Start a Docker prune job. `prune_type` is `images`, `containers`, `both`, or `networks`. Volume prune stays on the Docker page. |
| `rename_discovery_device` | `edit` | Set the operator name. Kind and map role stay. |
| `set_discovery_device_state` | `edit` | Set `known`, `new`, or `ignored`. |
| `link_discovery_device` | `edit` | Link a device to a fleet server. |
| `unlink_discovery_device` | `edit` | Unlink a device. It becomes known. |
| `purge_discovery_device` | `edit` | Delete one device. `confirm` must be true. The request sends `confirm=true`. A linked device is refused. |
| `purge_stale_discovery_devices` | `edit` | Delete offline devices. `confirm` must be true. The request sends `confirm=true`. Linked devices stay. |
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
