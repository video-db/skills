"""Validate the shared VideoDB package for Cursor (requires jsonschema, PyYAML)."""
import json
from pathlib import Path
from urllib.request import urlopen

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_URL = (
    "https://raw.githubusercontent.com/cursor/plugins/"
    "41e400932eca14f289e7db717a70455256b6d388/schemas/plugin.schema.json"
)


def contained_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.exists():
        raise ValueError(f"Missing or escaping plugin path: {value}")
    return path


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    metadata = yaml.safe_load(text.split("---", 2)[1])
    if not isinstance(metadata, dict) or any(
        not isinstance(metadata.get(key), str) or not metadata[key].strip()
        for key in ("name", "description")
    ):
        raise ValueError(f"Missing name/description: {path}")
    return metadata


def main():
    manifest = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text())
    with urlopen(SCHEMA_URL, timeout=30) as response:
        schema = json.load(response)
    jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(manifest)
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    for key in ("name", "version"):
        if manifest[key] != claude[key]:
            raise ValueError(f"Cursor and Claude {key} differ")
    contained_path(manifest["logo"])
    skills = []
    for value in manifest["skills"]:
        directory = contained_path(value)
        direct = directory / "SKILL.md"
        skills.extend([direct] if direct.is_file() else sorted(directory.glob("*/SKILL.md")))
    skill_names = [frontmatter(path)["name"] for path in skills]
    expected = {"videodb", "video-search", "video-clips", "video-subtitles", "video-edit", "video-live"}
    if len(skill_names) != len(expected) or set(skill_names) != expected:
        raise ValueError(f"Unexpected or duplicate skills: {skill_names}")
    commands = sorted(contained_path(manifest["commands"]).glob("*.md"))
    names = [frontmatter(path)["name"] for path in commands]
    if len(names) != 4 or set(names) != {"setup", "find", "clip", "subtitles"}:
        raise ValueError(f"Unexpected or duplicate commands: {names}")
    mcp = json.loads(contained_path(manifest["mcpServers"]).read_text())
    if mcp != {"mcpServers": {"videodb": {"type": "http", "url": "https://mcp.videodb.io/mcp"}}}:
        raise ValueError("Unexpected VideoDB MCP configuration; review transport, endpoint, and authentication")
    print("Cursor package valid: six skills, four commands, one hosted MCP server; shared manifest identity matches.")


if __name__ == "__main__":
    main()
