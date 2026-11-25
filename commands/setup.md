---
name: setup
description: "Set up VideoDB in this project: SDK, API key and the hosted MCP server, then verify the connection"
---

First check what is already there:

- VideoDB connector tools present (names such as `upload_media`, `search_video`) and no shell: setup is done. Say so in one line and offer three things to try, for example "Upload a YouTube link and give me a shareable clip", "Find where they talk about X", "Add subtitles, white on a black box". Stop here.
- Connector tools present and a shell: chat tasks already work; continue below only if the user wants Python code, scripts, screen capture or AI generation.
- No connector tools: if the user wants hosted video tools, first authorize the bundled server in Cursor’s Customize → MCP panel or Claude Code’s `/mcp` menu, then verify with `list_collections`. Continue with SDK setup only for Python workflows or when no MCP connection is available.

Then set up the SDK by following the Setup section of the `videodb` skill (`python/SKILL.md` relative to this plugin’s root):

1. Install the SDK: `pip install "videodb[capture]>=0.5.0" python-dotenv` (without the capture extra if that fails on Linux).
2. Ask the user for their VideoDB API key in one line (free at https://console.videodb.io, $20 of free credits, no credit card). When they give it, write `VIDEO_DB_API_KEY=<key>` to the project's `.env` yourself and make sure `.env` is gitignored. Never print or echo the key.
3. For the hosted MCP server, authorize VideoDB in Cursor’s Customize → MCP panel, or run `/mcp` in Claude Code and pick videodb. Complete browser sign-in.
4. Verify: run a short inline Python that connects and prints the number of videos in the default collection, and if MCP tools are present, call `list_collections`.

Report what works and what is still missing in three lines or fewer.

Also follow any extra instructions the user supplied with this command (expanded as `$ARGUMENTS` in Claude Code).
