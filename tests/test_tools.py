import asyncio

import httpx2
import pytest

from piherder_mcp.client import MAX_FILE_BYTES, PiherderClient, present_file
from piherder_mcp.server import build_server, scopes_from_health

READ = {
    "health",
    "summary",
    "list_servers",
    "get_server",
    "inventory",
    "services",
    "list_jobs",
    "get_job",
    "read_discovery",
    "list_discovery_devices",
}
FILES = {"list_files", "read_file", "write_file", "mkdir", "rename_file", "delete_file"}


class Recording:
    def __init__(self):
        self.calls = []

    def health(self):
        self.calls.append("health")
        return {"ok": True, "scopes": ["read"]}

    def summary(self):
        return {"hosts": 1}

    def list_servers(self, q="", limit=100, offset=0):
        self.calls.append(("list_servers", q, limit, offset))
        return {"servers": []}

    def get_server(self, server_id):
        return {"id": server_id}

    def inventory(self, server_id=None):
        self.calls.append(("inventory", server_id))
        return {"server_id": server_id}

    def services(self):
        return {"services": []}

    def list_jobs(self, **kwargs):
        self.calls.append(("list_jobs", kwargs))
        return {"jobs": []}

    def get_job(self, job_id, *, detail=False):
        self.calls.append(("get_job", job_id, detail))
        return {"id": job_id, "detail": detail}

    def set_features(self, server_id, fields):
        self.calls.append(("set_features", server_id, fields))
        return {"ok": True, "features": fields}

    def trigger_job(self, server_id, body):
        self.calls.append(("trigger_job", server_id, body))
        if body["job_type"] == "backup":
            return {"status": 409, "job": {"id": 9, "status": "running"}}
        return {"status": 202, "job_id": 3, "job_type": body["job_type"]}

    def start_move(self, server_id, dest_server_id, project):
        self.calls.append(("start_move", server_id, dest_server_id, project))
        return {"status": 202, "job_id": 8, "leftover": "stopped"}

    def list_discovery(self):
        self.calls.append(("list_discovery",))
        return {"integrations": []}

    def get_discovery(self, integration_id):
        self.calls.append(("get_discovery", integration_id))
        return {"integration": {"id": integration_id}}

    def get_discovery_run(self, integration_id, run_id):
        self.calls.append(("get_discovery_run", integration_id, run_id))
        return {"run": {"id": run_id, "hosts_up": 2}}

    def start_discovery(self, integration_id, intensity):
        self.calls.append(("start_discovery", integration_id, intensity))
        return {
            "status": 202,
            "intensity": intensity,
            "targets": ["192.168.86.0/24"],
        }

    def list_discovery_devices(self, integration_id, *, state=None, limit=50, offset=0):
        self.calls.append(("list_discovery_devices", integration_id, state, limit, offset))
        return {"devices": [], "total": 0, "limit": limit, "offset": offset}

    def patch_discovery_device(self, integration_id, device_id, body):
        self.calls.append(("patch_discovery_device", integration_id, device_id, body))
        return {"device": {"id": device_id, **body}}

    def link_discovery_device(self, integration_id, device_id, server_id):
        self.calls.append(("link_discovery_device", integration_id, device_id, server_id))
        return {"device": {"id": device_id, "state": "linked", "linked_server_id": server_id}}

    def unlink_discovery_device(self, integration_id, device_id):
        self.calls.append(("unlink_discovery_device", integration_id, device_id))
        return {"device": {"id": device_id, "state": "known"}}

    def purge_discovery_device(self, integration_id, device_id):
        self.calls.append(("purge_discovery_device", integration_id, device_id))
        return {"device_ids": [device_id], "purged": 1}

    def purge_stale_discovery_devices(self, integration_id):
        self.calls.append(("purge_stale_discovery_devices", integration_id))
        return {"device_ids": [3], "purged": 1}

    def scan_discovery_device(self, integration_id, device_id, intensity):
        self.calls.append(("scan_discovery_device", integration_id, device_id, intensity))
        return {"status": 202, "targets": ["192.168.86.11"], "intensity": intensity}

    def list_files(self, server_id, p=""):
        return {"entries": [], "p": p}

    def read_file(self, server_id, p):
        return {"text": "hi", "truncated": False}

    def write_file(self, server_id, directory, name, text):
        self.calls.append(("write_file", server_id, directory, name, text))
        return {"ok": True}

    def mkdir(self, server_id, p, name):
        return {"ok": True, "name": name}

    def rename_file(self, server_id, p, src, dest):
        return {"ok": True, "from": src, "to": dest}

    def delete_file(self, server_id, p):
        self.calls.append(("delete_file", server_id, p))
        return {"ok": True}


