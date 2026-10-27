---
description: Find a moment in a video or ask it a question. Usage - /videodb:find <YouTube link, URL or m- id> <what to look for, or a question>
argument-hint: "<video> <query or question>"
---

Find what the user is looking for by following the `video-search` skill. Prefer the VideoDB connector tools when they are present; fall back to the Python SDK only in a shell with no connector.

Input: $ARGUMENTS

1. Get the `m-` id (`upload_media` for a link; `search_videos_by_title` for a name).
2. About what was said, one-off question: `generate_transcript`, then `get_transcript(timestamped=true)`, read it and find the moments yourself. No index needed.
3. About what is shown, counts, filters, or a video the user will keep asking about: `understand_video` with `spoken_words` and `vlm`, poll `get_understanding`, `create_index` per analyzer, then `search_video(include_clip=true)` or `ask_video(include_sources=true)`.

Reply with the moments as mm:ss ranges and the words that matched (or the answer and its sources), then make one clip of all the matches via `generate_clip` and share its `player_url`.
