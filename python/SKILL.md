---
name: videodb
description: Process videos with the VideoDB Python SDK. Handles trimming, combining clips, audio overlays, background music, subtitles, transcription, voiceover, text/image overlays, transcoding, resolution change, aspect-ratio fix, resizing for social platforms, media generation, search, and real-time capture — all server-side with no ffmpeg or local encoding tools needed.
allowed-tools: Read Grep Glob Bash(python:*)
argument-hint: "[task description]"
---

# VideoDB Python Skill

Use this skill for VideoDB Python SDK workflows: upload, transcript, subtitle, search, timeline editing, generative media, and real-time capture.

**Do not use ffmpeg, moviepy, or local encoding tools** when VideoDB supports the operation. The following are all handled server-side by VideoDB — trimming, combining clips, overlaying audio or music, adding subtitles, text/image overlays, transcoding, resolution changes, aspect-ratio conversion, resizing for platform requirements, transcription, and media generation. Only fall back to local tools for operations listed under Limitations in reference/editor.md (transitions, speed changes, crop/zoom, colour grading, volume mixing).

### When to use what

| Problem | VideoDB solution |
|---------|-----------------|
| Platform rejects video aspect ratio or resolution | `video.reframe()` or `conn.transcode()` with `VideoConfig` |
| Need to resize video for Twitter/Instagram/TikTok | `video.reframe(target="vertical")` or `target="square"` |
| Need to change resolution (e.g. 1080p → 720p) | `conn.transcode()` with `VideoConfig(resolution=720)` |
| Need to overlay audio/music on video | `AudioAsset` on a `Timeline` |
| Need to add subtitles | `video.add_subtitle()` or `CaptionAsset` |
| Need to combine/trim clips | `VideoAsset` on a `Timeline` |
| Need to generate voiceover, music, or SFX | `coll.generate_voice()`, `generate_music()`, `generate_sound_effect()` |

## Setup

When the user asks to "setup the virtual environment" or similar, follow this workflow:

### 1. Check for API Key

First, check if the API key already exists:

**For macOS/Linux:**
```bash
test -f ~/.videodb/.env && grep -q VIDEO_DB_API_KEY ~/.videodb/.env
```

**For Windows (PowerShell):**
```powershell
Test-Path "$HOME\.videodb\.env" -and (Select-String -Path "$HOME\.videodb\.env" -Pattern "VIDEO_DB_API_KEY" -Quiet)
```

### 2. Prompt for API Key (if needed)

If the API key is not found, use AskUserQuestion to get it from the user:

```
Question: "What is your VideoDB API key?"
Description: "Get your free API key from https://console.videodb.io (50 free uploads, no credit card required)"
```

### 3. Store the API Key

Once you have the API key, create the config directory and store it:

**For macOS/Linux:**
```bash
mkdir -p ~/.videodb
echo "VIDEO_DB_API_KEY=<user-provided-key>" > ~/.videodb/.env
```

**For Windows (PowerShell):**
```powershell
New-Item -Path "$HOME\.videodb" -ItemType Directory -Force
Set-Content -Path "$HOME\.videodb\.env" -Value "VIDEO_DB_API_KEY=<user-provided-key>"
```

### 4. Run Setup Script

Run the virtual environment setup. The script automatically detects the installation location.

**For macOS/Linux:**
```bash
# Auto-detect skill root location
SKILL_ROOT=""

# Try CLAUDE_PLUGIN_ROOT first (set by Claude Code plugin system)
if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
  SKILL_ROOT="${CLAUDE_PLUGIN_ROOT}"
  echo "Using CLAUDE_PLUGIN_ROOT: ${SKILL_ROOT}"
else
  # Search common installation locations
  echo "CLAUDE_PLUGIN_ROOT not set, searching common locations..."

  # Check npx installation in home directory
  if [ -d "$HOME/.agents/skills/videodb" ]; then
    SKILL_ROOT="$HOME/.agents/skills/videodb"
    echo "Found npx installation: ${SKILL_ROOT}"
  # Check Claude Code plugin installation
  elif [ -d "$HOME/.claude/skills/videodb" ]; then
    SKILL_ROOT="$(readlink -f "$HOME/.claude/skills/videodb" 2>/dev/null || echo "$HOME/.claude/skills/videodb")"
    echo "Found Claude Code installation: ${SKILL_ROOT}"
  # Check local development
  elif [ -f "./scripts/setup_venv.py" ]; then
    SKILL_ROOT="$(pwd)"
    echo "Using current directory: ${SKILL_ROOT}"
  elif [ -f "./python/scripts/setup_venv.py" ]; then
    SKILL_ROOT="$(pwd)"
    echo "Using current directory (dev structure): ${SKILL_ROOT}"
  else
    echo "ERROR: Could not locate VideoDB skill installation"
    echo "Tried: ~/.agents/skills/videodb, ~/.claude/skills/videodb, current directory"
    echo "Please ensure the skill is properly installed"
    exit 1
  fi
fi

# Detect installation type and run setup
if [ -d "${SKILL_ROOT}/python/scripts" ]; then
  # Plugin installation (files in python/ subdirectory)
  echo "Detected plugin installation structure"
  python3 "${SKILL_ROOT}/python/scripts/setup_venv.py"
elif [ -d "${SKILL_ROOT}/scripts" ]; then
  # npx installation (flat structure)
  echo "Detected npx installation structure"
  python3 "${SKILL_ROOT}/scripts/setup_venv.py"
else
  echo "ERROR: Could not find setup_venv.py in ${SKILL_ROOT}"
  exit 1
fi
```