def _tools(scopes):
    from mcp import Client

    api = Recording()
    server = build_server(api, scopes)

    async def run():
        async with Client(server) as client:
            listed = await client.list_tools()
            return api, listed.tools

    return asyncio.run(run())


def test_read_token_has_no_write_tools():
    _api, listed = _tools({"read"})
    names = {tool.name for tool in listed}
    assert names == READ
    assert all("__" not in tool.name for tool in listed)
    by_name = {tool.name: tool for tool in listed}
    assert by_name["summary"].annotations.read_only_hint is True


def test_scopes_add_write_tools_and_mark_them_destructive():
    _api, listed = _tools({"read", "jobs", "edit", "files"})
    names = {tool.name for tool in listed}
    assert names == READ | {
        "trigger_job",
        "start_move",
        "start_discovery",
        "scan_discovery_device",
        "set_features",
        "rename_discovery_device",
        "set_discovery_device_state",
        "link_discovery_device",
        "unlink_discovery_device",
        "purge_discovery_device",
        "purge_stale_discovery_devices",
    } | FILES
    by_name = {tool.name: tool for tool in listed}
    assert by_name["trigger_job"].annotations.destructive_hint is True
    assert by_name["start_move"].annotations.destructive_hint is True
    assert by_name["start_discovery"].annotations.destructive_hint is True
    assert by_name["scan_discovery_device"].annotations.destructive_hint is True
    assert by_name["purge_discovery_device"].annotations.destructive_hint is True
    assert by_name["read_discovery"].annotations.read_only_hint is True
    assert by_name["list_discovery_devices"].annotations.read_only_hint is True
    assert by_name["delete_file"].annotations.destructive_hint is True
    assert by_name["read_file"].annotations.read_only_hint is True


def test_missing_read_scope_fails_closed():
    with pytest.raises(SystemExit):
        scopes_from_health({"scopes": ["jobs"]})


def test_trigger_job_returns_409_and_refuses_other_types():
    from mcp import Client

    api = Recording()
    server = build_server(api, {"read", "jobs"})

    async def run():
        async with Client(server) as client:
            accepted = await client.call_tool(
                "trigger_job", {"server_id": 4, "job_type": "os_update_check"}
            )
            conflict = await client.call_tool(
                "trigger_job", {"server_id": 4, "job_type": "backup"}
            )
            reboot = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "docker_stack_restart",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            refused = await client.call_tool(
                "trigger_job", {"server_id": 4, "job_type": "service_migrate"}
            )
            down = await client.call_tool(
                "trigger_job", {"server_id": 4, "job_type": "docker_stack_down"}
            )
            return accepted, conflict, reboot, refused, down

    accepted, conflict, reboot, refused, down = asyncio.run(run())
    assert accepted.structured_content["job_type"] == "os_update_check"
    assert conflict.structured_content["status"] == 409
    assert conflict.is_error is False
    assert reboot.structured_content["job_type"] == "docker_stack_restart"
    assert refused.is_error is True
    assert down.is_error is True
    posted = [call for call in api.calls if call[0] == "trigger_job"]
    assert ("service_migrate" in str(posted)) is False
    assert ("docker_stack_down" in str(posted)) is False
    assert posted[0][2] == {"job_type": "os_update_check"}
    assert posted[1][2] == {"job_type": "backup"}
    assert posted[2][2] == {
        "job_type": "docker_stack_restart",
        "source_filter": "/home/pi/docker/grafana",
    }


