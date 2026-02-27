---
name: videodb
description: |
  What you get
    A single API-first video stack for agents.
    Ingest anything, process server-side, and ship playable streams without FFmpeg glue.

  • Core capabilities

    Ingest + Transcode
    - Accept any format
    - Change codec, bitrate, FPS, resolution
    - Output a playable stream for your app (CDN + hosting)

    Scene-level Search Engine
    - Build a searchable index of your media, scene by scene
    - Find exact moments and auto-create clips
    - "Indexes as code": describe what you need, programmatically
    - Manage 1000s of hours of footage cleanly

    Generate + Compose
    - Generate assets: image, audio, video, text
    - Overlay text/images, branding, motion captions
    - Dub videos, translate captions, add animations

    Real-time RTSP
    - Connect live streams and create understanding in real time
    - Define events and set up alerts
    - Ideal for security cams and monitoring workflows

    Desktop Perception
    - Capture screen, mic, and system audio for real-time context
    - Stream your desktop live
    - Define alerts and triggers from what's happening on screen
    - Store episodic memory and semantic-search sessions
    - Record local sessions for QA and review

  • Try it now
    "Ingest this file and give me a playable web stream link"
    "Generate subtitles, burn them in, and add light background music"
    "Index this folder and find every scene with people"
    "Connect this RTSP URL and alert when a person enters the zone"
    "start recording and give me a actionable summary when it ends"
allowed-tools: Read Grep Glob Bash(python:*)
argument-hint: "[task description]"
---

# VideoDB Python Skill

Use this skill for VideoDB Python SDK workflows: upload, transcript, subtitle, search, timeline editing, generative media, and real-time capture.

**Do not use ffmpeg, moviepy, or local encoding tools** when VideoDB supports the operation. The following are all handled server-side by VideoDB — trimming, combining clips, overlaying audio or music, adding subtitles, text/image overlays, transcoding, resolution changes, aspect-ratio conversion, resizing for platform requirements, transcription, and media generation. Only fall back to local tools for operations listed under Limitations in reference/editor.md (transitions, speed changes, crop/zoom, colour grading, volume mixing).

### When to use what

| Problem | VideoDB solution |
|---------|-----------------|
| Platform rejects video aspect ratio or resolution | `video.reframe()` or `conn.transcode()` with `VideoConfig` |
| Need to resize video for Twitter/Instagram/TikTok | `video.reframe(target="vertical")` or `target="square"` |
| Need to change resolution (e.g. 1080p → 720p) | `conn.transcode()` with `VideoConfig(resolution=720)` |
| Need to overlay audio/music on video | `AudioAsset` on a `Timeline` |
| Need to add subtitles | `video.add_subtitle()` or `CaptionAsset` |
| Need to combine/trim clips | `VideoAsset` on a `Timeline` |
| Need to generate voiceover, music, or SFX | `coll.generate_voice()`, `generate_music()`, `generate_sound_effect()` |

## Running Python code

`scripts/videodb_env.py` handles environment loading and SDK validation. Call `load_vdb_env()` before any VideoDB code — it checks the SDK is installed, loads `VIDEO_DB_API_KEY` from environment variable → `./.env` → `~/.videodb/.env`, and exits with clear error messages if anything is missing. All scripts in `scripts/` already call this at the top.

Inline usage:

```bash
python -c "from scripts.videodb_env import load_vdb_env; load_vdb_env(); print('OK')"
```

Usage in a script file:

```python
from scripts.videodb_env import load_vdb_env
load_vdb_env()

import videodb
conn = videodb.connect()
```

`videodb.connect()` reads `VIDEO_DB_API_KEY` from the environment automatically.

Do NOT write a script file when a short inline command works. Use whichever Python command is available (`python` or `python3`).

When writing inline Python (`python -c "..."`), always use properly formatted code — use semicolons to separate statements and keep it readable. For anything longer than ~3 statements, use a heredoc instead:

```bash
python3 << 'EOF'
from scripts.videodb_env import load_vdb_env
load_vdb_env()

import videodb
conn = videodb.connect()
coll = conn.get_collection()
print(f"Videos: {len(coll.get_videos())}")
EOF
```

## Setup

When the user asks to "setup videodb" or similar:

### 1. Install SDK

Detect the Python executable — try `python` first, fall back to `python3`:

```bash
python --version 2>/dev/null || python3 --version
```

Then install:

```bash
python -m pip install "videodb[capture]" || python3 -m pip install "videodb[capture]"
```

### 2. Verify environment

Run `load_vdb_env()` to verify the SDK and API key:

```bash
python -c "from scripts.videodb_env import load_vdb_env; load_vdb_env(); print('OK')" || python3 -c "from scripts.videodb_env import load_vdb_env; load_vdb_env(); print('OK')"
```

If it prints `OK`, setup is done.

If it fails with `VIDEO_DB_API_KEY not found`, ask the user to:
1. Get a free API key at https://console.videodb.io (50 free uploads, no credit card)
2. Set it up using **either** of these methods:
   - Set it as an environment variable: `export VIDEO_DB_API_KEY=your-key`
   - Or save it to `~/.videodb/.env` as `VIDEO_DB_API_KEY=your-key`

Then re-run to confirm.

**Do NOT** read, write, or handle the API key yourself. Always let the user set it.

## Quick Reference

### Upload media

