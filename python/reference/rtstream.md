# Real-Time Streams Guide

VideoDB supports real-time stream generation for live playback of composed timelines, dynamic overlays, and on-the-fly compilations. Streams are generated server-side and return an HLS-compatible URL that can be played in any standard video player or embedded in web applications. VideoDB also provides an RTStream class for ingesting and working with live RTMP streams.

## Prerequisites

Videos **must be uploaded** to a collection before streams can be generated. For search-based streams, the video must also be **indexed** (spoken words and/or scenes). See [search.md](search.md) for indexing details.

## Core Concepts

### Stream Generation

Every video, search result, and timeline in VideoDB can produce a **stream URL**. This URL points to an HLS (HTTP Live Streaming) manifest that is compiled on demand.

```python
# From a video
stream_url = video.generate_stream()

# From a timeline
stream_url = timeline.generate_stream()

# From search results
stream_url = results.compile()
```

## Streaming a Single Video

### Basic Playback

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate stream URL
stream_url = video.generate_stream()
print(f"Stream: {stream_url}")

# Open in default browser
video.play()
```

### With Subtitles

```python
# Index and add subtitles first
video.index_spoken_words(force=True)
video.add_subtitle()

# Stream now includes subtitles
stream_url = video.generate_stream()
```

### Specific Segments

Stream only a portion of a video by passing a timeline of timestamp ranges:

```python
# Stream seconds 10-30 and 60-90
stream_url = video.generate_stream(timeline=[(10, 30), (60, 90)])
print(f"Segment stream: {stream_url}")
```

## Streaming Timeline Compositions

Build a multi-asset composition and stream it in real time:

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

video = coll.get_video(video_id)
music = coll.get_audio(music_id)

timeline = Timeline(conn)

# Main video content
timeline.add_inline(VideoAsset(asset_id=video.id))

# Background music overlay (starts at second 0)
timeline.add_overlay(0, AudioAsset(asset_id=music.id))

# Text overlay at the beginning
timeline.add_overlay(0, TextAsset(
    text="Live Demo",
    duration=3,
    style=TextStyle(fontsize=48, fontcolor="white", boxcolor="#000000"),
))

# Generate the composed stream
stream_url = timeline.generate_stream()
print(f"Composed stream: {stream_url}")
```

**Important:** `add_inline()` only accepts `VideoAsset`. Use `add_overlay()` for `AudioAsset`, `ImageAsset`, and `TextAsset`.

## Streaming Search Results

Compile search results into a single stream of all matching segments:

```python
from videodb import SearchType

video.index_spoken_words(force=True)
results = video.search("key announcement", search_type=SearchType.semantic)

# Compile all matching shots into one stream
stream_url = results.compile()
print(f"Search results stream: {stream_url}")

# Or play directly
results.play()
```

### Stream Individual Search Hits

```python
results = video.search("product demo", search_type=SearchType.semantic)

for i, shot in enumerate(results.get_shots()):
    stream_url = shot.generate_stream()
    print(f"Hit {i+1} [{shot.start:.1f}s-{shot.end:.1f}s]: {stream_url}")
```

## Audio Playback

Get a signed playback URL for audio content:

```python
audio = coll.get_audio(audio_id)
playback_url = audio.generate_url()
print(f"Audio URL: {playback_url}")
```

## Complete Workflow Examples

### Search-to-Stream Pipeline

Combine search, timeline composition, and streaming in one workflow:

```python
import videodb
from videodb import SearchType
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

# Search for key moments
queries = ["introduction", "main demo", "Q&A"]
timeline = Timeline(conn)

for query in queries:
    # Find matching segments
    results = video.search(query, search_type=SearchType.semantic)
    for shot in results.get_shots():
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )

    # Add section label as overlay on the first shot
    timeline.add_overlay(0, TextAsset(
        text=query.title(),
        duration=2,
        style=TextStyle(fontsize=36, fontcolor="white", boxcolor="#222222"),
    ))

stream_url = timeline.generate_stream()
print(f"Dynamic compilation: {stream_url}")
```

### Multi-Video Stream

Combine clips from different videos into a single stream:

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset

conn = videodb.connect()
coll = conn.get_collection()

video_clips = [
    {"id": "vid_001", "start": 0, "end": 15},
    {"id": "vid_002", "start": 10, "end": 30},
    {"id": "vid_003", "start": 5, "end": 25},
]

timeline = Timeline(conn)
for clip in video_clips:
    timeline.add_inline(
        VideoAsset(asset_id=clip["id"], start=clip["start"], end=clip["end"])
    )

stream_url = timeline.generate_stream()
print(f"Multi-video stream: {stream_url}")
```

### Conditional Stream Assembly

Build a stream dynamically based on search availability:

```python
import videodb
from videodb import SearchType
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

timeline = Timeline(conn)

# Try to find specific content; fall back to full video
topics = ["opening remarks", "technical deep dive", "closing"]

found_any = False
for topic in topics:
    results = video.search(topic, search_type=SearchType.semantic)
    shots = results.get_shots()
    if shots:
        found_any = True
        for shot in shots:
            timeline.add_inline(
                VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
            )
        # Add a label overlay for the section
        timeline.add_overlay(0, TextAsset(
            text=topic.title(),
            duration=2,
            style=TextStyle(fontsize=32, fontcolor="white", boxcolor="#1a1a2e"),
        ))

if found_any:
    stream_url = timeline.generate_stream()
    print(f"Curated stream: {stream_url}")
