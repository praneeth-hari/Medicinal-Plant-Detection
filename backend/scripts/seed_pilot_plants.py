"""
Seed Pilot Plants — Evidence-Based
====================================
Validates and seeds the 5 pilot plants (Tulsi, Neem, Ashwagandha, Turmeric, Bael)
into the database using the finalised evidence schema.

Steps
-----
1. Import pilot plants
2. Validate each plant with PlantValidator (abort on BLOCKING violation)
3. Upsert each plant into the database via evidence_to_db_fields()
4. Print a verification table showing computed + legacy fields for all 5 plants
"""
from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.future import select

from config.database import async_session_maker
from models.plant import Plant
from schemas.plant_validator import PlantValidator, ViolationSeverity
from utils.plant_serializer import evidence_to_db_fields

from pilot_plants import PILOT_PLANTS


# ── Validation ────────────────────────────────────────────────────────────────

def validate_all(plants) -> bool:
    """Validate all pilot plants. Returns True only when zero BLOCKING violations."""
    validator = PlantValidator()
    all_passed = True

    print("\n" + "=" * 70)
    print("  VALIDATION REPORT")
    print("=" * 70)

    for plant in plants:
        result = validator.validate(plant)

        blocking = result.blocking_violations
        warnings = result.warning_violations
        infos    = result.info_violations

        status = "[PASS]" if not blocking else "[BLOCKED]"
        print(f"\n{status} {plant.common_name} ({plant.scientific_name})")
        print(f"  Blocking: {len(blocking)}  Warnings: {len(warnings)}  Info: {len(infos)}")

        for v in blocking:
            print(f"  [BLOCKING] {v.rule_id} | {v.field_path}: {v.message}")
        for v in warnings:
            print(f"  [WARNING]  {v.rule_id} | {v.field_path}: {v.message}")
        for v in infos:
            print(f"  [INFO]     {v.rule_id} | {v.field_path}: {v.message}")

        if blocking:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("  All 5 plants passed validation — no BLOCKING violations.")
    else:
        print("  ABORT: One or more plants have BLOCKING violations.")
        print("  Fix all BLOCKING issues before seeding.")
    print("=" * 70 + "\n")

    return all_passed


# ── Database upsert ───────────────────────────────────────────────────────────

async def upsert_plants(plants) -> list[Plant]:
    """Insert or update all 5 pilot plants. Returns the ORM rows after commit."""
    seeded: list[Plant] = []

    async with async_session_maker() as session:
        for evidence_plant in plants:
            db_fields = evidence_to_db_fields(evidence_plant)

            query = select(Plant).where(
                Plant.scientific_name == evidence_plant.scientific_name
            )
            result = await session.execute(query)
            existing = result.scalars().first()

            if existing:
                for key, value in db_fields.items():
                    setattr(existing, key, value)
                print(f"  Updated : {evidence_plant.common_name}")
                seeded.append(existing)
            else:
                new_plant = Plant(**db_fields)
                session.add(new_plant)
                print(f"  Inserted: {evidence_plant.common_name}")
                seeded.append(new_plant)

        await session.commit()

        # Reload to get server-generated ids and timestamps
        reloaded: list[Plant] = []
        for orm_row in seeded:
            await session.refresh(orm_row)
            reloaded.append(orm_row)

    return reloaded


# ── Verification table ────────────────────────────────────────────────────────

def _trunc(s: str | None, n: int = 28) -> str:
    if not s:
        return "(none)"
    return s[:n] + "..." if len(s) > n else s


