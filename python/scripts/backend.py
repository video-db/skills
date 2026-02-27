#!/usr/bin/env python3
"""
Capture backend server for VideoDB Capture.

Runs a Flask server that:
  - Creates capture sessions and generates client tokens
  - Handles webhook events from VideoDB (session lifecycle)
  - Starts AI pipelines (transcription, audio indexing, visual indexing)
  - Streams real-time results via WebSocket listeners

Usage:
  .venv/bin/python scripts/backend.py

The server starts on port 5002. The client (scripts/client.py) connects to this backend
to initiate capture sessions.

Note: This version uses WebSocket for real-time communication instead of CloudFlare tunnels.
"""

import os
import logging
import threading
import queue
import asyncio
import traceback
from pathlib import Path
from flask import Flask, request, jsonify
import videodb

# Load environment variables from multiple locations
try:
    from env_loader import load_env
    load_env()
except ImportError:
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---

VIDEO_DB_API_KEY = os.getenv("VIDEO_DB_API_KEY")
PORT = int(os.getenv("BACKEND_PORT", "5002"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"http://localhost:{PORT}/webhook")

if not VIDEO_DB_API_KEY:
    raise ValueError("VIDEO_DB_API_KEY environment variable not set")

conn = None


# --- Helper Functions ---

def mask_api_key(key: str) -> str:
    """Mask API key for logging (show only first 4 and last 4 characters)."""
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


# --- Initialization ---

def setup():
    global conn
    masked_key = mask_api_key(VIDEO_DB_API_KEY)
    print(f"[backend] Connecting to VideoDB with API key: {masked_key}")

    try:
        conn = videodb.connect(api_key=VIDEO_DB_API_KEY)
        print("[backend] Successfully connected to VideoDB")
    except Exception as e:
        # Ensure API key is not exposed in error messages
        error_msg = str(e).replace(VIDEO_DB_API_KEY, mask_api_key(VIDEO_DB_API_KEY))
        print(f"[backend] Failed to connect to VideoDB: {error_msg}")
        raise

    print(f"[backend] Backend server starting on port {PORT}")
    print(f"[backend] Webhook URL: {WEBHOOK_URL}")
    print("\n" + "="*60)
    print("IMPORTANT: For webhooks to work, ensure WEBHOOK_URL is publicly accessible.")
    print("Options:")
    print("  1. Use ngrok: ngrok http 5002")
    print("  2. Use CloudFlare tunnel: cloudflared tunnel --url localhost:5002")
    print("  3. Deploy on a server with a public IP")
    print(f"  4. Set WEBHOOK_URL env var to your public URL")
    print("="*60 + "\n")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "port": PORT, "webhook_url": WEBHOOK_URL})


@app.route("/init-session", methods=["POST"])
def init_session():
    """Creates a capture session and returns a client token."""
    try:
        print(f"[backend] Creating session with webhook: {WEBHOOK_URL}")

        session = conn.create_capture_session(
            end_user_id="quickstart-user",
            collection_id="default",
            callback_url=WEBHOOK_URL,
            metadata={"app": "capture-skill"},
        )

        token = conn.generate_client_token()

        return jsonify(
            {"session_id": session.id, "token": token, "webhook_url": WEBHOOK_URL}
        )
    except Exception as e:
        # Mask API key in error messages
        error_msg = str(e).replace(VIDEO_DB_API_KEY, mask_api_key(VIDEO_DB_API_KEY))
        logger.error(f"[backend] Error creating session: {error_msg}")
        return jsonify({"error": error_msg}), 500


# --- WebSocket Listener ---
# Each WebSocket needs its own asyncio event loop for receiving messages.
# We run each in a daemon thread so the Flask request handler doesn't block.

def start_ws_listener(ws_id_queue, name="Listener"):
    """Starts a background thread that listens for real-time AI results via WebSocket."""

    def run():
        async def listen():
            try:
                print(f"[{name}] Connecting to WebSocket...")
                ws_wrapper = conn.connect_websocket()
                ws = await ws_wrapper.connect()
                ws_id = ws.connection_id
                print(f"[{name}] Connected! ID: {ws_id}")

                ws_id_queue.put(ws_id)

                async for msg in ws.receive():
                    channel = msg.get("channel")
                    data = msg.get("data", {})

                    if channel == "transcript":
                        text = data.get("text", "")
                        if text.strip():
                            print(f"[{name}] {text}")
                    elif channel == "audio_index":
                        text = data.get("text", "")
                        if text.strip():
                            print(f"\n{'*' * 50}")
                            print(f"[{name}] Audio Index: {text}")
                            print(f"{'*' * 50}")
                    elif channel in ["scene_index", "visual_index"]:
                        text = data.get("text", "")
                        if text.strip():
                            print(f"\n{'*' * 50}")
                            print(f"[{name}] Visual Index: {text}")
                            print(f"{'*' * 50}")

            except Exception as e:
                print(f"[{name}] Error: {e}")
                traceback.print_exc()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


