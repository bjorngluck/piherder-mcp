# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
