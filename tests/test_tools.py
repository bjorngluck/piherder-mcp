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
    assert names == READ | {"trigger_job", "set_features"} | FILES
    by_name = {tool.name: tool for tool in listed}
    assert by_name["trigger_job"].annotations.destructive_hint is True
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
            refused = await client.call_tool(
                "trigger_job", {"server_id": 4, "job_type": "service_migrate"}
            )
            return accepted, conflict, refused

    accepted, conflict, refused = asyncio.run(run())
    assert accepted.structured_content["job_type"] == "os_update_check"
    assert conflict.structured_content["status"] == 409
    assert conflict.is_error is False
    assert refused.is_error is True
    posted = [call for call in api.calls if call[0] == "trigger_job"]
    assert ("service_migrate" in str(posted)) is False
    assert posted[0][2] == {"job_type": "os_update_check"}


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
