---
description: Find a moment in a video or ask it a question. Usage - /videodb:find <YouTube link, URL or m- id> <what to look for, or a question>
argument-hint: "<video> <query or question>"
---

Find what the user is looking for by following the `video-search` skill. Prefer the VideoDB connector tools when they are present; fall back to the Python SDK only in a shell with no connector.

Input: $ARGUMENTS

1. Get the `m-` id (`upload_media` for a link; `search_videos_by_title` for a name).
2. If `list_indexes` shows nothing ready: `understand_video` with `spoken_words` and `vlm`, poll `get_understanding`, then `create_index` for each analyzer.
3. A question ("what did they say about pricing?"): `ask_video(include_sources=true)`. Anything else: `search_video(include_clip=true)`.

Reply with the moments as mm:ss ranges and the matched text (or the answer and its sources), plus the `player_url` of each clip, and offer one clip of all the matches via `generate_clip`.
