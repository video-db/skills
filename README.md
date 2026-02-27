<div align="center">

<img src="https://codaio.imgix.net/docs/_s5lUnUCIU/blobs/bl-RgjcFrrJjj/d3cbc44f8584ecd42f2a97d981a144dce6a66d83ddd5864f723b7808c7d1dfbc25034f2f25e1b2188e78f78f37bcb79d3c34ca937cbb08ca8b3da1526c29da9a897ab38eb39d084fd715028b7cc60eb595c68ecfa6fa0bb125ec2b09da65664a4f172c2f" alt="VideoDB Logo" width="300">

# VideoDB Skills

**Talk to your videos using natural language. Upload, search, edit, generate subtitles, create clips, and more.**

[![GitHub stars](https://img.shields.io/github/stars/video-db/skills.svg?style=for-the-badge)](https://github.com/video-db/skills/stargazers)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io)](https://videodb.io)

Built on the [VideoDB Python SDK](https://github.com/video-db/videodb-python) and [VideoDB Capture SDK](https://github.com/video-db/videodb-capture-quickstart)

Works with **Claude Code**, **Claude Web**, and the **Claude API**

---

**[📚 Explore the Docs](https://docs.videodb.io)**

</div>

---

## ✨ What You Can Do

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
| **Transcode** | Re-encode video with custom resolution, quality, framerate, and aspect ratio — server-side |
| **Reframe** | Convert aspect ratio (vertical, square, landscape) with smart object tracking |
| **Stream** | Get playable HLS links for anything you build |

---

## ⚙️ Prerequisites

- 🐍 **Python 3.9+**
- 🤖 **Claude Code** (for plugin usage) or any Claude interface
- 🔑 **VideoDB API key** — sign up free at [console.videodb.io](https://console.videodb.io)
  - 50 free uploads
  - No credit card required

**Supported Platforms:** macOS, Linux, Windows (PowerShell)

---

## 📦 Installation

### Option 1: Claude Code Plugin (Recommended)

**Step 1:** Open Claude Code and in the chat interface, type:
```bash
/plugin marketplace add video-db/skills
```
Wait for this to complete, then continue to Step 2.

**Step 2:** In the Claude Code chat, type:
```bash
/plugin install videodb@videodb-skills
```

### Option 2: npx (Universal AI Agents)

Install for multiple AI coding assistants (Claude Code, Cursor, Copilot, etc.):

```bash
# Recommended: run from your home directory
cd ~ && npx skills add video-db/skills
```

> This installs to `~/.agents/skills/videodb` (when run from home directory) and creates symlinks for supported agents.

---

## 🚀 Quick Start

### Step 1: Get your VideoDB API key

Sign up for a free account and get your API key:

<div align="center">

### 👉 **[Get your free API key at console.videodb.io](https://console.videodb.io)**

*50 free uploads • No credit card required*

</div>

Copy your API key - you'll need it in the next step.

### Step 2: Set up the environment

Open Claude Code and **in the chat interface**, type:

```bash
/videodb setup
```

Claude will:
- 🔑 Prompt you for your API key (stored at `~/.videodb/.env`)
- 📦 Install the SDK (see installation options below)
- ✅ Verify your connection to VideoDB

**Installation Options:**
```bash
# Option 1: Full installation with capture support (macOS, Windows)
pip install "videodb[capture]>=0.4.0"

# Option 2: Core SDK only (Linux, or if capture not needed)
pip install "videodb>=0.4.0"
```

> **Note**: The `[capture]` extra includes real-time screen/audio capture dependencies that may fail on some Linux distributions. Use the core SDK if you don't need capture features or encounter installation issues.

> **Note:** The `/videodb` command is typed in Claude Code's chat interface, not in your terminal.

### Step 3: Start using it

```bash
/videodb upload https://www.youtube.com/watch?v=VIDEO_ID and give me a transcript
```

You can also just describe what you want — Claude will load the skill automatically when the task involves video processing.

### 💡 Example Commands

```bash
# Search inside videos
/videodb search for "product demo" in my latest video
```

```bash
# Add styled subtitles
/videodb add subtitles to my video with white text on black background
```

```bash
# Create compilations
/videodb take clips from 10s-30s and 45s-60s, add a title card, and combine them
```

```bash
# Generate and add music
/videodb generate 30 seconds of background music and overlay it on my video
```

```bash
# Real-time capture
/videodb capture my screen and transcribe it in real-time
```

```bash
# Meeting recording
/videodb record my next meeting and summarize it with action items
```

---

## 🌐 Using with Claude Web (claude.ai)

You can use VideoDB with Claude on the web by giving it the SDK reference as project context.

### Setup

1. Create a new [Claude Project](https://claude.ai)
2. In the project knowledge, add the contents of these files:
   - [`python/SKILL.md`](./python/SKILL.md) — core SDK reference and quick-start patterns
   - [`python/reference/api-reference.md`](./python/reference/api-reference.md) — full API reference
3. Set the project system prompt to:

```
You are a video processing assistant using the VideoDB Python SDK.
Use the provided reference documentation to write correct Python code.
Always set VIDEO_DB_API_KEY as an environment variable before calling videodb.connect().
```

### Usage

Ask Claude to write Python scripts for your video tasks:

- *"Write a script that uploads this YouTube video and generates a transcript: https://www.youtube.com/watch?v=VIDEO_ID"*
- *"Create a script that searches for 'product launch' in a video and compiles the matching clips."*
- *"Build a timeline that combines three video clips with a title overlay and background music."*

Claude will generate standalone Python scripts you can run locally with:

```bash
VIDEO_DB_API_KEY=your-key python your_script.py  # or `python3` if `python` is not available
```

---

## 🔌 Using with the Claude API

Use the VideoDB skill as a system prompt for programmatic access via the [Anthropic SDK](https://docs.anthropic.com/en/api/getting-started).

### Setup

1. Read `python/SKILL.md` and `python/reference/api-reference.md` into your system prompt
2. Send user messages describing video tasks
3. Execute the generated Python code in your environment

### Example

```python
import anthropic

# Load the skill reference as system context
with open("python/SKILL.md") as f:
    skill_context = f.read()
with open("python/reference/api-reference.md") as f:
    reference_context = f.read()

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=f"""You are a video processing assistant using the VideoDB Python SDK.
Write correct, runnable Python code based on user requests.

{skill_context}

{reference_context}""",
    messages=[
        {
            "role": "user",
            "content": "Upload this YouTube video and search for mentions of 'AI': https://www.youtube.com/watch?v=VIDEO_ID"
        }
    ],
)

print(message.content[0].text)
```

### Tips

- Include `python/reference/search.md` or `python/reference/editor.md` in the system prompt when your use case focuses on search or editing
- Add `python/reference/capture.md` when your use case involves real-time screen/audio capture
- For token efficiency, use only `python/SKILL.md` for general tasks — it covers the most common operations
- Add `python/reference/generative.md` when you need AI-generated media (images, music, voice)

---

## 📁 Project Structure

```
video-db/skills/
├── .claude-plugin/
│   ├── marketplace.json              # Marketplace listing metadata
│   └── plugin.json                   # Plugin manifest
├── README.md
└── python/
    ├── SKILL.md                      # Skill definition (loaded by Claude Code)
    ├── requirements.txt              # Python dependencies
    ├── .env.example                  # Environment variable template
    ├── reference/
    │   ├── api-reference.md          # Complete API reference
    │   ├── search.md                 # Search and indexing guide
    │   ├── editor.md                 # Timeline editing guide
    │   ├── generative.md             # AI generation guide
    │   ├── meetings.md               # Meeting recording and analysis
    │   ├── rtstream.md               # Real-time streaming guide
    │   ├── capture.md                # Real-time capture architecture guide
    │   └── use-cases.md              # End-to-end workflow examples
    └── scripts/
        ├── env_loader.py             # Environment loader utility
        ├── setup_venv.py             # Virtual environment setup
        ├── setup.py                  # Dependency checker
        ├── check_connection.py       # API key verification
        ├── batch_upload.py           # Bulk upload from URL list or directory
        ├── search_and_compile.py     # Search + compile into stream
        ├── extract_clips.py          # Extract clips by timestamp
        ├── backend.py                # Capture backend (Flask server with WebSocket)
        ├── client.py                 # Capture client (screen + audio recording)
        ├── test_editor.py            # Integration test: timeline editing
        ├── test_meetings.py          # Integration test: meeting analysis
        └── test_rtstream.py          # Integration test: streaming
```

---

## 📖 Documentation

| Guide | What's Inside |
|---|---|
| [SKILL.md](./python/SKILL.md) | Skill definition and quick reference |
| [api-reference.md](./python/reference/api-reference.md) | Complete API reference for all objects and methods |
| [search.md](./python/reference/search.md) | Semantic, keyword, and scene-based search |
| [editor.md](./python/reference/editor.md) | Timeline editing with overlays, limitations |
| [generative.md](./python/reference/generative.md) | AI-generated images, video, music, voice, and text |
| [meetings.md](./python/reference/meetings.md) | Meeting recording, transcription, and analysis |
| [rtstream.md](./python/reference/rtstream.md) | Real-time HLS streaming |
| [capture.md](./python/reference/capture.md) | Real-time capture architecture and AI pipelines |
| [use-cases.md](./python/reference/use-cases.md) | End-to-end workflow examples |

---

## 🎥 Real-Time Capture

The plugin includes a ready-to-run capture setup powered by the [VideoDB Capture SDK](https://github.com/video-db/videodb-capture-quickstart). It uses a two-process model:

- **`python/scripts/backend.py`** — Flask server that creates capture sessions, handles webhook events via WebSocket, and starts AI pipelines (transcription, audio indexing, visual indexing)
- **`python/scripts/client.py`** — Captures screen, mic, and system audio using `CaptureClient` and streams to VideoDB for real-time processing

### Quick start

> **Note:** For manual clone users. Plugin users should use `/videodb` commands in Claude Code instead.

**Manual clone setup:**
```bash
# Terminal 1: start the backend
python python/scripts/backend.py

# Terminal 2: start the client
python python/scripts/client.py
```

The backend starts a Flask server for webhook handling. For webhooks to work, you'll need to expose the backend publicly (using ngrok, CloudFlare tunnel, or deploying on a server). The client requests device permissions, discovers channels, and begins streaming. Press Enter in the client terminal to stop recording.

See [capture.md](./python/reference/capture.md) for the full architecture guide, AI pipeline setup, and webhook event handling.

---

## 🛠️ Utility Scripts

> **Note:** These commands are for advanced users who manually cloned the repository. Most users should use Claude Code commands (e.g., `/videodb upload ...`) instead.

**For manual clone users only** - Run these from the cloned repository directory:

```bash
# Upload multiple files from a URL list
python python/scripts/batch_upload.py --urls urls.txt --collection "My Project"

# Search inside a video and compile results
python python/scripts/search_and_compile.py --video-id VIDEO_ID --query "product demo"

# Extract clips by timestamp ranges
python python/scripts/extract_clips.py --video-id VIDEO_ID --timestamps "10.0-25.0,45.0-60.0"

# Start the capture backend (Flask server)
python python/scripts/backend.py

# Start the capture client (screen + audio recording)
python python/scripts/client.py
```

---

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This plugin is provided as-is for use with Claude. The VideoDB SDK is governed by its own [license](https://github.com/video-db/videodb-python/blob/main/LICENSE).

---

## 💬 Community & Support

- **VideoDB SDK Issues:** [github.com/video-db/videodb-python/issues](https://github.com/video-db/videodb-python/issues)
- **VideoDB Capture Issues:** [github.com/video-db/videodb-capture-quickstart/issues](https://github.com/video-db/videodb-capture-quickstart/issues)
- **Documentation:** [docs.videodb.io](https://docs.videodb.io)
- **Discord:** [Join our community](https://discord.gg/py9P639jGz)

---

<div align="center">

Made with ❤️ by the VideoDB team

</div>
