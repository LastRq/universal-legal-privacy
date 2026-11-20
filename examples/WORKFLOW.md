# Example workflow (no invented company)

1. Owner says: "Analyze this SaaS application only. Do not write files."
2. Agent reads SKILL.md and performs project discovery; optional command: `python scripts/ulp.py scan --project PATH`.
3. Agent reports possible login, analytics and payment SDK *signals* with file/line citations. It does **not** claim all signals are active.
4. Agent asks: actual legal operator, countries served, roles, processing purposes, retention, vendors and contracts.
5. Agent verifies official laws and regulator guidance for **confirmed** jurisdictions, records legal sources and consulted dates.
6. Agent presents a bounded plan for **non-public** audit workfiles and seeks authorization.
7. Owner approves workfiles; agent runs `init-profile`, fills verified facts, validates and creates only approved drafts.
8. Agent separately requests permission for legal UI/pages, tracking controls and E2E tests.
9. Owner approves release **only after** reviewing documents, specialist review where applicable, and actual tests. Agent never publishes solely because tests are green.

For a dental clinic, the workflow additionally requires specialist attention to patient information and local professional/health privacy rules. For a property marketplace, identify platform vs brokerage responsibilities. Neither example supplies legal facts about an actual business.
