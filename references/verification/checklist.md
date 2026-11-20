# Verification and acceptance

- Verify skill metadata parser and installation paths; check local/global/project installs without overwriting existing directories by default.
- Compare recorded third-party SDKs and cookie inventory with browser/desktop/mobile runtime; audit network calls and tag managers where authorized.
- Run project build/lint/tests. For consent, cover denial, acceptance, revocation, storage failure, changed consent version, first page load and no prior third-party requests where required.
- For legal pages, check route existence, navigation/footer links, language, keyboard access, focus, viewport, and document version.
- For data rights requests, test anti-impersonation, rate limits, safe error messages and real backend workflows; never claim working integration from a static form.
- Compare policy statements with code and vendor contracts. For retention, check database, cache, backup and third-party deletion path; record unknowns.
- State every test command and exit status. If browser/devices/test services unavailable, mark untested; never substitute synthetic tests for end-to-end verification.
- Audit files from prior runs are append-only or versioned; do not discard developer changes. Never infer legal certification from green tests.
