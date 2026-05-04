# Generative Media Guide

VideoDB provides AI-powered generation of images, videos, music, sound effects, voice, and text content. All generation methods are on the **Collection** object.

## Prerequisites

You need a connection and a collection reference before calling any generation method:

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
```

## Image Generation

Generate images from text prompts:

```python
image = coll.generate_image(
    prompt="a futuristic cityscape at sunset with flying cars",
    aspect_ratio="16:9",
)

# Access the generated image
print(image.id)
print(image.generate_url())  # returns a signed download URL
```

### generate_image Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the image to generate |
| `aspect_ratio` | `str` | `"1:1"` | Aspect ratio: `"1:1"`, `"9:16"`, `"16:9"`, `"4:3"`, or `"3:4"` |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns an `Image` object with `.id`, `.name`, and `.collection_id`. The `.url` property may be `None` for generated images — always use `image.generate_url()` to get a reliable signed download URL.

> **Note:** Unlike `Video` objects (which use `.generate_stream()`), `Image` objects use `.generate_url()` to retrieve the image URL. The `.url` property is only populated for some image types (e.g. thumbnails).

## Video Generation

Generate short video clips from text prompts:

```python
video = coll.generate_video(
    prompt="a timelapse of a flower blooming in a garden",
    duration=5,
)

stream_url = video.generate_stream()
video.play()
```

### generate_video Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the video to generate |
| `duration` | `float` | `5` | Duration in seconds (must be integer value, 5-8) |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns a `Video` object. Generated videos are automatically added to the collection and can be used in timelines, searches, and compilations like any uploaded video.

## Audio Generation

VideoDB provides three separate methods for different audio types.

### Music

Generate background music from text descriptions:

```python
music = coll.generate_music(
    prompt="upbeat electronic music with a driving beat, suitable for a tech demo",
    duration=30,
)

print(music.id)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the music |
| `duration` | `int` | `5` | Duration in seconds |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

### Sound Effects

Generate specific sound effects:

