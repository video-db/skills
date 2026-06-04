# Connection & Collection Reference

## Connection

```python
import videodb

conn = videodb.connect(
    api_key="your-api-key",      # or set VIDEO_DB_API_KEY env var
    base_url=None,                # custom API endpoint (optional)
)
```

**Returns:** `Connection` object

### Connection Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `conn.get_collection(collection_id="default")` | `Collection` | Get collection (default if no ID) |
| `conn.get_collections()` | `list[Collection]` | List all collections |
| `conn.create_collection(name, description, is_public=False)` | `Collection` | Create new collection |
| `conn.update_collection(id, name, description)` | `Collection` | Update a collection |
| `conn.check_usage()` | `dict` | Get account usage stats |
| `conn.upload(source, media_type, name, ...)` | `Video\|Audio\|Image` | Upload to default collection |
| `conn.record_meeting(meeting_url, bot_name, ...)` | `Meeting` | Record a meeting |
| `conn.youtube_search(query, result_threshold, duration)` | `list[dict]` | Search YouTube |
| `conn.transcode(source, callback_url, mode, ...)` | `str` | Transcode video (returns job ID) |
| `conn.get_transcode_details(job_id)` | `dict` | Get transcode job status and details |

### Transcode

Transcode a video from a URL with custom resolution, quality, and audio settings. Processing happens server-side — no local ffmpeg required.

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23),
    audio_config=AudioConfig(mute=False),
)
```

#### transcode Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | URL of the video to transcode (preferably a downloadable URL) |
| `callback_url` | `str` | required | URL to receive the callback when transcoding completes |
| `mode` | `TranscodeMode` | `TranscodeMode.economy` | Transcoding speed: `economy` or `lightning` |
| `video_config` | `VideoConfig` | `VideoConfig()` | Video encoding settings |
| `audio_config` | `AudioConfig` | `AudioConfig()` | Audio encoding settings |

Returns a job ID (`str`). Use `conn.get_transcode_details(job_id)` to check job status.

```python
details = conn.get_transcode_details(job_id)
```

#### VideoConfig

```python
from videodb import VideoConfig, ResizeMode

