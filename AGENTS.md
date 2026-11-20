# Branches

- `claude-plugin` is the branch the Claude plugin directory installs from. Keep it small: the directory's automated policy review must be able to read every file, or the version is held for manual review.
- `main` carries the full skill, including `python/reference/`, for `npx skills add` and other agents.
- Change skills on `main` first, then port to `claude-plugin`. Never merge `main` into `claude-plugin` wholesale; it brings `python/reference/` back.
- On `claude-plugin`, link to docs.videodb.io instead of adding reference files. No evals, tests or scripts on this branch.
- Scope of this branch: search, clips, subtitles and translation, timeline editing with media the user supplies, smart reframe, live streams, and the SDK for those.
- Describe what VideoDB does; don't instruct Claude about which other tools to use or avoid.
