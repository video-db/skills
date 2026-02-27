# Capture Architecture Guide

## Overview

VideoDB Capture uses a **two-process model**: a **backend** server that manages sessions and AI pipelines, and a **client** that runs on the user's machine to capture screen and audio.

```
┌─────────────┐     webhook events     ┌──────────────┐
│   VideoDB    │ ────────────────────>  │   Backend    │
│   Cloud      │ <────────────────────  │   (Flask)    │
└─────────────┘     API calls           └──────────────┘
       ^                                       ^
       │                                       │
       │  streams                              │  /init-session
       │                                       │
┌─────────────┐                         ┌──────────────┐
│   Capture    │ ──────────────────────> │   Client     │
│   Client     │     HTTP request        │   App        │
└─────────────┘                         └──────────────┘
```

**Backend** — A Flask server that creates capture sessions, handles webhook events via WebSocket, and starts AI pipelines when a session becomes active.

**Client** — A Python process using `CaptureClient` from `videodb.capture`. It requests device permissions, discovers channels, and streams audio/video to VideoDB.

## Quick Reference

### Create a Capture Session

```python
session = conn.create_capture_session(
    end_user_id="user-123",
    collection_id="default",
    callback_url="https://your-server.com/webhook",
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

## Backend Setup

### Flask Server for Webhook Handling

```python
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
import videodb
import os

# Load API key from ~/.videodb/.env
load_dotenv(Path.home() / ".videodb" / ".env")

app = Flask(__name__)
conn = videodb.connect()

# Configure webhook URL (must be publicly accessible)
# Use ngrok, CloudFlare tunnel, or deploy on a server
PORT = 5002
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"http://localhost:{PORT}/webhook")
```

### Session Initialization Endpoint

```python
@app.route("/init-session", methods=["POST"])
def init_session():
    session = conn.create_capture_session(
        end_user_id="user-123",
        collection_id="default",
        callback_url=WEBHOOK_URL,
        metadata={"app": "my-app"},
    )
    token = conn.generate_client_token()
    return jsonify({
        "session_id": session.id,
        "token": token,
        "webhook_url": WEBHOOK_URL,
    })
```

### Webhook Handler

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = data.get("event")

    if event == "capture_session.active":
        # Session is streaming -- start AI pipelines
        session = conn.get_capture_session(data["capture_session_id"])
        start_ai_pipelines(session)

    elif event == "capture_session.stopping":
        print("Session stopping...")

    elif event == "capture_session.stopped":
        print("Session stopped. All streams finalized.")

    elif event == "capture_session.exported":
        export_data = data.get("data", {})
        video_id = export_data.get("exported_video_id")
        stream_url = export_data.get("stream_url")
        print(f"Exported! Video ID: {video_id}, Stream: {stream_url}")

    return jsonify({"received": True})
```

### Retrieve Session in Webhook

```python
session = conn.get_capture_session(capture_session_id)

mics = session.get_rtstream("mic")
displays = session.get_rtstream("screen")
system_audios = session.get_rtstream("system_audio")
```

### Webhook Events

| Event | When | Action |
|-------|------|--------|
| `capture_session.active` | Session starts streaming | Start AI pipelines (transcription, indexing) |
| `capture_session.stopping` | Stop requested | Finalize streams |
| `capture_session.stopped` | All streams finalized | Cleanup resources |
| `capture_session.exported` | Recording exported to video | Access `exported_video_id`, `stream_url`, `player_url` |

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
    prompt="In one sentence, describe what is on screen",
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
  ┌───────────────┐     webhook: capture_session.active
  │    active      │ ──> Start AI pipelines
  └───────┬───────┘
          │  client.stop_session()
          v
  ┌───────────────┐     webhook: capture_session.stopping
  │   stopping     │ ──> Finalize streams
  └───────┬───────┘
          │
          v
  ┌───────────────┐     webhook: capture_session.stopped
  │   stopped      │ ──> All streams finalized
  └───────┬───────┘
          │  (if store=True)
          v
  ┌───────────────┐     webhook: capture_session.exported
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
