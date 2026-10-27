[![Add to Claude](https://img.shields.io/badge/Add%20to%20Claude-VideoDB-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3%40anthropic-plugin-directory)
[![License][license-shield]][license-url]
[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img width="1200" height="372" alt="banner" src="https://github.com/user-attachments/assets/fdbf3879-dcd6-443c-93e0-9a7e1bfdfa90" />

**Edit, clip, subtitle and search video from any AI agent.**

VideoDB does the video work on its servers. The agent asks for it in plain language.

**[📚 Docs](https://docs.videodb.io)** &emsp; **[ Watch Demos ](https://www.youtube.com/playlist?list=PLhxAMFLSSK01IONxpqtEqj0UUQyFswiaR)** &emsp; **[Discord](https://discord.com/invite/py9P639jGz)**

</div>

## Three ways to use it

| You are using | Do this | What you get |
| --- | --- | --- |
| **Claude** (web, desktop, mobile), Cowork, Claude Code | [Add to Claude](https://claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3%40anthropic-plugin-directory), one click, log in to VideoDB when asked | The skills below plus the VideoDB connector. Paste a YouTube link and ask. No install, no API key. |
| **Any MCP client or chatbot** (Cursor, Claude Code, ChatGPT, MCP Inspector, your own agent) | Connect `https://mcp.videodb.io/mcp` | 89 tools over your VideoDB account: upload, transcribe, subtitle, search, ask, clip, reframe, compose, live streams, meeting recording. |
| **A coding agent with a shell** (Claude Code, Cursor, Codex, Copilot, others) | `npx skills add video-db/skills` | The skills teach the agent the VideoDB Python SDK, so it can write and run code: everything the connector does, plus local files, AI generation, dubbing, sandbox compute and desktop capture. |

A free VideoDB account comes with $20 of credits, no credit card: [console.videodb.io](https://console.videodb.io).

## Add to Claude

One click from the [Claude plugin directory](https://claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3%40anthropic-plugin-directory). Then try:

- "Upload https://www.youtube.com/watch?v=MnrJzXM7a6o and give me a shareable link"
- "Find where they talk about pricing and give me one clip of it"
- "Cut 1:10 to 1:40, make it vertical for Shorts, and burn in white subtitles on a black box"
- "Which objects appear most often in this video? Break it down by count"
- "Ask this video what the presenter said about pricing, and show me the clips"
- "Give me the timestamped transcript, then translate it to Spanish"
- "Here is the RTSP link for my camera. Alert this webhook whenever a person enters the room"

In Claude chat and Cowork the skills use the VideoDB connector, which the plugin sets up. In Claude Code they can also use the Python SDK.

## Connect the MCP server in any client

Endpoint: `https://mcp.videodb.io/mcp` (Streamable HTTP). Your client asks you to log in to your VideoDB account once.

- **Claude** (custom connector): Settings → Connectors → Add custom connector, paste the URL, click Connect.
- **Claude Code**: `claude mcp add --transport http videodb https://mcp.videodb.io/mcp`, then `/mcp` to authorize.
- **Cursor** (Settings → MCP → Add new global MCP server):

  ```json
  { "mcpServers": { "videodb": { "url": "https://mcp.videodb.io/mcp" } } }
  ```

- **Other clients**: any client that speaks Streamable HTTP and OAuth works the same way. Full guide and the tool reference: [docs.videodb.io/pages/mcp](https://docs.videodb.io/pages/mcp/index).

The MCP server takes public URLs and YouTube links, not local files; it does not generate media or dub, and it cannot capture a desktop. For those, use the SDK through a coding agent.

## Install the skills in a coding agent

```bash
npx skills add video-db/skills
```

Works with Claude Code, Cursor, Codex, Copilot and other agents that read `SKILL.md` files. Or, in Claude Code, install the plugin, which bundles the MCP server as well:

```bash
/plugin marketplace add video-db/skills
/plugin install videodb@videodb-skills
```

Then say "setup videodb" (in Claude Code: `/videodb:setup`). The agent installs the SDK (Python 3.9+, `videodb>=0.5.0`), asks for your [API key](https://console.videodb.io) and saves it to the project's `.env` for you. If you would rather set it yourself:

```bash
export VIDEO_DB_API_KEY=sk-xxx     # or VIDEO_DB_API_KEY=sk-xxx in .env
```

`npx skills add` installs the skills only. To give the agent the MCP tools as well, connect the server as above.

## What works where

| Capability | Claude chat and any MCP client | Coding agent with the SDK |
| --- | :---: | :---: |
| Upload from a YouTube link or public URL | ✓ | ✓ |
| Upload a local file | | ✓ |
| Transcripts, subtitles, translation | ✓ | ✓ |
| Find a moment, ask a video, count what appears | ✓ | ✓ |
| Clips, highlight reels, supercuts, thumbnails, MP4 | ✓ | ✓ |
| Vertical and square cuts for Shorts, Reels, TikTok | ✓ | ✓ |
| Timeline edits: music, overlays, captions, transitions | ✓ | ✓ |
| Transcode and reframe on the server | ✓ | ✓ |
| Live streams (RTSP, RTMP, HLS) with alerts | ✓ | ✓ |
| Record a Zoom, Google Meet or Teams meeting | ✓ | ✓ |
| AI generation: images, video, music, voiceover | | ✓ |
| Dubbing | | ✓ |
| Open-weight models on sandbox compute | | ✓ |
| Desktop screen, mic and system audio capture | | ✓ macOS only, agent running on your Mac |

Every result comes back as a playable stream link (built-in CDN) or a download.

## What is inside

| Skill | Use it for |
| --- | --- |
| `video-search` | Find a moment, ask a video a question, count what appears, search a whole library |
| `video-clips` | Clips of a time range, highlight reels from a prompt, supercuts, vertical cuts, thumbnails, MP4s |
| `video-subtitles` | Transcripts, burned-in subtitles with styling, translation |
| `video-edit` | Background music, voiceover, text and logo overlays, animated captions, compositions |
| `video-live` | Cameras and live streams with alerts, meeting recording, desktop screen capture |
| `videodb` | Setup, the Python SDK reference, AI generation, dubbing, sandbox compute |

Four slash commands for Claude Code: `/videodb:setup`, `/videodb:find`, `/videodb:clip`, `/videodb:subtitles`. The plugin also carries the hosted MCP server configuration (`.mcp.json`).

### If you are an agent reading this

Use the VideoDB connector tools when they are present. Load the skill that matches the job (the table above). With a shell and no connector, ask the user for their API key once, save it to `.env`, and use the Python SDK as the `videodb` skill describes. Long jobs return `status: processing`; poll with the tool the reply names until `done`, and never re-run the write.

## Community & Support

- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.com/invite/py9P639jGz)
- **Privacy policy:** [videodb.io/legal/privacy](https://videodb.io/legal/privacy)

<div align="center">

Made with ❤️ by the VideoDB team

</div>

[license-shield]: https://img.shields.io/github/license/video-db/skills.svg?style=for-the-badge
[license-url]: https://github.com/video-db/skills/blob/main/LICENSE
