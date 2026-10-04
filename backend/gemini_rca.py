import os
import json
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()


def generate_gemini_rca(evidence):
    """
    Send deterministic supply-chain evidence to Gemini
    and return a structured RCA response.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")

    prompt = f"""
You are a Supply Chain Control Tower RCA assistant.

Analyze ONLY the evidence provided below.

Do not invent numbers.
Do not create evidence that is not present.
Do not recalculate unavailable metrics.

Return the response as valid JSON with exactly these fields:

{{
  "headline": "...",
  "root_cause": "...",
  "evidence": [
    "...",
    "..."
  ],
  "business_impact": "...",
  "recommended_action": "...",
  "owner": "...",
  "confidence": "High|Medium|Low"
}}

Supply-chain evidence:

{json.dumps(evidence, indent=2)}
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash-lite:generateContent"
        f"?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(request, timeout=60) as response:

            response_data = json.loads(
                response.read().decode("utf-8")
            )

        text = response_data["candidates"][0]["content"]["parts"][0]["text"]

        return json.loads(text)

    except urllib.error.HTTPError as error:

        error_body = error.read().decode("utf-8")

        raise RuntimeError(
            f"Gemini API error {error.code}: {error_body}"
        )

    except Exception as error:

        raise RuntimeError(
            f"Gemini RCA failed: {error}"
        )


if __name__ == "__main__":

    test_evidence = {
        "material_id": "MAT049",
        "plant_id": "PL004",
        "exception_type": "SUPPLY_RISK",
        "exception_status": "OPEN",
        "risk_score": 1,
        "demand": {
            "risk_flag": True,
            "demand_qty": 2946,
            "order_count": 40
        },
        "supply": {
            "risk_flag": True,
            "open_po_qty": 24889,
            "late_open_schedule_lines": 10
        },
        "inventory": {},
        "transport": {}
    }

    result = generate_gemini_rca(test_evidence)

    print("\nGEMINI RCA")
    print("=" * 60)
    print(json.dumps(result, indent=2))