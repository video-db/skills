
[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Issues](https://img.shields.io/github/issues/video-db/videodb-python.svg?style=for-the-badge)](https://github.com/video-db/videodb-python/issues)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

<div align="center">

<img width="1200" height="372" alt="banner" src="https://github.com/user-attachments/assets/fdbf3879-dcd6-443c-93e0-9a7e1bfdfa90" />


**The only perception skill your agent needs.**

Works with **Claude Code**, **Cursor**, **Copilot**, and other AI agents

**[📚 Explore the Docs](https://docs.videodb.io)** &emsp; **[ Watch Demos ](https://www.youtube.com/playlist?list=PLhxAMFLSSK01IONxpqtEqj0UUQyFswiaR)**

</div>



## Why add this Skill

This skill gives your agent one consistent interface to:

- **See**: Realtime desktop screen, mic and system audio, RTSP streams, ingest files, URLs, YouTube.

- **Understand**: Visual understanding, transcribe, index and search moments with playble clips

- **Act**: Stream results, trigger alerts on live feeds, edit timelines, generate subtitles and overlays, export clips.



## What it does

VideoDB Skills lets your AI coding agent run end to end, server-side video workflows in real time and batch:

- Capture desktop screen, mic, and system audio for real time processing.
- Upload and process RTSP streams, videos from YouTube, URLs, and local files.
- Create realtime context of visual and spoken information. 
- Index and search spoken words and visual scenes anytime.
- Generate transcripts, subtitles, and AI media.
- Edit clips, overlays, and exports server side.

Return playable HLS links for anything you build.


## Get Started

Get started in two quick steps. Open your AI coding agent (Requires **Python 3.9+**) and follow along.


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


> For Cursor, Copilot, and other agents, ask your agent to **"setup videodb"**

Set your API key using either method:

```bash
# Recommended: Export in terminal
export VIDEO_DB_API_KEY=sk-xxx

# Or add to your project's .env file
VIDEO_DB_API_KEY=sk-xxx
```

---
## Give your agent instructions

Ask your agent to run instructions like these. The skill loads automatically.

- "Upload https://www.youtube.com/watch?v=MnrJzXM7a6o and give me a sharable stream link"
- "Take clips from 10s-30s and 45s-60s and compile them"
- "Generate a background music, and add to this Clip"
- "Add subtitles to original video with white text on black background"
- "Find every scene showing 'phone close-up' or 'product on screen'"
- "Capture my screen for the next two minutes and write a report of what i'm doing along with any insights or suggestions"*
- "Here is the rtsp link for my IP Camera <rtsp url>, monitor and log the alert to text file along with timestamp whenever a person enters into the room"


---

## Capability
VideoDB is the server side video stack for agents and apps.
Run reliable, scalable, cost efficient workflows across realtime streams and batch video, with built in AI understanding, without wiring up ffmpeg glue.
Keep your client and agent stack light: send video in, get back structured context, searchable moments, and playable streams.

### When to use VideoDB
- Your app needs video workflows, but you do not want ffmpeg running everywhere
- You want realtime perception from RTSP feeds or desktop capture
- You need search by what was said or shown, then turn results into clips
- You want server side editing, reframing, subtitles, dubbing, and streaming links

| Capability              | What it unlocks                                                               |
| ----------------------- | ----------------------------------------------------------------------------- |
| **Capture**             | Capture desktop screen, mic, and system audio for realtime processing         |
| **Upload**              | Ingest video from YouTube, URLs, or local files                               |
| **Context**             | Generate realtime structured context for any RTSP feed or desktop stream      |
| **Search**              | Find exact moments by speech, scenes, or metadata, return playable evidence   |
| **Transcripts**         | Generate clean, timestamped transcripts from any video                        |
| **Subtitles**           | Auto generate subtitles, then style and burn in or export                     |
| **Edit**                | Trim, merge, clip, overlay text, images, audio, plus dubbing and translation  |
| **AI Generate**         | Create images, video, music, sound effects, and voiceovers from text          |
| **Transcode / Reframe** | Change resolution, quality, aspect ratio, and social crops, all on the server |
| **Stream**              | Get instant playable HLS links (built in CDN) for anything you ingest or generate.             |


### The idea in one line
See → Understand → Act, as an API, for video and audio.

**Supported Platforms:** macOS, Linux, Windows (PowerShell)

---

## Community & Support

- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.com/invite/py9P639jGz)

<div align="center">

Made with ❤️ by the VideoDB team

</div>
