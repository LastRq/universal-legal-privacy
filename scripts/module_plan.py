"""Offline modular audit planner. No legal decisions, scanning or writes."""
import argparse
import json
import re
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "references/modular/catalog.json"
COUNTS = {"sectors": 40, "models": 24, "capabilities": 35}
FIELDS = {"id", "activation", "investigate", "controls", "review"}


def load_catalog(path=CATALOG):
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data["modules"]
    if set(groups) != set(COUNTS):
        raise ValueError("Unexpected module categories")
    for category, count in COUNTS.items():
        items = groups[category]
        ids = [item["id"] for item in items]
        if len(items) != count or len(set(ids)) != count:
            raise ValueError(f"Invalid count or duplicate in {category}")
        for item in items:
            if set(item) != FIELDS or any(not isinstance(v, str) or not v.strip() for v in item.values()):
                raise ValueError(f"Invalid module in {category}")
            if not re.fullmatch(r"[a-z][a-z0-9-]*", item["id"]):
                raise ValueError("Invalid module identifier")
    return groups


def plan(selection, jurisdictions=(), candidates=None):
    groups = load_catalog()
    candidates = {} if candidates is None else candidates
    for supplied in (selection, candidates):
        if set(supplied) - set(groups):
            raise ValueError("Unknown module category")
        for category, ids in supplied.items():
            if not isinstance(ids, (list, tuple)) or not all(isinstance(i, str) for i in ids):
                raise ValueError("Expected a list of module IDs")
            if set(ids) - {item["id"] for item in groups[category]}:
                raise ValueError(f"Unknown module ID in {category}")
    active, pending = [], []
    for category, items in groups.items():
        chosen = set(selection.get(category, []))
        tentative = set(candidates.get(category, [])) - chosen
        for item in items:
            if item["id"] in chosen:
                active.append({"category": category, **item})
            elif item["id"] in tentative:
                pending.append({"category": category, "id": item["id"], "activation": item["activation"]})
    markets = sorted(set(jurisdictions))
    return {
        "status": "research-required",
        "modules": active,
        "candidate_modules": pending,
        "jurisdictions_to_verify": markets,
        "blockers": (["Confirm applicable jurisdictions"] if not markets else [])
            + (["Resolve candidate module applicability"] if pending else [])
            + (["Confirm sector and business model or document why not applicable"]
               if not selection.get("sectors") or not selection.get("models") else [])
            + ["Verify official legal sources and applicability",
               "Resolve material facts and conflicts; obtain required review and approvals"],
        "note": "Selected modules are audit scope, not verified obligations. No publication authorized.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List the full module catalog")
    for category in COUNTS:
        parser.add_argument("--" + category, nargs="*", default=[])
        parser.add_argument("--candidate-" + category, nargs="*", default=[])
    parser.add_argument("--jurisdiction", action="append", default=[])
    args = parser.parse_args()
    try:
        result = load_catalog() if args.list else plan(
            {k: getattr(args, k) for k in COUNTS},
            args.jurisdiction,
            {k: getattr(args, "candidate_" + k) for k in COUNTS},
        )
        print(json.dumps(result, ensure_ascii=True, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