config = VideoConfig(
    resolution=720,              # Target resolution height (e.g. 480, 720, 1080)
    quality=23,                  # Encoding quality (lower = better, default 23)
    framerate=30,                # Target framerate
    aspect_ratio="16:9",         # Target aspect ratio
    resize_mode=ResizeMode.crop, # How to fit: crop, fit, or pad
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `resolution` | `int\|None` | `None` | Target resolution height in pixels |
| `quality` | `int` | `23` | Encoding quality (lower = higher quality) |
| `framerate` | `int\|None` | `None` | Target framerate |
| `aspect_ratio` | `str\|None` | `None` | Target aspect ratio (e.g. `"16:9"`, `"9:16"`) |
| `resize_mode` | `str` | `ResizeMode.crop` | Resize strategy: `crop`, `fit`, or `pad` |

#### AudioConfig

```python
from videodb import AudioConfig

config = AudioConfig(mute=False)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mute` | `bool` | `False` | Mute the audio track |

## Collections

```python
coll = conn.get_collection()
```

### Collection Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `coll.get_videos()` | `list[Video]` | List all videos |
| `coll.get_video(video_id)` | `Video` | Get specific video |
| `coll.get_audios()` | `list[Audio]` | List all audios |
| `coll.get_audio(audio_id)` | `Audio` | Get specific audio |
| `coll.get_images()` | `list[Image]` | List all images |
| `coll.get_image(image_id)` | `Image` | Get specific image |
| `coll.upload(source=None, media_type=None, name=None, description=None, callback_url=None, file_path=None, url=None)` | `Video\|Audio\|Image` | Upload media from URL, local file, or `source` (auto-detects) |
| `coll.search(query, search_type, index_type, result_threshold, score_threshold, dynamic_score_percentage, filter, namespace, scene_index_id)` | `SearchResult\|RTStreamSearchResult` | Search across collection. Only `search_type=SearchType.semantic` is supported — keyword and scene raise `NotImplementedError`. Pass `namespace="rtstream"` to search live streams instead of stored videos. |
| `coll.search_title(query)` | `list[dict]` | LLM-powered title search across videos in the collection. Returns `[{"video": Video}, ...]`. |
| `coll.generate_image(prompt, aspect_ratio="1:1", callback_url=None)` | `Image` | Generate image with AI. `aspect_ratio` ∈ `"1:1"`, `"9:16"`, `"16:9"`, `"4:3"`, `"3:4"`. |
| `coll.generate_video(prompt, duration=5, callback_url=None)` | `Video` | Generate video with AI. `duration` must be an integer between 5 and 8 inclusive. |
| `coll.generate_music(prompt, duration=5, callback_url=None)` | `Audio` | Generate music with AI |
| `coll.generate_sound_effect(prompt, duration=2, config={}, callback_url=None)` | `Audio` | Generate sound effect |
| `coll.generate_voice(text, voice_name="Default", config={}, callback_url=None)` | `Audio` | Generate speech from text |
| `coll.generate_text(prompt, model_name="basic", response_type="text")` | `dict\|str` | LLM text generation. `model_name` ∈ `"basic"`, `"pro"`, `"ultra"`; `response_type` ∈ `"text"`, `"json"`. |
| `coll.dub_video(video_id, language_code, callback_url=None)` | `Video` | Dub video into another language |
| `coll.record_meeting(meeting_url, bot_name=None, bot_image_url=None, meeting_title=None, callback_url=None, callback_data=None, time_zone="UTC")` | `Meeting` | Record a live meeting (Google Meet, Zoom, Teams) |
| `coll.get_meeting(meeting_id)` | `Meeting` | Fetch a meeting by ID (refreshes from server) |
| `coll.connect_rtstream(url, name, media_types=None, sample_rate=None, store=None, enable_transcript=None, ws_connection_id=None)` | `RTStream` | Connect to a live stream (see [rtstream-reference.md](rtstream-reference.md)) |
| `coll.get_rtstream(id)` | `RTStream` | Get RTStream by ID |
| `coll.list_rtstreams(limit=None, offset=None, status=None, name=None, ordering=None)` | `list[RTStream]` | List RTStreams in the collection with optional filters |
| `coll.make_public()` | `None` | Make collection public |
| `coll.make_private()` | `None` | Make collection private |
| `coll.delete_video(video_id)` | `None` | Delete a video |
| `coll.delete_audio(audio_id)` | `None` | Delete an audio |
| `coll.delete_image(image_id)` | `None` | Delete an image |
| `coll.delete()` | `None` | Delete the collection |

### Upload Parameters

```python
video = coll.upload(
    url=None,            # Remote URL (HTTP, YouTube)
    file_path=None,      # Local file path
    media_type=None,     # "video", "audio", or "image" (auto-detected if omitted)
    name=None,           # Custom name for the media
    description=None,    # Description
    callback_url=None,   # Webhook URL for async notification
)
```

## Meeting Object

```python
meeting = coll.record_meeting(
    meeting_url="https://meet.google.com/...",
    bot_name="Bot",
    callback_url=None,          # Webhook URL for status updates
    callback_data=None,         # Optional dict passed through to callbacks
    time_zone="UTC",            # Time zone for the meeting
)
```

### Meeting Properties

| Property | Type | Description |
|----------|------|-------------|
| `meeting.id` | `str` | Unique meeting ID |
| `meeting.collection_id` | `str` | Parent collection ID |
| `meeting.status` | `str` | Current status |
| `meeting.video_id` | `str` | Recorded video ID (after completion) |
| `meeting.bot_name` | `str` | Bot name |
| `meeting.meeting_title` | `str` | Meeting title |
| `meeting.meeting_url` | `str` | Meeting URL |
| `meeting.speaker_timeline` | `dict` | Speaker timeline data |
| `meeting.is_active` | `bool` | True if initializing or processing |
| `meeting.is_completed` | `bool` | True if done |

### Meeting Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `meeting.refresh()` | `Meeting` | Refresh data from server |
| `meeting.wait_for_status(target_status, timeout=14400, interval=120)` | `bool` | Poll until status reached |

## Enums & Exceptions

See [api-reference.md](api-reference.md) for the full list of enums (`SearchType`, `SceneExtractionType`, `SubtitleStyle`, `TextStyle`, `IndexType`, `MediaType`, `Segmenter`, `SegmentationType`, `TranscodeMode`, `ResizeMode`, `ReframeMode`) and exceptions (`AuthenticationError`, `InvalidRequestError`, `RequestTimeoutError`, `SearchError`, `VideodbError`).
