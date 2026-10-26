---
name: video-clips
description: Cut clips and highlights from a video. Use when the user wants a clip of a time range, a highlight reel of the moments that match a prompt ("every time they demo the product"), a supercut across several videos, a vertical or square cut for Shorts, Reels or TikTok, a thumbnail, or an MP4 to download. Works on YouTube links, public video URLs and videos already in the user's VideoDB account.
---

# Clips, highlights and social cuts

## Which path

1. **VideoDB connector tools present** (names such as `generate_clip`, `create_highlight_clip`, `compile_clips`, `reframe_video`, `upload_media`): use them. This is the path in Claude chat on web, desktop and mobile, and in Cowork. Do not install anything and do not ask for an API key.
2. **No VideoDB tools, in Claude chat or Cowork**: tell the user, in one line, to connect VideoDB: Settings, then Connectors, then VideoDB, then Connect, and log in to their VideoDB account when asked (free, no card needed). Then retry.
3. **Claude Code with a shell and no VideoDB tools**: run `/mcp`, pick videodb and authorize. Or use the Python SDK path at the end of this file.

Every cut is a long job: the call returns `status: processing`. Wait about 30 seconds, then read the result with the tool the reply names (`retry_with`) or `get_job_result` with its `output_url`. Never re-run the write. The finished result carries a `stream_url` and a `player_url`; share the `player_url`, it opens in any browser.

## With the connector tools

**Get the video.** A YouTube link or public URL: `upload_media(url)`; note the `m-` id. Already in the account: `list_videos` or `search_videos_by_title(query)`. Local files cannot come through the connector; the user uploads at https://console.videodb.io and shares the `m-` id.

| The user wants | Call |
|---|---|
| One range, or several ranges joined, from one video | `generate_clip(video_id, timeline=[[10, 25], [60, 90]])` (seconds) |
| The moments that match a description | `index_spoken_words(video_id)` once, then `create_highlight_clip(video_id, prompt="every product demo")` |
| Control over which moments make the cut | `search_video(video_id, query)` (see the `video-search` skill for indexing), pick the shots, then `generate_clip` |
| A reel across several videos | `compile_clips(clips=[{"video_id": "m-a", "shots": [[5, 20]]}, {"video_id": "m-b", "shots": [[0, 12]]}])` |
| Vertical for Shorts, Reels, TikTok, or square | `reframe_video(video_id, start, end, target="vertical")` (`"square"`, `"landscape"`, or `{"width", "height"}`); `mode="smart"` follows the subject |
| A thumbnail | `generate_thumbnail(video_id, time_seconds=42)` |
| An MP4 file | `download_stream(stream_url, name="demo-reel")`, poll, share the download URL |

Notes that save a retry:

- `create_highlight_clip` matches spoken content by default and returns an empty `shots` list on a video with no spoken-word index. Index first.
- `reframe_video` is slow on long videos. Always pass `start` and `end` for the segment the user wants; it saves a new video in the collection, and subtitles or further cuts go on that new `m-` id.
- Subtitles on the clip: reframe first, then `index_spoken_words` on the new video, then `add_subtitles` (the `video-subtitles` skill).
- Timestamps the user gives as mm:ss are converted to seconds before any call.

**Deliver.** Share the `player_url`, the ranges used, and offer the MP4.

## With the Python SDK (Claude Code)

Set up first with `/videodb:setup` if `import videodb` fails. Full reference: `${CLAUDE_PLUGIN_ROOT}/python/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/python/reference/editor.md`.

```python
from dotenv import load_dotenv; load_dotenv(".env")
import videodb
from videodb import ReframeMode
conn = videodb.connect(); coll = conn.get_collection()
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")
stream_url = video.generate_stream(timeline=[(10, 30), (45, 60)])        # ranges joined, no re-encode
vertical = video.reframe(start=10, end=30, target="vertical", mode=ReframeMode.smart)
print(f"https://console.videodb.io/player?url={stream_url}")
```
