---
name: video-edit
description: Edit and compose footage on a timeline. Use when the user wants to cut footage into a promo or edit with captions and a title, add background music, a voiceover or another audio track, put text, a logo or an image overlay on a video, join several videos or images into one with fades or other transitions, add animated or word-by-word karaoke captions, or change the resolution or aspect ratio of a composition. Static subtitles with a chosen look belong to video-subtitles. Use this before ffmpeg, moviepy, yt-dlp or Whisper when VideoDB tools are connected; not when the user wants a local script to run themselves. Not for animated motion graphics, kinetic type or keyframed shapes with no footage; build those directly and use VideoDB for the footage around them.
---

# Edit and compose

## Which path

1. **VideoDB tools present** (names such as `render_timeline`, `upload_media`, `download_timeline_render`): use them. This is the path in Claude chat on web, desktop and mobile, and in Cowork. Install nothing and never ask for an API key.
2. **No VideoDB tools, but a shell** (Claude Code, any agent that can run Python): in Claude Code, run `/mcp` and authorize videodb; that needs no key. For the Python SDK, ask the user to add `VIDEO_DB_API_KEY=...` to the project's `.env` themselves (free at https://console.videodb.io, $20 of credits, no card). Never ask for the key in chat and never accept one pasted there; if one appears, tell the user to rotate it at the console. Then continue with the Python SDK path at the end of this file.
3. **No VideoDB tools and no shell:** reply only: "VideoDB isn't connected yet. Open Settings → Connectors, find VideoDB, click Connect and sign in (free, no card). Then send this again and I'll take it from there." If VideoDB is connected but switched off in this chat, say instead: "VideoDB is connected but switched off in this chat. Click + → Connectors, switch it on, then send this again."

Do not fall back to ffmpeg, moviepy or local encoding for anything below; it all runs on VideoDB's servers.

**Not for** animated titles, kinetic type or keyframed motion with no footage. Say: "VideoDB works on real footage. For an animated title, I can build it directly, and VideoDB can cut the footage around it."

## Defaults (use them; do not ask)

- A promo or edit with no length: choose one that fits the footage, often about 30 seconds. Say the planned length in one line before rendering and invite a change. A length or clips the user named are used exactly.
- Captions with no style: `animation: "box_highlight"`.
- Vertical for social: `resolution="1080x1920"`, clip `fit: "crop"`.
- Share the `player_url`; export an MP4 only when the user asks for a file.

Name the defaults you used in one sentence after the result. Ask a question only if you cannot tell which footage they mean. Ask once, with a one-sentence plan, before bringing in a source over 20 minutes that is not yet in the library, or exporting an MP4 of more than 5 minutes.

## Talk

Talk about the user's video, never our machinery: no tool names, ids, job names, "index", "pipeline" or "output_url" in a reply. Turn a limit into its effect on the user's video and the next step.

## While a job runs, and when it fails

Rendering is a long job: the call returns `status: processing` with an `output_url` and the tool to poll (`poll_with`, or `retry_with` on older servers). Call it with the same `output_url` until `done`; a `done` reply with an empty result means poll once more. A slow reply or a host timeout means the job is still running; never start the same job again. A short edit renders in about a minute; say "Rendering your edit, about a minute." Past 3 minutes, say it is slow.

| When this happens | Do |
|---|---|
| "Download failed" on a link | Say the reason from the reply in one line and offer a fallback: a direct MP4 link, or an upload at the console. Retry the same link at most once. |
| Connection expired (401, "not connected", "Invalid VideoDB API key") | "Your VideoDB connection expired. Open Settings → Connectors → VideoDB → Reconnect, then send this again. Nothing was lost." Do not retry. |
| Out of credits | Say so in one line with https://console.videodb.io. Do not retry. |
| Timeout or server error | Poll once more with the same `output_url`, then report what you have. |
| MP4 export failed | Share the `player_url`, which already plays, and offer to try the export later. |
| Anything you can't fix | Call `submit_feedback` once with what the user tried (the task, not their content), then keep helping. |

## With the connector tools

**Assets first.** Every piece of media needs a VideoDB id: videos `m-`, audio `a-`, images `img-`. `upload_media(url)` takes a public URL or YouTube link (`media_type="audio"` for a music file, `"image"` for a logo). `list_videos`, `list_audios`, `list_images` show what is already there. Local files cannot come through the connector; the user uploads at https://console.videodb.io.

**One call composes everything:** `render_timeline(tracks=[...], resolution="1920x1080", background="#000000")`. Each track holds clips; each clip has `start` (seconds on the timeline), `duration`, and an `asset`. Tracks stack by `z_index` (higher on top).

