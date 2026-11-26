#!/usr/bin/env python3
"""Read-only platform and capability triage. No runtime execution or legal conclusions."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
from ulp import SKIP_DIRS, SKIP_NAME, PATTERNS, MAX_BYTES

# Only source code is read; manifests are identified by name without reading contents.
SOURCE_EXT = {".js", ".jsx", ".ts", ".tsx", ".py", ".rs", ".go", ".java", ".kt",
              ".kts", ".swift", ".vue", ".svelte", ".html", ".php", ".cs", ".dart",
              ".rb", ".cpp", ".c", ".h", ".hpp", ".gd", ".lua", ".sh", ".ps1"}
PRIVATE_DIR = re.compile(r"^(?:data|userdata|user-data|users|profiles|records|secrets|credentials|keys|vaults|exports|backups|dumps|logs|uploads|storage|databases|fixtures|testdata|samples|\.ssh|\.aws|\.gnupg)$", re.I)
PLATFORM_NAMES = {
    "index.html": "web",
    "next.config.js": "web", "next.config.ts": "web", "next.config.mjs": "web",
    "angular.json": "web", "vite.config.ts": "web-or-webview", "vite.config.js": "web-or-webview",
    "tauri.conf.json": "desktop", "tauri.conf.json5": "desktop",
    "electron-builder.yml": "desktop", "electron.vite.config.ts": "desktop",
    "androidmanifest.xml": "android", "info.plist": "apple-platform",
    "capacitor.config.ts": "hybrid", "capacitor.config.json": "hybrid",
    "pubspec.yaml": "dart-or-flutter", "project.godot": "game",
    "projectsettings.asset": "game", "dockerfile": "infrastructure",
    "compose.yaml": "infrastructure", "docker-compose.yml": "infrastructure",
    "manifest.json": "manifest-needs-classification", "openapi.yaml": "api",
    "openapi.json": "api", "swagger.json": "api", "pyproject.toml": "python-project",
    "cargo.toml": "rust-project", "package.json": "javascript-project",
    "go.mod": "go-project", "pom.xml": "jvm-project",
}
EXTRA = {
    "cryptography": r"Argon2|XChaCha20|AESGCM|AES-GCM|scrypt|PBKDF2|crypto\.subtle|keyring|Keychain|DPAPI",
    "credential-vault": r"(?i)\b(?:passwordVault|vaultItem|totp|otpauth|seedPhrase|mnemonicPhrase|apiKey)\b",
    "network-egress": r"(?i)\b(?:fetch|axios|reqwest|HttpClient|URLSession|WebSocket|requests\.post)\b",
    "export-backup": r"(?i)\b(?:exportVault|importVault|backupVault|exportData|restoreBackup)\b",
    "sync": r"(?i)\b(?:syncEngine|syncVault|syncDevice|cloudSync|devicePairing)\b",
    "native-bridge": r"tauri::command|#\[tauri::command\]|ipcMain|ipcRenderer|MethodChannel",
    "clipboard": r"(?i)\b(?:navigator\.clipboard|ClipboardManager|Clipboard\.SetText|clipboard::)\b",
    "updates": r"(?i)\b(?:autoUpdater|tauri_plugin_updater|checkForUpdates|UpdateManager)\b",
    "extension": r"chrome\.runtime|chrome\.storage|browser\.runtime|browser\.storage",
    "cli": r"argparse\.ArgumentParser|clap::Parser|commander\.program|click\.command",
    "api-server": r"FastAPI\(|express\(|axum::Router|@RestController|app\.MapGet",
}
RULES = {**PATTERNS, **{k: re.compile(v) for k, v in EXTRA.items()}}
CANDIDATE_MODULES = {
    "cryptography": ("encryption", "security"), "credential-vault": ("security", "authentication"),
    "sync": ("device-sync",), "export-backup": ("portability", "retention"),
    "analytics-provider": ("cookies-trackers", "third-party-services"),
    "advertising-provider": ("personalized-advertising", "third-party-services"),
    "auth-system": ("authentication",), "precise-location": ("geolocation",),
    "potential-health-data": ("sensitive-data",), "payment-provider": ("payments",),
    "ai-provider": ("artificial-intelligence", "third-party-services"),
    "crash-reporting": ("third-party-services",), "browser-storage": ("cookies-trackers",),
}
MAX_ENTRIES = 40000
MAX_SIGNALS = 3000


def audit(root, max_files=4000, max_entries=MAX_ENTRIES):
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or not 1 <= max_files <= 20000 or not 1 <= max_entries <= MAX_ENTRIES:
        raise ValueError("Invalid project or scan limits")
    signals, platforms = [], []
    categories, omissions = Counter(), Counter()
    examined = scanned = 0
    truncated = False
    candidates = set()
    def walk_error(_):
        omissions["directory-error"] += 1
    for parent, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        examined += len(dirs)
        if examined > max_entries:
            truncated = True
            break
        kept = []
        for d in sorted(dirs):
            if (d in SKIP_DIRS or d.startswith(".") or PRIVATE_DIR.fullmatch(d)
                    or SKIP_NAME.search(d) or (Path(parent) / d).is_symlink()):
                omissions["excluded-directory"] += 1
            else:
                kept.append(d)
        dirs[:] = kept
        for name in sorted(files):
            examined += 1
            if examined > max_entries or scanned >= max_files:
                truncated = True
                break
            p = Path(parent) / name
            if name.startswith(".") or SKIP_NAME.search(name):
                omissions["excluded-name"] += 1
                continue
            try:
                st = p.lstat()
                if not stat.S_ISREG(st.st_mode) or not p.resolve().is_relative_to(root):
                    omissions["non-regular-or-external"] += 1
                    continue
                rel = p.relative_to(root).as_posix()
                platform = PLATFORM_NAMES.get(name.lower())
                if name.lower().endswith((".csproj", ".sln")):
                    platform = "dotnet-project"
                elif name.lower().endswith(".uproject"):
                    platform = "game"
                if platform and len(platforms) < MAX_SIGNALS:
                    platforms.append({"file": rel, "platform": platform, "confidence": "candidate-only"})
                elif platform:
                    omissions["platform-limit"] += 1
                if p.suffix.lower() not in SOURCE_EXT:
                    continue
                if st.st_size > MAX_BYTES:
                    omissions["oversize-source"] += 1
                    continue
                scanned += 1
                with p.open("rb") as f:
                    raw = f.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES or b"\x00" in raw:
                    omissions["oversize-or-binary"] += 1
                    continue
                for n, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
                    for label, rule in RULES.items():
                        if rule.search(line):
                            categories[label] += 1
                            candidates.update(CANDIDATE_MODULES.get(label, ()))
                            if len(signals) < MAX_SIGNALS:
                                signals.append({"file": rel, "line": n, "signal": label,
                                                "confidence": "candidate-only"})
                            else:
                                omissions["signal-limit"] += 1
            except OSError:
                omissions["file-error"] += 1
        if truncated:
            break
    return {"status": "manual-review-required", "mode": "read-only-project-triage",
            "entries_examined": examined, "source_files_attempted": scanned, "truncated": truncated,
            "omissions": dict(omissions), "platform_candidates": platforms,
            "signal_categories": dict(categories), "signals": signals,
            "candidate_modules": {"capabilities": sorted(candidates)},
            "limitations": ["Manifest names and source patterns are candidates only.",
                            "Excluded paths and non-source files require separate safe review.",
                            "No runtime, legal, sector or jurisdiction determination; no absence claims."]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--max-files", type=int, default=4000)
    args = p.parse_args()
    try:
        print(json.dumps(audit(args.project, args.max_files), indent=2, ensure_ascii=True))
    except (OSError, ValueError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
