# Universal Legal & Privacy

**Evidence-first privacy engineering skill for Google Antigravity, Claude Code and OpenAI Codex.**

**Español:** Analiza un proyecto real, descubre posibles tratamientos de datos, investiga las obligaciones aplicables en **fuentes oficiales**, pregunta por información empresarial faltante y prepara documentos y cambios de privacidad para revisión y autorización humana. No inventa hechos, no ofrece una certificación legal y no publica automáticamente.

> **Status:** v1.1.0 — modular audit framework and local safety utilities. Agent-runtime integrations need validation in the user's installed Antigravity/Claude/Codex environments. A green local test suite does **not** mean legal compliance.
>
> **License:** [Apache License 2.0](LICENSE). Copyright © 2026 LastRq. You may use, modify and redistribute this skill, including commercially, subject to the license terms. See [COPYRIGHT.md](COPYRIGHT.md).

## Capabilities

- Eight ordered stages: read-only discovery, technical mapping, entity/jurisdiction identification, official legal research, gap analysis + approval, draft documents, approved integration, verification/reporting.
- Monorepo support: separately track apps, services, shared systems, brands and different legal operators.
- Technical observations use **file paths and line numbers**, not raw personal values; the scanner returns *candidate signals*, not confirmed collection.
- Privacy, terms and cookie/storage **draft templates**, gated on verified profiles, official sources and explicit workfile permission. Expand to refund, consumer, regulated-sector and other documents through the agent only after applicable analysis.
- Consent rules: no chatbot; assess whether a banner is needed, block optional technologies before permission where required, test withdrawal/rejection and accessibility.
- Read-only by default; non-public workfiles can be preauthorized, but code changes, publishing and Git actions always require separate approval.
- No external dependencies for the bundled Python 3.10+ CLI.

## Modular audit framework

The [catalog](references/modular/catalog.json) includes 40 sectors, 24 business models and 35 capabilities (99 investigation modules). Each has activation criteria, investigation topics, candidate technical controls and specialist-review triggers. The [workflow](references/modular/workflow.md) explains multi-module composition, per-operator scope and jurisdiction research.

```bash
python scripts/module_plan.py --list
python scripts/module_plan.py --sectors healthcare --models saas multitenant --capabilities sensitive-data authentication --jurisdiction EC
```

The offline planner validates explicit module IDs, separates uncertain candidates, and outputs a research plan without modifying the project. Selection is not automatic detection or a determination of law. Official legal verification, technical testing and explicit approvals remain required.

## Installation (Python 3.10+)

Download or clone this repository, then run from its root:

```bash
python scripts/ulp.py verify-bundle
python scripts/ulp.py install --agent antigravity --scope project --project /path/to/project --approve-install
python scripts/ulp.py install --agent claude --scope project --project /path/to/project --approve-install
python scripts/ulp.py install --agent codex --scope project --project /path/to/project --approve-install
```

**Only run installation after explicitly authorizing it.** If the destination already exists, installation refuses to overwrite it. To install for the current user globally, use `--scope global` without `--project`. Windows PowerShell uses the same Python command (`py -3 scripts/ulp.py ...`).

| Agent | Project directory | Global directory | Invocation |
|---|---|---|---|
| Antigravity | `.agents/skills/universal-legal-privacy/` | `~/.gemini/config/skills/universal-legal-privacy/` | `/universal-legal-privacy` |
| Claude Code | `.claude/skills/universal-legal-privacy/` | `~/.claude/skills/universal-legal-privacy/` | `/universal-legal-privacy` |
| Codex | `.agents/skills/universal-legal-privacy/` | `~/.agents/skills/universal-legal-privacy/` | `$universal-legal-privacy` |

You can also ask for an audit in natural language; discovery depends on agent settings and session. New installations may require a restart/reload.

### Official format documentation

- [Agent Skills specification](https://agentskills.io/specification)
- [Google Antigravity skills](https://antigravity.google/docs/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex skills](https://developers.openai.com/codex/skills)

## Working locally

```bash
# Read-only scan: candidate indicators only, no code snippets in the output
python scripts/ulp.py scan --project /path/to/project

# With prior permission to write non-public audit files
python scripts/ulp.py scan --project /path/to/project \
  --out .legal-privacy/work/scan-initial.json --approve-workfiles

# After approval, create a blank profile in an excluded work directory
python scripts/ulp.py init-profile --project /path/to/project --approve-workfiles

# Human completes the profile using observed facts and official legal references
python scripts/ulp.py validate-profile \
  --profile /path/to/project/.legal-privacy/work/profile.json --types privacy

# After a confirmed profile and approved scope, generate private draft only
python scripts/ulp.py draft --project /path/to/project \
  --profile /path/to/project/.legal-privacy/work/profile.json \
  --types privacy --approve-workfiles
```

**Never treat `--approve-workfiles` or `--approve-install` as consent on their own.** The agent/user must have explicitly approved scope first. This tool has no identity or legal-source verification backend.

### What the local helper does not do

It does not discover all data flows, run a browser, check network requests, check legal sources live, establish which laws apply, verify the authenticity of corporate claims, or install a production cookie manager. The skill instructs the coding agent to perform those tasks *when authorized and when tools are available* and to mark unverified steps as blocked or pending.

## Test suite

```bash
python -m unittest discover -s tests -v
python scripts/ulp.py verify-bundle
```

The tests validate package structure, safe defaults, low-risk scanning, profile gates and installer paths. They do **not** prove that proprietary agent runtimes loaded the skill. For live agent acceptance, use [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Repository contents

- `SKILL.md`: complete agent workflow and stop/approval rules.
- `references/`: focused security, privacy, consent, drafting and sector guidance.
- `scripts/ulp.py`: offline read-only scan, safe workfiles, strict profile checks, draft generation and installer.
- `assets/templates/`: JSON profile shape, audit and permission templates.
- `assets/consent-example/`: illustrative opt-in JavaScript sample, **not production-ready compliance code**.
- `adapters/`: agent-specific setup and invocation notes.
- `tests/`: deterministic local test suite and fixtures.
- `docs/`: threat model, compatibility plan, acceptance criteria and release notes.

## Security and boundaries

No cookies or SDKs are automatically installed. We never use competitor policies as a substitute for law. Missing legal/identity facts block affected documents. A project may be technically implemented yet require legal specialist review. Do not push `.legal-privacy/work/`, secret files or sensitive evidence into Git; the `.gitignore` excludes them when used in this repository, and target projects may require their own local ignore rules.

## Maintenance

Official law varies by jurisdiction and can change. Check original regulations and government/regulatory guidance at the time of each audit. A source ledger should include jurisdiction, issuing authority, URL, section, consultation date, reason it applies and uncertainty. Re-run tests on changes to the helper, references or agent interfaces; compare drafts rather than overwriting human edits.

## Links

Project: https://github.com/LastRq/universal-legal-privacy

No external issue-reporting telemetry, background tracking or automatic publishing is included.
