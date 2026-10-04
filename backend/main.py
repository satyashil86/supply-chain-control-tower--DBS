import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rca_engine import get_rca_evidence
from gemini_rca import generate_gemini_rca

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = FastAPI(
    title="Supply Chain Control Tower API",
    version="2.0.0"
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

frontend_urls = os.getenv(
    "FRONTEND_URLS",
    "http://localhost:5173"
)

allowed_origins = [
    url.strip().rstrip("/")
    for url in frontend_urls.split(",")
    if url.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def read_csv(filename: str):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    return pd.read_csv(file_path)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "Supply Chain Control Tower API",
        "status": "running",
        "version": "2.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# KPI APIs
# ---------------------------------------------------------

@app.get("/api/kpi/inventory")
def inventory_kpi():
    df = read_csv("inventory_kpi.csv")
    return df.to_dict(orient="records")


@app.get("/api/kpi/demand")
def demand_kpi():
    df = read_csv("demand_kpi.csv")
    return df.to_dict(orient="records")


@app.get("/api/kpi/supply")
def supply_kpi():
    df = read_csv("supply_kpi.csv")
    return df.to_dict(orient="records")


@app.get("/api/kpi/transport")
def transport_kpi():
    df = read_csv("transport_kpi.csv")
    return df.to_dict(orient="records")


@app.get("/api/kpi/warehouse")
def warehouse_kpi():
    df = read_csv("warehouse_kpi.csv")
    return df.to_dict(orient="records")


# ---------------------------------------------------------
# Exceptions
# ---------------------------------------------------------

@app.get("/api/exceptions")
def exceptions():
    df = read_csv("supply_chain_exceptions.csv")
    return df.to_dict(orient="records")


# ---------------------------------------------------------
# Deterministic fallback RCA
# ---------------------------------------------------------

def build_fallback_rca(evidence):

    material_id = evidence["material_id"]
    plant_id = evidence["plant_id"]
    exception_type = evidence["exception_type"]

    demand = evidence.get("demand") or {}
    supply = evidence.get("supply") or {}
    inventory = evidence.get("inventory") or {}
    transport = evidence.get("transport") or {}

    evidence_list = []

    if demand:
        evidence_list.append(
            f"Demand quantity is {demand['demand_qty']} "
            f"across {demand['order_count']} orders."
        )

    if supply:
        evidence_list.append(
            f"Open PO quantity is {supply['open_po_qty']} "
            f"with {supply['late_open_schedule_lines']} "
            f"late open schedule lines."
        )

    if inventory:
        evidence_list.append(
            f"Unrestricted stock is {inventory['unrestricted_stock']}, "
            f"safety stock is {inventory['safety_stock']}, "
            f"and reorder point is {inventory['reorder_point']}."
        )

    if transport:
        evidence_list.append(
            f"Delayed shipments are {transport['delayed_shipments']} "
            f"and on-time delivery is "
            f"{transport['on_time_delivery_pct']}%."
        )

    if exception_type == "SUPPLY_RISK":

        root_cause = (
            f"Supply risk is driven by "
            f"{supply.get('late_open_schedule_lines', 0)} "
            f"late open schedule lines."
        )

        action = (
            "Follow up with suppliers on late schedule lines "
            "and confirm recovery dates."
        )

        owner = "Procurement / Supplier Management"

    elif exception_type == "TRANSPORT_RISK":

        root_cause = (
            f"Transport risk is driven by "
            f"{transport.get('delayed_shipments', 0)} "
            f"delayed shipments and an on-time delivery "
            f"of {transport.get('on_time_delivery_pct', 0)}%."
        )

        action = (
            "Review delayed shipments with the carrier "
            "and establish recovery actions."
        )

        owner = "Logistics / Transportation"

    elif exception_type == "INVENTORY_RISK":

        root_cause = (
            "Inventory risk is indicated by the inventory "
            "risk evidence available for this material and plant."
        )

        action = (
            "Review inventory position against safety stock "
            "and replenishment requirements."
        )

        owner = "Inventory Planning"

    else:

        root_cause = (
            f"{exception_type} has been identified for "
            f"{material_id} at {plant_id}."
        )

        action = "Review the available demand and supply evidence."

        owner = "Supply Chain Planning"

    if demand:
        business_impact = (
            f"Potential fulfillment impact against "
            f"{demand['demand_qty']} units of demand "
            f"across {demand['order_count']} orders."
        )
    else:
        business_impact = (
            "Potential supply chain service impact."
        )

    return {
        "headline": (
            f"{exception_type.replace('_', ' ').title()} "
            f"identified for {material_id} at {plant_id}"
        ),
        "root_cause": root_cause,
        "evidence": evidence_list,
        "business_impact": business_impact,
        "recommended_action": action,
        "owner": owner,
        "confidence": "High"
    }


# ---------------------------------------------------------
# AI RCA
# ---------------------------------------------------------

@app.get("/api/rca/{material_id}/{plant_id}")
def rca(material_id: str, plant_id: str):

    evidence = get_rca_evidence(
        material_id,
        plant_id
    )

    if "error" in evidence:
        return evidence

    try:

        ai_rca = generate_gemini_rca(
            evidence
        )

        return {
            "evidence": evidence,
            "rca": ai_rca,
            "ai_status": "available"
        }

    except Exception as error:

        print(
            f"Gemini RCA unavailable: {type(error).__name__}"
        )

        # Do NOT break the dashboard when Gemini
        # is temporarily unavailable.
        fallback = build_fallback_rca(
            evidence
        )

        return {
            "evidence": evidence,
            "rca": fallback,
            "ai_status": "unavailable",
            "ai_message": (
                "AI service temporarily unavailable. "
                "Showing deterministic RCA."
            )
        }