# --- Webhook Handler & AI Pipelines ---

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives webhook events from VideoDB and starts AI pipelines."""
    data = request.json
    event = data.get("event")

    if event is None:
        print("\n[WEBHOOK] Received event with no type")
        print(f"  Payload: {data}")
        return jsonify({"received": True})

    print(f"\n[WEBHOOK] Event: {event}")

    if event not in [
        "capture_session.active",
        "capture_session.stopping",
        "capture_session.stopped",
        "capture_session.exported",
    ]:
        return jsonify({"received": True})

    if event == "capture_session.active":
        print("[backend] Capture Session Active! Starting AI pipelines...")
        capture_session_id = data.get("capture_session_id")

        try:
            session = conn.get_capture_session(capture_session_id)
            print(f"[backend] Retrieved Session: {session.id}")

            mics = session.get_rtstream("mic")
            displays = session.get_rtstream("screen")
            system_audios = session.get_rtstream("system_audio")

            print(
                f"  Mics: {len(mics)} | System Audio: {len(system_audios)} | Displays: {len(displays)}"
            )

            # Start AI on System Audio
            if system_audios:
                sys_audio = system_audios[0]
                print(f"  Indexing system audio: {sys_audio.id}")

                q = queue.Queue()
                start_ws_listener(q, name="SystemAudioWatcher")
                ws_id = q.get(timeout=10)

                sys_audio.start_transcript(ws_connection_id=ws_id)
                sys_audio.index_audio(
                    prompt="Summarize what is being discussed",
                    ws_connection_id=ws_id,
                    batch_config={"type": "time", "value": 30},
                )
                print(f"  System Audio indexing started (socket: {ws_id})")

            # Start AI on Mic
            if mics:
                mic = mics[0]
                print(f"  Indexing mic: {mic.id}")

                q = queue.Queue()
                start_ws_listener(q, name="MicWatcher")
                ws_id = q.get(timeout=10)

                mic.start_transcript(ws_connection_id=ws_id)
                mic.index_audio(
                    prompt="Summarize what is being discussed",
                    ws_connection_id=ws_id,
                    batch_config={"type": "time", "value": 30},
                )
                print(f"  Mic indexing started (socket: {ws_id})")

            # Start AI on Displays
            if displays:
                display = displays[0]
                print(f"  Indexing display: {display.id}")

                q = queue.Queue()
                start_ws_listener(q, name="VisualWatcher")
                ws_id = q.get(timeout=10)

                display.index_visuals(
                    prompt="In one sentence, describe what is on screen",
                    ws_connection_id=ws_id,
                )
                print(f"  Visual indexing started (socket: {ws_id})")

        except Exception as e:
            # Mask API key in error messages
            error_msg = str(e).replace(VIDEO_DB_API_KEY, mask_api_key(VIDEO_DB_API_KEY))
            print(f"[backend] Error in webhook processing: {error_msg}")
            traceback.print_exc()

    elif event == "capture_session.stopping":
        print("[backend] Session stopping...")

    elif event == "capture_session.stopped":
        print("[backend] Session stopped. All streams finalized.")

    elif event == "capture_session.exported":
        export_data = data.get("data", {})
        video_id = export_data.get("exported_video_id")
        stream_url = export_data.get("stream_url")
        player_url = export_data.get("player_url")

        print(f"\n[backend] Recording Exported! Video ID: {video_id}")
        if stream_url:
            print(f"  Stream URL: {stream_url}")
        if player_url:
            print(f"  Player URL: {player_url}")

        print(f"\n{'=' * 60}")
        print("[backend] What's next?")
        print("  - Try different index_audio() prompts for richer insights")
        print("  - Build alerts with rtstream.create_alert()")
        print("  - Explore the full SDK: https://docs.videodb.io")
        print(f"{'=' * 60}")

    return jsonify({"received": True})


if __name__ == "__main__":
    setup()
    app.run(port=PORT)
