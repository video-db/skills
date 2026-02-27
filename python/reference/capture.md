# Capture Architecture Guide

## Overview

VideoDB Capture enables real-time screen and audio recording with AI processing.

**IMPORTANT:** Use `/usr/bin/python3` (system Python 3.9+) instead of conda/anaconda Python for capture.

## Quick Start (Recommended)

### Background Recording with `capture_bg.py`

Best for CLI/agent use — runs in background with file-based stop control:

**Start recording:**
```bash
export VIDEO_DB_API_KEY=<key>
/usr/bin/python3 scripts/capture_bg.py start &
```

**Check status:**
```bash
cat /tmp/videodb_capture_state.json
```

**Stop recording:**
```bash
touch /tmp/videodb_capture_stop
```

**Get shareable link:** After stopping, read `/tmp/videodb_capture_state.json` for `player_url`.

## Other Approaches

1. **Interactive** (`capture.py`) — Waits for Enter key to stop (requires terminal)
2. **Two-process** (`backend.py` + `client.py`) — Separate backend for AI pipelines

All use **WebSocket polling** instead of webhooks, so no external tunnel (Cloudflare, ngrok) is required.

```
┌─────────────┐     WebSocket (AI results)    ┌──────────────┐
│   VideoDB    │ ─────────────────────────────> │   Backend    │
│   Cloud      │ <───────────────────────────── │   (Python)   │
└─────────────┘     API calls + polling        └──────────────┘
       ^                                              ^
       │                                              │
       │  streams                                     │  HTTP
       │                                              │
┌─────────────┐                                ┌──────────────┐
│   Capture    │                                │   Client     │
│   Client     │                                │   App        │
└─────────────┘                                └──────────────┘
```

## Quick Start

### Option 1: Single Process (Recommended)

The simplest approach — one script handles everything:

```bash
python scripts/capture.py
```

This will:
1. Create a capture session
2. Request microphone and screen permissions
3. Start recording
4. Run AI pipelines (transcription, visual indexing)
5. Export to a shareable video when you press Enter

### Option 2: Two Process

For more control, run backend and client separately:

**Terminal 1 — Backend:**
```bash
python scripts/backend.py
```

**Terminal 2 — Client:**
```bash
python scripts/client.py
```

## Quick Reference

### Create a Capture Session

```python
# No callback_url needed — we poll instead
session = conn.create_capture_session(
    end_user_id="user-123",
    collection_id="default",
    metadata={"app": "my-app"},
)
print(f"Session ID: {session.id}")
```

### Generate a Client Token

```python
token = conn.generate_client_token()
```

### Start the Capture Client

```python
from videodb.capture import CaptureClient

client = CaptureClient(client_token=token)
```

### Request Permissions

```python
await client.request_permission("microphone")
await client.request_permission("screen_capture")
```

### List Available Channels

```python
channels = await client.list_channels()
for ch in channels.all():
    print(f"  {ch.id} ({ch.type}): {ch.name}")

mic = channels.mics.default
display = channels.displays.default
system_audio = channels.system_audio.default
```

### Enable Storage (Persist Recording)

```python
# store=True saves the recording to VideoDB after capture stops
mic.store = True
display.store = True
system_audio.store = True
```

Without `store = True`, streams are processed in real-time but not saved.

### Start a Session

```python
selected_channels = [c for c in [mic, display, system_audio] if c]
await client.start_session(
    capture_session_id=session.id,
    channels=selected_channels,
    primary_video_channel_id=display.id if display else None,
)
```

### Stop a Session

```python
await client.stop_session()
await client.shutdown()
```

## Backend Setup (WebSocket Polling)

### Local Flask Server (No Tunnel Required)

```python
from flask import Flask, jsonify
from pathlib import Path
import videodb
import threading
import time

app = Flask(__name__)
conn = videodb.connect()
active_sessions = {}

@app.route("/init-session", methods=["POST"])
def init_session():
    # Create session without callback_url
    session = conn.create_capture_session(
        end_user_id="user-123",
        collection_id="default",
        metadata={"app": "my-app"},
    )
    token = conn.generate_client_token()

    # Start background polling for this session
    threading.Thread(
        target=poll_and_start_ai,
        args=(session.id,),
        daemon=True
    ).start()

    return jsonify({
        "session_id": session.id,
        "token": token,
    })
```

### Polling for Session Status

Instead of webhooks, poll the session status:

```python
def poll_and_start_ai(session_id):
    """Poll session status and start AI pipelines when active."""
    max_wait = 60  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            session = conn.get_capture_session(session_id)

            if session.status == "active" and session_id not in active_sessions:
                active_sessions[session_id] = True
                start_ai_pipelines(session)
                break

            elif session.status in ["stopped", "exported"]:
                handle_session_end(session)
                break

        except Exception:
            pass  # Session might not be ready yet

        time.sleep(1)
```

### Retrieve RTStreams

```python
session = conn.get_capture_session(session_id)

mics = session.get_rtstream("mic")
displays = session.get_rtstream("screen")
system_audios = session.get_rtstream("system_audio")
```

