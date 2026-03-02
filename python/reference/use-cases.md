# Real-World Use Cases

End-to-end workflows demonstrating common VideoDB operations.

## Create Video Highlight Reel

Upload a long video, search for key moments, and compile them into a highlight reel:

```python
import videodb
from videodb import SearchType
from videodb.timeline import Timeline
from videodb.asset import VideoAsset

conn = videodb.connect()
coll = conn.get_collection()

# 1. Upload the full video
video = coll.upload(url="https://example.com/conference-talk.mp4")

# 2. Index spoken content
video.index_spoken_words(force=True)

# 3. Search for key topics
topics = [
    "announcing the new product",
    "live demo of the feature",
    "audience Q&A session",
]

all_shots = []
for topic in topics:
    results = video.search(topic, search_type=SearchType.semantic)
    all_shots.extend(results.get_shots())

# 4. Build a timeline from the shots
timeline = Timeline(conn)
for shot in all_shots:
    asset = VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
    timeline.add_inline(asset)

# 5. Generate and share
stream_url = timeline.generate_stream()
print(f"Highlight reel: {stream_url}")
```

## Build a Searchable Video Library

Batch upload, index, and enable cross-collection search:

```python
import videodb

conn = videodb.connect()
coll = conn.create_collection(name="Training Videos", description="Internal training library")

# 1. Upload multiple videos
urls = [
    "https://example.com/onboarding-part1.mp4",
    "https://example.com/onboarding-part2.mp4",
    "https://example.com/security-training.mp4",
]

videos = []
for url in urls:
    video = coll.upload(url=url)
    videos.append(video)
    print(f"Uploaded: {video.name} ({video.id})")

# 2. Index all videos
for video in videos:
    video.index_spoken_words(force=True)
    print(f"Indexed: {video.name}")

# 3. Search across the entire collection
results = coll.search(
    query="how to reset your password",
    search_type=videodb.SearchType.semantic,
)

for shot in results.get_shots():
    print(f"Found in {shot.video_id}: [{shot.start:.1f}s - {shot.end:.1f}s]")

# 4. Play compiled results
results.play()
```

## Add Professional Polish to Raw Footage

Upload raw footage, add subtitles, and generate a thumbnail:

```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()

# 1. Upload raw footage
video = coll.upload(file_path="/path/to/raw-footage.mp4")

# 2. Generate transcript
video.index_spoken_words(force=True)
transcript = video.get_transcript_text()
print(f"Transcript ({len(transcript)} chars): {transcript[:200]}...")

# 3. Add auto-subtitles
stream_url = video.add_subtitle()

# 4. Generate thumbnail
thumbnail = video.generate_thumbnail(time=15.0)

print(f"Stream with subtitles: {stream_url}")
```

## Search and Extract Specific Clips

Find moments and download them as individual clips:

```python
import videodb
from videodb import SearchType

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# 1. Index if not already done
video.index_spoken_words(force=True)

# 2. Search for a specific topic
results = video.search("budget discussion", search_type=SearchType.semantic)

# 3. Extract each matching clip
shots = results.get_shots()
print(f"Found {len(shots)} matching segments")

for i, shot in enumerate(shots):
    stream_url = shot.generate_stream()
    print(f"Clip {i+1}: {shot.start:.1f}s - {shot.end:.1f}s -> {stream_url}")
```

## Generate AI-Enhanced Video Content

Combine generative AI with existing video:

```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# 1. Generate a summary of the video
video.index_spoken_words(force=True)
transcript_text = video.get_transcript_text()
result = coll.generate_text(
    prompt=f"Create a concise 2-sentence summary of this video:\n{transcript_text}",
    model_name="pro",
)
print(f"Summary: {result['output']}")

# 2. Generate background music
music = coll.generate_music(
    prompt="calm corporate background music, professional and modern",
    duration=int(video.length),
)

# 3. Generate intro image
intro = coll.generate_image(
    prompt="modern professional title card with abstract tech background",
    aspect_ratio="16:9",
)

# 4. Combine into a polished timeline
timeline = Timeline(conn)

# Add the main video
timeline.add_inline(VideoAsset(asset_id=video.id))

# Overlay intro image for first 5 seconds
timeline.add_overlay(0, ImageAsset(asset_id=intro.id, duration=5, width=1280, height=720, x=0, y=0))

# Overlay background music (mixed with original audio)
timeline.add_overlay(0, AudioAsset(asset_id=music.id, disable_other_tracks=False))

# 5. Generate final stream
stream_url = timeline.generate_stream()
print(f"Enhanced video: {stream_url}")
```

## Basic Screen + Audio Capture with Transcription

Record screen and microphone with live transcription.

### Backend

