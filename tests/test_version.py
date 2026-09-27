"""Keep the package version and registry name from drifting across files."""

import json
import re
from importlib.metadata import version as dist_version
from pathlib import Path

import piherder_mcp

ROOT = Path(__file__).resolve().parents[1]


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
    assert f"adapter-v{package_version}" in readme
    assert f"**Adapter {package_version}**" in readme

    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert f"## [{package_version}]" in changelog

    continue_yaml = (ROOT / "clients/continue/piherder.yaml").read_text()
    assert f"version: {package_version}" in continue_yaml
