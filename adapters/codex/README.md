# OpenAI Codex adapter

Install with `python scripts/ulp.py install --agent codex --scope project --project PATH --approve-install` **after approval**; or use `--scope global` for `~/.agents/skills`.

Expected project path: `.agents/skills/universal-legal-privacy/SKILL.md`. Invoke as `$universal-legal-privacy` (or describe the privacy task). Restart session if discovery is stale. The identical `.agents/skills` project location may be shared with Antigravity; do not overwrite an existing installation.

Test that the skill refuses legal drafts when facts are missing and records observations without disclosing source values. Connector sandbox permissions can differ between Codex environments.

Official reference: https://developers.openai.com/codex/skills
