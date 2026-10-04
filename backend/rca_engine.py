import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "supply_chain_exceptions.csv"


def load_exceptions():
    """Load supply chain exceptions from the existing CSV."""
    return pd.read_csv(DATA_FILE)


def build_rca_evidence(row):
    """Build deterministic evidence for one supply chain exception."""

    evidence = {
        "material_id": row["material_id"],
        "plant_id": row["plant_id"],
        "exception_type": row["exception_type"],
        "exception_status": row["exception_status"],
        "risk_score": int(row["risk_score"]),
        "demand": {},
        "supply": {},
        "inventory": {},
        "transport": {},
    }

    # Demand evidence
    if row["demand_risk_flag"] == 1:
        evidence["demand"] = {
            "risk_flag": True,
            "demand_qty": int(row["demand_qty"]),
            "order_count": int(row["order_count"]),
        }

    # Supply evidence
    if row["supply_risk_flag"] == 1:
        evidence["supply"] = {
            "risk_flag": True,
            "open_po_qty": int(row["open_po_qty"]),
            "late_open_schedule_lines": int(
                row["late_open_schedule_lines"]
            ),
        }

    # Inventory evidence
    if row["inventory_risk_flag"] == 1:
        evidence["inventory"] = {
            "risk_flag": True,
            "unrestricted_stock": int(row["unrestricted_stock"]),
            "safety_stock": int(row["safety_stock"]),
            "reorder_point": int(row["reorder_point"]),
        }

    # Transport evidence
    if row["transport_risk_flag"] == 1:
        evidence["transport"] = {
            "risk_flag": True,
            "delayed_shipments": int(row["delayed_shipments"]),
            "on_time_delivery_pct": float(
                row["on_time_delivery_pct"]
            ),
        }

    return evidence


def get_rca_evidence(material_id, plant_id):
    """Return deterministic RCA evidence for a material and plant."""

    df = load_exceptions()

    match = df[
        (df["material_id"] == material_id)
        & (df["plant_id"] == plant_id)
    ]

    if match.empty:
        return {
            "error": (
                f"No exception found for "
                f"{material_id} at {plant_id}"
            )
        }

    row = match.iloc[0]

    return build_rca_evidence(row)


if __name__ == "__main__":

    result = get_rca_evidence(
        "MAT049",
        "PL004"
    )

    print("\nRCA EVIDENCE")
    print("=" * 50)
    print(result)