#!/usr/bin/env python3
"""Deterministic checks for the VideoDB plugin. No model calls, no network needed (links are optional).

Run from the repo root:  python3 tests/static_checks.py [--links]
Exit code 1 on any failure.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK_LINKS = "--links" in sys.argv
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def unconditional_isw(text):
    """Lines that tell Claude to run index_spoken_words. Subtitles, captions and highlights read the transcript
    (generate_transcript); index_spoken_words is legacy v1 and may only appear in a line that says so."""
    return [l for l in text.splitlines() if "`index_spoken_words`" in l and "legacy" not in l]


# --- manifests -------------------------------------------------------------
pj = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
mj = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
entry = mj["plugins"][0]
ok(pj["name"] == "videodb" and entry["name"] == "videodb", "plugin name is videodb in both manifests")
ok(pj["version"] == entry["version"], f"version identical in both manifests ({pj['version']})")
ok(re.fullmatch(r"\d+\.\d+\.\d+", pj["version"]) is not None, "version is x.y.z")
ok(pj.get("displayName") == "VideoDB" and entry.get("displayName") == "VideoDB", "displayName VideoDB in both")
ok(pj["description"] == entry["description"], "description identical in both manifests")
ok("—" not in pj["description"], "no em dash in description")
ok(len(pj["description"].split()) <= 60, "description is 60 words or fewer")
ok(pj["keywords"] == entry["keywords"] and len(set(pj["keywords"])) == len(pj["keywords"]), "keywords identical, no duplicates")
for k in ["homepage", "documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl", "repository"]:
    ok(str(pj.get(k, "")).startswith("https://"), f"{k} is an https URL")
ok(pj.get("skills") == ["./python", "./skills"], "skills paths are ./python and ./skills")
ok(pj.get("commands") == "./commands", "commands path is ./commands")
mcp = json.loads((ROOT / ".mcp.json").read_text())
ok(mcp["mcpServers"]["videodb"]["url"].startswith("https://"), ".mcp.json videodb server is https")

# --- skills ----------------------------------------------------------------
job_skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
base = ROOT / "python/SKILL.md"
expected = {"video-search", "video-clips", "video-subtitles", "video-edit", "video-live"}
names = set()
for f in job_skills + [base]:
    rel = f.relative_to(ROOT)
    s = f.read_text()
    m = re.match(r"---\n(.*?)\n---\n", s, re.S)
    fm = m.group(1) if m else ""
    name = re.search(r"^name: (\S+)$", fm, re.M)
    desc = re.search(r"^description: (.+)$", fm, re.M)
    ok(bool(name and desc), f"{rel}: frontmatter has name and description")
    if not (name and desc):
        continue
    names.add(name.group(1))
    want = "videodb" if f == base else f.parent.name
    ok(name.group(1) == want, f"{rel}: name matches folder ({want})")
    ok(10 <= len(desc.group(1).split()) <= 90, f"{rel}: description between 10 and 90 words")
    ok("Use when" in desc.group(1) or "Use for" in desc.group(1), f"{rel}: description says when to use it")
    if f != base:
        ok("allowed-tools" not in fm, f"{rel}: no allowed-tools pre-approval (directory policy)")
    else:
        ok(re.search(r"^allowed-tools: Read Grep Glob$", fm, re.M) is not None, f"{rel}: allowed-tools is exactly Read Grep Glob")
    ok("## Which path" in s, f"{rel}: has a Which path section")
    which = s.split("## Which path", 1)[1].split("\n## ", 1)[0]
    ok("connector tools present" in which.lower(), f"{rel}: Which path starts with the connector")
    ok("Connectors" in which, f"{rel}: Which path has the chat connect instruction")
    ok("API key" in which, f"{rel}: Which path has the shell take-the-key instruction")
    conn_part = s.split("## Running Python code", 1)[0] if f == base else s.split("## With the Python SDK", 1)[0]
    ok("pip install" not in conn_part, f"{rel}: no pip install outside the SDK section")
    ok(not unconditional_isw(conn_part), f"{rel}: index_spoken_words only as a conditional step after generate_transcript")
    ok("retry_with`)" not in s, f"{rel}: polling text names poll_with")
    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w/.-]+)", s):
        ok((ROOT / ref).exists(), f"{rel}: referenced file exists: {ref}")
    new_text = s.split("## Running Python code", 1)[0] if f == base else s
    ok("—" not in new_text, f"{rel}: no em dash in skill text")
    ok("50 uploads" not in s, f"{rel}: no 50-uploads claim")
ok(names == expected | {"videodb"}, f"the six skills are present: {sorted(names)}")

# --- commands --------------------------------------------------------------
cmds = sorted((ROOT / "commands").glob("*.md"))
ok([c.stem for c in cmds] == ["clip", "find", "setup", "subtitles"], "four commands: clip, find, setup, subtitles")
for c in cmds:
    s = c.read_text()
    ok(re.search(r"^description: .+$", s, re.M) is not None, f"commands/{c.name}: has a description")
    ok("$ARGUMENTS" in s, f"commands/{c.name}: uses $ARGUMENTS")
    ok("—" not in s, f"commands/{c.name}: no em dash")
    ok(not unconditional_isw(s), f"commands/{c.name}: index_spoken_words only as a conditional step after generate_transcript")

# --- README (the listing's long description) -------------------------------
rd = (ROOT / "README.md").read_text()
ok(rd.lstrip().startswith("[![Add to Claude]"), "README starts with the Add to Claude badge")
ok("claude.ai/customize/plugins/id/52e93c02-c63f-4724-9716-d283e23e64e3" in rd, "README links the directory listing")
ok("$20" in rd and "50 uploads" not in rd, "README states $20 free credits and no 50-uploads claim")
ok(rd.index("## Add to Claude") < rd.index("## Install in Claude Code"), "README: Add to Claude section comes before the install section")

# --- connector tool names used in skills exist in the documented tool list --
doc_tools = set((ROOT / "tests/connector_tools.txt").read_text().split())
used = set()
for f in job_skills + [base] + cmds:
    text = f.read_text()
    if f == base:
        text = text.split("## Running Python code", 1)[0]
    for t in re.findall(r"`([a-z]+(?:_[a-z]+)+)\(", text):
        used.add(t)
sdk_methods = {"generate_stream", "load_dotenv", "index_spoken_words", "add_subtitle", "generate_music", "generate_voice",
               "dub_video", "wait_until_complete", "list_analyzers", "get_collection", "connect_rtstream", "generate_image"}
unknown = sorted(t for t in used if t not in doc_tools and t not in sdk_methods)
ok(not unknown, f"connector tool names in skills are documented (unknown: {unknown})")

# --- eval suites are well formed -------------------------------------------
for suite in ["evals", "evals-no-connector"]:
    cases = [p for p in (ROOT / suite).iterdir() if p.is_dir() and p.name not in ("mocks", "results")]
    for case in cases:
        ok((case / "prompt.md").exists(), f"{suite}/{case.name}: has prompt.md")
        graders = list((case / "graders").glob("*.md")) if (case / "graders").exists() else []
        ok(len(graders) >= 1, f"{suite}/{case.name}: has at least one grader")
mocks = list((ROOT / "evals/mocks/videodb").glob("*.md"))
ok(len(mocks) >= 15, f"evals/mocks/videodb has the mocked connector ({len(mocks)} tools)")

# --- links (optional) ------------------------------------------------------
if CHECK_LINKS:
    urls = set()
    for f in [ROOT / "README.md"] + job_skills + [base] + cmds:
        urls |= {u.rstrip(".,;:") for u in re.findall(r"https?://[^\s)\]>\"`]+", f.read_text())}
    skip = ("example.com", "camera.local", "VIDEO_ID", "player?url=", "{", "mcp.videodb.io", "claude.ai/", "github.com", "10.0.0.5", "https://...")
    bad = []
    for u in sorted(urls):
        if any(x in u for x in skip) or not re.match(r"https?://[\w.-]+\.[a-z]{2,}", u):
            continue
        code = subprocess.run(["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", u], capture_output=True, text=True).stdout
        if not code.startswith(("2", "3")):
            bad.append((u, code))
    ok(not bad, f"public links resolve (bad: {bad})")

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