```python
sfx = coll.generate_sound_effect(
    prompt="thunderstorm with heavy rain and distant thunder",
    duration=10,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the sound effect |
| `duration` | `int` | `2` | Duration in seconds |
| `config` | `dict` | `{}` | Additional configuration |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

### Voice (Text-to-Speech)

Generate speech from text:

```python
voice = coll.generate_voice(
    text="Welcome to our product demo. Today we'll walk through the key features.",
    voice_name="Default",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Text to convert to speech |
| `voice_name` | `str` | `"Default"` | Voice to use |
| `config` | `dict` | `{}` | Additional configuration |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

All three audio methods return an `Audio` object with `.id`, `.name`, `.length`, and `.collection_id`.

## Slow Operations: Use `callback_url` to Avoid Timeouts

The following generative operations are **expensive and frequently exceed the socket timeout** when invoked synchronously:

| Operation | Typical latency | Recommendation |
|-----------|-----------------|----------------|
| `coll.generate_music(...)` | 30 s – 2 min | Pass `callback_url` |
| `coll.generate_video(...)` | 1 – 5 min | Pass `callback_url` |
| `coll.dub_video(...)` | 2 – 5 min | **Always** pass `callback_url` — sync dubs routinely time out |
| `video.reframe(...)` (full length) | minutes | Pass `callback_url`, or limit with `start`/`end` |

### Async pattern

Kick the job off with a callback and tell the user what to expect:

```python
dubbed = coll.dub_video(
    video_id=video.id,
    language_code="es",
    callback_url="https://example.com/videodb-callback",
)

output = [{
    "type": "text",
    "status_message": "Dub started",
    "text": (
        f"Started Spanish dub for **{video.name}**. "
        f"This typically takes 2–5 minutes — you'll be notified via the callback when it's ready.\n\n"
        f"- Job: `{getattr(dubbed, 'id', 'unknown')}`"
    )
}]
```

### If a sync call times out

If `RequestTimeoutError` is raised, do **not** re-run the same synchronous call — switch to the async callback pattern above, or reduce the work (shorter segment, fewer seconds of generated audio).

## Text Generation (LLM Integration)

Use `coll.generate_text()` to run LLM analysis. This is a **Collection-level** method -- pass any context (transcripts, descriptions) directly in the prompt string.

```python
# Get transcript from a video first
transcript_text = video.get_transcript_text()

# Generate analysis using collection LLM
result = coll.generate_text(
    prompt=f"Summarize the key points discussed in this video:\n{transcript_text}",
    model_name="pro",
)

print(result["output"])
```

### generate_text Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Prompt with context for the LLM |
| `model_name` | `str` | `"basic"` | Model tier: `"basic"`, `"pro"`, or `"ultra"` |
| `response_type` | `str` | `"text"` | Response format: `"text"` or `"json"` |

Returns a `dict` with an `output` key. When `response_type="text"`, `output` is a `str`. When `response_type="json"`, `output` is a `dict`.

```python
result = coll.generate_text(prompt="Summarize this", model_name="pro")
print(result["output"])  # access the actual text/dict
```

### Analyze Scenes with LLM

Combine scene extraction with text generation:

```python
from videodb import SceneExtractionType

# First index scenes
video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 10},
    prompt="Describe the visual content in this scene.",
)

# Get transcript for spoken context
transcript_text = video.get_transcript_text()

# Analyze with collection LLM
result = coll.generate_text(
    prompt=(
        f"Given this video transcript:\n{transcript_text}\n\n"
        "Based on the spoken and visual content, describe the main topics covered."
    ),
    model_name="pro",
)
print(result["output"])
```

## Dubbing and Translation

### Dub a Video

Dub a video into another language using the collection method:

```python
dubbed_video = coll.dub_video(
    video_id=video.id,
    language_code="es",  # Spanish
)

dubbed_video.play()
```

### dub_video Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_id` | `str` | required | ID of the video to dub |
| `language_code` | `str` | required | Target language code (e.g., `"es"`, `"fr"`, `"de"`) |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |

Returns a `Video` object with the dubbed content.

### Translate Transcript

Translate a video's transcript without dubbing:

```python
translated = video.translate_transcript(
    language="Spanish",
    additional_notes="Use formal tone",
)

for entry in translated:
    print(entry)
```

**Supported languages** include: `en`, `es`, `fr`, `de`, `it`, `pt`, `ja`, `ko`, `zh`, `hi`, `ar`, and more.

### Prerequisite: transcript must exist

`translate_transcript`, `dub_video`, `generate_voice` from a script derived from transcript, and any `generate_text` call that feeds in `video.get_transcript_text()` all require the video to have spoken content.

If the video has no speech (music video, silent footage, b-roll), the API returns an error like **`No spoken data found`**. Pre-check before invoking transcript-dependent operations and return a clean message:

```python
try:
    transcript_text = video.get_transcript_text()
except Exception as e:
    msg = str(e)
    if "No spoken data" in msg or "transcript" in msg.lower():
        output = [{
            "type": "text",
            "status_message": "No speech to work with",
            "text": (
                f"I found **{video.name}**, but it contains no spoken content, "
                "so I can't transcribe, translate, summarize, or dub it."
            )
        }]
        transcript_text = None
    else:
        # Try indexing once as recovery, then bail cleanly
        try:
            video.index_spoken_words(force=True)
            transcript_text = video.get_transcript_text()
        except Exception as ee:
            output = [{
                "type": "text",
                "status_message": "Transcript unavailable",
                "text": f"Could not build a transcript for **{video.name}**: {ee}"
            }]
            transcript_text = None

if transcript_text:
    # proceed with translate / dub / summarise / etc.
    ...
```

## Complete Workflow Examples

### Generate Narration for a Video

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Get transcript
transcript_text = video.get_transcript_text()

# Generate narration script using collection LLM
result = coll.generate_text(
    prompt=(
        f"Write a professional narration script for this video content:\n"
        f"{transcript_text[:2000]}"
    ),
    model_name="pro",
)
script = result["output"]

# Convert script to speech
narration = coll.generate_voice(text=script)
print(f"Narration audio: {narration.id}")
```

### Generate Thumbnail from Prompt

```python
thumbnail = coll.generate_image(
    prompt="professional video thumbnail showing data analytics dashboard, modern design",
    aspect_ratio="16:9",
)
print(f"Thumbnail URL: {thumbnail.generate_url()}")
```

### Add Generated Music to Video

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate background music
music = coll.generate_music(
    prompt="calm ambient background music for a tutorial video",
    duration=60,
)

# Build timeline with video + music overlay
timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id))
timeline.add_overlay(0, AudioAsset(asset_id=music.id, disable_other_tracks=False))

stream_url = timeline.generate_stream()
print(f"Video with music: {stream_url}")
```

### Structured JSON Output

```python
transcript_text = video.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this transcript:\n{transcript_text}\n\n"
        "Return a JSON object with keys: summary, topics (array), action_items (array)."
    ),
    model_name="pro",
    response_type="json",
)

# result["output"] is a dict when response_type="json"
print(result["output"]["summary"])
print(result["output"]["topics"])
```

## Tips

- **Generated media is persistent**: All generated content is stored in your collection and can be reused.
- **Three audio methods**: Use `generate_music()` for background music, `generate_sound_effect()` for SFX, and `generate_voice()` for text-to-speech. There is no unified `generate_audio()` method.
- **Text generation is collection-level**: `coll.generate_text()` does not have access to video content automatically. Fetch the transcript with `video.get_transcript_text()` and pass it in the prompt.
- **Model tiers**: `"basic"` is fastest, `"pro"` is balanced, `"ultra"` is highest quality. Use `"pro"` for most analysis tasks.
- **Combine generation types**: Generate images for overlays, music for backgrounds, and voice for narration, then compose using timelines (see [editor.md](editor.md)).
- **Prompt quality matters**: Descriptive, specific prompts produce better results across all generation types.
- **Aspect ratios for images**: Choose from `"1:1"`, `"9:16"`, `"16:9"`, `"4:3"`, or `"3:4"`.
