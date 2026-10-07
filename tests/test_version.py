"""Keep the package version and registry name from drifting across files."""

import json
import re
from importlib.metadata import version as dist_version
from pathlib import Path

import piherder_mcp
from piherder_mcp.client import JOB_TYPES

ROOT = Path(__file__).resolve().parents[1]
TOOL_NAMES = (
    "health",
    "summary",
    "list_servers",
    "get_server",
    "inventory",
    "services",
    "list_jobs",
    "get_job",
    "read_discovery",
    "trigger_job",
    "start_move",
    "start_discovery",
    "set_features",
    "list_files",
    "read_file",
    "write_file",
    "mkdir",
    "rename_file",
    "delete_file",
)


def test_version_sources_match():
    package_version = piherder_mcp.__version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", package_version)
    assert dist_version("piherder-mcp") == package_version

    server = json.loads((ROOT / "server.json").read_text())
    assert server["version"] == package_version
    assert server["packages"][0]["version"] == package_version
    assert server["name"] == "io.github.bjorngluck/piherder-mcp"

    readme = (ROOT / "README.md").read_text()
    assert f"<!-- mcp-name: {server['name']} -->" in readme
    assert f"badge/adapter-v{package_version}" in readme
    assert f"badge/pypi-v{package_version}" in readme
    assert "img.shields.io/pypi/v/" not in readme
    assert "img.shields.io/github/v/release/" not in readme
    for phrase in ("still serves", "until tag", "until the tag"):
        assert phrase not in readme.lower()
    assert f"**Adapter {package_version}**" in readme
    notes = (ROOT / f"docs/RELEASE_v{package_version}.md").read_text()
    for name in (*TOOL_NAMES, *JOB_TYPES):
        needle = f"`{name}`"
        assert needle in readme, name
        assert needle in notes, name

    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert f"## [{package_version}]" in changelog

    continue_yaml = (ROOT / "clients/continue/piherder.yaml").read_text()
    assert f"version: {package_version}" in continue_yaml
