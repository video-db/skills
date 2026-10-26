---
name: video-subtitles
description: Subtitles, captions and transcripts for a video. Use when the user wants a transcript (plain or timestamped), subtitles burned into a video with a chosen style, captions on a clip, a transcript translated into another language, or dubbing. Works on YouTube links, public video URLs and videos already in the user's VideoDB account.
---

# Subtitles and transcripts

## Which path

1. **VideoDB connector tools present** (names such as `generate_transcript`, `add_subtitles`, `index_spoken_words`, `upload_media`): use them. This is the path in Claude chat on web, desktop and mobile, and in Cowork. Do not install anything and do not ask for an API key.
2. **No VideoDB tools, in Claude chat or Cowork**: tell the user, in one line, to connect VideoDB: Settings, then Connectors, then VideoDB, then Connect, and log in to their VideoDB account when asked (free, no card needed). Then retry.
3. **Claude Code with a shell and no VideoDB tools**: run `/mcp`, pick videodb and authorize. Or use the Python SDK path at the end of this file.

Long jobs return `status: processing`. Wait about 30 seconds, then read the result with the tool the reply names (`retry_with`) or `get_job_result` with its `output_url`. Never re-run the write.

## With the connector tools

**Get the video.** A YouTube link or public URL: `upload_media(url)`; note the `m-` id. Already in the account: `list_videos` or `search_videos_by_title(query)`. Local files cannot come through the connector; the user uploads at https://console.videodb.io and shares the `m-` id.

**Transcript.** `generate_transcript(video_id)` (add `language_code` if the speech is not English), then `get_transcript(video_id, timestamped=true)` for timestamps, or `timestamped=false` for plain text. For a time window pass `start` and `end`.

**Subtitles burned into the video.**

1. `index_spoken_words(video_id)` (subtitles read this index; skip if it already exists, `force=true` to redo it).
2. `add_subtitles(video_id, ...)`. Returns a `stream_url` and a `player_url`.
3. An MP4 file: `download_stream(stream_url, name="...")`, poll, then share the download link.

Style options on `add_subtitles`: `font_name`, `font_size` (default 18), `bold`, `alignment` (`bottom_center` default, `top_center`, ...), `border_style` (`outline` or `opaque_box`), `outline`, `shadow`, margins. Colours use the ASS format `&HAABBGGRR`: opaque white `&H00FFFFFF`, black `&H00000000`, yellow `&H0000FFFF`. "White text on a black box" is `primary_colour="&H00FFFFFF", back_colour="&H00000000", border_style="opaque_box"`.

**Captions on a clip or a composed video.** Use the `video-edit` skill's `render_timeline` with a `caption` asset (`src: "auto"`). The video must already have a spoken-word index, or the render comes back with no captions and no error.

**Translate.** `translate_transcript(video_id, language="Spanish")` returns the translated, timestamped segments. Give them to the user as text or as an SRT-style list.

**Dubbing and translated voiceover.** Not available through the connector. In Claude Code, the SDK does it (`${CLAUDE_PLUGIN_ROOT}/python/reference/editor.md`, dubbing section). In chat, offer the translated transcript and say that dubbing needs the SDK.

## With the Python SDK (Claude Code)

Set up first with `/videodb:setup` if `import videodb` fails. Full reference: `${CLAUDE_PLUGIN_ROOT}/python/SKILL.md`.

```python
from dotenv import load_dotenv; load_dotenv(".env")
import videodb
from videodb import SubtitleStyle, SubtitleAlignment, SubtitleBorderStyle
conn = videodb.connect(); coll = conn.get_collection()
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")
video.index_spoken_words(force=True)
print(video.get_transcript_text())
stream_url = video.add_subtitle(SubtitleStyle(font_size=20, primary_colour="&H00FFFFFF",
                                              back_colour="&H00000000", border_style=SubtitleBorderStyle.opaque_box,
                                              alignment=SubtitleAlignment.bottom_center))
print(f"https://console.videodb.io/player?url={stream_url}")
```
