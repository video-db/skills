#!/usr/bin/env python3
"""
Batch upload utility for VideoDB Python Skill.

Uploads multiple videos from a list of URLs or file paths.
Tracks progress and handles errors gracefully.

Usage:
  python scripts/batch_upload.py --urls urls.txt
  python scripts/batch_upload.py --urls urls.txt --collection "My Collection"
  python scripts/batch_upload.py --files /path/to/dir/*.mp4
"""

import argparse
import sys
from pathlib import Path

from videodb_env import init
init()

import videodb


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch upload media to VideoDB.")
    parser.add_argument("--urls", help="Path to a text file containing one URL per line.")
    parser.add_argument("--files", nargs="*", help="Local file paths to upload.")
    parser.add_argument("--collection", default=None, help="Collection name (creates if needed).")
    parser.add_argument("--media-type", choices=["video", "audio", "image"], default=None, help="Media type override.")
    args = parser.parse_args()

    if not args.urls and not args.files:
        print("[batch_upload] ERROR: Provide --urls or --files.", file=sys.stderr)
        sys.exit(1)

    # Gather upload sources
    sources = []
    if args.urls:
        urls_path = Path(args.urls)
        if not urls_path.is_file():
            print(f"[batch_upload] ERROR: File not found: {args.urls}", file=sys.stderr)
            sys.exit(1)
        with open(urls_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    sources.append(("url", line))

    if args.files:
        for fp in args.files:
            path = Path(fp)
            if path.is_file():
                sources.append(("file", str(path.resolve())))
            else:
                print(f"[batch_upload] WARNING: File not found, skipping: {fp}")

    if not sources:
        print("[batch_upload] No valid sources found.")
        sys.exit(0)

    print(f"[batch_upload] {len(sources)} source(s) to upload.")

    try:
        conn = videodb.connect()

        if args.collection:
            # Find or create collection
            existing = conn.get_collections()
            coll = None
            for c in existing:
                if c.name == args.collection:
                    coll = c
                    break
            if coll is None:
                coll = conn.create_collection(name=args.collection, description=f"Batch upload: {args.collection}")
                print(f"[batch_upload] Created collection: {coll.id} ({args.collection})")
            else:
                print(f"[batch_upload] Using existing collection: {coll.id} ({args.collection})")
        else:
            coll = conn.get_collection()
            print(f"[batch_upload] Using default collection: {coll.id}")

        uploaded = []
        failed = []

        for i, (source_type, source_value) in enumerate(sources, 1):
            label = source_value if len(source_value) <= 60 else f"...{source_value[-57:]}"
            print(f"[batch_upload] [{i}/{len(sources)}] Uploading: {label}")

            try:
                upload_kwargs = {}
                if args.media_type:
                    upload_kwargs["media_type"] = args.media_type

                if source_type == "url":
                    media = coll.upload(url=source_value, **upload_kwargs)
                else:
                    media = coll.upload(file_path=source_value, **upload_kwargs)

                uploaded.append({"id": media.id, "name": media.name, "source": source_value})
                print(f"  -> OK: {media.name} ({media.id})")

            except Exception as exc:
                failed.append({"source": source_value, "error": str(exc)})
                print(f"  -> FAIL: {exc}")

        # Summary
        print(f"\n[batch_upload] Complete: {len(uploaded)} uploaded, {len(failed)} failed.")

        if uploaded:
            print("\nUploaded:")
            for item in uploaded:
                print(f"  {item['id']}  {item['name']}")

        if failed:
            print("\nFailed:")
            for item in failed:
                print(f"  {item['source']}: {item['error']}")

    except Exception as exc:
        print(f"[batch_upload] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