else:
    # Fall back to full video stream
    stream_url = video.generate_stream()
    print(f"Full video stream: {stream_url}")
```

### Live Event Recap

Process an event recording into a streamable recap with multiple sections:

```python
import videodb
from videodb import SearchType
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

# Upload event recording
event = coll.upload(url="https://example.com/event-recording.mp4")
event.index_spoken_words(force=True)

# Generate background music
music = coll.generate_music(
    prompt="upbeat corporate background music",
    duration=120,
)

# Generate title image
title_img = coll.generate_image(
    prompt="modern event recap title card, dark background, professional",
    aspect_ratio="16:9",
)

# Build the recap timeline
timeline = Timeline(conn)

# Main video segments from search
keynote = event.search("keynote announcement", search_type=SearchType.semantic)
if keynote.get_shots():
    for shot in keynote.get_shots()[:5]:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )

demo = event.search("product demo", search_type=SearchType.semantic)
if demo.get_shots():
    for shot in demo.get_shots()[:5]:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )

# Overlay title card image
timeline.add_overlay(0, ImageAsset(
    asset_id=title_img.id, width=100, height=100, x=80, y=20, duration=5
))

# Overlay section labels
timeline.add_overlay(5, TextAsset(
    text="Keynote Highlights",
    duration=3,
    style=TextStyle(fontsize=40, fontcolor="white", boxcolor="#0d1117"),
))

# Overlay background music
timeline.add_overlay(0, AudioAsset(
    asset_id=music.id, fade_in_duration=3
))

# Stream the final recap
stream_url = timeline.generate_stream()
print(f"Event recap: {stream_url}")
```

## RTStream: Live Stream Ingestion

The `RTStream` class lets you connect to a live RTMP stream, record it, search over it, and export recordings to video assets.

### Connecting to a Live Stream

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# Connect to an RTMP stream source
rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="My Live Stream",
)
```

### Starting and Stopping

```python
# Begin ingestion
rtstream.start()

# ... stream is being recorded ...

# Stop ingestion
rtstream.stop()
```

### Generating a Stream from a Recording

Use Unix timestamps (not seconds offsets) to generate a playback stream from the recorded content:

```python
import time

start_ts = time.time()
rtstream.start()

# Let it record for a while...
time.sleep(60)

end_ts = time.time()
rtstream.stop()

# Generate a stream URL for the recorded segment
stream_url = rtstream.generate_stream(start=start_ts, end=end_ts)
print(f"Recorded stream: {stream_url}")
```

### Exporting to a Video Asset

Export the recorded stream to a permanent video in the collection:

```python
export_result = rtstream.export(name="Meeting Recording 2024-01-15")

print(f"Video ID: {export_result.video_id}")
print(f"Stream URL: {export_result.stream_url}")
print(f"Player URL: {export_result.player_url}")
print(f"Duration: {export_result.duration}s")
```

The `RTStreamExportResult` contains `video_id`, `stream_url`, `player_url`, `name`, and `duration`.

### Indexing and Searching Live Streams

Index the recorded content and search over it:

```python
# Index content
rtstream.index_spoken_words(force=True)
rtstream.index_scenes()

# Search the recorded stream
results = rtstream.search("important announcement")
```

### Transcription

```python
# Start live transcription (requires a WebSocket connection ID)
rtstream.start_transcript(ws_connection_id="your-ws-id")

# Get transcript pages
transcript = rtstream.get_transcript(page=1, page_size=50)

# Stop transcription
rtstream.stop_transcript()
```

### Complete RTStream Workflow

```python
import time
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# 1. Connect and start recording
rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="Weekly Standup",
)
rtstream.start()

# 2. Record for the duration of the meeting
start_ts = time.time()
time.sleep(1800)  # 30 minutes
end_ts = time.time()
rtstream.stop()

# 3. Export to a permanent video
export_result = rtstream.export(name="Weekly Standup Recording")
print(f"Exported video: {export_result.video_id}")

# 4. Index the exported video for search
video = coll.get_video(export_result.video_id)
video.index_spoken_words(force=True)

# 5. Search for action items
results = video.search("action items and next steps")
stream_url = results.compile()
print(f"Action items clip: {stream_url}")
```

## Tips

- **HLS compatibility**: Stream URLs return HLS manifests (`.m3u8`). They work in Safari natively, and in other browsers via hls.js or similar libraries.
- **On-demand compilation**: Streams are compiled server-side when requested. The first play may have a brief compilation delay; subsequent plays of the same composition are cached.
- **Caching**: Calling `video.generate_stream()` a second time without arguments returns the cached stream URL rather than recompiling.
- **Segment streams**: `video.generate_stream(timeline=[(start, end)])` is the fastest way to stream a specific clip without building a full `Timeline` object.
- **Inline vs overlay**: `add_inline()` only accepts `VideoAsset` and places assets sequentially on the main track. `add_overlay()` accepts `AudioAsset`, `ImageAsset`, and `TextAsset` and layers them on top at a given start time.
- **TextStyle defaults**: `TextStyle` defaults to `font='Sans'`, `fontcolor='black'`. Use `boxcolor` (not `bgcolor`) for background color on text.
- **Combine with generation**: Use `coll.generate_music(prompt, duration)` and `coll.generate_image(prompt, aspect_ratio)` to create assets for timeline compositions.
- **Playback**: `.play()` opens the stream URL in the default system browser. For programmatic use, work with the URL string directly.
- **RTStream timestamps**: `rtstream.generate_stream(start, end)` takes Unix timestamps, not seconds offsets from the start of recording.
