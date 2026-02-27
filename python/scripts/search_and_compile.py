#!/usr/bin/env python3
"""
Search and compile workflow script for VideoDB Python Skill.

Searches within a video for a query, compiles matching segments,
and returns a stream URL.

Usage:
  python scripts/search_and_compile.py --video-id <VIDEO_ID> --query "your search query"
  python scripts/search_and_compile.py --video-id <VIDEO_ID> --query "your query" --search-type keyword
  python scripts/search_and_compile.py --collection-id <COLL_ID> --query "your query"
"""

import argparse
import sys

from videodb_env import init
init()

import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError


def ensure_indexed(video, search_type: str) -> None:
    """Ensure the video is indexed for the given search type."""
    if search_type in ("semantic", "keyword"):
        print(f"[search_compile] Indexing spoken words for video: {video.id}")
        try:
            video.index_spoken_words()
            print("[search_compile] Spoken word indexing complete.")
        except Exception:
            # May already be indexed; continue
            print("[search_compile] Spoken words may already be indexed. Continuing.")
    elif search_type == "scene":
        print(f"[search_compile] Indexing scenes for video: {video.id}")
        try:
            from videodb import SceneExtractionType
            video.index_scenes(
                extraction_type=SceneExtractionType.shot_based,
                prompt="Describe the visual content in this scene.",
            )
            print("[search_compile] Scene indexing complete.")
        except Exception:
            print("[search_compile] Scenes may already be indexed. Continuing.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search within a video and compile results.")
    parser.add_argument("--video-id", required=False, help="VideoDB video ID to search within.")
    parser.add_argument("--collection-id", required=False, help="Collection ID for cross-video search.")
    parser.add_argument("--query", required=True, help="Search query string.")
    parser.add_argument(
        "--search-type",
        choices=["semantic", "keyword", "scene"],
        default="semantic",
        help="Type of search (default: semantic).",
    )
    args = parser.parse_args()

    if not args.video_id and not args.collection_id:
        print("[search_compile] ERROR: Provide --video-id or --collection-id.", file=sys.stderr)
        sys.exit(1)

    search_type_map = {
        "semantic": SearchType.semantic,
        "keyword": SearchType.keyword,
        "scene": SearchType.scene,
    }

    def run_search(target, query, search_type):
        """Run a search and handle 'no results' errors gracefully."""
        try:
            return target.search(query=query, search_type=search_type)
        except InvalidRequestError as exc:
            if "No results found" in str(exc):
                print("[search_compile] No results found for this query.")
                sys.exit(0)
            raise

    try:
        conn = videodb.connect()

        if args.video_id:
            coll = conn.get_collection()
            video = coll.get_video(args.video_id)
            print(f"[search_compile] Video: {video.name} ({video.id})")

            ensure_indexed(video, args.search_type)

            print(f"[search_compile] Searching for: \"{args.query}\" (type: {args.search_type})")
            results = run_search(video, args.query, search_type_map[args.search_type])
        else:
            coll = conn.get_collection(args.collection_id)
            print(f"[search_compile] Collection: {coll.id}")
            if args.search_type != "semantic":
                print(f"[search_compile] ERROR: Collection-level search only supports 'semantic'. "
                      f"'{args.search_type}' search is only available on individual videos (use --video-id).",
                      file=sys.stderr)
                sys.exit(1)
            print(f"[search_compile] Searching for: \"{args.query}\" (type: {args.search_type})")
            results = run_search(coll, args.query, search_type_map[args.search_type])

        shots = results.get_shots()
        if not shots:
            print("[search_compile] No results found.")
            sys.exit(0)

        print(f"[search_compile] Found {len(shots)} matching segment(s):")
        for i, shot in enumerate(shots, 1):
            print(f"  {i}. [{shot.start:.1f}s - {shot.end:.1f}s] {shot.text[:80] if shot.text else '(no text)'}")

        stream_url = results.compile()
        print(f"\n[search_compile] Compiled stream URL: {stream_url}")

    except Exception as exc:
        print(f"[search_compile] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
