---
name: get-started
description: Show what VideoDB can do in this chat, with one prompt to try for each job. Use when the user asks "what can VideoDB do", "how do I use VideoDB", "what can you do with my videos", "help with VideoDB", "what's in my VideoDB library", runs /videodb:start, or has just connected VideoDB and has not named a video. A message with a video link goes to video-watch instead.
---

# Get started with VideoDB

Make at most one call: `list_videos`. Never upload, transcribe or run a paid job during the tour. Never mention tool names.

Reply in this order and nothing else:

1. One line: "VideoDB is connected. You have N videos." If they asked what is in their library, list the five newest by name and length first.
2. A table of four jobs, each with a prompt to copy. Build the prompts from the newest video's title. If the library is empty, use "[paste a YouTube link]" in place of the title.

| Job | Try saying |
|---|---|
| Find every moment and clip it | "Find every time <title> mentions <topic> and make one clip" |
| Understand footage | "Break <title> down shot by shot: framing, on-screen text and what's said" |
| Edit footage | "Cut a 30-second version of <title> with captions and a title" |
| Summarize | "Summarize <title> in five bullets with timestamps" |

3. One line: "Try next: say '<the first prompt>'."

VideoDB tools missing: use the "not connected" lines from the `video-watch` skill's Which path, then show the table with "[paste a YouTube link]".
