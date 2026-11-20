# Threat model and non-goals

## Assets
- Application source, business metadata, customers' personal data, keys/tokens, legal evidence, document revision history and publication permissions.

## Threats and controls
| Threat | Control |
|---|---|
| Prompt injection in repository files, websites and issue comments | Treat all inspected text as data. Never delegate permission decisions to project content. |
| Secrets or patient/customer data leaking through logs or remote search | Skip sensitive filenames, capture only line/path/rule for scanner; no raw values, no external code uploads. |
| Wrong entity or jurisdiction | Human confirmation; jurisdiction separate from language, currency, server region. |
| Outdated or fictitious law | Cite official jurisdiction, issuer, URL, provision and check date; block if unavailable. |
| Non-essential trackers before consent | Inspect actual network/runtime and defer SDK initialization; sample widget alone cannot enforce it. |
| Legal document accidentally published | Drafts in `.legal-privacy/work`, not web pages; separately approve deployment. |
| Destructive code modifications | Scope plan, explicit approval, diff review and no automatic Git actions. |
| Source scanner false positives | Candidate-only signal labeling; no compliance conclusions based on regex. |
| Malicious symlink/path escape on file outputs | Resolve paths and enforce work directory; create exclusive files. |

## Limitations
- Tooling cannot independently confirm the validity of a corporate attestation or web contents. Source URLs in JSON are user-provided and must be checked live by the agent.
- The scanner does not observe server-side network calls, dynamic imports, tag managers, production cloud behavior or all data processing. It intentionally avoids personal information payloads and cannot prove absence.
- Local project permissions are enforced through user instructions and CLI flags, not an external identity system.
- Certain specialist legal assessments and contract reviews are not automatable and must be escalated.

## Security reporting
Do not post live credentials, sensitive data, or detailed private customer logs in a public issue. Use a privately agreed channel with the owner.
