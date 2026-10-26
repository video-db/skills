---
description: Set up VideoDB in this project: SDK, API key and the hosted MCP server, then verify the connection
---

Set up VideoDB for this project by following the Setup section of the `videodb` skill (`${CLAUDE_PLUGIN_ROOT}/python/SKILL.md`):

1. Install the SDK: `pip install "videodb[capture]>=0.5.0" python-dotenv` (without the capture extra if that fails on Linux).
2. Ask the user to set `VIDEO_DB_API_KEY` (export it, or put it in the project's `.env`). Do not read, write or echo the key yourself. A free key is at https://console.videodb.io ($20 of free credits, no credit card).
3. For the hosted MCP server, tell the user to run `/mcp`, pick videodb and authorize in the browser.
4. Verify: run a short inline Python that connects and prints the number of videos in the default collection, and if MCP tools are present, call `list_collections`.

Report what works and what is still missing in three lines or fewer.

Extra instructions from the user: $ARGUMENTS
