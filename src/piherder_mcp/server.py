"""stdio MCP server. Tools follow the token scopes from GET /api/v1/health."""

from __future__ import annotations

import logging
import os
import sys
from typing import Annotated, Any, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from piherder_mcp.client import (
    DISCOVERY_INTENSITIES,
    JOB_TYPES,
    SERVICE_JOB_TYPES,
    PiherderClient,
    PiherderError,
)

JobType = Literal[
    "backup",
    "retention",
    "os_patch",
    "container_patch",
    "os_update_check",
    "container_update_check",
    "host_reboot",
    "docker_stack_check",
    "docker_stack_deploy",
    "docker_stack_stop",
    "docker_stack_start",
    "docker_stack_restart",
    "template_deploy",
    "template_redeploy",
    "container_start",
    "container_stop",
    "container_restart",
    "container_redeploy",
]

_READ = ToolAnnotations(read_only_hint=True, open_world_hint=True)
_WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=True)


def scopes_from_health(health: dict[str, Any]) -> set[str]:
    scopes = {str(item) for item in (health.get("scopes") or [])}
    if "read" not in scopes:
        print("PiHerder token has no read scope", file=sys.stderr)
        raise SystemExit(1)
    return scopes


def build_server(client: PiherderClient, scopes: set[str]) -> MCPServer:
    mcp = MCPServer("piherder")

    def health() -> dict[str, Any]:
        """Token health, scopes, and allowed features."""
        return client.health()

    def summary() -> dict[str, Any]:
        """Fleet heartbeat from the database. Does not SSH."""
        return client.summary()

    def list_servers(q: str = "", limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """List servers. limit default 100, max 100."""
        return client.list_servers(q=q, limit=limit, offset=offset)

    def get_server(server_id: int) -> dict[str, Any]:
        """One server, including feature flags."""
        return client.get_server(server_id)

    def inventory(server_id: int | None = None) -> dict[str, Any]:
        """Stored Docker inventory. Omit server_id for the fleet. Does not SSH."""
        return client.inventory(server_id)

    def services() -> dict[str, Any]:
        """Stored service up/down chips. Does not poll Kuma or NPM."""
        return client.services()

    def list_jobs(
        server_id: int | None = None,
        status_filter: str | None = None,
        job_type: str | None = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List jobs. Pass server_id to limit the list to one host."""
        return client.list_jobs(
            server_id=server_id,
            status_filter=status_filter,
            job_type=job_type,
            active_only=active_only,
            limit=limit,
            offset=offset,
        )

    def get_job(job_id: int, detail: bool = False) -> dict[str, Any]:
        """One job. detail=true includes a longer log tail."""
        return client.get_job(job_id, detail=detail)

    mcp.tool(annotations=_READ)(health)
    mcp.tool(annotations=_READ)(summary)
    mcp.tool(annotations=_READ)(list_servers)
    mcp.tool(annotations=_READ)(get_server)
    mcp.tool(annotations=_READ)(inventory)
    mcp.tool(annotations=_READ)(services)
    def read_discovery(
        integration_id: int | None = None,
        run_id: int | None = None,
    ) -> dict[str, Any]:
        """Read LAN Discovery. Omit integration_id to list saved ranges and the latest scan.

        Pass integration_id for recent scans and a short device list. Pass run_id
        with integration_id for one scan. No credentials and no script output.
        """
        if run_id is not None and integration_id is None:
            raise ValueError("run_id requires integration_id")
        if run_id is not None:
            return client.get_discovery_run(integration_id, run_id)
        if integration_id is not None:
            return client.get_discovery(integration_id)
        return client.list_discovery()

    def list_discovery_devices(
        integration_id: int,
        state: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Page LAN Discovery devices. state is new, known, linked, ignored, or stale.

        limit defaults to 50 and caps at 200. offset pages. No MAC, notes, or script output.
        """
        chosen = (state or "").strip().lower() or None
        if chosen is not None and chosen not in ("new", "known", "linked", "ignored", "stale"):
            raise ValueError("state must be one of new, known, linked, ignored, stale")
        return client.list_discovery_devices(
            integration_id,
            state=chosen,
            limit=limit,
            offset=offset,
        )

    mcp.tool(annotations=_READ)(list_jobs)
    mcp.tool(annotations=_READ)(get_job)
    mcp.tool(annotations=_READ)(read_discovery)
    mcp.tool(annotations=_READ)(list_discovery_devices)

    if "edit" in scopes:

        def set_features(
            server_id: int,
            backup: bool | None = None,
            os_patch: bool | None = None,
            docker: bool | None = None,
        ) -> dict[str, Any]:
            """Toggle backup, os_patch, or docker. Omit a field to leave it unchanged."""
            fields = {
                key: value
                for key, value in {
                    "backup": backup,
                    "os_patch": os_patch,
                    "docker": docker,
                }.items()
                if value is not None
            }
            if not fields:
                return {
                    "ok": False,
                    "detail": "No feature fields to change. Pass backup, os_patch, or docker.",
                }
            return client.set_features(server_id, fields)

        def rename_discovery_device(
            integration_id: int,
            device_id: int,
            display_name: str,
        ) -> dict[str, Any]:
            """Set the operator name. Kind and map role stay. An empty name clears it.

            A new or offline device becomes known.
            """
            return client.patch_discovery_device(
                integration_id,
                device_id,
                {"display_name": display_name},
            )

        def set_discovery_device_state(
            integration_id: int,
            device_id: int,
            state: str,
        ) -> dict[str, Any]:
            """Set known, new, or ignored. A linked device cannot be marked new."""
            chosen = (state or "").strip().lower()
            if chosen not in ("known", "new", "ignored"):
                raise ValueError("state must be one of known, new, ignored")
            return client.patch_discovery_device(
                integration_id,
                device_id,
                {"state": chosen},
            )

        def link_discovery_device(
            integration_id: int,
            device_id: int,
            server_id: int,
        ) -> dict[str, Any]:
            """Link a LAN Discovery device to a fleet server."""
            return client.link_discovery_device(integration_id, device_id, server_id)

        def unlink_discovery_device(integration_id: int, device_id: int) -> dict[str, Any]:
            """Unlink a LAN Discovery device. The device becomes known."""
            return client.unlink_discovery_device(integration_id, device_id)

        def purge_discovery_device(
            integration_id: int,
            device_id: int,
            confirm: bool,
        ) -> dict[str, Any]:
            """Permanently delete one device. confirm must be true. A linked device is refused.

            There is no undo.
            """
            if confirm is not True:
                raise ValueError("confirm must be true")
            return client.purge_discovery_device(integration_id, device_id)

        def purge_stale_discovery_devices(integration_id: int, confirm: bool) -> dict[str, Any]:
            """Permanently delete offline devices. confirm must be true. Linked devices stay.

            There is no undo. The result lists the removed ids.
            """
            if confirm is not True:
                raise ValueError("confirm must be true")
            return client.purge_stale_discovery_devices(integration_id)

        mcp.tool(annotations=_WRITE)(set_features)
        mcp.tool(annotations=_WRITE)(rename_discovery_device)
        mcp.tool(annotations=_WRITE)(set_discovery_device_state)
        mcp.tool(annotations=_WRITE)(link_discovery_device)
        mcp.tool(annotations=_WRITE)(unlink_discovery_device)
        mcp.tool(annotations=_WRITE)(purge_discovery_device)
        mcp.tool(annotations=_WRITE)(purge_stale_discovery_devices)

    if "jobs" in scopes:

        def trigger_job(
            server_id: int,
            job_type: JobType,
            source_filter: Annotated[
                str | None,
                Field(
                    description=(
                        "Backup source name, or the compose project directory for a "
                        "docker_stack job. Required with service for container_start, "
                        "container_stop, container_restart, and container_redeploy."
                    )
                ),
            ] = None,
            service: Annotated[
                str | None,
                Field(
                    description=(
                        "Compose service name. Required with source_filter for "
                        "container_start, container_stop, container_restart, and "
                        "container_redeploy. Sent on POST /api/v1/servers/{id}/jobs."
                    )
                ),
            ] = None,
            os_steps: list[str] | None = None,
        ) -> dict[str, Any]:
            """Start backup, retention, os_patch, container_patch, os_update_check, container_update_check, host_reboot, docker_stack_check, docker_stack_deploy, docker_stack_stop, docker_stack_start, docker_stack_restart, template_deploy, template_redeploy, container_start, container_stop, container_restart, or container_redeploy.

            For a docker_stack job, source_filter is the compose project path. For container_start, container_stop, container_restart, and container_redeploy, service (compose service name) and source_filter (compose project directory) are required. HTTP 202 means accepted. HTTP 409 means that job is already active: poll get_job and do not start another.
            """
            if job_type not in JOB_TYPES:
                raise ValueError(f"job_type must be one of {', '.join(JOB_TYPES)}")
            project = (source_filter or "").strip()
            service_name = (service or "").strip()
            if job_type in SERVICE_JOB_TYPES and (not service_name or not project):
                raise ValueError(
                    "container_start, container_stop, container_restart, and "
                    "container_redeploy require service and source_filter"
                )
            body: dict[str, Any] = {"job_type": job_type}
            if project:
                body["source_filter"] = project
            if service_name:
                body["service"] = service_name
            if os_steps:
                body["os_steps"] = os_steps
            return client.trigger_job(server_id, body)

        def start_move(
            server_id: int,
            dest_server_id: int,
            project: str,
            confirm: bool,
        ) -> dict[str, Any]:
            """Start a stop-first Move. confirm must be true.

            server_id is the source. project is the compose project name, not a
            directory. The source stack is left stopped. There is no undo.
            HTTP 202 means accepted. HTTP 409 means a stack, Move, or backup is
            already running: poll get_job.
            """
            if confirm is not True:
                raise ValueError("confirm must be true")
            name = (project or "").strip()
            if not name:
                raise ValueError("project is required")
            return client.start_move(server_id, dest_server_id, name)

        def start_discovery(
            integration_id: int,
            confirm: bool,
            intensity: str | None = None,
        ) -> dict[str, Any]:
            """Start a LAN Discovery scan of the ranges saved on that integration.

            confirm must be true. intensity is discovery, inventory, detailed, or
            deep. The agent does not choose targets. Vulnerability scripts stay off.
            """
            if confirm is not True:
                raise ValueError("confirm must be true")
            chosen = (intensity or "discovery").strip().lower() or "discovery"
            if chosen not in DISCOVERY_INTENSITIES:
                allowed = ", ".join(DISCOVERY_INTENSITIES)
                raise ValueError(f"intensity must be one of {allowed}")
            return client.start_discovery(integration_id, chosen)

        def scan_discovery_device(
            integration_id: int,
            device_id: int,
            confirm: bool,
            intensity: str | None = None,
        ) -> dict[str, Any]:
            """Scan one LAN Discovery device. confirm must be true.

            intensity is discovery, inventory, detailed, or deep. Default deep.
            The device address must sit inside the saved ranges. Vulnerability
            scripts stay off.
            """
            if confirm is not True:
                raise ValueError("confirm must be true")
            chosen = (intensity or "deep").strip().lower() or "deep"
            if chosen not in DISCOVERY_INTENSITIES:
                allowed = ", ".join(DISCOVERY_INTENSITIES)
                raise ValueError(f"intensity must be one of {allowed}")
            return client.scan_discovery_device(integration_id, device_id, chosen)

        mcp.tool(annotations=_WRITE)(trigger_job)
        mcp.tool(annotations=_WRITE)(start_move)
        mcp.tool(annotations=_WRITE)(start_discovery)
        mcp.tool(annotations=_WRITE)(scan_discovery_device)

    if "files" in scopes:

        def list_files(server_id: int, p: str = "") -> dict[str, Any]:
            """List a fleet-jail directory. p is jail-relative."""
            return client.list_files(server_id, p)

        def read_file(server_id: int, p: str) -> dict[str, Any]:
            """Download one fleet-jail file. Result is capped around 256 KiB and says when it was cut."""
            return client.read_file(server_id, p)

        def write_file(server_id: int, p: str, name: str, text: str) -> dict[str, Any]:
            """Upload text into the fleet jail. p is the directory. name is the file basename. Cap 256 KiB."""
            return client.write_file(server_id, p, name, text)

        def mkdir(server_id: int, p: str, name: str) -> dict[str, Any]:
            """Create a directory in the fleet jail. p is the parent. name is the new directory."""
            return client.mkdir(server_id, p, name)

        def rename_file(server_id: int, p: str, src: str, dest: str) -> dict[str, Any]:
            """Rename inside the current fleet-jail directory."""
            return client.rename_file(server_id, p, src, dest)

        def delete_file(server_id: int, p: str) -> dict[str, Any]:
            """Delete one file or an empty directory in the fleet jail. Not recursive."""
            return client.delete_file(server_id, p)

        mcp.tool(annotations=_READ)(list_files)
        mcp.tool(annotations=_READ)(read_file)
        mcp.tool(annotations=_WRITE)(write_file)
        mcp.tool(annotations=_WRITE)(mkdir)
        mcp.tool(annotations=_WRITE)(rename_file)
        mcp.tool(annotations=_WRITE)(delete_file)

    return mcp


def main() -> None:
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
    url = os.environ.get("PIHERDER_URL", "").strip()
    token = os.environ.get("PIHERDER_TOKEN", "").strip()
    if not url or not token:
        print("PIHERDER_URL and PIHERDER_TOKEN are required", file=sys.stderr)
        raise SystemExit(1)
    client = PiherderClient(url, token)
    try:
        health = client.health()
    except PiherderError as exc:
        print(f"PiHerder refused the token: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    mcp = build_server(client, scopes_from_health(health))
    mcp.run(transport="stdio")