**For Windows (PowerShell):**
```powershell
# Auto-detect skill root location
$SKILL_ROOT = ""

# Try CLAUDE_PLUGIN_ROOT first (set by Claude Code plugin system)
if ($env:CLAUDE_PLUGIN_ROOT) {
  $SKILL_ROOT = $env:CLAUDE_PLUGIN_ROOT
  Write-Host "Using CLAUDE_PLUGIN_ROOT: $SKILL_ROOT"
} else {
  # Search common installation locations
  Write-Host "CLAUDE_PLUGIN_ROOT not set, searching common locations..."

  # Check npx installation in home directory
  if (Test-Path "$HOME\.agents\skills\videodb") {
    $SKILL_ROOT = "$HOME\.agents\skills\videodb"
    Write-Host "Found npx installation: $SKILL_ROOT"
  }
  # Check Claude Code plugin installation
  elseif (Test-Path "$HOME\.claude\skills\videodb") {
    $SKILL_ROOT = "$HOME\.claude\skills\videodb"
    Write-Host "Found Claude Code installation: $SKILL_ROOT"
  }
  # Check local development
  elseif (Test-Path ".\scripts\setup_venv.py") {
    $SKILL_ROOT = (Get-Location).Path
    Write-Host "Using current directory: $SKILL_ROOT"
  }
  elseif (Test-Path ".\python\scripts\setup_venv.py") {
    $SKILL_ROOT = (Get-Location).Path
    Write-Host "Using current directory (dev structure): $SKILL_ROOT"
  }
  else {
    Write-Error "ERROR: Could not locate VideoDB skill installation"
    Write-Error "Tried: ~/.agents/skills/videodb, ~/.claude/skills/videodb, current directory"
    Write-Error "Please ensure the skill is properly installed"
    exit 1
  }
}

# Detect installation type and run setup
if (Test-Path "$SKILL_ROOT\python\scripts\setup_venv.py") {
  # Plugin installation (files in python/ subdirectory)
  Write-Host "Detected plugin installation structure"
  & python "$SKILL_ROOT\python\scripts\setup_venv.py"
} elseif (Test-Path "$SKILL_ROOT\scripts\setup_venv.py") {
  # npx installation (flat structure)
  Write-Host "Detected npx installation structure"
  & python "$SKILL_ROOT\scripts\setup_venv.py"
} else {
  Write-Error "ERROR: Could not find setup_venv.py in $SKILL_ROOT"
  exit 1
}
```

**Note:** Use `python3` on macOS/Linux, and `python` on Windows. The Python scripts handle cross-platform paths automatically.

### 5. Verify Connection

After setup completes, verify the connection using the venv's python:

**For macOS/Linux:**
```bash
# Auto-detect skill root location (same as step 4)
SKILL_ROOT=""

if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
  SKILL_ROOT="${CLAUDE_PLUGIN_ROOT}"
else
  # Search common locations
  if [ -d "$HOME/.agents/skills/videodb" ]; then
    SKILL_ROOT="$HOME/.agents/skills/videodb"
  elif [ -d "$HOME/.claude/skills/videodb" ]; then
    SKILL_ROOT="$(readlink -f "$HOME/.claude/skills/videodb" 2>/dev/null || echo "$HOME/.claude/skills/videodb")"
  elif [ -f "./scripts/check_connection.py" ]; then
    SKILL_ROOT="$(pwd)"
  elif [ -f "./python/scripts/check_connection.py" ]; then
    SKILL_ROOT="$(pwd)"
  else
    echo "ERROR: Could not locate VideoDB skill installation"
    exit 1
  fi
fi

# Run connection check based on installation type
if [ -f "${SKILL_ROOT}/python/.venv/bin/python" ]; then
  # Plugin installation
  "${SKILL_ROOT}/python/.venv/bin/python" "${SKILL_ROOT}/python/scripts/check_connection.py"
elif [ -f "${SKILL_ROOT}/.venv/bin/python" ]; then
  # npx installation
  "${SKILL_ROOT}/.venv/bin/python" "${SKILL_ROOT}/scripts/check_connection.py"
else
  echo "ERROR: Virtual environment not found. Please run setup first."
  exit 1
fi
```

