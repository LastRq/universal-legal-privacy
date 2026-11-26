# Universal project audit: platform-independent legal and privacy engineering

This workflow extends the 99 modules. Platform is an independent axis, not a sector. Audit all authorized source roots, products and deployable units. A documentation website does not define the behavior of the executable it describes.

## 1. Read-only discovery
Confirm project root/revision, intended scope, app boundaries, build targets, distribution channels and execution environments. Inspect tracked source, manifests, dependency declarations, installers, app permissions, infrastructure definitions, tests and existing policies. Record evidence and gaps per component, build variant and platform; do not assume a target is shipped just because a manifest mentions it. Do not run untrusted code, builds, installers, migrations, package scripts or binaries without explicit permission. Never inspect production records, personal vaults, keys, seed phrases, tokens, .env values, user profiles or database contents. Use synthetic fixtures for runtime verification after approval. Analyze archive contents only through bounded, safe extraction in an authorized workspace; do not follow external symlinks.

## 2. Platform profiles (combine as needed)

| Platform | Evidence and controls to investigate | Possible delivery surfaces |
|---|---|---|
| Static web / web app | Routes, forms, cookies, storage, network requests, third-party scripts, consent | Footer, privacy page, contextual notices, preferences |
| Desktop / native / hybrid | Installer/update, native bridge, filesystem, registry/keychain, IPC, crash reports, telemetry, permissions, background tasks | About/settings/legal screen, installer disclosures, EULA where applicable |
| Mobile | Android/iOS manifests, SDKs, permissions, background tasks, store metadata, account deletion, deep links | Settings, onboarding, permission rationale, store privacy disclosures |
| Games | Accounts, age, multiplayer/chat, moderation, purchases, game telemetry, anti-cheat, virtual assets | Launcher, in-game legal menu, purchase disclosures |
| API/backend/microservice | Endpoints, auth, schema, persistence, logs, queues, tenants, vendors, backups, transfers, retention | Developer docs, API terms, service agreements, privacy notices |
| Library/SDK/plugin | Public interfaces, permissions, default data collection, telemetry, distribution, downstream responsibilities, dependencies | README, SDK docs, license/NOTICE, integration guide |
| Browser extension | Manifest, host permissions, content scripts, storage, network, browsing history, store declarations | Extension options, contextual permission notices, store listing |
| CLI / automation / agent | Flags, stdin/stdout, filesystem scope, subprocesses, provider calls, logs, telemetry, prompts | Help, documentation, configurable preferences |
| AI service / model | Model providers, data inputs/outputs, training/reuse, retention, tools, oversight, decision impact | Model documentation, in-product notices, settings, human escalation |
| Local-first/offline | Local persistence, encryption, key custody, exports, backup, opt-in synchronization, offline network behavior | Settings, recovery warning, export/delete controls, EULA if relevant |
| IoT / hardware | Device permissions, sensor data, firmware, pairing, telemetry, support lifecycle | Companion app, product manual, setup screen |
| Infrastructure / cloud | Deployment topology, storage regions, access, secrets handling, service contracts, incident response | Internal runbooks, contractual documents, customer notices as applicable |
| Monorepo / multi-product | Separate operator, platform, build variants, shared services, tenants, integrations and audiences | Per-product notices plus shared documents only if accurate |

These are candidate checks, not legal requirements. Cookies are not presumed on native software; a WebView, embedded browser or SDK may use storage/tracking. A legal screen is not an excuse to introduce a cookie banner on an offline program. Do not add telemetry, tracking or cloud services to implement compliance.

## 3. Evidence-first data-flow analysis
For each component trace collection/source -> purpose -> processing -> local persistence -> network egress (including DNS/update/crash/analytics) -> recipients -> backups/export -> deletion. Distinguish content held exclusively on user devices from data actually accessible to the developer, cloud operator, vendor or customer organization. Verify code path, feature flag, default state, configuration, platform and release behavior. Identify controller/processor roles per operation; local storage does not automatically establish absence of legal obligations. Inspect licenses and third-party notices, distribution terms, security claims and actual product lifecycle. Missing artifacts or unavailable runtime/network tests are gaps, not passing results.

Use `python scripts/project_audit.py --project PATH` for read-only platform and capability candidates. The helper uses bounded source traversal and existing scan signals; it does not run the software, determine its sector automatically, infer applicable law or certify privacy. Resolve candidates manually against evidence, select catalog IDs via module_plan.py, and research official sources as required by SKILL.md. Unknown technology or niche: use a custom evidence-based review rather than excluding the project.

## 4. Credential vault / password manager reference case
Hypothetical example: vault for passwords, API credentials, wallets and authenticator/TOTP data. Candidate sectors: cybersecurity, technology, digital-identity only if identity services are present; candidate models: local-first, proprietary-software/open-source, SaaS only if delivered as hosted service. Candidate capabilities: encryption, authentication, security, retention, portability, incident-notification; device-sync, cloud-storage, third-party-services, international-transfers, payments, OCR or AI only if supported by evidence. Do not classify merely storing wallet credentials as operating an exchange or providing financial advice.
- Inspect source-level schema and cryptographic configuration, KDF, key generation/custody, lock/recovery, clipboard, autofill, memory handling, logs, exports, backups, deletion and update verification. Do not open real vault contents or export actual secrets.
- Trace whether any credential material, metadata, device identifiers, crash dumps or telemetry can leave the device; test with synthetic credentials and approved isolated network observation. Do not claim "zero knowledge", "no data collection", "end-to-end encrypted" or "offline only" without evidence for every relevant release path.
- Evaluate operator roles, privacy disclosure, license/EULA, recovery limitations, support/incident policy, export/deletion and third-party licenses; add cloud/sync terms, transfer and vendor review only if applicable. Research relevant jurisdictions and specialist review before release.
- No real code or legal conclusions are supplied by this example.

## 5. Deliverables and gates
Produce an inventory per component/platform, data-flow matrix, evidenced module selection, jurisdiction/official-source ledger, existing legal document and license inventory, risk register with severity and remediation tests, unknowns and focused owner questions, proposed docs and integration locations, and release validation status. Report code evidence as paths/lines without secrets or source excerpts. Use private workfiles only with prior approval. Draft policy/EULA/terms/cookie notices/consumer terms/security disclosures as applicable after facts and official legal sources are verified. Integrate only after separate approval; reuse existing legal screens and language. Verify with tests and synthetic runtime behavior; do not publish or merge target project changes without explicit approval.
