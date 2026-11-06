---
description: Find a moment in a video or ask it a question. Usage - /videodb:find <YouTube link, URL or m- id> <what to look for, or a question>
argument-hint: "<video> <query or question>"
---

Find what the user is looking for by following the `video-search` skill. Prefer the VideoDB connector tools when they are present; with no connector on the user's own computer, offer `/mcp` first and the Python SDK second. Never use the SDK in a Claude chat or Cowork sandbox.

Input: $ARGUMENTS

1. Get the `m-` id (`upload_media` for a link; `search_videos_by_title` for a name).
2. Short video and a question about what was said: `generate_transcript`, then `get_transcript(timestamped=true, segmenter="sentence")`, read it and find the moments yourself.
3. A longer video, something shown, counts or filters: make it searchable as the skill describes, then two or three narrow `search_video` queries, or `ask_video(include_sources=true)`.

Reply with the moments as mm:ss ranges and the words that matched (or the answer and its sources), then make one clip of all the matches via `generate_clip` and lead with its `player_url`. End with two next jobs as short prompts.
