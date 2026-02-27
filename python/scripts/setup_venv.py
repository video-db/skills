#!/usr/bin/env python3
"""
Virtual environment setup script for VideoDB Python Skill.

Logic:
  1. Checks if .venv/ exists in the skill root directory.
  2. If .venv/ exists and has a valid Python interpreter -> skip creation and dependency install.
  3. If .venv/ does NOT exist -> create it, then install dependencies from requirements.txt.
  4. Reusable across future executions (idempotent).

Usage:
  python scripts/setup_venv.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Load environment variables from multiple locations
try:
    from env_loader import load_env
    load_env()
except ImportError:
    # Fallback if env_loader is not available
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass


def get_skill_root() -> Path:
    """Return the skill root directory (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def get_venv_dir() -> Path:
    """Return the .venv directory path."""
    return get_skill_root() / ".venv"


def get_requirements_file() -> Path:
    """Return the requirements.txt path."""
    return get_skill_root() / "requirements.txt"


def get_venv_python(venv_dir: Path) -> Path:
    """Return the Python interpreter path inside the venv."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def get_venv_pip(venv_dir: Path) -> Path:
    """Return the pip path inside the venv."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def venv_is_valid(venv_dir: Path) -> bool:
    """
    Check if the virtual environment exists and has a working Python interpreter.
    A directory alone is not sufficient; the interpreter must be executable.
    """
    python_path = get_venv_python(venv_dir)
    if not python_path.is_file():
        return False

    try:
        result = subprocess.run(
            [str(python_path), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def create_venv(venv_dir: Path) -> None:
    """Create a virtual environment at the given path."""
    print(f"[setup_venv] Creating virtual environment at: {venv_dir}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"[setup_venv] ERROR: Failed to create venv", file=sys.stderr)
            print(f"  stdout: {result.stdout.strip()}", file=sys.stderr)
            print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        print("[setup_venv] Virtual environment created successfully.")
    except subprocess.TimeoutExpired:
        print("[setup_venv] ERROR: Timed out creating virtual environment.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[setup_venv] ERROR: OS error creating venv: {exc}", file=sys.stderr)
        sys.exit(1)


def upgrade_pip(venv_dir: Path) -> None:
    """Upgrade pip inside the venv to avoid install warnings."""
    python_path = get_venv_python(venv_dir)
    print("[setup_venv] Upgrading pip...")
    try:
        result = subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            # Non-fatal: pip upgrade failure should not block dependency install
            print(f"[setup_venv] WARNING: pip upgrade failed (continuing anyway).", file=sys.stderr)
    except (subprocess.TimeoutExpired, OSError):
        print("[setup_venv] WARNING: pip upgrade timed out (continuing anyway).", file=sys.stderr)


def install_dependencies(venv_dir: Path, requirements_file: Path) -> None:
    """Install dependencies from requirements.txt into the venv."""
    if not requirements_file.is_file():
        print(f"[setup_venv] WARNING: {requirements_file} not found. Skipping dependency install.")
        return

    python_path = get_venv_python(venv_dir)

    # Use python -m pip as the more reliable invocation method
    cmd = [str(python_path), "-m", "pip", "install", "-r", str(requirements_file)]

    print(f"[setup_venv] Installing dependencies from: {requirements_file}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"[setup_venv] ERROR: Dependency installation failed.", file=sys.stderr)
            print(f"  stdout: {result.stdout.strip()}", file=sys.stderr)
            print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        print("[setup_venv] Dependencies installed successfully.")
    except subprocess.TimeoutExpired:
        print("[setup_venv] ERROR: Dependency installation timed out.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[setup_venv] ERROR: OS error during pip install: {exc}", file=sys.stderr)
        sys.exit(1)


def verify_videodb_import(venv_dir: Path) -> bool:
    """Verify that videodb can be imported inside the venv."""
    python_path = get_venv_python(venv_dir)
    try:
        result = subprocess.run(
            [str(python_path), "-c", "import videodb; from videodb.__about__ import __version__; print(f'videodb {__version__}')"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            version_info = result.stdout.strip()
            print(f"[setup_venv] Verified: {version_info}")
            return True
        return False
    except (subprocess.TimeoutExpired, OSError):
        return False


def check_api_key() -> bool:
    """Check if the VIDEO_DB_API_KEY environment variable is set."""
    key = os.environ.get("VIDEO_DB_API_KEY", "")
    if key:
        masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        print(f"[setup_venv] API key found: {masked}")
        return True
    print("[setup_venv] Note: API key will be needed to use VideoDB.")
    return False


def main() -> None:
    """
    Main entry point. Idempotent virtual environment setup:
      - If .venv/ exists with valid Python -> skip entirely
      - If .venv/ does not exist -> create + install deps
    """
    venv_dir = get_venv_dir()
    requirements_file = get_requirements_file()

    print(f"[setup_venv] Skill root: {get_skill_root()}")
    print(f"[setup_venv] Venv path:  {venv_dir}")

    if venv_is_valid(venv_dir):
        print("[setup_venv] Virtual environment already exists and is valid. Skipping creation.")
        print("[setup_venv] Skipping dependency installation (venv already provisioned).")
    else:
        if venv_dir.exists():
            print("[setup_venv] .venv/ exists but is corrupt or incomplete. Recreating...")
            shutil.rmtree(venv_dir)

        create_venv(venv_dir)
        upgrade_pip(venv_dir)
        install_dependencies(venv_dir, requirements_file)

    # Post-setup verification
    if not verify_videodb_import(venv_dir):
        print("[setup_venv] WARNING: Could not import videodb. You may need to install manually.")

    check_api_key()

    # Print activation instructions
    venv_python = get_venv_python(venv_dir)
    print()
    print("[setup_venv] Setup complete.")
    print(f"[setup_venv] Python: {venv_python}")
    if sys.platform == "win32":
        print(f"[setup_venv] Activate: {venv_dir}\\Scripts\\activate")
    else:
        print(f"[setup_venv] Activate: source {venv_dir}/bin/activate")


if __name__ == "__main__":
    main()
