---
description: Burn subtitles into a video, or get its transcript. Usage - /videodb:subtitles <YouTube link, URL or m- id> [style, e.g. "white on black box" or "translate to Spanish"]
argument-hint: "<video> [style or language]"
---

Subtitle or transcribe the video by following the `video-subtitles` skill. Prefer the VideoDB connector tools when they are present; fall back to the Python SDK only in a shell with no connector.

Input: $ARGUMENTS

- Default: `generate_transcript` and poll until done, then `add_subtitles` with the style the user described, and reply with the `player_url`.
- "transcript": `generate_transcript`, then `get_transcript(timestamped=true)`, and paste the transcript.
- "translate to <language>": `translate_transcript` and give the translated segments. Say that dubbing needs the SDK.

Offer an MP4 via `download_stream` at the end.
