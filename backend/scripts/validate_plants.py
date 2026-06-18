"""
Plant Validation CLI
====================
Validates EvidenceBasedPlant instances and prints a structured report.

Usage:
    cd backend
    python scripts/validate_plants.py

Add plants to PLANTS_TO_VALIDATE below as they are written.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.plant_validator import PlantValidator, ViolationSeverity, ValidationResult

validator = PlantValidator()


def print_result(result: ValidationResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    b = result.blocking_count
    w = result.warning_count
    i = result.info_count

    print(f"\n{'=' * 70}")
    print(f"  [{status}]  {result.plant_name}")
    print(f"  Blocking: {b}   Warnings: {w}   Info: {i}")
    print(f"{'=' * 70}")

    if not result.violations:
        print("  No violations found.")
        return

    for sev in (ViolationSeverity.BLOCKING, ViolationSeverity.WARNING, ViolationSeverity.INFO):
        group = [v for v in result.violations if v.severity == sev]
        if not group:
            continue
        print(f"\n  {sev.value}S ({len(group)}):")
        for v in group:
            print(f"    {v.rule_id}  [{v.field_path}]")
            print(f"         {v.message}")


def run_all(plants) -> bool:  # type: ignore[no-untyped-def]
    """Validate all plants. Returns True if all pass."""
    results = [validator.validate(p) for p in plants]
    all_passed = all(r.passed for r in results)

    for r in results:
        print_result(r)

    total_blocking = sum(r.blocking_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    total_info     = sum(r.info_count for r in results)

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY — {len(results)} plants validated")
    print(f"  Total blocking:  {total_blocking}")
    print(f"  Total warnings:  {total_warnings}")
    print(f"  Total info:      {total_info}")
    overall = "ALL PASSED" if all_passed else f"{sum(1 for r in results if not r.passed)} FAILED"
    print(f"  Result:          {overall}")
    print(f"{'=' * 70}")

    return all_passed


if __name__ == "__main__":
    # Import pilot plants here as they are written.
    # Example:
    #   from scripts.pilot_plants import TULSI, NEEM, ASHWAGANDHA, TURMERIC, BAEL
    #   sys.exit(0 if run_all([TULSI, NEEM, ASHWAGANDHA, TURMERIC, BAEL]) else 1)

    print("No plants loaded. Add pilot plants to PLANTS_TO_VALIDATE in this script.")
    sys.exit(0)
