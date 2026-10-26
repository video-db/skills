# Tests for the VideoDB plugin

Three layers, cheapest first. Every change to a skill, command or manifest should keep all of them green.

| Layer | Command | What it checks | Cost |
| --- | --- | --- | --- |
| Static | `tests/run.sh static` | Manifests, skill frontmatter, the Which-path block in every skill, no pre-approved tools, no setup talk in the connector section, connector tool names against the documented list, README order and claims, eval suite shape, `claude plugin validate` | Free, seconds |
| Chat (mocked) | `tests/run.sh chat` | `claude plugin eval` with the VideoDB connector mocked under `evals/mocks/videodb/`. Four chat tasks (find a moment and clip, subtitles, vertical cut, make searchable and ask) and six routing cases. Graders check the tool chain, the tool inputs (clip range, subtitle colours, reframe target), no shell use, no "index" jargon, no setup talk, and the link in the reply | Model calls only, no VideoDB account |
| Offline | `tests/run.sh offline` | `evals-no-connector/`: what Claude does before the connector is connected (chat), and with a shell but no key, and with a key pasted in chat | Model calls; the shell cases need Claude Code's sandbox (bubblewrap + socat on Linux) and a normal user account (as root the run's workspace mounts read-only, which the key-given case tolerates but a real SDK call would not) |
| Live | `tests/run.sh live` | The chat smoke cases against the real hosted MCP server. Needs `claude` with the videodb server authorized (`/mcp`) | Model calls plus VideoDB credits |

`claude plugin eval` reruns each case `RUNS` times (default 1 here; the tool's own default is 3) and passes a case when its score reaches `THRESHOLD` (0.8). Results land in `evals/results/<timestamp>/` with an HTML report; `last-*.json` holds the latest run for scripts.

## How the chat surface is simulated

`claude plugin eval` runs inside Claude Code, so a chat case grants only `Skill` and adds an `append_system_prompt` line saying the run is the claude.ai chat app with no shell. Without that line the model knows it is in Claude Code and offers the shell path instead of the connect line. The mocked tools are named `mcp__videodb__<tool>` in the transcript, and `evals/mocks/videodb/_tools.json` gives them their real parameter schemas so the model sees `media_id`, `timeline`, the ASS colour fields and so on.

## What the chat cases encode

The thing we optimise for is a first result in Claude.ai chat with no setup. So the chat cases grant only the `Skill` tool plus the mocked connector, and fail if Claude:

- calls a shell tool,
- tells the user about pip, API keys, `.env` or environment variables,
- says "index" to the user instead of "make it searchable",
- skips the transcript fast path for a one-off spoken question,
- or does not end with a player link.

The mocked job store (`evals/mocks/videodb/get_job_result.md`) answers `processing` on the first poll of every job and `done` with an empty result on the first `done` of a clip, which is how the real server behaves, so polling discipline is tested too.

## Adding a case

```
evals/<case-name>/prompt.md        the user message, with allowed_tools and limits in frontmatter
evals/<case-name>/graders/*.md     one check per file: tool_used, tool_order, regex, llm
```

Mock a tool the case needs in `evals/mocks/videodb/<tool>.md` (fixed JSON body, optional `expect:` on the input). See `claude plugin eval --help` and the plugin evals docs for the full format.

## CI

`.github/workflows/plugin-tests.yml` runs the static layer on every pull request and push to main. The chat and offline-chat suites run on pull requests only when `ANTHROPIC_API_KEY` is set as a repository secret. Without the secret the `evals` job still reports green but runs nothing; it posts a warning annotation and a step summary saying so, so a green check on a repo without the secret means static checks only. The live layer is manual.
