[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img src="assets/skills-banner.jpeg" alt="VideoDB Skills" width="800">

**The only skill your agent needs for video.**

Works with **Claude Code**, **Cursor**, **Copilot**, and other AI agents

---

**[📚 Explore the Docs](https://docs.videodb.io)**

</div>

---

## Prerequisites

- **Python 3.9+**
- **An AI coding agent** (Claude Code, Cursor, Copilot, etc.)
- **VideoDB API key** — sign up free at [console.videodb.io](https://console.videodb.io)
  - $20 free credits
  - No credit card required

**Supported Platforms:** macOS, Linux, Windows (PowerShell)

---

## Installation

### Option 1: npx (Recommended)

Install for multiple AI coding assistants (Claude Code, Cursor, Copilot, etc.):

```bash
npx skills add video-db/skills
```

### Option 2: Claude Code Plugin

```bash
/plugin marketplace add video-db/skills
/plugin install videodb@videodb-skills
```

---

## Quick Start

Get started in two steps. Open your AI coding agent (Claude Code, Cursor, Copilot) and follow along.

### Step 1: Setup

```
/videodb setup
```

The agent will prompt for your [VideoDB API key](https://console.videodb.io) ($20 free credits, no credit card required), install the SDK, and verify the connection.

> **Cursor, Copilot, and other agents:** just ask your agent to "setup videodb".

### Step 2: Start building

Describe what you want in natural language. The skill loads automatically.

- *"Upload https://www.youtube.com/watch?v=FgrO9ADPZSA and give me a transcript"*
- *"Search for 'product demo' in my latest video"*
- *"Add subtitles with white text on black background"*
- *"Take clips from 10s-30s and 45s-60s, add a title card, and combine them"*
- *"Generate background music and overlay it on my video"*
- *"Capture my screen and transcribe it in real-time"*

---

## Capabilities

| Capability | Description |
|---|---|
| **Upload** | Ingest videos from YouTube, URLs, or local files |
| **Search** | Find moments by what was said (speech) or what was shown (scenes) |
| **Transcripts** | Generate timestamped transcripts from any video |
| **Edit** | Combine clips, trim, add text/image/audio overlays |
| **Subtitles** | Auto-generate and style subtitles |
| **AI Generate** | Create images, video, music, sound effects, and voiceovers from text |
| **Meetings** | Record meetings, extract transcripts, get summaries and action items |
| **Capture** | Record screen, mic, and system audio in real-time with AI transcription and indexing |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, or reframe for social platforms — all server-side |
| **Stream** | Get playable HLS links for anything you build |

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