```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# Local file
video = coll.upload(file_path="/path/to/video.mp4")
```

### Transcript + subtitle

```python
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### Search inside videos

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)

# search() raises InvalidRequestError when no results are found.
# Always wrap in try/except and treat "No results found" as empty.
try:
    results = video.search("product demo")
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Scene search

```python
import re
from videodb import SearchType, IndexType, SceneExtractionType
from videodb.exceptions import InvalidRequestError

# index_scenes() has no force parameter — it raises an error if a scene
# index already exists. Extract the existing index ID from the error.
try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise

# Use score_threshold to filter low-relevance noise (recommended: 0.3+)
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Timeline editing

**Important:** Always validate timestamps before building a timeline:
- `start` must be >= 0 (negative values are silently accepted but produce broken output)
- `start` must be < `end`
- `end` must be <= `video.length`

```python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id, start=10, end=30))
timeline.add_overlay(0, TextAsset(text="The End", duration=3, style=TextStyle(fontsize=36)))
stream_url = timeline.generate_stream()
```

### Transcode video (resolution / quality change)

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### Reframe aspect ratio (for social platforms)

**Warning:** `reframe()` is a slow server-side operation. For long videos it can take
several minutes and may time out. Best practices:
- Always limit to a short segment using `start`/`end` when possible
- For full-length videos, use `callback_url` for async processing
- Trim the video on a `Timeline` first, then reframe the shorter result

```python
from videodb import ReframeMode

# Always prefer reframing a short segment:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Presets: "vertical" (9:16), "square" (1:1), "landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```

### Generative media

```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",
)
```

## Error handling

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```

### Common pitfalls

| Scenario | Error message | Solution |
|----------|--------------|----------|
| Indexing an already-indexed video | `Spoken word index for video already exists` | Use `video.index_spoken_words(force=True)` to skip if already indexed |
| Scene index already exists | `Scene index with id XXXX already exists` | Extract the existing `scene_index_id` from the error with `re.search(r"id\s+([a-f0-9]+)", str(e))` |
| Search finds no matches | `InvalidRequestError: No results found` | Catch the exception and treat as empty results (`shots = []`) |
| Reframe times out | Blocks indefinitely on long videos | Use `start`/`end` to limit segment, or pass `callback_url` for async |
| Negative timestamps on Timeline | Silently produces broken stream | Always validate `start >= 0` before creating `VideoAsset` |
| `generate_video()` / `create_collection()` fails | `Operation not allowed` or `maximum limit` | Plan-gated features — inform the user about plan limits |

## Additional docs

Reference documentation is in the `reference/` directory adjacent to this SKILL.md file. Use the Glob tool to locate it if needed.

- [reference/api-reference.md](reference/api-reference.md) - Complete VideoDB Python SDK API reference
- [reference/search.md](reference/search.md) - In-depth guide to video search (spoken word and scene-based)
- [reference/editor.md](reference/editor.md) - Timeline editing, assets, and composition
- [reference/generative.md](reference/generative.md) - AI-powered media generation (images, video, audio)
- [reference/rtstream.md](reference/rtstream.md) - Real-time streaming capabilities
- [reference/capture.md](reference/capture.md) - Screen and audio capture
- [reference/use-cases.md](reference/use-cases.md) - Common video processing patterns and examples

## Screen Recording (Desktop Capture)

Use `scripts/capture_bg.py` for screen and audio recording with AI transcription and visual indexing.

**IMPORTANT:** Use `/usr/bin/python3` (system Python) instead of conda/anaconda Python, as the capture module requires Python 3.9+.

### Start Recording

Run in background mode:

```bash
export VIDEO_DB_API_KEY=<key>
/usr/bin/python3 scripts/capture_bg.py start &
```

The recording will capture:
- Screen video
- Microphone audio
- System audio
- Real-time AI transcription
- Visual scene descriptions

### Check Status

```bash
cat /tmp/videodb_capture_state.json
```

### Stop Recording

Create the stop file to signal recording to finish:

```bash
touch /tmp/videodb_capture_stop
```

Or run:

```bash
/usr/bin/python3 scripts/capture_bg.py stop
```

### Get Shareable Link

After stopping, the state file contains the video URL:

```bash
cat /tmp/videodb_capture_state.json
```

Returns JSON with `player_url` for sharing.

## Utility scripts

Ready-to-run scripts are in the `scripts/` directory adjacent to this SKILL.md file. Read and execute them directly instead of rewriting the logic.

- [scripts/videodb_env.py](scripts/videodb_env.py) - Environment loading and SDK validation (called by all scripts)
- [scripts/capture_bg.py](scripts/capture_bg.py) - **Screen recording with AI** (recommended for capture)
- [scripts/capture.py](scripts/capture.py) - Interactive screen capture (requires terminal input)
- [scripts/batch_upload.py](scripts/batch_upload.py) - Bulk upload from a URL list or directory
- [scripts/search_and_compile.py](scripts/search_and_compile.py) - Search inside a video and compile matching clips into a stream
- [scripts/extract_clips.py](scripts/extract_clips.py) - Extract clips by timestamp ranges
- [scripts/backend.py](scripts/backend.py) - Capture backend server (WebSocket polling, no tunnel required)
- [scripts/client.py](scripts/client.py) - Capture client (connects to backend)
- [scripts/check_connection.py](scripts/check_connection.py) - Verify API key and connection