def test_trigger_job_schema_includes_service():
    _api, listed = _tools({"read", "jobs"})
    by_name = {tool.name: tool for tool in listed}
    schema = by_name["trigger_job"].input_schema
    service = schema["properties"]["service"]
    assert "string" in str(service)
    assert "container_start" in service["description"]
    assert "Required" in service["description"]
    enum = schema["properties"]["job_type"].get("enum")
    assert enum is not None
    for name in (
        "container_start",
        "container_stop",
        "container_restart",
        "container_redeploy",
    ):
        assert name in enum
    assert "server_id" in schema["required"]
    assert "job_type" in schema["required"]


def test_container_service_jobs_require_service_and_source_filter():
    from mcp import Client

    api = Recording()
    server = build_server(api, {"read", "jobs"})

    async def run():
        async with Client(server) as client:
            started = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_start",
                    "service": " grafana ",
                    "source_filter": " /home/pi/docker/grafana ",
                },
            )
            stopped = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_stop",
                    "service": "grafana",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            restarted = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_restart",
                    "service": "grafana",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            updated = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_redeploy",
                    "service": "grafana",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            missing_service = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_restart",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            missing_path = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_redeploy",
                    "service": "grafana",
                },
            )
            blank = await client.call_tool(
                "trigger_job",
                {
                    "server_id": 4,
                    "job_type": "container_stop",
                    "service": "  ",
                    "source_filter": "/home/pi/docker/grafana",
                },
            )
            return started, stopped, restarted, updated, missing_service, missing_path, blank

    started, stopped, restarted, updated, missing_service, missing_path, blank = asyncio.run(run())
    assert started.structured_content["job_type"] == "container_start"
    assert stopped.structured_content["job_type"] == "container_stop"
    assert restarted.structured_content["job_type"] == "container_restart"
    assert updated.structured_content["job_type"] == "container_redeploy"
    assert missing_service.is_error is True
    assert missing_path.is_error is True
    assert blank.is_error is True
    posted = [call for call in api.calls if call[0] == "trigger_job"]
    assert [call[2]["job_type"] for call in posted] == [
        "container_start",
        "container_stop",
        "container_restart",
        "container_redeploy",
    ]
    assert posted[0][2] == {
        "job_type": "container_start",
        "source_filter": "/home/pi/docker/grafana",
        "service": "grafana",
    }
    assert all(call[2]["service"] == "grafana" for call in posted)
    assert all("source_filter" in call[2] for call in posted)


def test_set_features_omits_untouched_flags():
    from mcp import Client

    api = Recording()
    server = build_server(api, {"read", "edit"})

    async def run():
        async with Client(server) as client:
            changed = await client.call_tool(
                "set_features", {"server_id": 2, "docker": False}
            )
            empty = await client.call_tool("set_features", {"server_id": 2})
            return changed, empty

    changed, empty = asyncio.run(run())
    assert changed.structured_content["features"] == {"docker": False}
    assert empty.structured_content["ok"] is False
    assert api.calls == [("set_features", 2, {"docker": False})]