def print_verification_table(plants: list[Plant]) -> None:
    """Print a compact table verifying key computed and legacy columns."""
    col_w = [22, 26, 20, 20, 6, 30]
    headers = [
        "Common Name",
        "Evidence Strength",
        "Safety Class",
        "Review Status",
        "ID",
        "medicinal_uses (preview)",
    ]

    sep = "+" + "+".join("-" * (w + 2) for w in col_w) + "+"

    def row(*cells):
        parts = []
        for cell, w in zip(cells, col_w):
            s = str(cell)
            parts.append(f" {s:<{w}} ")
        return "|" + "|".join(parts) + "|"

    print("\n" + "=" * 70)
    print("  VERIFICATION TABLE — POST-SEED DATABASE STATE")
    print("=" * 70)
    print(sep)
    print(row(*headers))
    print(sep)

    for p in plants:
        print(row(
            _trunc(p.common_name, col_w[0]),
            _trunc(p.evidence_strength, col_w[1]),
            _trunc(p.safety_class, col_w[2]),
            _trunc(p.review_status, col_w[3]),
            p.id,
            _trunc(p.medicinal_uses, col_w[5]),
        ))

    print(sep)

    print("\n  Legacy field spot-check:")
    for p in plants:
        mu_ok   = bool(p.medicinal_uses)
        prec_ok = bool(p.precautions)
        prep_ok = bool(p.preparation_methods)
        flag = "[OK]" if (mu_ok and prec_ok and prep_ok) else "[MISSING]"
        print(
            f"  {flag} {p.common_name:20s} "
            f"medicinal_uses={'Y' if mu_ok else 'N'}  "
            f"precautions={'Y' if prec_ok else 'N'}  "
            f"preparation_methods={'Y' if prep_ok else 'N'}"
        )

    print("\n  Computed field spot-check:")
    expected = {
        # Tulsi/Ashwagandha both have pregnancy Contraindication → CONTRAINDICATED
        "Tulsi":       ("Limited Clinical Evidence",  "Contraindicated in Groups", "Reviewed"),
        "Neem":        ("Moderate Clinical Evidence", "Contraindicated in Groups", "Reviewed"),
        "Ashwagandha": ("Strong Clinical Evidence",   "Contraindicated in Groups", "Reviewed"),
        "Turmeric":    ("Moderate Clinical Evidence", "Contraindicated in Groups", "Reviewed"),
        "Bael":        ("Limited Clinical Evidence",  "Use With Caution",          "Pending Review"),
    }

    all_ok = True
    for p in plants:
        exp = expected.get(p.common_name)
        if not exp:
            continue
        ev_ok   = p.evidence_strength == exp[0]
        sc_ok   = p.safety_class      == exp[1]
        rs_ok   = p.review_status     == exp[2]
        ok = ev_ok and sc_ok and rs_ok
        if not ok:
            all_ok = False
        flag = "[OK]" if ok else "[MISMATCH]"
        print(
            f"  {flag} {p.common_name:20s} "
            f"ev={'OK' if ev_ok else 'FAIL'}  "
            f"safety={'OK' if sc_ok else 'FAIL'}  "
            f"review={'OK' if rs_ok else 'FAIL'}"
        )
        if not ev_ok:
            print(f"         evidence  expected='{exp[0]}'  got='{p.evidence_strength}'")
        if not sc_ok:
            print(f"         safety    expected='{exp[1]}'  got='{p.safety_class}'")
        if not rs_ok:
            print(f"         review    expected='{exp[2]}'  got='{p.review_status}'")

    print()
    if all_ok:
        print("  All computed fields match expected values.")
    else:
        print("  WARNING: Some computed fields did not match expectations.")
        print("  Review pilot_plants.py and plant_serializer.py for discrepancies.")

    print("=" * 70 + "\n")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    print("\n" + "=" * 70)
    print("  PILOT PLANT SEEDER")
    print("  Plants : Tulsi, Neem, Ashwagandha, Turmeric, Bael")
    print("  Schema : EvidenceBasedPlant (Phase 1 finalised)")
    print("=" * 70)

    # Step 1 — Validate
    passed = validate_all(PILOT_PLANTS)
    if not passed:
        print("Seeding aborted due to BLOCKING validation violations.")
        sys.exit(1)

    # Step 2 — Seed
    print("Seeding to database...")
    orm_rows = await upsert_plants(PILOT_PLANTS)
    print(f"  Committed {len(orm_rows)} plants.\n")

    # Step 3 — Verify
    print_verification_table(orm_rows)

    print("Phase 3 complete. Awaiting review before proceeding to Phase 4.")


if __name__ == "__main__":
    asyncio.run(main())
