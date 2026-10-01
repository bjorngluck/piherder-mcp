---
name: piherder
description: Operate a PiHerder fleet through the piherder MCP tools. Use when the user asks about hosts, jobs, backups, patches, Docker inventory, or fleet files.
---

Call summary before changing a host. trigger_job accepts backup, retention, os_patch, container_patch, os_update_check, container_update_check, host_reboot, docker_stack_check, docker_stack_deploy, docker_stack_stop, docker_stack_start, docker_stack_restart, template_deploy, template_redeploy, container_start, container_stop, container_restart, and container_redeploy. For a docker_stack job, source_filter is the compose project path. For container_start, container_stop, container_restart, and container_redeploy, service is the compose service name and source_filter is the compose project directory; both are required. When the result status is 409, poll get_job for that job and do not start another. Files stay inside the fleet jail: list, read, write, mkdir, rename, and delete of a file or an empty directory. Do not invent SSH, a console, Move, undo, nmap, or token admin. A token without jobs, edit, or files has no tool for that scope. Feature flags and feature:* scopes are enforced by PiHerder.
