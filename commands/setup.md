---
description: "Set up VideoDB in this project: the hosted MCP server, or the SDK and API key, then verify the connection"
---

First check what is already there:

- In Claude chat or Cowork (even with a code sandbox): never set up the SDK or ask for a key there. With connector tools present (names such as `upload_media`, `search_video`), setup is done. Say so in one line and offer three things to try: "What's in my VideoDB library?", "Find every time they mention pricing in this video and make one clip: [link]", "Summarize this video in five bullets: [link]". Stop here. Without them, tell the user to open Settings → Connectors, find VideoDB and click Connect. Stop here.
- In Claude Code or another coding agent, with connector tools present: chat tasks already work. Skip to the SDK below only if the user wants Python code, scripts, screen capture or AI generation.
- In Claude Code or another coding agent, with no connector tools: recommend the connector below; set up the SDK only if the user picks it or needs Python.

Connector, no key: if a VideoDB `authenticate` tool is present, call it and give the user the sign-in link it returns. Otherwise tell the user to run `/mcp`, pick videodb and authorize in the browser.

SDK, only when chosen or needed:

Python SDK, following the Setup section of the `videodb` skill (`${CLAUDE_PLUGIN_ROOT}/python/SKILL.md`): install it with `pip install "videodb[capture]>=0.5.0" python-dotenv` (without the capture extra if that fails on Linux). Ask the user to add `VIDEO_DB_API_KEY=<their key>` to the project's `.env` themselves (free at https://console.videodb.io, $20 of free credits, no credit card), and make sure `.env` is gitignored. Never ask for the key in chat and never read it back. If a key appears in the chat, tell the user to rotate it.
Then verify what was set up: if MCP tools are present, call `list_collections`; for the SDK, run a short inline Python that connects and prints the number of videos in the default collection.

Report what works and what is still missing in three lines or fewer.

Extra instructions from the user: $ARGUMENTS
