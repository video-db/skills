#!/usr/bin/env python3
"""
Test script for reference/editor.md — validates timeline editing operations.

Tests:
  1. Connect and get collection
  2. Upload a sample video
  3. Create a timeline with trimmed VideoAsset (inline)
  4. Add a TextAsset overlay with TextStyle
  5. Multi-clip inline timeline
"""

import os
import sys
from pathlib import Path

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

def main() -> None:
    api_key = os.environ.get("VIDEO_DB_API_KEY", "")
    if not api_key:
        print("[test_editor] FAIL: VIDEO_DB_API_KEY not set.")
        sys.exit(1)

    import videodb
    from videodb.timeline import Timeline
    from videodb.asset import VideoAsset, TextAsset, TextStyle

    print("[test_editor] Connecting to VideoDB...")
    conn = videodb.connect(api_key=api_key)
    coll = conn.get_collection()
    print(f"[test_editor] Collection: {coll.id}")

    # Upload a short sample video (configurable via VIDEODB_TEST_VIDEO_URL)
    sample_url = os.environ.get(
        "VIDEODB_TEST_VIDEO_URL",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Default test video
    )
    print(f"[test_editor] Uploading sample video from {sample_url}...")
    video = coll.upload(url=sample_url)
    print(f"[test_editor] Uploaded: {video.name} (id={video.id}, length={video.length:.1f}s)")

    # --- Test 1: Timeline with trimmed inline clip ---
    print("\n[test_editor] Test 1: Timeline with trimmed VideoAsset")
    timeline = Timeline(conn)
    trim_end = min(10.0, video.length)
    clip = VideoAsset(asset_id=video.id, start=0, end=trim_end)
    timeline.add_inline(clip)
    stream_url = timeline.generate_stream()
    print(f"  Stream URL: {stream_url}")
    assert stream_url and stream_url.startswith("http"), "Expected valid stream URL"
    print("  PASS")

    # --- Test 2: TextAsset overlay with TextStyle ---
    print("\n[test_editor] Test 2: TextAsset overlay with TextStyle")
    timeline2 = Timeline(conn)
    timeline2.add_inline(VideoAsset(asset_id=video.id, start=0, end=trim_end))
    title = TextAsset(
        text="Editor Test",
        duration=3,
        style=TextStyle(
            fontsize=36,
            fontcolor="white",
            alpha=0.8,
            font="Arial",
        ),
    )
    timeline2.add_overlay(0, title)
    stream_url2 = timeline2.generate_stream()
    print(f"  Stream URL: {stream_url2}")
    assert stream_url2 and stream_url2.startswith("http"), "Expected valid stream URL"
    print("  PASS")

    # --- Test 3: Multi-clip timeline ---
    print("\n[test_editor] Test 3: Multi-clip inline timeline")
    timeline3 = Timeline(conn)
    mid = video.length / 2
    timeline3.add_inline(VideoAsset(asset_id=video.id, start=0, end=min(5, mid)))
    timeline3.add_inline(VideoAsset(asset_id=video.id, start=mid, end=min(mid + 5, video.length)))
    stream_url3 = timeline3.generate_stream()
    print(f"  Stream URL: {stream_url3}")
    assert stream_url3 and stream_url3.startswith("http"), "Expected valid stream URL"
    print("  PASS")

    # Cleanup
    print(f"\n[test_editor] Cleaning up: deleting video {video.id}")
    video.delete()

    print("\n[test_editor] All editor tests PASSED.")


if __name__ == "__main__":
    main()
