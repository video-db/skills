#!/usr/bin/env python3
"""
Multi-clip extraction utility for VideoDB Python Skill.

Extracts clips from a video at specified timestamp ranges and
generates individual stream URLs or a compiled stream.

Usage:
  python scripts/extract_clips.py --video-id <VIDEO_ID> --timestamps "10.0-25.0,45.0-60.0"
  python scripts/extract_clips.py --video-id <VIDEO_ID> --timestamps "10.0-25.0,45.0-60.0" --compile
"""

import argparse
import sys

from videodb_env import init
init()

import videodb


def parse_timestamps(raw: str) -> list[tuple[float, float]]:
    """
    Parse a comma-separated list of 'start-end' timestamp pairs.
    Example: "10.0-25.0,45.0-60.0,120.0-135.0"
    Returns: [(10.0, 25.0), (45.0, 60.0), (120.0, 135.0)]
    """
    pairs = []
    for segment in raw.split(","):
        segment = segment.strip()
        if not segment:
            continue
        parts = segment.split("-", 1)
        if len(parts) != 2:
            print(f"[extract_clips] WARNING: Invalid timestamp format '{segment}', skipping.")
            continue
        try:
            start = float(parts[0].strip())
            end = float(parts[1].strip())
            if start >= end:
                print(f"[extract_clips] WARNING: Start >= end in '{segment}', skipping.")
                continue
            pairs.append((start, end))
        except ValueError:
            print(f"[extract_clips] WARNING: Non-numeric timestamp in '{segment}', skipping.")
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract clips from a VideoDB video.")
    parser.add_argument("--video-id", required=True, help="VideoDB video ID.")
    parser.add_argument("--timestamps", required=True, help="Comma-separated 'start-end' pairs (seconds).")
    parser.add_argument("--compile", action="store_true", help="Compile all clips into one stream.")
    args = parser.parse_args()

    timestamps = parse_timestamps(args.timestamps)
    if not timestamps:
        print("[extract_clips] ERROR: No valid timestamps provided.", file=sys.stderr)
        sys.exit(1)

    try:
        conn = videodb.connect()
        coll = conn.get_collection()
        video = coll.get_video(args.video_id)
        print(f"[extract_clips] Video: {video.name} ({video.id}), duration: {video.length:.1f}s")
        print(f"[extract_clips] Extracting {len(timestamps)} clip(s)...")

        if args.compile:
            # Compile all clips into a single stream
            for i, (start, end) in enumerate(timestamps, 1):
                print(f"  Clip {i}: {start:.1f}s - {end:.1f}s")

            stream_url = video.generate_stream(timeline=timestamps)
            print(f"\n[extract_clips] Compiled stream URL: {stream_url}")
        else:
            # Generate individual clip streams
            for i, (start, end) in enumerate(timestamps, 1):
                print(f"  Clip {i}: {start:.1f}s - {end:.1f}s")
                stream_url = video.generate_stream(timeline=[(start, end)])
                print(f"    -> {stream_url}")

        print(f"\n[extract_clips] Done.")

    except Exception as exc:
        print(f"[extract_clips] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
