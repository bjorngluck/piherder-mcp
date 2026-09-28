"""stdio MCP server. Tools follow the token scopes from GET /api/v1/health."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from piherder_mcp.client import JOB_TYPES, PiherderClient, PiherderError

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
    mcp.tool(annotations=_READ)(list_jobs)
    mcp.tool(annotations=_READ)(get_job)

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

        mcp.tool(annotations=_WRITE)(set_features)

    if "jobs" in scopes:

        def trigger_job(
            server_id: int,
            job_type: JobType,
            source_filter: str | None = None,
            os_steps: list[str] | None = None,
        ) -> dict[str, Any]:
            """Start backup, retention, os_patch, container_patch, os_update_check, container_update_check, host_reboot, docker_stack_check, docker_stack_deploy, docker_stack_stop, docker_stack_start, docker_stack_restart, template_deploy, or template_redeploy.

            For a docker_stack job, source_filter is the compose project path. HTTP 202 means accepted. HTTP 409 means that job is already active: poll get_job and do not start another.
            """
            if job_type not in JOB_TYPES:
                raise ValueError(f"job_type must be one of {', '.join(JOB_TYPES)}")
            body: dict[str, Any] = {"job_type": job_type}
            if source_filter:
                body["source_filter"] = source_filter
            if os_steps:
                body["os_steps"] = os_steps
            return client.trigger_job(server_id, body)

        mcp.tool(annotations=_WRITE)(trigger_job)

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
