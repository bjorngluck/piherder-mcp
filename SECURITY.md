# Security policy

## Supported versions

| Version | Support |
|---------|---------|
| **0.4.x** | Supported (`uvx piherder-mcp`) |
| **0.3.x and older** | Upgrade to **0.4.2** |

## Reporting a vulnerability

Do not open a public GitHub issue for a security vulnerability.

Email the maintainer listed on [github.com/bjorngluck](https://github.com/bjorngluck), or use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) on [bjorngluck/piherder-mcp](https://github.com/bjorngluck/piherder-mcp) if it is enabled.

Include what the issue is, how to reproduce it, the adapter version, and whether you plan a public write-up.

This program calls a PiHerder herder with `PIHERDER_TOKEN`. It does not run the hosted browser sign-in. Herder vulnerabilities belong on [bjorngluck/piherder](https://github.com/bjorngluck/piherder) ([SECURITY.md](https://github.com/bjorngluck/piherder/blob/main/SECURITY.md)).
