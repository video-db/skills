"""
Common environment loader for VideoDB scripts.

Loads .env files from multiple locations in order of priority:
1. Environment variables (highest priority)
2. ~/.videodb/.env (central location - recommended for Claude Code plugin)
3. Local .env in skill directory (for manual clones)
"""

import os
from pathlib import Path


def load_env():
    """Load environment variables from .env files in multiple locations."""
    env_locations = [
        Path.home() / ".videodb" / ".env",  # Central location (recommended for plugins)
        Path(__file__).resolve().parent.parent / ".env",  # Local skill directory
    ]

    for env_file in env_locations:
        if env_file.is_file():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return
            except ImportError:
                # Fallback: manually parse .env if python-dotenv is not yet installed
                try:
                    for _line in env_file.read_text().splitlines():
                        _line = _line.strip()
                        if _line and not _line.startswith("#") and "=" in _line:
                            _key, _, _val = _line.partition("=")
                            _key = _key.strip()
                            # Validate key format: non-empty and valid env var name
                            if _key and _key.replace("_", "").replace("-", "").isalnum():
                                os.environ.setdefault(_key, _val.strip())
                except Exception as e:
                    # If parsing fails, continue to next env file location
                    print(f"Warning: Failed to parse {env_file}: {e}")
                    continue
                return
