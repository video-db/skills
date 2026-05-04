# API Reference Index

This is the top-level index for the VideoDB SDK reference. The detailed material lives in the per-object files below — read whichever matches your task, rather than loading this whole file.

## Where to look

| Topic | File | Covers |
|-------|------|--------|
| Connection, Collections, Meetings, Transcode | [collection.md](collection.md) | `videodb.connect()`, `Connection` methods, `Collection` methods, upload, `transcode` + `VideoConfig` / `AudioConfig`, `Meeting` object |
| Video object | [video.md](video.md) | `Video` properties/methods, transcript, spoken/scene/visual/audio indexing, scene extraction, reframe, clip, insert, download, `SearchResult`, `Shot` |
| Audio object | [audio.md](audio.md) | `Audio` properties/methods, generation shortcuts, using audio in timelines |
| Image object | [image.md](image.md) | `Image` properties/methods, generation, thumbnails, using images in timelines |
| Timeline & Editor (assets) | [editor.md](editor.md) | `Timeline`, `VideoAsset`, `AudioAsset`, `ImageAsset`, `TextAsset`, `CaptionAsset`, overlays, styling |
| Search & indexing | [search.md](search.md) | Semantic / keyword / scene search, `search_type`, `index_type`, thresholds, compiling clips |
| Streaming & playback | [streaming.md](streaming.md) | HLS streams, `generate_stream()`, player URLs |
| Generative | [generative.md](generative.md) | `generate_image`, `generate_video`, `generate_music`, `generate_sound_effect`, `generate_voice` |
| RTStream (live) | [rtstream.md](rtstream.md), [rtstream-reference.md](rtstream-reference.md) | RTSP/RTMP ingest, real-time indexing, events, webhooks, `connect_rtstream`, `RTStream` methods |
| Asset discovery | [asset_discovery.md](asset_discovery.md) | Resolving video/audio/image names to IDs |
| Censoring | [censor.md](censor.md) | Profanity detection and beep overlays |
| Use cases | [use-cases.md](use-cases.md) | End-to-end workflows |

Everything below is only the bits that don't belong to a single object: cross-cutting enums and exceptions.

## Enums & Constants

### SearchType

```python
from videodb import SearchType

SearchType.semantic    # Natural language semantic search
SearchType.keyword     # Exact keyword matching
SearchType.scene       # Visual scene search (may require paid plan)
SearchType.llm         # LLM-powered search
```

### SceneExtractionType

```python
from videodb import SceneExtractionType

SceneExtractionType.shot_based   # Automatic shot boundary detection
SceneExtractionType.time_based   # Fixed time interval extraction
SceneExtractionType.transcript   # Transcript-based scene extraction
```

### SubtitleStyle

```python
from videodb import SubtitleStyle

style = SubtitleStyle(
    font_name="Arial",
    font_size=18,
    primary_colour="&H00FFFFFF",
    bold=False,
    # ... see SubtitleStyle for all options
)
video.add_subtitle(style=style)
```

### SubtitleAlignment & SubtitleBorderStyle

```python
from videodb import SubtitleAlignment, SubtitleBorderStyle
```

### TextStyle

```python
from videodb import TextStyle
# or: from videodb.asset import TextStyle

style = TextStyle(
    fontsize=24,
    fontcolor="black",
    boxcolor="white",
    font="Sans",
    text_align="T",
    alpha=1.0,
)
```

### Other Constants

```python
from videodb import (
    IndexType,          # spoken_word, scene
    MediaType,          # video, audio, image
    Segmenter,          # word, sentence, time
    SegmentationType,   # sentence, llm
    TranscodeMode,      # economy, lightning
    ResizeMode,         # crop, fit, pad
    ReframeMode,        # simple, smart
    RTStreamChannelType,
)
```

## Exceptions

```python
from videodb.exceptions import (
    AuthenticationError,     # Invalid or missing API key
    InvalidRequestError,     # Bad parameters or malformed request
    RequestTimeoutError,     # Request timed out
    SearchError,             # Search operation failure (e.g. not indexed)
    VideodbError,            # Base exception for all VideoDB errors
)
```

| Exception | Common Cause |
|-----------|-------------|
| `AuthenticationError` | Missing or invalid `VIDEO_DB_API_KEY` |
| `InvalidRequestError` | Invalid URL, unsupported format, bad parameters |
| `RequestTimeoutError` | Server took too long to respond |
| `SearchError` | Searching before indexing, invalid search type |
| `VideodbError` | Server errors, network issues, generic failures |