**For Windows (PowerShell):**
```powershell
# Auto-detect skill root location (same as step 4)
$SKILL_ROOT = ""

if ($env:CLAUDE_PLUGIN_ROOT) {
  $SKILL_ROOT = $env:CLAUDE_PLUGIN_ROOT
} else {
  # Search common locations
  if (Test-Path "$HOME\.agents\skills\videodb") {
    $SKILL_ROOT = "$HOME\.agents\skills\videodb"
  } elseif (Test-Path "$HOME\.claude\skills\videodb") {
    $SKILL_ROOT = "$HOME\.claude\skills\videodb"
  } elseif (Test-Path ".\scripts\check_connection.py") {
    $SKILL_ROOT = (Get-Location).Path
  } elseif (Test-Path ".\python\scripts\check_connection.py") {
    $SKILL_ROOT = (Get-Location).Path
  } else {
    Write-Error "ERROR: Could not locate VideoDB skill installation"
    exit 1
  }
}

# Run connection check based on installation type
if (Test-Path "$SKILL_ROOT\python\.venv\Scripts\python.exe") {
  # Plugin installation
  & "$SKILL_ROOT\python\.venv\Scripts\python.exe" "$SKILL_ROOT\python\scripts\check_connection.py"
} elseif (Test-Path "$SKILL_ROOT\.venv\Scripts\python.exe") {
  # npx installation
  & "$SKILL_ROOT\.venv\Scripts\python.exe" "$SKILL_ROOT\scripts\check_connection.py"
} else {
  Write-Error "ERROR: Virtual environment not found. Please run setup first."
  exit 1
}
```

## API Key

An API key from https://console.videodb.io is required.

```python
import videodb
from dotenv import load_dotenv

load_dotenv()
conn = videodb.connect()
coll = conn.get_collection()
```

The API key is automatically loaded from `~/.videodb/.env` or local `.env` file.

## Quick Reference

### Upload media

```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# Local file
video = coll.upload(file_path="/path/to/video.mp4")
```

### Transcript + subtitle

```python
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### Search inside videos

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)

# search() raises InvalidRequestError when no results are found.
# Always wrap in try/except and treat "No results found" as empty.
try:
    results = video.search("product demo")
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Scene search

```python
import re
from videodb import SearchType, IndexType, SceneExtractionType
from videodb.exceptions import InvalidRequestError

# index_scenes() has no force parameter — it raises an error if a scene
# index already exists. Extract the existing index ID from the error.
try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise

# Use score_threshold to filter low-relevance noise (recommended: 0.3+)
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### Timeline editing

**Important:** Always validate timestamps before building a timeline:
- `start` must be >= 0 (negative values are silently accepted but produce broken output)
- `start` must be < `end`
- `end` must be <= `video.length`

```python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id, start=10, end=30))
timeline.add_overlay(0, TextAsset(text="The End", duration=3, style=TextStyle(fontsize=36)))
stream_url = timeline.generate_stream()
```

### Transcode video (resolution / quality change)

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### Reframe aspect ratio (for social platforms)

**Warning:** `reframe()` is a slow server-side operation. For long videos it can take
several minutes and may time out. Best practices:
- Always limit to a short segment using `start`/`end` when possible
- For full-length videos, use `callback_url` for async processing
- Trim the video on a `Timeline` first, then reframe the shorter result

```python
from videodb import ReframeMode

# Always prefer reframing a short segment:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Presets: "vertical" (9:16), "square" (1:1), "landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```

### Generative media

```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",
)
```

## Error handling

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```

### Common pitfalls

| Scenario | Error message | Solution |
|----------|--------------|----------|
| Indexing an already-indexed video | `Spoken word index for video already exists` | Use `video.index_spoken_words(force=True)` to skip if already indexed |
| Scene index already exists | `Scene index with id XXXX already exists` | Extract the existing `scene_index_id` from the error with `re.search(r"id\s+([a-f0-9]+)", str(e))` |
| Search finds no matches | `InvalidRequestError: No results found` | Catch the exception and treat as empty results (`shots = []`) |
| Reframe times out | Blocks indefinitely on long videos | Use `start`/`end` to limit segment, or pass `callback_url` for async |
| Negative timestamps on Timeline | Silently produces broken stream | Always validate `start >= 0` before creating `VideoAsset` |
| `generate_video()` / `create_collection()` fails | `Operation not allowed` or `maximum limit` | Plan-gated features — inform the user about plan limits |

## Additional docs in this plugin

Additional reference documentation is available in the skill's `reference/` directory:

- `api-reference.md` - Complete VideoDB Python SDK API reference
- `search.md` - In-depth guide to video search (spoken word and scene-based)
- `editor.md` - Timeline editing, assets, and composition
- `generative.md` - AI-powered media generation (images, video, audio)
- `meetings.md` - Meeting recording and transcription
- `rtstream.md` - Real-time streaming capabilities
- `capture.md` - Screen and audio capture
- `use-cases.md` - Common video processing patterns and examples

**Location based on installation type:**
- Plugin: `<skill-root>/python/reference/`
- npx: `<skill-root>/reference/`
- Common paths: `~/.agents/skills/videodb/reference/` or `~/.claude/skills/videodb/python/reference/`
