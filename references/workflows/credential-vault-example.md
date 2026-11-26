# Credential vault audit fixture (synthetic; not a finding about any real app)

Scenario: a desktop/web/mobile vault may store passwords, API keys, wallet information and TOTP secrets. Platform and feature facts must be established from source. Start read-only; never access actual vault contents.

| Question | Required evidence | Result before inspection |
|---|---|---|
| Local-only or remote? | storage implementation, sync routes, update/crash/analytics config and isolated runtime test | Unknown |
| Encryption and key custody? | KDF/AEAD configuration, key storage and recovery implementation | Unknown |
| Exports and deletion? | export/backup/delete code and synthetic tests | Unknown |
| Data controller and jurisdiction? | owner-confirmed entity, distribution/markets and official sources | Unknown |
| Existing legal disclosures? | legal screen, website, installer, store listing, license notices | Unknown |

Example invocation: ask the agent to audit the current project with Universal Legal & Privacy, using this reference and the universal workflow. Start with discovery and report; do not generate or integrate documents until facts, permissions and legal sources are verified.
