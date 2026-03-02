[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Issues](https://img.shields.io/github/issues/video-db/videodb-python.svg?style=for-the-badge)](https://github.com/video-db/videodb-python/issues)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img width="1856" height="576" alt="github_banner_skills" src="https://github.com/user-attachments/assets/a99b59d1-62de-43be-afcd-af5347372db6" width="800"/>


**The only perception skill your agent needs.**

Works with **Claude Code**, **Cursor**, **Copilot**, and other AI agents

**[📚 Explore the Docs](https://docs.videodb.io)**

</div>

---

## Why add this Skill

This skill gives your agent one consistent interface to:

**See**: Realtime desktop screen, mic and system audio, RTSP streams, ingest files, URLs, YouTube.

**Understand**: Visual understanding, transcribe, index and search moments with playble clips

**Act**: Stream results, trigger alerts on live feeds, edit timelines, generate subtitles and overlays, export clips.

---

## What it does

VideoDB Skills lets your AI coding agent run end to end video workflows:

- Capture desktop screen, mic, and system audio for real time processing.
- Upload and process RTSP streams, videos from YouTube, URLs, and local files.
- Create realtime context of visual and spoken information. 
- Index and search spoken words and visual scenes anytime.
- Generate transcripts, subtitles, and AI media.
- Edit clips, overlays, and exports server side.

Return playable HLS links for anything you build

## Start building

Get started in two quick steps. Open your AI coding agent (Claude Code, Cursor, Copilot) and follow along.
- **Python 3.9+**

### Step 1: Install the skill

```bash
npx skills add video-db/skills
```

Or install with Claude Code plugin:

```bash
/plugin marketplace add video-db/skills
/plugin install videodb@videodb-skills
```

### Step 2: Setup

```
/videodb setup
```

The agent will guide setup for your [VideoDB API key](https://console.videodb.io) ($20 free credits, no credit card required), install the SDK, and verify the connection.

If needed, you can also set the API key in your current terminal session:

```bash
export VIDEO_DB_API_KEY=sk-xxx
```

This is optional when your key is already available via `.env`.
Use only `VIDEO_DB_API_KEY=...` (without `export`) when writing to `.env` files.

> **Cursor, Copilot, and other agents:** ask your agent to "setup videodb".

## Give your agent instructions

Ask your agent to run instructions like these. The skill loads automatically.

- *"Upload https://www.youtube.com/watch?v=FgrO9ADPZSA and give me a transcript"*
- *"Search for 'product demo' in my latest video"*
- *"Add subtitles with white text on black background"*
- *"Take clips from 10s-30s and 45s-60s, add a title card, and combine them"*
- *"Capture my screen and tell me what's happening in real-time"*
- *"Start recording my meeting and give me a summary of actionable points at the end"*
- *"Generate background music and overlay it on my video"*


---

## Capability

| Capability | Description |
|---|---|
| **Capture** | Capture visual and audio to unlock real-time processing |
| **Upload** | Ingest videos from YouTube, URLs, or local files |
| **Search** | Find moments by what was said (speech) or what was shown (scenes) |
| **Transcripts** | Generate timestamped transcripts from any video |
| **Edit** | Combine clips, trim, add text/image/audio overlays |
| **Subtitles** | Auto-generate and style subtitles |
| **AI Generate** | Create images, video, music, sound effects, and voiceovers from text |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, or reframe for social platforms — all server-side |
| **Stream** | Get playable HLS links for anything you build |

---


**Supported Platforms:** macOS, Linux, Windows (PowerShell)

---

## Community & Support

- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.com/invite/py9P639jGz)

---

<div align="center">

Made with ❤️ by the VideoDB team

</div>
