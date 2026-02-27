#!/usr/bin/env python3
"""
Connection verification script for VideoDB Python Skill.

Verifies that the API key is valid and a connection to VideoDB can be established.
Outputs a clear success or error message.

Usage:
  python scripts/check_connection.py
"""

import sys

from videodb_env import load_vdb_env
load_vdb_env()

import videodb


def main() -> None:
    try:
        conn = videodb.connect()
        coll = conn.get_collection()
        videos = coll.get_videos()
        print(f"[check_connection] SUCCESS: Connected to VideoDB.")
        print(f"  Default collection: {coll.id}")
        print(f"  Videos in collection: {len(videos)}")
    except videodb.exceptions.AuthenticationError:
        print("[check_connection] FAIL: Authentication failed. Check your API key.")
        sys.exit(1)
    except Exception as exc:
        print(f"[check_connection] FAIL: Connection error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