### Session States

| Status | Description |
|--------|-------------|
| `created` | Session created, waiting for client |
| `active` | Client streaming, start AI pipelines |
| `stopping` | Stop requested, finalizing streams |
| `stopped` | All streams finalized |
| `exported` | Recording exported to video |

## Client Setup

### CaptureClient Initialization

```python
import asyncio
from videodb.capture import CaptureClient

client = CaptureClient(client_token=token)
```

### Requesting Permissions

The client must request permissions before discovering channels:

```python
await client.request_permission("microphone")
await client.request_permission("screen_capture")
```

### Discovering Channels

```python
channels = await client.list_channels()

# Access channel groups
mic = channels.mics.default
display = channels.displays.default
system_audio = channels.system_audio.default

# List all available channels
for ch in channels.all():
    print(f"  {ch.id} ({ch.type}): {ch.name}")
```

### Enabling Storage

Set `store = True` on channels to persist the recording to VideoDB after the session stops:

```python
mic.store = True
display.store = True
system_audio.store = True
```

Without `store = True`, streams are processed in real-time but not saved.

### Starting the Session

```python
selected_channels = [c for c in [mic, display, system_audio] if c]
await client.start_session(
    capture_session_id=session_id,
    channels=selected_channels,
    primary_video_channel_id=display.id if display else None,
)
```

### Stopping the Session

```python
await client.stop_session()
await client.shutdown()
```

## AI Pipelines

AI pipelines run on the backend and process live streams. They require a WebSocket connection ID to stream results back in real-time.

### Setting Up a WebSocket Listener

```python
import queue
import threading
import asyncio

def start_ws_listener(ws_id_queue, name="Listener"):
    def run():
        async def listen():
            ws_wrapper = conn.connect_websocket()
            ws = await ws_wrapper.connect()
            ws_id = ws.connection_id
            ws_id_queue.put(ws_id)

            async for msg in ws.receive():
                channel = msg.get("channel")
                data = msg.get("data", {})
                text = data.get("text", "")

                if channel == "transcript" and text.strip():
                    print(f"[{name}] {text}")
                elif channel == "audio_index" and text.strip():
                    print(f"[{name}] Audio Index: {text}")
                elif channel in ["scene_index", "visual_index"] and text.strip():
                    print(f"[{name}] Visual Index: {text}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t
```

### Transcription Pipeline

Start live transcription on an audio RTStream:

```python
q = queue.Queue()
start_ws_listener(q, name="TranscriptWatcher")
ws_id = q.get(timeout=10)

rtstream.start_transcript(ws_connection_id=ws_id)
```

Results arrive on the `transcript` WebSocket channel.

### Audio Indexing Pipeline

Generate LLM summaries of audio content at fixed intervals:

```python
q = queue.Queue()
start_ws_listener(q, name="AudioIndexWatcher")
ws_id = q.get(timeout=10)

rtstream.index_audio(
    prompt="Summarize what is being discussed",
    ws_connection_id=ws_id,
    batch_config={"type": "time", "value": 30},
)
```

Results arrive on the `audio_index` WebSocket channel.

### Visual Indexing Pipeline

Generate AI descriptions of screen content:

```python
q = queue.Queue()
start_ws_listener(q, name="VisualWatcher")
ws_id = q.get(timeout=10)

rtstream.index_visuals(
    prompt="Describe what is happening on screen",
    ws_connection_id=ws_id,
)
```

Results arrive on the `scene_index` or `visual_index` WebSocket channel.

## Session Lifecycle

A capture session follows this lifecycle:

```
  create_capture_session()
          │
          v
  ┌───────────────┐
  │    created     │
  └───────┬───────┘
          │  client.start_session()
          v
  ┌───────────────┐     poll: status == "active"
  │    active      │ ──> Start AI pipelines
  └───────┬───────┘
          │  client.stop_session()
          v
  ┌───────────────┐     poll: status == "stopping"
  │   stopping     │ ──> Finalize streams
  └───────┬───────┘
          │
          v
  ┌───────────────┐     poll: status == "stopped"
  │   stopped      │ ──> All streams finalized
  └───────┬───────┘
          │  (if store=True)
          v
  ┌───────────────┐     poll: status == "exported"
  │   exported     │ ──> Access video_id, stream_url, player_url
  └───────────────┘
```

## Batch Config Options

The `batch_config` parameter controls how audio and visual indexing segments content:

| Key | Type | Values | Description |
|-----|------|--------|-------------|
| `type` | `str` | `"time"` | Segmentation strategy |
| `value` | `int` | seconds (e.g., `30`) | Interval for each batch |

Example: `{"type": "time", "value": 30}` processes audio in 30-second chunks.

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/capture_bg.py` | **Background capture with file-based stop (recommended)** |
| `scripts/capture.py` | Interactive capture (waits for Enter key) |
| `scripts/backend.py` | Backend server with AI pipelines |
| `scripts/client.py` | Capture client (connects to backend) |
