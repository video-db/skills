---
description: Cut a clip or highlight reel from a video. Usage - /videodb:clip <YouTube link, URL or m- id> <mm:ss-mm:ss | "highlights of ...">
argument-hint: "<video> <range or prompt>"
---

Make the clip the user asked for by following the `video-clips` skill. Prefer the VideoDB connector tools when they are present; fall back to the Python SDK only in a shell with no connector.

Input: $ARGUMENTS

- A time range (mm:ss-mm:ss, or seconds): `generate_clip` on that range.
- A description ("highlights of the demo"): `generate_transcript` once and poll until done (plus `index_spoken_words` where the server has it), then `create_highlight_clip` with that prompt, then `compile_clips` with the shots it returns.
- The word vertical, square, Shorts, Reels or TikTok: `reframe_video` on the range first.

Poll the job until it finishes, then reply with the `player_url`, the ranges used, and an offer of an MP4 via `download_stream`.
