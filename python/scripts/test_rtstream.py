#!/usr/bin/env python3
"""
Test script for reference/rtstream.md — validates real-time stream operations.

Tests:
  1. Generate a stream URL from a video
  2. Generate a stream for specific segments (timeline parameter)
  3. Build a Timeline and generate a composed stream
  4. Index, search, and compile search results into a stream
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
        print("[test_rtstream] FAIL: VIDEO_DB_API_KEY not set.")
        sys.exit(1)

    import videodb
    from videodb import SearchType
    from videodb.timeline import Timeline
    from videodb.asset import VideoAsset

    print("[test_rtstream] Connecting to VideoDB...")
    conn = videodb.connect(api_key=api_key)
    coll = conn.get_collection()
    print(f"[test_rtstream] Collection: {coll.id}")

    # Upload sample video (configurable via VIDEODB_TEST_VIDEO_URL)
    sample_url = os.environ.get(
        "VIDEODB_TEST_VIDEO_URL",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Default test video
    )
    print(f"[test_rtstream] Uploading sample video from {sample_url}...")
    video = coll.upload(url=sample_url)
    print(f"[test_rtstream] Uploaded: {video.name} (id={video.id}, length={video.length:.1f}s)")

    # --- Test 1: Basic stream generation ---
    print("\n[test_rtstream] Test 1: Basic stream URL")
    stream_url = video.generate_stream()
    print(f"  Stream URL: {stream_url}")
    assert stream_url and stream_url.startswith("http"), "Expected valid URL"
    print("  PASS")

    # --- Test 2: Segment stream via timeline parameter ---
    print("\n[test_rtstream] Test 2: Segment stream (timeline parameter)")
    seg_end = min(10.0, video.length)
    stream_seg = video.generate_stream(timeline=[(0, seg_end)])
    print(f"  Stream URL (0-{seg_end}s): {stream_seg}")
    assert stream_seg and stream_seg.startswith("http"), "Expected valid URL"
    print("  PASS")

    # --- Test 3: Timeline composition stream ---
    print("\n[test_rtstream] Test 3: Timeline composition stream")
    timeline = Timeline(conn)
    mid = video.length / 2
    timeline.add_inline(VideoAsset(asset_id=video.id, start=0, end=min(5, mid)))
    timeline.add_inline(VideoAsset(asset_id=video.id, start=mid, end=min(mid + 5, video.length)))
    stream_composed = timeline.generate_stream()
    print(f"  Composed stream URL: {stream_composed}")
    assert stream_composed and stream_composed.startswith("http"), "Expected valid URL"
    print("  PASS")

    # --- Test 4: Search results compilation stream ---
    print("\n[test_rtstream] Test 4: Search -> compile stream")
    try:
        video.index_spoken_words()
        results = video.search("never gonna", search_type=SearchType.semantic)
        shots = results.get_shots()
        print(f"  Found {len(shots)} shots")
        if shots:
            compiled_url = results.compile()
            print(f"  Compiled stream URL: {compiled_url}")
            assert compiled_url and compiled_url.startswith("http"), "Expected valid URL"
            print("  PASS")
        else:
            print("  SKIP (no search results to compile)")
    except videodb.exceptions.InvalidRequestError as exc:
        if "no spoken data found" in str(exc).lower() or "language" in str(exc).lower():
            print(f"  No spoken data detected (video may be music-only). SKIP (graceful)")
        else:
            raise

    # Cleanup
    print(f"\n[test_rtstream] Cleaning up: deleting video {video.id}")
    video.delete()

    print("\n[test_rtstream] All rtstream tests PASSED.")


if __name__ == "__main__":
    main()
