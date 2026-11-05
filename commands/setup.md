---
description: "Set up VideoDB in this project: the hosted MCP server, or the SDK and API key, then verify the connection"
---

First check what is already there:

- VideoDB connector tools present (names such as `upload_media`, `search_video`) and no shell: setup is done. Say so in one line and offer three things to try: "What's in my VideoDB library?", "Find every time they mention pricing in this video and make one clip: [link]", "Summarize this video in five bullets: [link]". Stop here.
- Connector tools present and a shell: chat tasks already work; continue below only if the user wants Python code, scripts, screen capture or AI generation.
- No connector tools: continue below.

Then set up the SDK by following the Setup section of the `videodb` skill (`${CLAUDE_PLUGIN_ROOT}/python/SKILL.md`):

1. Install the SDK: `pip install "videodb[capture]>=0.5.0" python-dotenv` (without the capture extra if that fails on Linux).
2. Ask the user to add `VIDEO_DB_API_KEY=<their key>` to the project's `.env` themselves (free at https://console.videodb.io, $20 of free credits, no credit card), and make sure `.env` is gitignored. Never ask for the key in chat and never read it back. If a key appears in the chat, tell the user to rotate it.
3. For the hosted MCP server, which needs no key, tell the user to run `/mcp`, pick videodb and authorize in the browser.
4. Verify: run a short inline Python that connects and prints the number of videos in the default collection, and if MCP tools are present, call `list_collections`.

Report what works and what is still missing in three lines or fewer.

Extra instructions from the user: $ARGUMENTS