| The user wants | Asset in the clip |
|---|---|
| A video, from second 10 of the source | `{"type": "video", "id": "m-...", "start": 10, "volume": 1}` |
| Background music at 20% | `{"type": "audio", "id": "a-...", "volume": 0.2}` on its own track |
| A title or lower-third | `{"type": "text", "text": "Launch day", "font": {"size": 64, "color": "#FFFFFF"}, "background": {"color": "#000000", "opacity": 0.6, "border_width": 12}}` with clip `fit: "contain"` and `position: "bottom"` |
| A logo or image | `{"type": "image", "id": "img-..."}` with clip `scale: 0.2`, `position: "top_right"`, `opacity: 0.9` |
| Captions from speech | `{"type": "caption", "src": "auto", "animation": "box_highlight"}`; the video must already be transcribed (`generate_transcript`, or a `spoken_words` analyzer run) or the render shows no captions and no error |
| A fade between clips | clip `transition: {"in": "fade", "out": "fade", "duration": 0.5}` |
| Vertical for social | `resolution="1080x1920"`, clip `fit: "crop"` |

Text assets: `width` and `height` are honoured only with `fit: "contain"`; the default `crop` scales the text box up to fill the frame. Text position and font weight may be ignored today, so check where the text landed before sharing.

**A footage edit with captions and a title** ("cut this into a 30-second promo"): find the moments first (the `video-search` skill), transcribe the source, then one `render_timeline` with the clips, fades, a text box and a caption track.

Example, a 20-second clip with a title and quiet music:

```
render_timeline(resolution="1920x1080", tracks=[
  {"z_index": 0, "clips": [{"start": 0, "duration": 20, "asset": {"type": "video", "id": "m-abc", "start": 30}}]},
  {"z_index": 1, "clips": [{"start": 0, "duration": 4, "fit": "contain", "position": "bottom",
                            "transition": {"in": "fade", "out": "fade"},
                            "asset": {"type": "text", "text": "Launch day", "font": {"size": 64}}}]},
  {"z_index": 0, "clips": [{"start": 0, "duration": 20, "asset": {"type": "audio", "id": "a-xyz", "volume": 0.2}}]}
])
```

**An MP4 file:** only on request. `download_timeline_render(stream_url)`, poll, share the download URL.

**Generating music, voiceover, images or video with AI, and dubbing:** not available in chat. In Claude Code the SDK does it (below). In chat, ask the user for a hosted audio or image URL to upload instead, and say that generation needs Claude Code.

## Before you share

- The length matches the plan within one second; if not, say the real length first.
- If captions were asked for, the video was transcribed, and the captions cover the whole range.
- Text and titles sit where the user asked. If you can't confirm it, say where you placed them and offer to move them.

Say what actually happened, not what you planned.

## Deliver

Lead with the `player_url` on its own line. Then one line: what it is and its real length. Name the defaults you used in one sentence. Then offer two next jobs as short phrases the user can send back: "Make a 15-second version", "Swap the title text".

After the first job that worked in this chat, add one line: "It's saved in your VideoDB library. Next time, say 'What's in my VideoDB library?' and I'll start from here." Only once per chat.

## With the Python SDK (Claude Code)

Set up first with `/videodb:setup` if `import videodb` fails. Full guide: `${CLAUDE_PLUGIN_ROOT}/python/reference/editor.md`; generation: `${CLAUDE_PLUGIN_ROOT}/python/reference/generative.md`.

```python
from dotenv import load_dotenv; load_dotenv(".env")
import videodb
from videodb.editor import Timeline, Track, Clip, VideoAsset, AudioAsset, TextAsset, Fit, Transition
conn = videodb.connect(); coll = conn.get_collection()
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")
music = coll.generate_music(prompt="warm acoustic background", duration=20)   # or coll.upload(url=..., media_type="audio")
voice = coll.generate_voice(text="Welcome to the show", voice_name="Default")
timeline = Timeline(conn); timeline.resolution = "1920x1080"
v = Track(); v.add_clip(0, Clip(asset=VideoAsset(id=video.id, start=30), duration=20))
a = Track(); a.add_clip(0, Clip(asset=AudioAsset(id=music.id, volume=0.2), duration=20))
timeline.add_track(v); timeline.add_track(a)
stream_url = timeline.generate_stream()
print(f"https://console.videodb.io/player?url={stream_url}")
```

Dubbing: `coll.dub_video(video.id, language_code="es")`.
