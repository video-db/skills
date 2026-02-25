# VideoDB Skills

Talk to your videos using natural language. Upload, search, edit, generate subtitles, create clips, and more.

> Built on the [VideoDB Python SDK](https://github.com/video-db/videodb-python) and [VideoDB Capture SDK](https://github.com/video-db/videodb-capture-quickstart) | Works with **Claude Code**, **Claude Web**, and the **Claude API**

---

## What You Can Do

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

## Prerequisites

- **Python 3.9+**
- **Claude Code** (for plugin usage) or any Claude interface
- **VideoDB API key** — sign up free at [console.videodb.io](https://console.videodb.io) (50 free uploads, no credit card)

---

## Installation

### Option 1: Claude Code Plugin (Recommended)

**Step 1:** Add the marketplace (run this first and wait for it to complete):
```
/plugin marketplace add video-db/skills
```

**Step 2:** Install the plugin (run this after step 1 succeeds):
```
/plugin install videodb@videodb-skills
```

### Option 2: Manual Clone

```bash
git clone https://github.com/video-db/skills.git
```

---

## Quick Start

### 1. Get your VideoDB API key

Sign up free at [console.videodb.io](https://console.videodb.io) (50 free uploads, no credit card required). Copy your API key from the dashboard.

### 2. Add your API key

Create a central config directory and add your API key:

```bash
mkdir -p ~/.videodb
echo "VIDEO_DB_API_KEY={YOUR_API_KEY_HERE}" > ~/.videodb/.env
```

Replace `{YOUR_API_KEY_HERE}` with your actual VideoDB API key (e.g., `vdb_xxxxx...`).

> **Note:** This central location (`~/.videodb/.env`) works for both plugin installations and manual clones. You can also set the `VIDEO_DB_API_KEY` environment variable in your shell profile, or create a local `.env` file in the skill directory.

### 3. Set up the Python environment

In Claude Code, run:

```
/videodb setup the virtual environment
```

This creates the virtual environment and installs all dependencies.

### 4. Verify the connection

In Claude Code, run:

```
/videodb check the connection to VideoDB
```

This confirms your API key is valid and the SDK can connect to VideoDB.

### 5. Start using it

```
/videodb upload https://www.youtube.com/watch?v=VIDEO_ID and give me a transcript
```

You can also just describe what you want — Claude will load the skill automatically when the task involves video processing.

**More examples:**

```
/videodb search for "product demo" in my latest video
```

```
/videodb add subtitles to my video with white text on black background
```

```
/videodb take clips from 10s-30s and 45s-60s, add a title card, and combine them
```

```
/videodb generate 30 seconds of background music and overlay it on my video
```

```
/videodb capture my screen and transcribe it in real-time
```

```
/videodb record my next meeting and summarize it with action items
```

---

## Using with Claude Web (claude.ai)

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
Always use `from dotenv import load_dotenv; load_dotenv()` before `videodb.connect()`.
```

### Usage

Ask Claude to write Python scripts for your video tasks:

- *"Write a script that uploads this YouTube video and generates a transcript: https://www.youtube.com/watch?v=VIDEO_ID"*
- *"Create a script that searches for 'product launch' in a video and compiles the matching clips."*
- *"Build a timeline that combines three video clips with a title overlay and background music."*

Claude will generate standalone Python scripts you can run locally with:

```bash
# If you have a venv setup (manual clone):
python/.venv/bin/python your_script.py

# Or use system Python:
python3 your_script.py
```

---

## Using with the Claude API

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

## Project Structure

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
        ├── backend.py                # Capture backend (Flask + Cloudflare tunnel)
        ├── client.py                 # Capture client (screen + audio recording)
        ├── test_editor.py            # Integration test: timeline editing
        ├── test_meetings.py          # Integration test: meeting analysis
        └── test_rtstream.py          # Integration test: streaming
```

---

## Documentation

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

## Real-Time Capture

The plugin includes a ready-to-run capture setup powered by the [VideoDB Capture SDK](https://github.com/video-db/videodb-capture-quickstart). It uses a two-process model:

- **`python/scripts/backend.py`** — Flask server with a Cloudflare tunnel that creates capture sessions, handles webhook events, and starts AI pipelines (transcription, audio indexing, visual indexing)
- **`python/scripts/client.py`** — Captures screen, mic, and system audio using `CaptureClient` and streams to VideoDB for real-time processing

### Quick start

> **Note:** For manual clone users. Plugin users should use `/videodb` commands in Claude Code instead.

**Manual clone setup:**
```bash
# Terminal 1: start the backend
python/.venv/bin/python python/scripts/backend.py

# Terminal 2: start the client
python/.venv/bin/python python/scripts/client.py
```

The backend automatically creates a Cloudflare tunnel for the webhook URL. The client requests device permissions, discovers channels, and begins streaming. Press Enter in the client terminal to stop recording.

See [capture.md](./python/reference/capture.md) for the full architecture guide, AI pipeline setup, and webhook event handling.

---

## Utility Scripts

> **Note:** These commands are for advanced users who manually cloned the repository. Most users should use Claude Code commands (e.g., `/videodb upload ...`) instead.

**For manual clone users only** - Run these from the cloned repository directory:

```bash
# Upload multiple files from a URL list
python/.venv/bin/python python/scripts/batch_upload.py --urls urls.txt --collection "My Project"

# Search inside a video and compile results
python/.venv/bin/python python/scripts/search_and_compile.py --video-id VIDEO_ID --query "product demo"

# Extract clips by timestamp ranges
python/.venv/bin/python python/scripts/extract_clips.py --video-id VIDEO_ID --timestamps "10.0-25.0,45.0-60.0"

# Start the capture backend (Flask + Cloudflare tunnel)
python/.venv/bin/python python/scripts/backend.py

# Start the capture client (screen + audio recording)
python/.venv/bin/python python/scripts/client.py
```

---

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

This plugin is provided as-is for use with Claude. The VideoDB SDK is governed by its own [license](https://github.com/video-db/videodb-python/blob/main/LICENSE).
