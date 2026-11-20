# Technical data-map checklist

1. Identify applications and services independently; inventory user, employee, customer, patient, child, merchant and third-party contexts.
2. Trace fields and categories from UI forms, account flows, notifications, camera/microphone/location/biometrics, background tasks, authentication, logging and tracking into API calls, queues, persistent stores and external processors.
3. For each processing activity collect: operator/role, data subjects, categories, origin, purpose, asserted basis (must be confirmed), necessity, recipients, country/location if known, transfers, safeguards, security controls, retention/deletion/copy behavior, user control, proof/source.
4. Compare documented deletion with database cascades, cache, backups, analytics, logs, third-party deletion and irreversible exports. Never invent a retention period.
5. Mark unobservable runtime behavior, configurable cloud regions, contracts and third-party training settings as `unknown` unless verified from actual configuration/contract.
6. Review cross-tenant boundaries, multi-entity roles, access control, export requests and breach response. Do not access production personal data without separate authorization.
7. Treat scanners/dependencies as candidate signals only; demonstrate actual execution paths and run network/SDK tests in approved nonproduction environments before claiming facts.
