#!/usr/bin/env bash
# Test runner for the VideoDB plugin. Run from the repo root.
#
#   tests/run.sh static      deterministic checks + claude plugin validate   (free, seconds)
#   tests/run.sh chat        mocked-connector eval suite, chat + routing      (model calls, no VideoDB account)
#   tests/run.sh offline     no-connector suite: chat-not-connected, shell cases (model calls; shell cases need bubblewrap+socat)
#   tests/run.sh live        the chat suite against the REAL hosted MCP server (needs `claude` with videodb authorized; uses credits)
#   tests/run.sh all         static + chat + offline
#
# Env: RUNS (default 1), THRESHOLD (default 0.8), MAX_COST (default 10), MODEL / JUDGE_MODEL (optional pins).
set -euo pipefail
cd "$(dirname "$0")/.."
RUNS="${RUNS:-1}"; THRESHOLD="${THRESHOLD:-0.8}"; MAX_COST="${MAX_COST:-10}"
PIN=(); [ -n "${MODEL:-}" ] && PIN+=(--model "$MODEL"); [ -n "${JUDGE_MODEL:-}" ] && PIN+=(--judge-model "$JUDGE_MODEL")
# ${PIN[@]+"${PIN[@]}"} expands an empty array safely under set -u on bash 3.2 (macOS)
COMMON=(--trust-plugin --no-publish --runs "$RUNS" --threshold "$THRESHOLD" --max-cost-usd "$MAX_COST" --ablation none ${PIN[@]+"${PIN[@]}"})

static() {
  python3 tests/static_checks.py "$@"
  claude plugin validate .
}
chat() {
  claude plugin eval . --eval-dir evals "${COMMON[@]}" --json evals/results/last-chat.json
}
offline() {
  claude plugin eval . --eval-dir evals-no-connector --tag chat "${COMMON[@]}" --json evals-no-connector/results/last-chat.json
  claude plugin eval . --eval-dir evals-no-connector --tag shell --allow-tools Bash Write "${COMMON[@]}" --json evals-no-connector/results/last-shell.json
}
live() {
  # Real server: every mocked tool is ignored, the plugin's own MCP server starts, and its tools need a grant by name.
  claude plugin eval . --eval-dir evals --tag smoke --mocks off --allow-tools "mcp__plugin_videodb_videodb__*" \
    --trust-plugin --no-publish --runs 1 --threshold "$THRESHOLD" --max-cost-usd "$MAX_COST" --ablation none ${PIN[@]+"${PIN[@]}"} \
    --json evals/results/last-live.json
}

case "${1:-all}" in
  static) static --links ;;
  chat) chat ;;
  offline) offline ;;
  live) live ;;
  all) static; chat; offline ;;
  *) echo "usage: tests/run.sh {static|chat|offline|live|all}"; exit 2 ;;
esac
