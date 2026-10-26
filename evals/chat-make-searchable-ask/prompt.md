---
description: Claude.ai chat, connector present. The user wants the video searchable for later and asks a question; expect understand_video then create_index, then ask_video or search_video, and plain words (searchable, not index) in the reply.
tags: [chat]
max_turns: 25
allowed_tools: [Skill]
append_system_prompt: "You are Claude in the claude.ai chat app on the web. There is no shell, no file system, no project directory and no Claude Code here. The only tools are the ones listed; if a VideoDB tool is not listed, it is not connected."
---

I'll be asking a lot of questions about this video later, so make it searchable: https://www.youtube.com/watch?v=MnrJzXM7a6o. First question: what price did he announce?
