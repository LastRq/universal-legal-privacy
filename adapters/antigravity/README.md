# Google Antigravity adapter

Install with `python scripts/ulp.py install --agent antigravity --scope project --project PATH --approve-install` **after user approval**; or use `--scope global` for `~/.gemini/config/skills`.

Expected project path: `.agents/skills/universal-legal-privacy/SKILL.md`.

Start a new session or refresh skills, then ask `/universal-legal-privacy audit this workspace in read-only mode`. Confirm that it stops before any write. The CLI/App/IDE may differ in invocation. Do not assume a live Antigravity environment was tested merely from the installer unit test.

Official reference: https://antigravity.google/docs/skills
