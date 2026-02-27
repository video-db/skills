#!/usr/bin/env python3
"""
Capture client for VideoDB Capture.

Connects to the backend server to create a capture session, then records
screen and audio using the VideoDB CaptureClient. Streams are sent to
VideoDB for real-time AI processing.

Usage:
  .venv/bin/python scripts/client.py

Prerequisites:
  - The backend server must be running: .venv/bin/python scripts/backend.py
  - VIDEO_DB_API_KEY must be set in .env
"""

import asyncio
import sys

from videodb_env import load_vdb_env
load_vdb_env()

try:
    import requests
except ImportError:
    print("[client] Missing dependency: requests. Run: pip install requests")
    sys.exit(1)

from videodb.capture import CaptureClient

BACKEND_URL = "http://localhost:5002"


def create_session():
    """Creates a capture session via the backend."""
    try:
        print(f"[client] Connecting to backend at {BACKEND_URL}...")
        resp = requests.post(f"{BACKEND_URL}/init-session", json={}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"[client] Cannot connect to backend at {BACKEND_URL}")
        print("  Make sure the backend is running: .venv/bin/python scripts/backend.py")
        sys.exit(1)
    except Exception as e:
        print(f"[client] Failed to create session: {e}")
        sys.exit(1)


async def run_capture(token, session_id):
    """Captures screen and audio, streaming to VideoDB."""
    print("\n[client] --- Starting Capture Client ---")
    client = CaptureClient(client_token=token)

    try:
        print("[client] Requesting Permissions...")
        await client.request_permission("microphone")
        await client.request_permission("screen_capture")

        print("\n[client] Discovering Channels...")
        channels = await client.list_channels()
        for ch in channels.all():
            print(f"  - {ch.id} ({ch.type}): {ch.name}")

        mic = channels.mics.default
        display = channels.displays.default
        system_audio = channels.system_audio.default

        # store=True saves the recording to VideoDB after capture stops.
        # Without this, streams are processed in real-time but not persisted.
        mic.store = True
        display.store = True
        system_audio.store = True
        selected_channels = [c for c in [mic, display, system_audio] if c]
        if not selected_channels:
            print("[client] No channels found.")
            return

        print(f"\n[client] Starting Recording with {len(selected_channels)} channel(s):")
        for ch in selected_channels:
            print(f"  - {ch.type}: {ch.id}")

        await client.start_session(
            capture_session_id=session_id,
            channels=selected_channels,
            primary_video_channel_id=display.id if display else None,
        )

        print("\n[client] Recording... Press Enter to stop (or Ctrl+C to force quit).")

        # Wait for Enter key in a background thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, input)

        # Graceful stop
        print("\n[client] Stopping capture...")
        await client.stop_session()
        await client.shutdown()
        print("[client] Capture stopped.")

    except Exception as e:
        print(f"[client] Capture error: {e}")


async def main():
    print("=" * 60)
    print("[client] VideoDB Capture Client")
    print("=" * 60)

    session_data = create_session()
    token = session_data["token"]
    session_id = session_data["session_id"]
    print("[client] Session created successfully")
    print(f"  Token: {token[:10]}...")
    print(f"  Session ID: {session_id}\n")

    await run_capture(token, session_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[client] Force quit. The server will detect the disconnect and clean up.")
        sys.exit(1)
