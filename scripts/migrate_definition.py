"""
Migrate definition.json from old schema to new schema.

Changes applied:
  1. Ship statistics: list of single-key objects → flat dict
  2. Pilot statistics: full list with nulls → sparse `stat_overrides` dict
  3. Pilot field renames:
       limit (int 0|1)    → unique (bool)
       actions            → extra_actions
       upgrade_slots      → extra_upgrade_slots
  4. Upgrade boolean strings → real booleans (autoinclude, epic, solitary)
  5. Variable cost attribute key: {"attribute": "x", ...} → {"type": "by_x", ...}
  6. Upgrade restrictions: always-full object with nulls → sparse object
     (only fields with non-null / non-empty / non-zero values are kept)

Usage:
    python scripts/migrate_definition.py [input] [output]

Defaults:
    input  = data/definition.json
    output = data/definition.json  (in-place)
"""
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bool_str(v) -> bool:
    """Convert "True"/"False" string (or actual bool) to real bool."""
    if isinstance(v, bool):
        return v
    return str(v) == "True"


def _migrate_ship_statistics(stats_list: list) -> dict:
    """[{"attacks": [...]}, {"agility": 3}, ...] → {"attacks": [...], "agility": 3, ...}"""
    out = {}
    for obj in stats_list:
        for k, v in obj.items():
            out[k] = v
    return out


def _stat_has_value(value) -> bool:
    """Return True if a pilot stat value is a real override (not all-null)."""
    if value is None:
        return False
    if isinstance(value, list):
        return bool(value)  # non-empty list counts as override
    if isinstance(value, dict):
        return any(v is not None for v in value.values())
    return True  # int/float/bool


def _migrate_pilot_statistics(pilot_stats_list: list) -> dict:
    """Convert full pilot stats list to a sparse stat_overrides dict."""
    overrides = {}
    for obj in pilot_stats_list:
        for k, v in obj.items():
            if _stat_has_value(v):
                overrides[k] = v
    return overrides


def _migrate_pilot(pilot: dict) -> dict:
    p = dict(pilot)

    # statistics → stat_overrides (sparse)
    p["stat_overrides"] = _migrate_pilot_statistics(p.pop("statistics", []))

    # limit (0=generic, 1=unique) → unique (bool)
    p["unique"] = bool(p.pop("limit", 0))

    # actions → extra_actions
    p["extra_actions"] = p.pop("actions", [])

    # upgrade_slots → extra_upgrade_slots
    p["extra_upgrade_slots"] = p.pop("upgrade_slots", [])

    return p


def _migrate_ship(ship: dict) -> dict:
    s = dict(ship)

    # statistics: list → flat dict
    if isinstance(s.get("statistics"), list):
        s["statistics"] = _migrate_ship_statistics(s["statistics"])

    # recurse into pilots
    s["pilots"] = [_migrate_pilot(p) for p in s.get("pilots", [])]

    return s


def _migrate_faction(faction: dict) -> dict:
    f = dict(faction)
    f["ships"] = [_migrate_ship(ship) for ship in f.get("ships", [])]
    return f


# ---------------------------------------------------------------------------
# Restriction migration: always-full → sparse
# ---------------------------------------------------------------------------

def _range_has_value(rng: dict) -> bool:
    return rng.get("low") is not None or rng.get("high") is not None


def _adv_range_has_value(adv: dict) -> bool:
    """e.g. {"shield": {"low":1,"high":3}, "recharge": {...}, "decharge": {...}}"""
    return any(_range_has_value(v) for v in adv.values() if isinstance(v, dict))


def _migrate_restrictions(restrictions: dict) -> dict:
    """Keep only restriction fields that carry actual constraints."""
    out = {}

    # limit: 0 means "no restriction"
    if restrictions.get("limit"):
        out["limit"] = restrictions["limit"]

    # simple range fields
    for key in ("pilot_initiative", "pilot_limit", "attacks", "agility", "hull"):
        val = restrictions.get(key)
        if val and _range_has_value(val):
            out[key] = val

    # list fields
    for key in ("factions", "ships", "base_sizes", "arc_types", "keywords",
                "other_equipped_upgrades"):
        val = restrictions.get(key)
        if val:
            out[key] = val

    # advanced range fields (shield/force/energy/charge)
    for key in ("shield", "force", "energy", "charge"):
        val = restrictions.get(key)
        if val and _adv_range_has_value(val):
            out[key] = val

    # actions (list of action dicts)
    if restrictions.get("actions"):
        out["actions"] = restrictions["actions"]

    return out


# ---------------------------------------------------------------------------
# Cost migration: {"attribute": "x", ...} → {"type": "by_x", ...}
# ---------------------------------------------------------------------------

def _migrate_cost(cost):
    if isinstance(cost, int):
        return cost
    if not isinstance(cost, dict):
        return cost
    c = dict(cost)
    attribute = c.pop("attribute", None)
    if attribute is not None:
        c["type"] = f"by_{attribute}"
    return c


# ---------------------------------------------------------------------------
# Upgrade migration
# ---------------------------------------------------------------------------

def _migrate_upgrade(upgrade: dict) -> dict:
    u = dict(upgrade)

    # string booleans → real booleans
    for flag in ("autoinclude", "epic", "solitary"):
        if flag in u:
            u[flag] = _bool_str(u[flag])

    # variable cost attribute → type
    u["cost"] = _migrate_cost(u.get("cost"))

    # sparse restrictions
    if "restrictions" in u:
        u["restrictions"] = _migrate_restrictions(u["restrictions"])

    return u


# ---------------------------------------------------------------------------
# Top-level migration
# ---------------------------------------------------------------------------

def migrate(data: dict) -> dict:
    out = {}
    out["factions"] = [_migrate_faction(f) for f in data.get("factions", [])]
    out["upgrades"] = [_migrate_upgrade(u) for u in data.get("upgrades", [])]
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    repo_root = Path(__file__).resolve().parent.parent
    default_input = repo_root / "data" / "definition.json"

    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_input
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

    with open(input_path) as f:
        old_data = json.load(f)

    new_data = migrate(old_data)

    with open(output_path, "w") as f:
        json.dump(new_data, f, indent=4)

    factions = new_data["factions"]
    ships = sum(len(fa["ships"]) for fa in factions)
    pilots = sum(len(s["pilots"]) for fa in factions for s in fa["ships"])
    upgrades = len(new_data["upgrades"])
    print(f"Migrated: {len(factions)} factions, {ships} ships, {pilots} pilots, {upgrades} upgrades")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    main()
