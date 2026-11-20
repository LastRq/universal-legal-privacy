# Consent and cookie engineering

First decide whether consent is required for each specific technology under each applicable law. Do not deploy banners where unnecessary. For jurisdiction-requiring prior consent, block non-essential scripts, requests, cookies and SDK initialization BEFORE permission; avoid preloading trackers. Treat analytics, advertising, personalization, essential functionality separately according to actual purposes.

UI should provide equivalent accessible choices for accept, reject and configure when required; use accessible headings, keyboard focus, readable text and an always-reachable preference link. No conversational chatbot. Explain purposes and vendors; avoid dark patterns. Persist versioned choices only for justified duration, without setting tracking prior to consent. Keep consent receipts proportionate and privacy-preserving when evidence is needed; document basis and storage. Respect withdrawal and re-consent when material changes legally warrant it.

For native apps, distinguish webview cookies, device identifiers, OS permissions, push notifications, local storage and SDK initialization. Browser `localStorage` consent values are not universal: assess jurisdiction, security, cross-domain and multi-device needs before reuse.

The example in `assets/consent-example/` is a **non-production reference**, not a drop-in declaration of compliance. It only gates client-side initialization of optional capabilities registered through its API. Real third-party scripts already in HTML, build-time imports, tag managers, server-side tracking and network requests must be audited and blocked separately.

Verification: test first visit, reload, accept, reject, category selection, withdrawal, multi-tab behavior (if applicable), accessibility, keyboard, locale, storage failures, script loading before/after, and consent-version changes. Evidence must include actual runtime behavior, not just UI screenshots.