```python
import queue
import asyncio
import threading
from flask import Flask, request, jsonify
from pycloudflared import try_cloudflare
from dotenv import load_dotenv
from pathlib import Path
import videodb

# Load API key from ~/.videodb/.env
load_dotenv(Path.home() / ".videodb" / ".env")

app = Flask(__name__)
conn = videodb.connect()
tunnel = try_cloudflare(port=5002)
public_url = tunnel.tunnel


def start_ws_listener(ws_id_queue, name="Listener"):
    def run():
        async def listen():
            ws_wrapper = conn.connect_websocket()
            ws = await ws_wrapper.connect()
            ws_id_queue.put(ws.connection_id)
            async for msg in ws.receive():
                if msg.get("channel") == "transcript":
                    text = msg.get("data", {}).get("text", "")
                    if text.strip():
                        print(f"[{name}] {text}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())
    threading.Thread(target=run, daemon=True).start()


@app.route("/init-session", methods=["POST"])
def init_session():
    session = conn.create_capture_session(
        end_user_id="user-123",
        collection_id="default",
        callback_url=f"{public_url}/webhook",
    )
    token = conn.generate_client_token()
    return jsonify({"session_id": session.id, "token": token})


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = data.get("event")

    if event == "capture_session.active":
        session = conn.get_capture_session(data["capture_session_id"])
        mics = session.get_rtstream("mic")
        if mics:
            q = queue.Queue()
            start_ws_listener(q, name="Transcript")
            ws_id = q.get(timeout=10)
            mics[0].start_transcript(ws_connection_id=ws_id)

    elif event == "capture_session.exported":
        export_data = data.get("data", {})
        print(f"Exported! Video: {export_data.get('exported_video_id')}")
        print(f"  Stream: {export_data.get('stream_url')}")

    return jsonify({"received": True})


if __name__ == "__main__":
    print(f"Backend ready at {public_url}")
    app.run(port=5002)
```

### Client

```python
import asyncio
import requests
from videodb.capture import CaptureClient

async def main():
    resp = requests.post("http://localhost:5002/init-session", json={})
    data = resp.json()

    client = CaptureClient(client_token=data["token"])
    await client.request_permission("microphone")
    await client.request_permission("screen_capture")

    channels = await client.list_channels()
    mic = channels.mics.default
    display = channels.displays.default

    mic.store = True
    display.store = True

    selected = [c for c in [mic, display] if c]
    await client.start_session(
        capture_session_id=data["session_id"],
        channels=selected,
        primary_video_channel_id=display.id if display else None,
    )

    print("Recording... Press Enter to stop.")
    await asyncio.get_running_loop().run_in_executor(None, input)

    await client.stop_session()
    await client.shutdown()

asyncio.run(main())
```

---

## Real-Time Meeting Capture with AI Summarization

Capture a meeting with live transcription and periodic AI summaries.

### Backend (webhook handler)

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = data.get("event")

    if event == "capture_session.active":
        session = conn.get_capture_session(data["capture_session_id"])

        # Transcribe system audio (captures meeting audio)
        system_audios = session.get_rtstream("system_audio")
        if system_audios:
            q = queue.Queue()
            start_ws_listener(q, name="MeetingTranscript")
            ws_id = q.get(timeout=10)

            system_audios[0].start_transcript(ws_connection_id=ws_id)
            system_audios[0].index_audio(
                prompt="Summarize the key discussion points, decisions, and action items",
                ws_connection_id=ws_id,
                batch_config={"type": "time", "value": 60},
            )

        # Also transcribe mic for local speaker
        mics = session.get_rtstream("mic")
        if mics:
            q = queue.Queue()
            start_ws_listener(q, name="LocalSpeaker")
            ws_id = q.get(timeout=10)
            mics[0].start_transcript(ws_connection_id=ws_id)

    return jsonify({"received": True})
```

The `audio_index` WebSocket channel will deliver periodic summaries with key points, decisions, and action items every 60 seconds.

---

## Capture with Visual Indexing for Screen Activity Tracking

Track what's happening on screen with AI-generated descriptions.

### Backend (webhook handler)

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = data.get("event")

    if event == "capture_session.active":
        session = conn.get_capture_session(data["capture_session_id"])

        # Index screen visuals
        displays = session.get_rtstream("screen")
        if displays:
            q = queue.Queue()
            start_ws_listener(q, name="ScreenTracker")
            ws_id = q.get(timeout=10)

            displays[0].index_visuals(
                prompt="Describe the application in use and what the user is doing",
                ws_connection_id=ws_id,
            )

        # Also index system audio for context
        system_audios = session.get_rtstream("system_audio")
        if system_audios:
            q = queue.Queue()
            start_ws_listener(q, name="AudioContext")
            ws_id = q.get(timeout=10)

            system_audios[0].index_audio(
                prompt="What is being discussed or played",
                ws_connection_id=ws_id,
                batch_config={"type": "time", "value": 30},
            )

    return jsonify({"received": True})
```

The `visual_index` / `scene_index` channel will deliver descriptions like:
- "User is browsing a spreadsheet in Google Sheets"
- "User switched to a code editor with a Python file open"
- "User is on a video call with screen sharing enabled"

---

## Export and Post-Process Captured Video

After a capture session with `store=True`, the recording is automatically exported. Use the exported video ID to perform further operations.

### Backend (webhook handler for export)

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = data.get("event")

    if event == "capture_session.exported":
        export_data = data.get("data", {})
        video_id = export_data.get("exported_video_id")
        stream_url = export_data.get("stream_url")
        player_url = export_data.get("player_url")

        print(f"Video exported: {video_id}")
        print(f"  Stream: {stream_url}")
        print(f"  Player: {player_url}")

        # Post-process: generate transcript and search
        coll = conn.get_collection()
        video = coll.get_video(video_id)

        # Generate searchable transcript
        video.index_spoken_words(force=True)
        transcript = video.get_transcript_text()
        print(f"Transcript ({len(transcript)} chars):")
        print(transcript[:500])

        # Search for specific topics
        results = video.search("action items")
        if results.get_shots():
            compiled_url = results.compile()
            print(f"Action items clip: {compiled_url}")

    return jsonify({"received": True})
```

This workflow:
1. Captures screen and audio with `store=True`
2. Waits for the `capture_session.exported` webhook
3. Retrieves the exported video by ID
4. Indexes spoken words for search
5. Searches for specific content and compiles matching clips