def test_start_move_and_discovery_use_saved_routes():
    from mcp import Client

    api = Recording()
    server = build_server(api, {"read", "jobs"})

    async def run():
        async with Client(server) as client:
            listed = {tool.name for tool in (await client.list_tools()).tools}
            refused = await client.call_tool(
                "start_move",
                {
                    "server_id": 1,
                    "dest_server_id": 2,
                    "project": "web",
                    "confirm": False,
                },
            )
            moved = await client.call_tool(
                "start_move",
                {
                    "server_id": 1,
                    "dest_server_id": 2,
                    "project": "web",
                    "confirm": True,
                },
            )
            scan_refused = await client.call_tool(
                "start_discovery",
                {"integration_id": 4, "confirm": False, "intensity": "deep"},
            )
            scan = await client.call_tool(
                "start_discovery",
                {"integration_id": 4, "confirm": True},
            )
            bad = await client.call_tool(
                "start_discovery",
                {"integration_id": 4, "confirm": True, "intensity": "nope"},
            )
            read = await client.call_tool(
                "read_discovery",
                {"integration_id": 4, "run_id": 9},
            )
            return listed, refused, moved, scan_refused, scan, bad, read

    listed, refused, moved, scan_refused, scan, bad, read = asyncio.run(run())
    assert "start_move" in listed
    assert "start_discovery" in listed
    assert refused.is_error is True
    assert scan_refused.is_error is True
    assert bad.is_error is True
    assert moved.structured_content["leftover"] == "stopped"
    assert scan.structured_content["targets"] == ["192.168.86.0/24"]
    assert read.structured_content["run"]["hosts_up"] == 2
    assert ("start_move", 1, 2, "web") in api.calls
    assert ("start_discovery", 4, "discovery") in api.calls
    assert ("get_discovery_run", 4, 9) in api.calls
    assert all(call[0] != "trigger_job" or call[2].get("job_type") != "service_migrate" for call in api.calls)
    posted_moves = [call for call in api.calls if call[0] == "start_move"]
    assert len(posted_moves) == 1


def test_discovery_device_tools_confirm_and_bodies():
    from mcp import Client

    api = Recording()
    server = build_server(api, {"read", "edit", "jobs"})

    async def run():
        async with Client(server) as client:
            refused = await client.call_tool(
                "purge_discovery_device",
                {"integration_id": 3, "device_id": 8, "confirm": False},
            )
            purged = await client.call_tool(
                "purge_discovery_device",
                {"integration_id": 3, "device_id": 8, "confirm": True},
            )
            stale_refused = await client.call_tool(
                "purge_stale_discovery_devices",
                {"integration_id": 3, "confirm": False},
            )
            renamed = await client.call_tool(
                "rename_discovery_device",
                {"integration_id": 3, "device_id": 8, "display_name": "Front camera"},
            )
            scan_refused = await client.call_tool(
                "scan_discovery_device",
                {"integration_id": 3, "device_id": 8, "confirm": False},
            )
            scanned = await client.call_tool(
                "scan_discovery_device",
                {"integration_id": 3, "device_id": 8, "confirm": True},
            )
            return refused, purged, stale_refused, renamed, scan_refused, scanned

    refused, purged, stale_refused, renamed, scan_refused, scanned = asyncio.run(run())
    assert refused.is_error is True
    assert stale_refused.is_error is True
    assert scan_refused.is_error is True
    assert purged.structured_content["device_ids"] == [8]
    assert renamed.structured_content["device"]["display_name"] == "Front camera"
    assert scanned.structured_content["intensity"] == "deep"
    assert ("purge_discovery_device", 3, 8) in api.calls
    assert ("scan_discovery_device", 3, 8, "deep") in api.calls
    assert all(call[0] != "purge_stale_discovery_devices" for call in api.calls)

    seen = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        body = {}
        if request.content:
            body = httpx2.Response(200, content=request.content).json()
        seen.append((request.method, request.url.path, dict(request.url.params), body))
        if request.method == "DELETE":
            return httpx2.Response(200, json={"device_ids": [8], "purged": 1})
        if request.url.path.endswith("/purge-stale"):
            return httpx2.Response(200, json={"device_ids": [3], "purged": 1})
        if request.url.path.endswith("/scans"):
            return httpx2.Response(202, json={"targets": ["192.168.86.11"], "intensity": "deep"})
        if request.method == "PATCH":
            return httpx2.Response(200, json={"device": body})
        if request.method == "GET":
            return httpx2.Response(200, json={"devices": [], "total": 0})
        return httpx2.Response(200, json={"ok": True})

    http = PiherderClient(
        "https://herder.example",
        "ph_test",
        transport=httpx2.MockTransport(handler),
    )
    http.list_discovery_devices(3, state="stale", limit=10, offset=0)
    http.patch_discovery_device(3, 8, {"display_name": "Front camera"})
    http.purge_discovery_device(3, 8)
    http.scan_discovery_device(3, 8, "deep")
    assert seen[0][0] == "GET"
    assert seen[0][1].endswith("/discovery/3/devices")
    assert seen[0][2]["state"] == "stale"
    assert seen[1] == (
        "PATCH",
        "/api/v1/discovery/3/devices/8",
        {},
        {"display_name": "Front camera"},
    )
    assert seen[2][0] == "DELETE"
    assert seen[2][1].endswith("/devices/8")
    assert seen[2][2].get("confirm") == "true"
    http.purge_stale_discovery_devices(3)
    assert seen[4][0] == "POST"
    assert seen[4][1].endswith("/purge-stale")
    assert seen[4][2].get("confirm") == "true"
    assert seen[3][3] == {"confirm": True, "intensity": "deep"}
    assert "targets" not in seen[3][3]
    http.close()


