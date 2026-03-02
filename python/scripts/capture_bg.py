#!/usr/bin/env python3
"""
VideoDB Capture - Background recording with file-based stop control.

Usage:
  Start recording:  python scripts/capture_bg.py start
  Stop recording:   python scripts/capture_bg.py stop
  Check status:     python scripts/capture_bg.py status

The recording runs until you run 'stop' or the stop file is created.
"""

import sys
import asyncio
import threading
import queue
import time
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import videodb
from videodb.capture import CaptureClient

# --- Configuration ---
STATE_FILE = Path("/tmp/videodb_capture_state.json")
STOP_FILE = Path("/tmp/videodb_capture_stop")

conn = None


def setup():
    global conn
    conn = videodb.connect()


def start_ws_listener(ws_id_queue, name="Listener"):
    def run():
        async def listen():
            try:
                ws_wrapper = conn.connect_websocket()
                ws = await ws_wrapper.connect()
                ws_id = ws.connection_id
                ws_id_queue.put(ws_id)

                async for msg in ws.receive():
                    if STOP_FILE.exists():
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
                            print(f"[Audio Summary] {text}")
                    elif channel in ["scene_index", "visual_index"]:
                        text = data.get("text", "")
                        if text.strip():
                            print(f"[Visual] {text}")
            except Exception as e:
                if "closed" not in str(e).lower():
                    print(f"[{name}] Error: {e}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen())

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def start_ai_pipelines(session):
    mics = session.get_rtstream("mic")
    displays = session.get_rtstream("screen")
    system_audios = session.get_rtstream("system_audio")

    if system_audios:
        q = queue.Queue()
        start_ws_listener(q, name="SystemAudio")
        try:
            ws_id = q.get(timeout=10)
            system_audios[0].start_transcript(ws_connection_id=ws_id)
            system_audios[0].index_audio(
                prompt="Summarize what is being discussed",
                ws_connection_id=ws_id,
                batch_config={"type": "time", "value": 30},
            )
        except:
            pass

    if mics:
        q = queue.Queue()
        start_ws_listener(q, name="Mic")
        try:
            ws_id = q.get(timeout=10)
            mics[0].start_transcript(ws_connection_id=ws_id)
        except:
            pass

    if displays:
        q = queue.Queue()
        start_ws_listener(q, name="Visual")
        try:
            ws_id = q.get(timeout=10)
            displays[0].index_visuals(
                prompt="Describe what is happening on screen",
                ws_connection_id=ws_id,
            )
        except:
            pass


async def run_capture():
    # Clean up any existing stop file
    if STOP_FILE.exists():
        STOP_FILE.unlink()

    # Create session
    session = conn.create_capture_session(
        end_user_id="capture-user",
        collection_id="default",
        metadata={"app": "videodb-capture"},
    )
    token = conn.generate_client_token()

    # Save state
    STATE_FILE.write_text(json.dumps({
        "session_id": session.id,
        "status": "starting",
        "started_at": time.time(),
    }))

    print(f"[capture] Session: {session.id}")

    # Initialize client
    client = CaptureClient(client_token=token)

    try:
        await client.request_permission("microphone")
        await client.request_permission("screen_capture")

        channels = await client.list_channels()
        mic = channels.mics.default
        display = channels.displays.default
        system_audio = channels.system_audio.default

        if mic:
            mic.store = True
        if display:
            display.store = True
        if system_audio:
            system_audio.store = True

        selected = [c for c in [mic, display, system_audio] if c]

        print(f"[capture] Channels: {len(selected)}")
        for ch in selected:
            print(f"  - {ch.type}: {ch.name}")

        # Start capture
        await client.start_session(
            capture_session_id=session.id,
            channels=selected,
            primary_video_channel_id=display.id if display else None,
        )

        # Update state
        STATE_FILE.write_text(json.dumps({
            "session_id": session.id,
            "status": "recording",
            "started_at": time.time(),
        }))

        # Start AI
        time.sleep(2)
        try:
            active_session = conn.get_capture_session(session.id)
            start_ai_pipelines(active_session)
        except:
            pass

        print("\n[capture] RECORDING... Run 'python scripts/capture_bg.py stop' to finish.\n")

        # Wait for stop signal
        while not STOP_FILE.exists():
            await asyncio.sleep(1)

        # Stop
        print("\n[capture] Stopping...")
        await client.stop_session()
        await client.shutdown()

        # Wait for export
        print("[capture] Waiting for export...")
        time.sleep(5)

        # Get video URL
        coll = conn.get_collection()
        videos = coll.get_videos()
        if videos:
            latest = videos[-1]
            player_url = f"https://console.videodb.io/player?url={latest.stream_url}"

            STATE_FILE.write_text(json.dumps({
                "session_id": session.id,
                "status": "completed",
                "video_id": latest.id,
                "stream_url": latest.stream_url,
                "player_url": player_url,
            }))

            print("\n" + "=" * 60)
            print("  RECORDING COMPLETE!")
            print("=" * 60)
            print(f"\n  Video ID: {latest.id}")
            print(f"  Player: {player_url}")
            print()

            return player_url

    except Exception as e:
        print(f"[capture] Error: {e}")
        STATE_FILE.write_text(json.dumps({
            "session_id": session.id,
            "status": "error",
            "error": str(e),
        }))

    finally:
        if STOP_FILE.exists():
            STOP_FILE.unlink()

    return None


def cmd_start():
    print("=" * 60)
    print("  VideoDB Capture (Background Mode)")
    print("=" * 60 + "\n")

    setup()
    asyncio.run(run_capture())


def cmd_stop():
    STOP_FILE.touch()
    print("[capture] Stop signal sent. Recording will finish shortly.")


def cmd_status():
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        print(json.dumps(state, indent=2))
    else:
        print("No active capture session.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python capture_bg.py [start|stop|status]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "start":
        cmd_start()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
