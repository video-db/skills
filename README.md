[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Issues](https://img.shields.io/github/issues/video-db/videodb-python.svg?style=for-the-badge)](https://github.com/video-db/videodb-python/issues)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img width="1856" height="576" alt="github_banner_skills" src="https://github.com/user-attachments/assets/a99b59d1-62de-43be-afcd-af5347372db6" width="800"/>


**The only video skill your agent needs.**

Works with **Claude Code**, **Cursor**, **Copilot**, and other AI agents

**[📚 Explore the Docs](https://docs.videodb.io)**

</div>

---

## What it does

VideoDB Skills lets your AI coding agent run end-to-end video workflows.

- Upload and process videos from YouTube, URLs, and local files
- Search spoken words and visual scenes
- Generate transcripts, subtitles, and AI media
- Edit clips, overlays, and exports server-side
- Capture visual and audio streams for real-time processing

---

## Start building

Get started in three quick steps. Open your AI coding agent (Claude Code, Cursor, Copilot) and follow along.

### Step 1: Install the skill

```bash
npx skills add video-db/skills
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

### Step 3: Give your agent instructions

Ask your agent to run instructions like these. The skill loads automatically.

- *"Upload https://www.youtube.com/watch?v=FgrO9ADPZSA and give me a transcript"*
- *"Search for 'product demo' in my latest video"*
- *"Add subtitles with white text on black background"*
- *"Take clips from 10s-30s and 45s-60s, add a title card, and combine them"*
- *"Generate background music and overlay it on my video"*
- *"Capture my screen and transcribe it in real-time"*

---

## Capability

| Capability | Description |
|---|---|
| **Upload** | Ingest videos from YouTube, URLs, or local files |
| **Search** | Find moments by what was said (speech) or what was shown (scenes) |
| **Transcripts** | Generate timestamped transcripts from any video |
| **Edit** | Combine clips, trim, add text/image/audio overlays |
| **Subtitles** | Auto-generate and style subtitles |
| **AI Generate** | Create images, video, music, sound effects, and voiceovers from text |
| **Capture** | Capture visual and audio to unlock real-time processing |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, or reframe for social platforms — all server-side |
| **Stream** | Get playable HLS links for anything you build |

---

## Detailed installation steps

1. Ensure prerequisites:
   - **Python 3.9+**
   - **An AI coding agent** (Claude Code, Cursor, Copilot, etc.)
   - **VideoDB API key** from [console.videodb.io](https://console.videodb.io)
2. Install the skill (recommended):

```bash
npx skills add video-db/skills
```

3. Or install with Claude Code plugin:

```bash
/plugin marketplace add video-db/skills
/plugin install videodb@videodb-skills
```

4. Run setup inside your agent:

```
/videodb setup
```

**Supported Platforms:** macOS, Linux, Windows (PowerShell)

---

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## Community & Support

- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.com/invite/py9P639jGz)

---

<div align="center">

Made with ❤️ by the VideoDB team

</div>
