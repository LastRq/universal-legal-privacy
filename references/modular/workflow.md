# Modular audit framework (v1.1)
 
The catalog contains 40 industry sectors, 24 business models and 35 cross-cutting capabilities. Entries are investigation guides, not statements of law or automatic authorization. The legacy sector matrix remains useful as a supplementary reference.

## Activation and composition
1. In stages 0–2 of SKILL.md, inventory each app, service, legal operator, actual activity, audience, data flow and market. Record file/line evidence or human confirmation; treat signals as candidates. Never infer regulated activities, children, sensitive data or applicable law merely from a sector label.
2. Load catalog.json. Select zero or more IDs per category for each app/operator; record reason, evidence and confidence for each. Mark uncertain candidates and scope gaps separately. No default blanket activation. If no module fits, document a custom review rather than inventing IDs. Exclude a candidate only with a documented reason; absence of detection is not proof.
3. Compose selected modules as a union; deduplicate only identical requirements for the same operator, processing purpose and jurisdiction. Do not collapse tenant-specific responsibilities or conflicting laws. Each module supplies activation cues, investigation topics, candidate controls and specialist escalation triggers. Check related capabilities separately (e.g. health does not prove biometrics, and marketplace does not prove payments).
4. Build a jurisdiction matrix from actual establishment, targeting, users, processing locations, transfers and regulated activity. Research official law and regulator guidance with dates, exact sections and applicability. Consult references/legal-research/source-policy.md. Do not infer jurisdiction from language or server location; do not resolve conflicts by simply choosing the strictest rule.
5. For each investigated issue record module ID, entity/app, jurisdiction, verified factual evidence, official source, applicability rationale, duty, proposed document/control, verification test, owner, status and residual risk. If unknown, conflicting or unverified, block the affected action. Preserve source provenance when merging requirements.
6. Translate verified duties into appropriate documents (privacy, terms, cookie/storage, consumer/refund, licensing, sector disclosures, contracts or internal records as applicable), and into UI/backend changes and verification tests. Never imply that every document or control is mandatory. Follow the existing eight stages and separate approval gates. Specialist review is mandatory where required or where high risk cannot be resolved.
7. Produce redacted report, risk register, proposed changes, test results and outstanding blockers. No raw data, automatic publication or certification.

## Offline helper
Run from the repository or installed skill root:
```sh
python scripts/module_plan.py --list
python scripts/module_plan.py --sectors healthcare technology --models saas multitenant --capabilities sensitive-data authentication --candidate-capabilities biometrics --jurisdiction EC
```
Selection is supplied by the caller after evidence review. The helper validates IDs, deduplicates modules, preserves candidate separation and emits a read-only research plan to stdout. It does not inspect the project, determine law, fetch legal sources, validate approvals, write files or generate final policies. Treat any selection as scope, not a finding. Use a separate plan for each operator/app; keep evidence and actual legal research in the authorized private work area.

## Acceptance
```sh
python -m unittest discover -s tests -v
python scripts/ulp.py verify-bundle
```
Test at least static no-tracking websites, hybrid regulated SaaS, multitenant isolation, ambiguous signals, and cross-jurisdiction conflicts during live agent acceptance. Catalog tests only check structure and deterministic planning; live agent and legal validation are separate.
