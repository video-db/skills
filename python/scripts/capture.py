#!/usr/bin/env python3
"""
VideoDB Capture - Single-process screen and audio recorder.

Uses WebSocket polling instead of Cloudflare webhooks. No external tunnel required.
Records screen, microphone, and system audio, then exports to a shareable video.

Usage:
  python scripts/capture.py

Requirements:
  pip install "videodb[capture]"
"""

import sys
import asyncio
import threading
import queue
import time
import traceback

from videodb_env import init
init()

import videodb
from videodb.capture import CaptureClient

# --- Configuration ---

# Global connection and state
conn = None
session = None
exported_video = None


def setup():
    """Connect to VideoDB."""
    global conn
    print("[capture] Connecting to VideoDB...")
    conn = videodb.connect()
    print("[capture] Connected!")


def create_session():
    """Create a capture session without webhook (we'll poll instead)."""
    global session
    print("[capture] Creating capture session...")
    session = conn.create_capture_session(
        end_user_id="capture-user",
        collection_id="default",
        metadata={"app": "videodb-capture"},
    )
    print(f"[capture] Session created: {session.id}")
    return session


def start_ws_listener(ws_id_queue, name="Listener", stop_event=None):
    """Start a WebSocket listener thread for real-time AI results."""

    def run():
        async def listen():
            try:
                ws_wrapper = conn.connect_websocket()
                ws = await ws_wrapper.connect()
                ws_id = ws.connection_id
                print(f"[{name}] WebSocket connected: {ws_id[:20]}...")
                ws_id_queue.put(ws_id)

                async for msg in ws.receive():
                    if stop_event and stop_event.is_set():
                        break

                    channel = msg.get("channel")
                    data = msg.get("data", {})

                    if channel == "transcript":
                        text = data.get("text", "")
                        if text.strip():
                            print(f"[Transcript] {text}")
                    elif channel == "audio_index":
                        text = data.get("text", "")
                        if text.strip():
                            print(f"\n{'─' * 50}")
                            print(f"[Audio Summary] {text}")
                            print(f"{'─' * 50}\n")
                    elif channel in ["scene_index", "visual_index"]:
                        text = data.get("text", "")
                        if text.strip():
                            print(f"\n{'─' * 50}")
                            print(f"[Visual] {text}")
                            print(f"{'─' * 50}\n")

            except Exception as e:
                if "closed" not in str(e).lower():
                    print(f"[{name}] WebSocket error: {e}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def start_ai_pipelines(session):
    """Start AI processing on all available streams."""
    print("[capture] Starting AI pipelines...")

    mics = session.get_rtstream("mic")
    displays = session.get_rtstream("screen")
    system_audios = session.get_rtstream("system_audio")

    print(f"  Streams: {len(mics)} mic, {len(system_audios)} system audio, {len(displays)} display")

    # System Audio
    if system_audios:
        sys_audio = system_audios[0]
        q = queue.Queue()
        start_ws_listener(q, name="SystemAudio")
        try:
            ws_id = q.get(timeout=10)
            sys_audio.start_transcript(ws_connection_id=ws_id)
            sys_audio.index_audio(
                prompt="Summarize what is being discussed",
                ws_connection_id=ws_id,
                batch_config={"type": "time", "value": 30},
            )
            print(f"  System audio AI started")
        except Exception as e:
            print(f"  System audio AI failed: {e}")

    # Microphone
    if mics:
        mic = mics[0]
        q = queue.Queue()
        start_ws_listener(q, name="Mic")
        try:
            ws_id = q.get(timeout=10)
            mic.start_transcript(ws_connection_id=ws_id)
            mic.index_audio(
                prompt="Summarize what is being discussed",
                ws_connection_id=ws_id,
                batch_config={"type": "time", "value": 30},
            )
            print(f"  Mic AI started")
        except Exception as e:
            print(f"  Mic AI failed: {e}")

    # Display
    if displays:
        display = displays[0]
        q = queue.Queue()
        start_ws_listener(q, name="Visual")
        try:
            ws_id = q.get(timeout=10)
            display.index_visuals(
                prompt="Describe what is happening on screen",
                ws_connection_id=ws_id,
            )
            print(f"  Visual AI started")
        except Exception as e:
            print(f"  Visual AI failed: {e}")


def poll_session_status(session_id, target_status, timeout=60):
    """Poll session status until it reaches target state."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            s = conn.get_capture_session(session_id)
            if s.status == target_status:
                return s
            time.sleep(1)
        except Exception as e:
            print(f"[capture] Poll error: {e}")
            time.sleep(1)
    return None


def poll_for_export(session_id, timeout=120):
    """Poll session until video is exported."""
    print("[capture] Waiting for video export...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            s = conn.get_capture_session(session_id)
            # Check if session has exported video info
            if hasattr(s, 'exported_video_id') and s.exported_video_id:
                return s
            if hasattr(s, 'stream_url') and s.stream_url:
                return s
            if s.status == "exported":
                return s
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
    return None


async def run_capture():
    """Main capture flow."""
    global session, exported_video

    # Create session
    session = create_session()
    token = conn.generate_client_token()

    # Initialize capture client
    print("\n[capture] Initializing capture client...")
    client = CaptureClient(client_token=token)

    try:
        # Request permissions
        print("[capture] Requesting permissions...")
        await client.request_permission("microphone")
        await client.request_permission("screen_capture")

        # Discover channels
        print("[capture] Discovering channels...")
        channels = await client.list_channels()

        mic = channels.mics.default
        display = channels.displays.default
        system_audio = channels.system_audio.default

        # Enable storage for shareable video
        if mic:
            mic.store = True
        if display:
            display.store = True
        if system_audio:
            system_audio.store = True

        selected = [c for c in [mic, display, system_audio] if c]

        if not selected:
            print("[capture] No capture channels available!")
            return None

        print(f"\n[capture] Available channels:")
        for ch in selected:
            print(f"  - {ch.type}: {ch.name}")

        # Start capture
        print(f"\n[capture] Starting recording...")
        await client.start_session(
            capture_session_id=session.id,
            channels=selected,
            primary_video_channel_id=display.id if display else None,
        )

        # Poll for active status and start AI
        print("[capture] Waiting for session to become active...")
        time.sleep(2)  # Give it a moment

        try:
            active_session = conn.get_capture_session(session.id)
            if active_session:
                start_ai_pipelines(active_session)
        except Exception as e:
            print(f"[capture] Could not start AI pipelines: {e}")

        print("\n" + "=" * 60)
        print("  RECORDING IN PROGRESS")
        print("  Press Enter to stop...")
        print("=" * 60 + "\n")

        # Wait for user to stop
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, input)

        # Stop capture
        print("\n[capture] Stopping recording...")
        await client.stop_session()
        await client.shutdown()

        # Wait for export
        print("[capture] Processing and exporting video...")
        time.sleep(3)  # Give server time to finalize

        # Get final session with export info
        final_session = None
        for _ in range(30):  # Try for 60 seconds
            try:
                final_session = conn.get_capture_session(session.id)
                if final_session.status == "exported":
                    break
            except:
                pass
            time.sleep(2)

        if final_session:
            print("\n" + "=" * 60)
            print("  RECORDING COMPLETE!")
            print("=" * 60)

            # Try to get the exported video
            try:
                coll = conn.get_collection()
                videos = coll.get_videos()
                if videos:
                    # Get most recent video
                    latest = videos[-1]
                    print(f"\n  Video ID: {latest.id}")
                    print(f"  Stream URL: {latest.stream_url}")
                    print(f"  Player: https://console.videodb.io/player?url={latest.stream_url}")
                    return latest
            except Exception as e:
                print(f"  Could not retrieve video details: {e}")

        return final_session

    except Exception as e:
        print(f"[capture] Error: {e}")
        traceback.print_exc()
        return None


async def main():
    print("=" * 60)
    print("  VideoDB Capture")
    print("  Screen + Audio Recording with AI")
    print("=" * 60 + "\n")

    setup()
    result = await run_capture()

    if result:
        print("\n[capture] Done!")
    else:
        print("\n[capture] Recording may have failed. Check the console for details.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[capture] Interrupted. Cleaning up...")
        sys.exit(0)
