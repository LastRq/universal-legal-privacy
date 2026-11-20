# Claude Code adapter

Install with `python scripts/ulp.py install --agent claude --scope project --project PATH --approve-install` **after approval**; or use `--scope global` for `~/.claude/skills`.

Expected project path: `.claude/skills/universal-legal-privacy/SKILL.md`. Invocation: `/universal-legal-privacy` or a natural language request. Restart or refresh the agent session. Cloud sessions may require the skill folder to be present in the cloned repository; local personal installations are not guaranteed to carry into cloud sessions.

Run a read-only test prompt; confirm the agent asks for company data and legal sources and does not create public routes without permission.

Official reference: https://code.claude.com/docs/en/skills
