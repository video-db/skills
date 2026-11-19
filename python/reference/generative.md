# Generative Media Guide

VideoDB provides AI-powered generation of images, videos, music, sound effects, voice, and text content. All generation methods are on the **Collection** object.

## Contents

- Prerequisites
- Image Generation
- Video Generation
- Audio Generation (music, sound effects, voice)
- Text Generation (LLM Integration)
- Dubbing and Translation (dub_video, translate_transcript)
- Complete Workflow Examples
- Tips

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
| `prompt` | `str\|None` | `None` | Text description; for `heygen`, the exact script spoken |
| `duration` | `float` | `5` | Seconds (`default` model: integer 5-8). Ignored by `heygen` |
| `callback_url` | `str\|None` | `None` | URL to receive async callback |
| `model` | `str\|None` | `None` | `"default"`, `"seedance"` or `"heygen"`. `conn.get_generation_models()` lists what the account can use |
| `image_url` | `str\|None` | `None` | Start frame; for `heygen`, the required face photo (public URL) |
| `reference_images` | `list[str]\|None` | `None` | Consistency images (`default` / `seedance`) |
| `aspect_ratio` | `str\|None` | `None` | `"16:9"` / `"9:16"`; `heygen` also `"4:5"`, `"5:4"`, `"1:1"`, `"auto"` |
| `resolution` | `str\|None` | `None` | `seedance`: `"480p"` / `"720p"`; `heygen`: `"360p"` to `"1080p"` |
| `config` | `HeyGenConfig\|dict\|None` | `None` | Model-specific options; only `heygen` takes any |

### Talking avatar (HeyGen)

`model="heygen"` turns one face photo and a script into a talking-head video. `prompt` is spoken word for word, so pass only the words to say, no instructions.

```python
from videodb import HeyGenConfig

video = coll.generate_video(
    prompt="Hi, I'm Maya. Here's our new dashboard in under a minute.",
    model="heygen",
    image_url="https://example.com/maya.png",
    aspect_ratio="9:16",
    config=HeyGenConfig(voice="Ivy", talking_style="expressive", caption=True),
)

# Lip-sync to the user's own audio instead of a script
video = coll.generate_video(model="heygen", image_url=face_url, config=HeyGenConfig(audio_id=audio.id))
```

| `HeyGenConfig` field | Values |
|---|---|
| `voice` | Exact voice name; `HeyGenConfig.voices` has 12 starters, all 102 at `HeyGenConfig.docs` |
| `audio_id` | User's audio to lip-sync; not with `voice` |
| `talking_style` | `HeyGenConfig.talking_styles`: `"stable"` (default), `"expressive"` |
| `expression` | `"happy"` |
| `caption` | `True` burns in subtitles |
| `background` | `{"type": "color", "value": "#FFFFFF"}`, or `"image"` / `"video"` with a public URL |

- Script up to `HeyGenConfig.max_seconds` (120 s of speech, about 1,800 characters); audio up to 120 s.
- Costs $0.50 per output second. Takes about 2 to 5 minutes; use `callback_url` for long scripts.
- Pro plans only. A free account gets `heygen is not enabled for your account.`
- Bad keys or values fail before generation, with the allowed values in the error. Read the message and fix the argument.

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

Run analyzers, read their output, and pass both the spoken and the visual context into the prompt. `generate_text()` has no access to the video — whatever you want it to reason about must be in the prompt string.

```python
understanding = video.understand(
    analyzers=[
        {"type": "spoken_words", "name": "transcript"},
        {"type": "vlm", "name": "scene",
         "config": {"prompt": "Describe the visual content in this scene."}},
    ],
    segmentation={"type": "time", "seconds": 10},
)
understanding.wait_until_complete(timeout=3600, poll_interval=15)

output = understanding.get_analyzer("scene").get_output()
scenes = output.get("scenes", output) if isinstance(output, dict) else output

visual_context = "\n".join(
    f"[{s['start']:.0f}s] {(s.get('data') or {}).get('scene_description', '')}"
    for s in scenes or []
)
transcript_text = video.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Transcript:\n{transcript_text}\n\n"
        f"Visual timeline:\n{visual_context}\n\n"
        "Using both the spoken and visual content, describe the main topics covered."
    ),
    model_name="pro",
)
print(result["output"])
```

See [indexing.md](indexing.md) for the full understanding pipeline.

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
- **`generate_music()` may return shorter audio**: `generate_music(duration=N)` does not guarantee exactly N seconds. Always check `music.length` after generation. If shorter than needed, loop by placing multiple `AudioAsset` clips on the music track at staggered start times.
