# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.2] - 2026-10-09

### Fixed

- `purge_discovery_device` and `purge_stale_discovery_devices` send `confirm=true` on the HTTP request. **0.4.1** checked `confirm` and then omitted it, so a v1.11 herder returned 400.

### Notes

- Tool list is unchanged. `trigger_job` is unchanged.
- Operator notes: [docs/RELEASE_v0.4.2.md](docs/RELEASE_v0.4.2.md).

## [0.4.1] - 2026-10-07

### Added

- `list_discovery_devices` pages LAN Discovery devices. `state` filters `new`, `known`, `linked`, `ignored`, or `stale`.
- `rename_discovery_device` sets the operator name. Kind and map role stay.
- `set_discovery_device_state` sets `known`, `new`, or `ignored`.
- `link_discovery_device` and `unlink_discovery_device` tie a device to a fleet server.
- `purge_discovery_device` and `purge_stale_discovery_devices` need `confirm: true`. A linked device cannot be purged. There is no undo.
- `scan_discovery_device` scans one device inside the saved ranges. Vulnerability scripts stay off.

### Notes

- `trigger_job` is unchanged.
- Operator notes: [docs/RELEASE_v0.4.1.md](docs/RELEASE_v0.4.1.md).

## [0.4.0] - 2026-10-07

### Added

- `start_move` starts a stop-first Move. `confirm` must be true. The source stack is left stopped. There is no undo.
- `read_discovery` reads saved LAN Discovery ranges and recent scans.
- `start_discovery` scans those saved ranges. `confirm` must be true. The agent does not choose the targets. Vulnerability scripts stay off.

### Notes

- `trigger_job` still refuses `service_migrate`, undo, and nmap job types.
- `start_move` calls `POST /api/v1/servers/{id}/moves`. That route is on PiHerder **1.10.0**.
- `read_discovery` and `start_discovery` call `/api/v1/discovery`. A herder without that route returns **404**.
- Operator notes: [docs/RELEASE_v0.4.0.md](docs/RELEASE_v0.4.0.md).

## [0.3.1] - 2026-10-02

### Fixed

- The PyPI project page no longer says the package is still **0.2.0**. Job behavior is unchanged from **0.3.0**.

## [0.3.0] - 2026-10-02

### Added

- `trigger_job` accepts `container_start`, `container_stop`, `container_restart`, and `container_redeploy`.
- Those four require `service` (compose service name) and `source_filter` (compose project directory). Both are sent on `POST /api/v1/servers/{id}/jobs`.

### Notes

- Hosted `POST /mcp` on PiHerder **v1.8.1** already accepts the same four types. This package is the air-gapped stdio client.
- Still refused: Move, undo, dest-up recover, nmap, `docker_stack_down`, `docker_stack_remove`, and `template_drift_check`.
- Operator notes: [docs/RELEASE_v0.3.0.md](docs/RELEASE_v0.3.0.md).

## [0.2.0] - 2026-09-28

### Changed

- `trigger_job` accepts the jobs POST types: `backup`, `retention`, `os_patch`, `container_patch`, `os_update_check`, `container_update_check`, `host_reboot`, `docker_stack_check`, `docker_stack_deploy`, `docker_stack_stop`, `docker_stack_start`, `docker_stack_restart`, `template_deploy`, and `template_redeploy`.
- For a `docker_stack_*` job, `source_filter` is the compose project path.
- Still refused: `container_start`, `container_stop`, `container_restart`, `container_redeploy`, Move, undo, nmap, `docker_stack_down`, `docker_stack_remove`, and `template_drift_check`.

### Notes

- The herder jobs POST already accepted these fourteen types in PiHerder **1.7.0**. Hosted `POST /mcp` on PiHerder **[v1.8.0](https://github.com/bjorngluck/piherder/blob/v1.8.0/docs/RELEASE_v1.8.0.md)** uses the same list. The v1.8 jobs POST also has four one-service types for Home Assistant plugin **0.4.3**. This package does not send them. This package is the air-gapped stdio client.
- Operator notes: [docs/RELEASE_v0.2.0.md](docs/RELEASE_v0.2.0.md). Package: https://pypi.org/project/piherder-mcp/0.2.0/

## [0.1.1] - 2026-09-27

### Added

- Richer `pyproject.toml` metadata (`[project.urls]`, classifiers, keywords).
- Release workflow builds sdist + wheel, attaches them to the GitHub Release, and publishes to PyPI via Trusted Publisher (OIDC).
- Official-style `server.json` for MCP registry readiness.
- Client samples for Windsurf, Continue, Goose, and Windows `cmd /c`.
- Maintainer checklist for one-time PyPI Trusted Publisher setup.
- Version alignment test so `__version__`, `server.json`, the changelog, and the Continue sample cannot drift quietly.

### Changed

- Primary install path is `uvx piherder-mcp` (git `uvx --from` remains as fallback).
- Auth docs: `${PIHERDER_TOKEN}` often does **not** expand inside client JSON `env`.
- CI test matrix covers Python 3.10–3.12.

### Notes

- MCP tool semantics are unchanged.
- `0.1.0` shipped as a GitHub Release only. `0.1.1` is the first PyPI release: https://pypi.org/project/piherder-mcp/

## [0.1.0] - 2026-09-26

### Added

- Initial stdio MCP adapter for the PiHerder bearer token API.
- Scope-gated tools: read, jobs, edit, files.
- Client samples for Cursor, Claude, Codex, and Grok Build.
