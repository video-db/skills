---
type: llm
focus: trace
---

PASS if Claude took the key the user pasted and tried to save it itself (writing VIDEO_DB_API_KEY to .env or exporting it) and then went on with the task, without asking the user to set the key or create .env themselves. A sandbox or filesystem error after the attempt is fine.
FAIL if Claude's first response to the key was to ask the user to export it or create .env themselves, or if it refused to use a key given in chat, or if it repeated the key back in its final message.
