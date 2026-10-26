---
name: video-search
description: Find a moment in a video or ask a question about it. Use when the user wants to search inside a video or a library of videos ("find where they talk about pricing", "which scenes show a phone"), get an answer with timestamps, count what appears, or turn the matches into a clip. Works on YouTube links, public video URLs and videos already in the user's VideoDB account.
---

# Find a moment, or ask a video

## Which path

1. **VideoDB connector tools present** (names such as `upload_media`, `search_video`, `ask_video`, `understand_video`): use them. This is the path in Claude chat on web, desktop and mobile, and in Cowork. Do not install anything and do not ask for an API key.
2. **No VideoDB tools, in Claude chat or Cowork**: tell the user, in one line, to connect VideoDB: Settings, then Connectors, then VideoDB, then Connect, and log in to their VideoDB account when asked (free, no card needed). Then retry. Nothing else to set up.
3. **Claude Code with a shell and no VideoDB tools**: run `/mcp`, pick videodb and authorize. Or use the Python SDK path at the end of this file when the user wants code.

Long jobs return `status: processing`. Wait about 30 seconds, then read the result with the tool the reply names (`retry_with`) or `get_job_result` with its `output_url`. Never re-run the write; that starts a second job.

## With the connector tools

**1. Get the video.** A YouTube link or public URL: `upload_media(url)`; note the `m-` id. Already in the account: `list_videos` or `search_videos_by_title(query)`. The user has no URL and the file is on their computer: the connector cannot take local files; point them to the console at https://console.videodb.io to upload, then continue with the `m-` id.

**2. Pick the fast path or the index path.**

*Fast path, the default for a one-off question about what was said.* Read the transcript yourself and find the moments:

```
generate_transcript(video_id)                       # once; returns quickly on short videos
get_transcript(video_id, timestamped=true)          # segments with start and end seconds
```

Scan the segments for the moments the user described, note their start and end, and go to step 4. No index needed. The transcript is the whole speech of the video in your context, so a long video (over roughly an hour, or a transcript the tool truncates) is a sign to use the index path instead.

*Index path.* Use it when the question is about what is shown rather than said, when the user wants counts or exact filters, when they will ask many questions about the same video or library, or when the transcript is too long to read. Check `list_indexes(video_id)` first; if nothing is ready:

```
understand_video(video_id, analyzers=[
  {"type": "spoken_words", "name": "transcript"},
  {"type": "vlm", "name": "scene", "config": {"prompt": "Describe the scene and any on-screen text."}}
])
```

Poll `get_understanding(video_id, understanding_id)` until every analyzer is `done`, then build one index per analyzer:

```
create_index(video_id, understanding_id, analyzer_name="transcript")
create_index(video_id, understanding_id, analyzer_name="scene")
```

Only speech matters (a podcast, a call): run just the `spoken_words` analyzer. Objects and counts ("how many cars"): add `{"type": "object_detection"}` or `{"type": "activity_recognition"}`.

**3. Retrieve (index path).**

| The user wants | Call |
|---|---|
| Moments with timestamps | `search_video(video_id, query, include_clip=true)` |
| A written answer with sources | `ask_video(video_id, question, include_sources=true)` |
| Across a whole library | `search_collection(query)` or `ask_collection(question)` |
| Counts and groups ("which objects appear most") | `aggregate_index(video_id, index_name="objects", group_by="frames.detections.label")` |
| Exact filters ("scenes with label = car") | `query_index(video_id, index_name, filter)` |
| A deeper investigation with follow-ups | `search_video(..., mode="deepsearch")`, then pass `session_id` on the next call |

**4. Deliver.** Give the moments as `start` to `end` in mm:ss with the words that matched (quote the transcript, or the `text` of each search hit), and the `player_url` of each clip when `include_clip` was set. Make one clip of the matches: `generate_clip(video_id, timeline=[[start, end], ...])` (seconds, a few seconds of padding on each side reads better), poll, then share the `player_url`.

Older videos that were indexed with `index_spoken_words` or `index_scenes` (v1) are searched with `legacy_search_video` and `legacy_search_collection`.

## With the Python SDK (Claude Code)

Set up first with `/videodb:setup` if `import videodb` fails. Full reference: `${CLAUDE_PLUGIN_ROOT}/python/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/python/reference/search.md`.

```python
from dotenv import load_dotenv; load_dotenv(".env")
import videodb, time
conn = videodb.connect(); coll = conn.get_collection()
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")
u = video.understand(analyzers=[{"type": "spoken_words", "name": "transcript"},
                                {"type": "vlm", "name": "scene", "config": {"prompt": "Describe the scene."}}])
while not all(a.is_complete for a in (u.refresh().list_analyzers() or [None])): time.sleep(15)
for a in u.list_analyzers():
    if a.is_successful: video.index(source=a, name=a.name).wait_until_complete()
r = video.search("the part about pricing")
for s in r.shots: print(f"[{s.start:.0f}s-{s.end:.0f}s] {s.text}")
print(r.compile())   # stream URL of the matches; player: https://console.videodb.io/player?url={STREAM_URL}
```
