[![Add to Claude](https://img.shields.io/badge/Add%20to%20Claude-VideoDB-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3%40anthropic-plugin-directory)
[![License][license-shield]][license-url]
[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img width="1200" height="372" alt="banner" src="https://github.com/user-attachments/assets/fdbf3879-dcd6-443c-93e0-9a7e1bfdfa90" />

**Edit, clip, subtitle and search your videos in Claude.**

Works in **Claude** (web, desktop, mobile), **Cowork**, **Claude Code**, and in **Cursor**, **Codex** and other agents

**[📚 Docs](https://docs.videodb.io)** &emsp; **[ Watch Demos ](https://www.youtube.com/playlist?list=PLhxAMFLSSK01IONxpqtEqj0UUQyFswiaR)**

</div>

## Add to Claude

One click from the [Claude plugin directory](https://claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3%40anthropic-plugin-directory) adds VideoDB to Claude. Log in to your VideoDB account when Claude asks ($20 of free credits, no credit card), then paste a YouTube link and ask for what you want. No install, no API key to copy.

Try these:

- "Upload https://www.youtube.com/watch?v=MnrJzXM7a6o and give me a shareable link"
- "Find every moment where they talk about pricing, and give me one clip of those moments"
- "Cut 1:10 to 1:40, make it vertical for Shorts, and burn in white subtitles on a black box"
- "Which objects appear most often in this video? Break it down by count"
- "Ask this video what the presenter said about pricing, and show me the clips"
- "Give me the timestamped transcript, then translate it to Spanish"
- "Here is the RTSP link for my camera. Alert this webhook whenever a person enters the room"

## What is inside

| Skill | Use it for |
| --- | --- |
| `video-search` | Find a moment, ask a video a question, count what appears, search a whole library |
| `video-clips` | Clips of a time range, highlight reels from a prompt, supercuts, vertical cuts, thumbnails, MP4s |
| `video-subtitles` | Transcripts, burned-in subtitles with styling, translation |
| `video-edit` | Background music, voiceover, text and logo overlays, captions, compositions |
| `video-live` | Cameras and live streams with alerts, meeting recording, desktop screen capture |
| `videodb` | Setup, the Python SDK, AI generation, dubbing, sandbox compute |

Plus the hosted MCP server at `https://mcp.videodb.io/mcp` (89 tools) and four slash commands for Claude Code: `/videodb:setup`, `/videodb:find`, `/videodb:clip`, `/videodb:subtitles`.

In Claude chat and Cowork the skills use the VideoDB connector, which the plugin sets up. In Claude Code they use the bundled MCP server and the Python SDK, so code, scripts, desktop capture and AI generation work there too.

## Install in Claude Code, Cursor, Codex and other agents

```bash
npx skills add video-db/skills
```

Or as a Claude Code plugin, which also bundles the MCP server:

```bash
/plugin marketplace add video-db/skills
/plugin install videodb@videodb-skills
```

After installing the plugin, run `/mcp`, select videodb, and authorize in the browser. Then ask Claude to "list my VideoDB collections" to verify. The MCP tools need no local Python and no API key. `npx skills add` installs the skills only; see the [MCP setup guide](https://docs.videodb.io/pages/mcp/connect) to add the server by URL, and the [privacy policy](https://videodb.io/legal/privacy).

### SDK setup (for code, scripts, capture and generation)

```
/videodb:setup
```

Requires Python 3.9+ and VideoDB Python SDK 0.5.0 or newer. The agent installs the SDK, asks you to set your [API key](https://console.videodb.io) ($20 of free credits, no credit card), and verifies the connection. In Cursor, Codex and other agents, say "setup videodb".

```bash
# Recommended: export in the terminal
export VIDEO_DB_API_KEY=sk-xxx

# Or add to your project's .env file
VIDEO_DB_API_KEY=sk-xxx
```

## Capability

VideoDB is the server-side video stack for agents and apps. Send video in, get back structured context, searchable moments and playable streams, with no ffmpeg glue on your side.

| Capability              | What it unlocks                                                               |
| ----------------------- | ----------------------------------------------------------------------------- |
| **Upload**              | Ingest video from YouTube, URLs, or local files                               |
| **Understand**          | Run analyzers (speech, scenes, objects, OCR, brands, activity) into reusable artifacts |
| **Search**              | Find exact moments by speech, scenes, or metadata, return playable evidence   |
| **Ask & Analyze**       | Get grounded answers with evidence, filter on exact fields, aggregate counts and facets |
| **Transcripts**         | Generate clean, timestamped transcripts from any video                        |
| **Subtitles**           | Auto generate subtitles, then style and burn in or export                     |
| **Edit**                | Trim, merge, clip, overlay text, images, audio, plus dubbing and translation  |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, and social crops, all on the server |
| **Stream**              | Get instant playable HLS links (built in CDN) for anything you ingest or generate |
| **Capture**             | Capture desktop screen, mic, and system audio for realtime processing (SDK, macOS) |
| **Context**             | Generate realtime structured context for any RTSP feed or desktop stream      |
| **AI Generate**         | Create images, video, music, sound effects, and voiceovers from text (SDK)    |
| **Sandbox Compute**     | Run open-weight models (Gemma, Qwen, Whisper, OmniVoice, FLUX, RT-DETR) on managed GPU sandboxes (SDK) |

See → Understand → Act, as an API, for video and audio.

**Supported platforms:** macOS, Linux, Windows (PowerShell)

---

## Community & Support

- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.com/invite/py9P639jGz)

<div align="center">

Made with ❤️ by the VideoDB team

</div>

[license-shield]: https://img.shields.io/github/license/video-db/skills.svg?style=for-the-badge
[license-url]: https://github.com/video-db/skills/blob/main/LICENSE
