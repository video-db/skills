# Audio Object Reference

```python
audio = coll.get_audio(audio_id)
```

## Audio Properties

| Property | Type | Description |
|----------|------|-------------|
| `audio.id` | `str` | Unique audio ID |
| `audio.collection_id` | `str` | Parent collection ID |
| `audio.name` | `str` | Audio name |
| `audio.length` | `float` | Duration in seconds |

## Audio Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `audio.generate_url()` | `str` | Generate signed URL for playback |
| `audio.get_transcript(start=None, end=None)` | `list[dict]` | Get timestamped transcript |
| `audio.get_transcript_text(start=None, end=None)` | `str` | Get full transcript text |
| `audio.generate_transcript(force=None)` | `dict` | Generate transcript |
| `audio.delete()` | `None` | Delete the audio |

## Generating Audio

Audio objects can be created from a `Collection` via AI generation. See [generative.md](generative.md) for full details.

```python
# Music
music = coll.generate_music(prompt="lofi hip-hop beat", duration=5)

# Sound effect
sfx = coll.generate_sound_effect(prompt="door slam", duration=2)

# Voice (TTS)
voice = coll.generate_voice(text="Hello world", voice_name="Default")
```

## Using Audio in Timelines

Audio objects are added to a timeline as an overlay via `AudioAsset`. See [editor.md](editor.md) for the full Editor API.

```python
from videodb.asset import AudioAsset

asset = AudioAsset(
    asset_id=audio.id,
    start=0,
    end=None,
    disable_other_tracks=True,   # mute original audio when True
    fade_in_duration=0,          # seconds (max 5)
    fade_out_duration=0,         # seconds (max 5)
)
timeline.add_overlay(start=0, asset=asset)
```
