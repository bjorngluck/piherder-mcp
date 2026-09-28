# Client samples

Primary launch command from [PyPI](https://pypi.org/project/piherder-mcp/): `uvx piherder-mcp`.

All samples need `PIHERDER_URL` and `PIHERDER_TOKEN`. Most MCP clients do **not** expand `${PIHERDER_TOKEN}` inside JSON `env` blocks — set the token in the host environment, the client's secret UI, or paste it once carefully. Do not commit real tokens.

Git fallback (pin a branch or commit):

```text
uvx --from git+https://github.com/bjorngluck/piherder-mcp.git piherder-mcp
```

| Client | Sample | Typical config path |
|--------|--------|---------------------|
| Cursor | [`cursor/mcp.json`](cursor/mcp.json) | project `.cursor/mcp.json` or Cursor MCP settings |
| Claude Desktop | [`claude/mcp.json`](claude/mcp.json) | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; Windows: `%APPDATA%\Claude\claude_desktop_config.json` |
| Codex | [`codex/config.toml`](codex/config.toml) | Codex `config.toml` (`[mcp_servers.piherder]`) |
| Grok Build | [`grok/config.toml`](grok/config.toml) | Grok / Cursor MCP import |
| Windsurf | [`windsurf/mcp_config.json`](windsurf/mcp_config.json) | `~/.codeium/windsurf/mcp_config.json` |
| Continue | [`continue/piherder.yaml`](continue/piherder.yaml) | `.continue/mcpServers/piherder.yaml` or `mcpServers` in Continue config |
| Goose | [`goose/config.yaml`](goose/config.yaml) | `~/.config/goose/config.yaml` (merge under `extensions`) |
| Windows (`cmd`) | [`windows/mcp.json`](windows/mcp.json) | Same JSON shape as Cursor/Claude; wraps via `cmd /c` |

`uvx` must be on the PATH of the Windows account that launches the client. `cmd /c` does not fix a missing PATH — non-interactive sessions often miss the user PATH from a terminal install of uv.

Operator skill text (0.2.0 job list): [`../skills/piherder/SKILL.md`](../skills/piherder/SKILL.md), [`cursor/piherder.mdc`](cursor/piherder.mdc), [`../CLAUDE.md`](../CLAUDE.md), [`../AGENTS.md`](../AGENTS.md).
