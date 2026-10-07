"""HTTP client for the PiHerder bearer API. No SSH."""

from __future__ import annotations

import base64
from typing import Any

import httpx2

MAX_FILE_BYTES = 256 * 1024

# One compose service. Both service and source_filter are required.
SERVICE_JOB_TYPES = (
    "container_start",
    "container_stop",
    "container_restart",
    "container_redeploy",
)

JOB_TYPES = (
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
    *SERVICE_JOB_TYPES,
)

DISCOVERY_INTENSITIES = (
    "discovery",
    "inventory",
    "detailed",
    "deep",
)


class PiherderError(Exception):
    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        text = body if isinstance(body, str) else repr(body)
        super().__init__(f"HTTP {status}: {text[:500]}")


def present_file(data: bytes, *, limit: int = MAX_FILE_BYTES) -> dict[str, Any]:
    """Turn a download into a capped MCP result."""
    truncated = len(data) > limit
    chunk = data[:limit]
    try:
        text = chunk.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "encoding": "base64",
            "truncated": truncated,
            "bytes": len(chunk),
            "content_base64": base64.b64encode(chunk).decode("ascii"),
        }
    return {
        "encoding": "utf-8",
        "truncated": truncated,
        "bytes": len(chunk),
        "text": text,
    }


def _params(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None and value != ""}


class PiherderClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 60.0,
        transport: httpx2.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._http = httpx2.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def _json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        ok: tuple[int, ...] = (200,),
    ) -> Any:
        response = self._http.request(
            method,
            path,
            params=_params(params or {}),
            json=json,
            data=data,
            files=files,
        )
        if response.status_code not in ok:
            try:
                body: Any = response.json()
            except Exception:
                body = response.text
            raise PiherderError(response.status_code, body)
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return {"ok": True, "status": response.status_code}

    def health(self) -> dict[str, Any]:
        return self._json("GET", "/api/v1/health")

    def summary(self) -> dict[str, Any]:
        return self._json("GET", "/api/v1/summary")

    def list_servers(self, q: str = "", limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._json(
            "GET",
            "/api/v1/servers",
            params={"q": q, "limit": limit, "offset": offset},
        )

    def get_server(self, server_id: int) -> dict[str, Any]:
        return self._json("GET", f"/api/v1/servers/{server_id}")

    def inventory(self, server_id: int | None = None) -> dict[str, Any]:
        if server_id is None:
            return self._json("GET", "/api/v1/inventory")
        return self._json("GET", f"/api/v1/servers/{server_id}/inventory")

    def services(self) -> dict[str, Any]:
        return self._json("GET", "/api/v1/services")

    def list_jobs(
        self,
        *,
        server_id: int | None = None,
        status_filter: str | None = None,
        job_type: str | None = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._json(
            "GET",
            "/api/v1/jobs",
            params={
                "server_id": server_id,
                "status_filter": status_filter,
                "job_type": job_type,
                "active_only": active_only,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_job(self, job_id: int, *, detail: bool = False) -> dict[str, Any]:
        params = {"detail": "true"} if detail else {}
        return self._json("GET", f"/api/v1/jobs/{job_id}", params=params)

    def set_features(self, server_id: int, fields: dict[str, bool]) -> dict[str, Any]:
        return self._json("PATCH", f"/api/v1/servers/{server_id}/features", json=fields)

    def trigger_job(self, server_id: int, body: dict[str, Any]) -> dict[str, Any]:
        """Return the API body on 202 and on 409 (already active)."""
        return self._json(
            "POST",
            f"/api/v1/servers/{server_id}/jobs",
            json=body,
            ok=(202, 409),
        )

    def start_move(self, server_id: int, dest_server_id: int, project: str) -> dict[str, Any]:
        """Stop-first Move. confirm is always true. 409 means a job is already active."""
        return self._json(
            "POST",
            f"/api/v1/servers/{server_id}/moves",
            json={
                "dest_server_id": dest_server_id,
                "project": project,
                "confirm": True,
            },
            ok=(202, 409),
        )

    def list_discovery(self) -> dict[str, Any]:
        return self._json("GET", "/api/v1/discovery")

    def get_discovery(self, integration_id: int) -> dict[str, Any]:
        return self._json("GET", f"/api/v1/discovery/{integration_id}")

    def get_discovery_run(self, integration_id: int, run_id: int) -> dict[str, Any]:
        return self._json("GET", f"/api/v1/discovery/{integration_id}/runs/{run_id}")

    def start_discovery(self, integration_id: int, intensity: str) -> dict[str, Any]:
        """Scan the ranges saved on the integration. The body has no targets."""
        return self._json(
            "POST",
            f"/api/v1/discovery/{integration_id}/scans",
            json={"confirm": True, "intensity": intensity},
            ok=(202,),
        )

    def list_files(self, server_id: int, p: str = "") -> dict[str, Any]:
        return self._json("GET", f"/api/v1/servers/{server_id}/files", params={"p": p})

    def read_file(self, server_id: int, p: str) -> dict[str, Any]:
        with self._http.stream(
            "GET",
            f"/api/v1/servers/{server_id}/files/download",
            params={"p": p},
        ) as response:
            if response.status_code != 200:
                raw = response.read()
                try:
                    body: Any = httpx2.Response(response.status_code, content=raw).json()
                except Exception:
                    body = raw.decode("utf-8", errors="replace")
                raise PiherderError(response.status_code, body)
            chunks: list[bytes] = []
            total = 0
            truncated = False
            for chunk in response.iter_bytes():
                if total >= MAX_FILE_BYTES:
                    truncated = True
                    break
                room = MAX_FILE_BYTES - total
                if len(chunk) > room:
                    chunks.append(chunk[:room])
                    truncated = True
                    break
                chunks.append(chunk)
                total += len(chunk)
        presented = present_file(b"".join(chunks))
        presented["truncated"] = truncated
        return presented

    def write_file(self, server_id: int, directory: str, name: str, text: str) -> dict[str, Any]:
        raw = text.encode("utf-8")
        if len(raw) > MAX_FILE_BYTES:
            raise ValueError(f"file is {len(raw)} bytes; cap is {MAX_FILE_BYTES}")
        return self._json(
            "POST",
            f"/api/v1/servers/{server_id}/files",
            data={"p": directory},
            files={"file": (name, raw, "application/octet-stream")},
        )

    def mkdir(self, server_id: int, p: str, name: str) -> dict[str, Any]:
        return self._json(
            "POST",
            f"/api/v1/servers/{server_id}/files/mkdir",
            json={"p": p, "name": name},
        )

    def rename_file(self, server_id: int, p: str, src: str, dest: str) -> dict[str, Any]:
        return self._json(
            "POST",
            f"/api/v1/servers/{server_id}/files/rename",
            json={"p": p, "src": src, "dest": dest},
        )

    def delete_file(self, server_id: int, p: str) -> dict[str, Any]:
        return self._json("DELETE", f"/api/v1/servers/{server_id}/files", params={"p": p})
