import os
import sys
from pathlib import Path


def init():
    try:
        import videodb  # noqa: F401
    except ImportError:
        print("ERROR: videodb is not installed.", file=sys.stderr)
        print("Run: pip install 'videodb[capture]'", file=sys.stderr)
        sys.exit(1)

    if os.environ.get("VIDEO_DB_API_KEY"):
        return

    from dotenv import load_dotenv

    for env_file in [Path.cwd() / ".env", Path.home() / ".videodb" / ".env"]:
        if env_file.is_file():
            load_dotenv(env_file)
            if os.environ.get("VIDEO_DB_API_KEY"):
                return

    print("ERROR: VIDEO_DB_API_KEY not found.", file=sys.stderr)
    print("Checked: environment, ./.env, ~/.videodb/.env", file=sys.stderr)
    print("Fix: add VIDEO_DB_API_KEY=your-key to ~/.videodb/.env", file=sys.stderr)
    print("Get a free key at https://console.videodb.io", file=sys.stderr)
    sys.exit(1)
