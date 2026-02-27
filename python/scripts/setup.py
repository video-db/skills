#!/usr/bin/env python3
"""
Dependency check and installation script for VideoDB Python Skill.

Checks if the videodb package is installed in the current Python environment.
If not, installs it via pip. Also verifies API key availability.

Usage:
  python scripts/setup.py
"""

import os
import subprocess
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


def check_videodb_installed() -> bool:
    """Check if videodb is importable in the current environment."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import videodb; from videodb.__about__ import __version__; print(__version__)"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[setup] videodb is installed: v{version}")
            return True
        return False
    except (subprocess.TimeoutExpired, OSError):
        return False


def install_videodb() -> bool:
    """Install dependencies from requirements.txt (or fall back to videodb alone)."""
    requirements_file = Path(__file__).resolve().parent.parent / "requirements.txt"
    if requirements_file.is_file():
        print(f"[setup] Installing dependencies from {requirements_file}...")
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
    else:
        print("[setup] Installing videodb with capture support...")
        cmd = [sys.executable, "-m", "pip", "install", "videodb[capture]>=0.4.0", "python-dotenv>=1.0.0"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print("[setup] Dependencies installed successfully.")
            return True

        # If capture installation failed (common on Linux), try core SDK
        if "[capture]" in " ".join(cmd):
            print("[setup] Capture installation failed. Trying core SDK (without capture)...")
            cmd_core = [sys.executable, "-m", "pip", "install", "videodb>=0.4.0", "python-dotenv>=1.0.0"]
            result = subprocess.run(
                cmd_core,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                print("[setup] Core SDK installed successfully.")
                print("[setup] Note: Real-time capture features are not available.")
                return True

        print(f"[setup] ERROR: Installation failed.", file=sys.stderr)
        print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("[setup] ERROR: Installation timed out.", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"[setup] ERROR: {exc}", file=sys.stderr)
        return False


def check_api_key() -> bool:
    """Check if VIDEO_DB_API_KEY is set in the environment."""
    key = os.environ.get("VIDEO_DB_API_KEY", "")
    if key:
        masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        print(f"[setup] API key found: {masked}")
        return True
    print("[setup] WARNING: VIDEO_DB_API_KEY is not set.")
    print("  Set it with: export VIDEO_DB_API_KEY=\"your-api-key\"")
    print("  Get a key from: https://console.videodb.io")
    return False


def main() -> None:
    print("[setup] Checking VideoDB environment...")

    if not check_videodb_installed():
        print("[setup] videodb is not installed.")
        if not install_videodb():
            sys.exit(1)
        if not check_videodb_installed():
            print("[setup] ERROR: videodb still not importable after install.", file=sys.stderr)
            sys.exit(1)

    check_api_key()
    print("[setup] Environment is ready.")


if __name__ == "__main__":
    main()
