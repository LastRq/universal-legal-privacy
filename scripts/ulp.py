#!/usr/bin/env python3
"""Universal Legal & Privacy: conservative local helpers. Python stdlib only.

None of these commands researches laws, certifies compliance, makes Git changes,
or deploys. Filesystem changes require explicit flags AND prior human approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

NAME = "universal-legal-privacy"
VERSION = "1.2.0"
ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 512_000
MAX_RESULTS = 3000
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".legal-privacy", "node_modules", "vendor", "dist", "build",
    "target", "coverage", ".next", ".nuxt", ".venv", "venv", "__pycache__", ".turbo",
    ".cache", "out", ".gradle", ".idea", ".tox", "Pods", ".dart_tool"
}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".py", ".rs", ".go", ".java", ".kt",
            ".swift", ".vue", ".svelte", ".html", ".php", ".cs", ".dart", ".rb", ".sql",
            ".json", ".toml", ".yaml", ".yml", ".xml", ".gradle", ".properties"}
SKIP_NAME = re.compile(r"(^\.env(?:\.|$)|secret|credential|private[_-]?key|\.pem$|\.p12$|\.pfx$|\.keystore$|\.lock$|\.min\.js$|package-lock\.json$|pnpm-lock\.yaml$|yarn\.lock$|(^|[_.-])backup([_.-]|$)|dump\.sql$)", re.I)
# Pattern descriptions are *signals*, never evidence that data was processed or disclosed.
PATTERNS = {
    "form-input": re.compile(r"<form\b|<input\b|formdata\b|request\.form\b", re.I),
    "contact-data": re.compile(r"(?:email|phone|telephone|postalAddress|contactInfo)[\s\"'_:={<(]", re.I),
    "precise-location": re.compile(r"navigator\.geolocation|ACCESS_FINE_LOCATION|requestLocationUpdates|CLLocationManager", re.I),
    "potential-health-data": re.compile(r"(?:patient|medicalRecord|diagnosis|clinicalHistory|dentalChart)[\s\"'_:={<(]", re.I),
    "payment-provider": re.compile(r"(?:@stripe/|stripe\.com|paypal\.com|mercadopago|@paypal/)", re.I),
    "analytics-provider": re.compile(r"google-analytics\.com|googletagmanager\.com|gtag\(|@vercel/analytics|mixpanel|posthog", re.I),
    "advertising-provider": re.compile(r"facebook\.net/en_US/fbevents|fbq\(|doubleclick\.net|tiktok-pixel", re.I),
    "firebase-sdk": re.compile(r"(?:firebase/app|firebase/auth|firebase/firestore|com\.google\.firebase)", re.I),
    "supabase-sdk": re.compile(r"(?:@supabase/|supabase\.com|createClient\()", re.I),
    "crash-reporting": re.compile(r"(?:@sentry/|sentry\.io|crashlytics)", re.I),
    "ai-provider": re.compile(r"(?:api\.openai\.com|@anthropic-ai/|generativelanguage\.googleapis\.com|@google/generative-ai)", re.I),
    "browser-storage": re.compile(r"(?:localStorage|sessionStorage|indexedDB|document\.cookie)", re.I),
    "server-storage": re.compile(r"(?:sqlite|postgres|prisma|sqlcipher|s3\.putObject|INSERT\s+INTO)", re.I),
    "permission-prompt": re.compile(r"(?:Notification\.requestPermission|permissions\.request|requestPermissions)", re.I),
    "consent-control": re.compile(r"(?:cookieConsent|consentManager|CookieBanner|ConsentProvider|consent_preferences)", re.I),
    "auth-system": re.compile(r"(?:signInWith|authenticate\(|OAuth|AuthProvider|sessionCookie)", re.I),
    "data-deletion": re.compile(r"(?:deleteAccount|erasePersonalData|deleteUserData|requestErasure)", re.I),
}


class UsageError(Exception):
    pass


def json_print(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def real_path(raw: str) -> Path:
    p = Path(raw).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise UsageError(f"Project directory does not exist: {raw}")
    return p


def work_area(project: Path) -> Path:
    return project / ".legal-privacy" / "work"


def require_work_permission(args: argparse.Namespace) -> None:
    if not getattr(args, "approve_workfiles", False):
        raise UsageError("Write refused: obtain human approval of workfile scope, then supply --approve-workfiles")


def safe_work_output(project: Path, relative: str) -> Path:
    dest = (project / relative).resolve()
    area = work_area(project).resolve()
    if not dest.is_relative_to(area):
        raise UsageError("Output must be inside the approved non-public .legal-privacy/work/ directory")
    if dest.exists():
        raise UsageError("Refusing to overwrite an existing workfile")
    return dest


def write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(path.parent, 0o700)
    except OSError:
        pass
    # Exclusive creation prevents unintended overwrite and symlink attacks on output files.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def iter_project_files(project: Path, max_files: int):
    examined = 0
    for parent, dirs, files in os.walk(project, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(parent) / d).is_symlink())
        for filename in sorted(files):
            candidate = Path(parent) / filename
            if candidate.is_symlink() or SKIP_NAME.search(filename) or candidate.suffix.lower() not in CODE_EXT:
                continue
            try:
                if not candidate.resolve().is_relative_to(project) or candidate.stat().st_size > MAX_BYTES:
                    continue
            except OSError:
                continue
            examined += 1
            if examined > max_files:
                return
            yield candidate


def scan_project(project: Path, max_files: int = 8000) -> dict:
    signals: list[dict] = []
    count = 0
    omitted = 0
    for file in iter_project_files(project, max_files):
        count += 1
        try:
            with file.open("r", encoding="utf-8", errors="replace") as f:
                for line_no, line in enumerate(f, 1):
                    if "\x00" in line:
                        break
                    # No source lines, personal values or matching substrings in output.
                    for rule, pattern in PATTERNS.items():
                        if pattern.search(line):
                            if len(signals) < MAX_RESULTS:
                                signals.append({"file": file.relative_to(project).as_posix(),
                                                "line": line_no, "signal": rule, "confidence": "candidate-only"})
                            else:
                                omitted += 1
        except (OSError, UnicodeError):
            continue
    return {
        "tool": NAME, "version": VERSION, "mode": "read-only-candidate-scan",
        "generated_on": date.today().isoformat(), "files_scanned": count,
        "max_files": max_files, "signals_count": len(signals), "signals_omitted": omitted,
        "signal_categories": dict(sorted(Counter(x["signal"] for x in signals).items())),
        "signals": signals,
        "disclaimer": "Candidate indicators, NOT proof of collection, vendor configuration, legality or absence of tracking. No source excerpts or values retained."
    }


def command_scan(args):
    project = real_path(args.project)
    report = scan_project(project, args.max_files)
    if args.out:
        require_work_permission(args)
        dest = safe_work_output(project, args.out)
        write_private(dest, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote non-public candidate scan: {dest.relative_to(project).as_posix()}")
    else:
        json_print(report)


def blank_profile() -> dict:
    return {
        "schema_version": 1,
        "owner_attestation": {"confirmed": False, "confirmed_on": "", "role": ""},
        "entity": {"legal_name": "", "country": "", "privacy_contact": "", "role": ""},
        "project": {"name": "", "description": "", "business_model": "", "audience": "", "languages": [], "service_countries": []},
        "processing": [],
        "vendors": [],
        "cookies": [],
        "terms": {"service_scope": "", "eligibility": "", "user_obligations": "", "termination": "", "payment_terms": ""},
        "legal_sources": [],
        "review": {"specialist_required": False, "specialist_review_confirmed": False}
    }


def command_init(args):
    require_work_permission(args)
    project = real_path(args.project)
    dest = safe_work_output(project, ".legal-privacy/work/profile.json")
    write_private(dest, json.dumps(blank_profile(), indent=2, ensure_ascii=False) + "\n")
    print(f"Created a blank, non-public profile: {dest.relative_to(project)}")
    print("Fill only human-confirmed facts. Never commit this profile without review.")


def text_field(obj: dict, key: str, label: str, errors: list):
    v = obj.get(key, "") if isinstance(obj, dict) else ""
    if not isinstance(v, str) or not v.strip() or v.strip().upper() in {"TBD", "TODO", "UNKNOWN", "PENDING", "N/A"}:
        errors.append(f"Missing verified field: {label}")
    return v


def list_field(obj: dict, key: str, label: str, errors: list):
    v = obj.get(key, []) if isinstance(obj, dict) else None
    if not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v):
        errors.append(f"Missing or invalid list: {label}")
    return v if isinstance(v, list) else []


def read_profile(path: str) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.is_file() or p.is_symlink():
        raise UsageError("Profile must be a regular local JSON file")
    if p.stat().st_size > 256_000:
        raise UsageError("Profile exceeds size limit")
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise UsageError(f"Profile JSON invalid: {e}") from e
    if not isinstance(obj, dict):
        raise UsageError("Profile must be a JSON object")
    return obj


def validate_profile(obj: dict, kinds: list[str]) -> list[str]:
    errors: list[str] = []
    if obj.get("schema_version") != 1:
        errors.append("Unsupported schema_version; expected 1")
    att = obj.get("owner_attestation") or {}
    if not isinstance(att, dict) or att.get("confirmed") is not True:
        errors.append("Owner attestation must be explicitly confirmed")
    else:
        text_field(att, "role", "owner_attestation.role", errors)
        try:
            if date.fromisoformat(att.get("confirmed_on", "")) > date.today():
                errors.append("owner_attestation.confirmed_on must not be future-dated")
        except (TypeError, ValueError):
            errors.append("owner_attestation.confirmed_on requires an ISO date")
    entity, proj = obj.get("entity") or {}, obj.get("project") or {}
    for key in ("legal_name", "country", "privacy_contact", "role"):
        text_field(entity, key, f"entity.{key}", errors)
    for key in ("name", "description", "business_model", "audience"):
        text_field(proj, key, f"project.{key}", errors)
    list_field(proj, "languages", "project.languages", errors)
    markets = list_field(proj, "service_countries", "project.service_countries", errors)
    sources = obj.get("legal_sources")
    if not isinstance(sources, list) or not sources:
        errors.append("At least one current, official legal source is required")
    else:
        covered = set()
        for i, src in enumerate(sources):
            label = f"legal_sources[{i}]"
            if not isinstance(src, dict):
                errors.append(f"{label} must be an object")
                continue
            for key in ("jurisdiction", "authority", "title", "url", "section", "checked_on", "applies_to"):
                text_field(src, key, f"{label}.{key}", errors)
            url = src.get("url", "")
            if not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{label}.url must be an official HTTPS address")
            if src.get("verified_from_official_site") is not True:
                errors.append(f"{label} must be human/agent-verified against official source")
            try:
                checked = date.fromisoformat(src.get("checked_on", ""))
                days = (date.today() - checked).days
                if not 0 <= days <= 120:
                    errors.append(f"{label} must be reverified: consultation older than 120 days or future-dated")
            except (TypeError, ValueError):
                errors.append(f"{label}.checked_on requires an ISO date")
            if isinstance(src.get("jurisdiction"), str):
                covered.add(src["jurisdiction"].strip().casefold())
        for market in markets:
            if market.casefold() not in covered:
                errors.append(f"No verified official source for service country: {market}")
    if "privacy" in kinds:
        operations = obj.get("processing")
        if not isinstance(operations, list) or not operations:
            errors.append("Privacy draft requires at least one verified processing activity")
        else:
            for i, op in enumerate(operations):
                label = f"processing[{i}]"
                if not isinstance(op, dict):
                    errors.append(f"{label} must be an object")
                    continue
                for k in ("purpose", "legal_basis", "retention", "source_of_data", "deletion_process"):
                    text_field(op, k, f"{label}.{k}", errors)
                for k in ("data_categories", "recipients", "transfer_countries"):
                    # Lists must exist, but can be empty if genuinely no recipients/foreign transfers.
                    if not isinstance(op.get(k), list) or any(not isinstance(v, str) for v in op[k]):
                        errors.append(f"{label}.{k} must be a list, possibly empty")
                if op.get("verified") is not True:
                    errors.append(f"{label}.verified must be true after tracing actual data handling")
    if "terms" in kinds:
        terms = obj.get("terms") or {}
        for k in ("service_scope", "eligibility", "user_obligations", "termination"):
            text_field(terms, k, f"terms.{k}", errors)
    if "cookies" in kinds:
        cookies = obj.get("cookies")
        if not isinstance(cookies, list) or not cookies:
            errors.append("Cookie draft requires a verified inventory; do not invent cookies")
        else:
            for i, cookie in enumerate(cookies):
                if not isinstance(cookie, dict):
                    errors.append(f"cookies[{i}] must be an object")
                    continue
                for k in ("name", "provider", "purpose", "category", "duration", "control"):
                    text_field(cookie, k, f"cookies[{i}].{k}", errors)
                if cookie.get("verified") is not True:
                    errors.append(f"cookies[{i}].verified must be true")
    return errors


def command_validate(args):
    profile = read_profile(args.profile)
    kinds = sorted(set(args.types.split(",")))
    if any(kind not in {"privacy", "terms", "cookies"} for kind in kinds):
        raise UsageError("Supported draft types: privacy,terms,cookies")
    errors = validate_profile(profile, kinds)
    json_print({"status": "valid" if not errors else "blocked", "errors": errors, "checked_types": kinds,
                "note": "Structural and attestation checks only. Official legal contents require independent human review."})
    if errors:
        sys.exit(2)


def markdown_clean(v: str) -> str:
    # Prevent arbitrary markup/embedded script in generated public-facing draft.
    return re.sub(r"[<>]", "", str(v)).strip().replace("\r", " ")


def li(items: list) -> str:
    if not items:
        return "- None identified in the confirmed inventory (verify this statement before publication)."
    return "\n".join(f"- {markdown_clean(x)}" for x in items)


def draft_header(kind: str, profile: dict) -> str:
    e, p = profile["entity"], profile["project"]
    return (f"# {kind} — {markdown_clean(p['name'])}\n\n"
            "> **DRAFT — NOT APPROVED FOR PUBLICATION.** Requires owner acceptance and any mandated specialist review.\n\n"
            f"- Prepared: {date.today().isoformat()}\n"
            f"- Legal operator: {markdown_clean(e['legal_name'])} ({markdown_clean(e['country'])})\n"
            f"- Controller/processor role as confirmed: {markdown_clean(e['role'])}\n"
            f"- Privacy contact: {markdown_clean(e['privacy_contact'])}\n"
            f"- Languages to review: {', '.join(map(markdown_clean, p['languages']))}\n"
            f"- Countries served: {', '.join(map(markdown_clean, p['service_countries']))}\n\n")


def draft_sources(profile: dict) -> str:
    lines = ["## Source register (internal audit; remove or adapt for published version)", ""]
    for src in profile["legal_sources"]:
        lines.append(f"- {markdown_clean(src['jurisdiction'])}: {markdown_clean(src['authority'])} — "
                     f"{markdown_clean(src['title'])}, § {markdown_clean(src['section'])}, "
                     f"consulted {markdown_clean(src['checked_on'])}. URL: {src['url']}")
    lines.append("\nThis register documents research inputs, not a declaration of legal compliance.\n")
    return "\n".join(lines)


def make_privacy(profile: dict) -> str:
    e, p = profile["entity"], profile["project"]
    lines = [draft_header("Privacy Notice", profile),
             "## Service and operator\n", markdown_clean(p["description"]) + "\n",
             f"Business model: {markdown_clean(p['business_model'])}. Audience: {markdown_clean(p['audience'])}.\n",
             "## Verified processing activities\n"]
    for op in profile["processing"]:
        lines += [f"### {markdown_clean(op['purpose'])}",
                  f"- Data categories: {', '.join(map(markdown_clean, op['data_categories'])) or 'No personal data confirmed'}",
                  f"- Source: {markdown_clean(op['source_of_data'])}",
                  f"- Legal basis (confirmed; legal review required): {markdown_clean(op['legal_basis'])}",
                  f"- Recipients: {', '.join(map(markdown_clean, op['recipients'])) or 'None confirmed'}",
                  f"- International destinations: {', '.join(map(markdown_clean, op['transfer_countries'])) or 'None confirmed'}",
                  f"- Retention: {markdown_clean(op['retention'])}",
                  f"- Deletion/erasure route: {markdown_clean(op['deletion_process'])}\n"]
    lines += ["## Questions and rights requests\n",
              f"Contact the confirmed privacy point of contact: {markdown_clean(e['privacy_contact'])}. "
              "The applicable rights, verification procedure, deadlines and appeal paths require jurisdiction-specific legal review.\n",
              draft_sources(profile)]
    return "\n".join(lines)


def make_terms(profile: dict) -> str:
    p, t = profile["project"], profile["terms"]
    return (draft_header("Terms of Service", profile)
            + f"## Service\n\n{markdown_clean(t['service_scope'])}\n\n"
            + f"## Audience and eligibility\n\n{markdown_clean(t['eligibility'])}\n\n"
            + f"## User responsibilities\n\n{markdown_clean(t['user_obligations'])}\n\n"
            + f"## Ending use of the service\n\n{markdown_clean(t['termination'])}\n\n"
            + (f"## Payments and billing\n\n{markdown_clean(t.get('payment_terms', ''))}\n\n" if t.get("payment_terms") else "")
            + "## Legal review pending\n\nApplicable mandatory consumer protections, withdrawal rights, "
              "warranties, liability and disputes must be determined from official sources and verified contracts "
              "before release. This draft does not waive statutory rights.\n\n"
            + draft_sources(profile))


def make_cookies(profile: dict) -> str:
    lines = [draft_header("Cookie and Device Storage Notice", profile),
             "## Verified technologies\n",
             "| Name | Provider | Purpose | Category | Duration | Control |",
             "|---|---|---|---|---|---|"]
    for c in profile["cookies"]:
        lines.append("| " + " | ".join(markdown_clean(c[k]).replace("|", "\\|") for k in
                        ("name", "provider", "purpose", "category", "duration", "control")) + " |")
    lines += ["\n## Consent and preferences\n",
              "Implement and test prior blocking, rejection and withdrawal for technologies that require it. "
              "The actual preference interface, vendors, jurisdiction-specific exemptions and retention "
              "of preference records must be validated against the running product.\n",
              draft_sources(profile)]
    return "\n".join(lines)


def command_draft(args):
    require_work_permission(args)
    project = real_path(args.project)
    kinds = [x.strip() for x in args.types.split(",")]
    if not kinds or any(x not in {"privacy", "terms", "cookies"} for x in kinds):
        raise UsageError("Choose privacy,terms,cookies")
    profile = read_profile(args.profile)
    errors = validate_profile(profile, kinds)
    if errors:
        json_print({"status": "blocked", "errors": errors})
        sys.exit(2)
    if profile.get("review", {}).get("specialist_required") and not profile.get("review", {}).get("specialist_review_confirmed"):
        raise UsageError("Specialist review required but not confirmed; block affected legal drafting")
    tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    funcs = {"privacy": make_privacy, "terms": make_terms, "cookies": make_cookies}
    outputs = []
    for kind in kinds:
        path = safe_work_output(project, f".legal-privacy/work/drafts/{tag}-{kind}.md")
        write_private(path, funcs[kind](profile) + "\n")
        outputs.append(path.relative_to(project).as_posix())
    json_print({"status": "draft-created-not-for-publication", "paths": outputs,
                "caution": "Structural validation is not independent legal source verification."})


INSTALL_PATHS = {
    "antigravity": (".agents/skills", ".gemini/config/skills"),
    "claude": (".claude/skills", ".claude/skills"),
    "codex": (".agents/skills", ".agents/skills"),
}


def skill_file_filter(root: Path):
    excluded = {".git", ".github", "tests", "docs", "examples", "adapters", ".pytest_cache", "__pycache__"}
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in excluded and not (Path(current)/d).is_symlink())
        for name in sorted(files):
            p = Path(current) / name
            if p.is_symlink() or p.suffix == ".pyc" or name.startswith("."):
                continue
            yield p, p.relative_to(root)


def command_install(args):
    if not args.approve_install:
        raise UsageError("Install refused: obtain approval, then supply --approve-install")
    parent = (real_path(args.project) if args.scope == "project" else Path.home())
    rel = INSTALL_PATHS[args.agent][0 if args.scope == "project" else 1]
    target = parent / rel / NAME
    if target.resolve().is_relative_to(ROOT.resolve()):
        raise UsageError("Refusing recursive installation inside the package source directory")
    if target.exists():
        raise UsageError(f"Target exists; refusing to overwrite: {target}")
    if not (ROOT / "SKILL.md").is_file():
        raise UsageError("Skill root SKILL.md not found")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Stage within target parent to ensure same-filesystem atomic directory rename.
    temp = Path(tempfile.mkdtemp(prefix=".ulp-stage-", dir=target.parent))
    try:
        for src, relfile in skill_file_filter(ROOT):
            dest = temp / relfile
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        if not (temp / "SKILL.md").is_file():
            raise UsageError("Staged package missing SKILL.md")
        temp.rename(target)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    print(f"Installed for {args.agent} ({args.scope}): {target}")
    print("Restart agent session or reload skills where supported. No project code was modified.")


def command_verify(args):
    root = real_path(args.root)
    failures = []
    manifest = root / "SKILL.md"
    if not manifest.exists():
        failures.append("Missing SKILL.md")
    else:
        contents = manifest.read_text(encoding="utf-8")
        if not contents.startswith("---\n") or f"name: {NAME}" not in contents or "description:" not in contents:
            failures.append("Missing required Agent Skills frontmatter")
    required = ["LICENSE", "COPYRIGHT.md", "references/workflows/permissions.md", "references/legal-research/source-policy.md",
                "references/consent/implementation.md", "scripts/ulp.py",
                "references/modular/catalog.json", "references/modular/workflow.md", "scripts/module_plan.py",
                "references/workflows/universal-project-audit.md", "references/workflows/credential-vault-example.md",
                "scripts/project_audit.py"]
    for p in required:
        if not (root / p).is_file():
            failures.append(f"Missing required resource: {p}")
    license_path = root / "LICENSE"
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text or "END OF TERMS AND CONDITIONS" not in license_text:
            failures.append("LICENSE file does not appear to contain the full Apache License 2.0")
    if manifest.is_file() and "license: Apache-2.0" not in manifest.read_text(encoding="utf-8"):
        failures.append("SKILL.md metadata does not declare Apache-2.0")
    json_print({"package": str(root), "status": "pass" if not failures else "fail", "failures": failures,
                "note": "Package structure check only; does not execute Antigravity, Claude or Codex."})
    if failures:
        sys.exit(2)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Conservative local helpers for Universal Legal & Privacy")
    parser.add_argument("--version", action="version", version=VERSION)
    sp = parser.add_subparsers(dest="command", required=True)
    scan = sp.add_parser("scan", help="Read-only candidate signal scan; no legal conclusions")
    scan.add_argument("--project", required=True)
    scan.add_argument("--max-files", type=int, default=8000)
    scan.add_argument("--out", help="Explicit path under PROJECT/.legal-privacy/work/")
    scan.add_argument("--approve-workfiles", action="store_true")
    scan.set_defaults(func=command_scan)
    init = sp.add_parser("init-profile", help="Create blank private profile after approval")
    init.add_argument("--project", required=True)
    init.add_argument("--approve-workfiles", action="store_true")
    init.set_defaults(func=command_init)
    val = sp.add_parser("validate-profile", help="Validate verified profile fields (not legal correctness)")
    val.add_argument("--profile", required=True)
    val.add_argument("--types", default="privacy,terms,cookies")
    val.set_defaults(func=command_validate)
    draft = sp.add_parser("draft", help="Create private evidence-backed DRAFT only after approval")
    draft.add_argument("--project", required=True)
    draft.add_argument("--profile", required=True)
    draft.add_argument("--types", default="privacy")
    draft.add_argument("--approve-workfiles", action="store_true")
    draft.set_defaults(func=command_draft)
    install = sp.add_parser("install", help="Copy skill to agent scope after approval")
    install.add_argument("--agent", choices=sorted(INSTALL_PATHS), required=True)
    install.add_argument("--scope", choices=["project", "global"], required=True)
    install.add_argument("--project", help="Project path; required for project scope")
    install.add_argument("--approve-install", action="store_true")
    install.set_defaults(func=command_install)
    verify = sp.add_parser("verify-bundle", help="Check portable bundle layout")
    verify.add_argument("--root", default=str(ROOT))
    verify.set_defaults(func=command_verify)
    args = parser.parse_args(argv)
    try:
        if args.command == "install" and args.scope == "project" and not args.project:
            raise UsageError("--project required for project-scoped install")
        if getattr(args, "max_files", 1) <= 0:
            raise UsageError("--max-files must be positive")
        args.func(args)
    except UsageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