def test_http_move_and_discovery_bodies():
    seen = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        body = {}
        if request.content:
            body = httpx2.Response(200, content=request.content).json()
        seen.append((request.method, request.url.path, body))
        if request.url.path.endswith("/moves"):
            return httpx2.Response(202, json={"job_id": 1, "leftover": "stopped"})
        if request.url.path.endswith("/scans"):
            return httpx2.Response(202, json={"job_id": 2, "targets": ["192.168.86.0/24"]})
        if request.url.path.endswith("/runs/9"):
            return httpx2.Response(200, json={"run": {"id": 9}})
        if request.url.path.endswith("/discovery"):
            return httpx2.Response(200, json={"integrations": []})
        return httpx2.Response(500, json={"detail": "unexpected"})

    client = PiherderClient(
        "https://herder.example",
        "ph_test",
        transport=httpx2.MockTransport(handler),
    )
    moved = client.start_move(5, 6, "web")
    assert moved["leftover"] == "stopped"
    scanned = client.start_discovery(3, "inventory")
    assert scanned["targets"] == ["192.168.86.0/24"]
    client.get_discovery_run(3, 9)
    client.list_discovery()
    move_body = seen[0][2]
    assert move_body == {"dest_server_id": 6, "project": "web", "confirm": True}
    assert "targets" not in seen[1][2]
    assert seen[1][2] == {"confirm": True, "intensity": "inventory"}
    assert seen[0][1].endswith("/servers/5/moves")
    assert seen[1][1].endswith("/discovery/3/scans")
    assert all("service_migrate" not in path for _method, path, _body in seen)
    client.close()


def test_present_file_caps_and_marks_binary():
    text = present_file(b"hello")
    assert text["encoding"] == "utf-8"
    assert text["truncated"] is False
    huge = present_file(b"a" * (MAX_FILE_BYTES + 5))
    assert huge["truncated"] is True
    assert huge["bytes"] == MAX_FILE_BYTES
    binary = present_file(b"\xff\xfe")
    assert binary["encoding"] == "base64"


def test_http_trigger_and_read_cap():
    seen = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append((request.method, request.url.path))
        if request.url.path.endswith("/jobs"):
            return httpx2.Response(409, json={"job": {"id": 9}, "already_active": True})
        if request.url.path.endswith("/files/download"):
            return httpx2.Response(200, content=b"abc" * (MAX_FILE_BYTES))
        if request.url.path.endswith("/files") and request.method == "POST":
            return httpx2.Response(200, json={"ok": True, "rel": "note.txt"})
        return httpx2.Response(500, json={"detail": "unexpected"})

    client = PiherderClient(
        "https://herder.example",
        "ph_test",
        transport=httpx2.MockTransport(handler),
    )
    body = client.trigger_job(3, {"job_type": "backup"})
    assert body["already_active"] is True
    downloaded = client.read_file(3, "big.txt")
    assert downloaded["truncated"] is True
    assert downloaded["bytes"] == MAX_FILE_BYTES
    with pytest.raises(ValueError):
        client.write_file(3, "", "big.txt", "a" * (MAX_FILE_BYTES + 1))
    assert all("/console" not in path and "migrate" not in path for _method, path in seen)
    client.close()
