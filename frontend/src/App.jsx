import { useEffect, useState } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

function App() {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rca, setRca] = useState(null);
  const [loadingRca, setLoadingRca] = useState(false);

  const [apiError, setApiError] = useState("");
  const [rcaError, setRcaError] = useState("");

  const loadExceptions = async () => {
    setLoading(true);
    setApiError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/exceptions`
      );

      if (!response.ok) {
        throw new Error(
          `API returned ${response.status}`
        );
      }

      const data = await response.json();

      setExceptions(data);
    } catch (error) {
      console.error(error);

      setExceptions([]);

      setApiError(
        "Control Tower API is currently unavailable."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExceptions();
  }, []);

  const handleRca = async (
    materialId,
    plantId
  ) => {

    setLoadingRca(true);
    setRca(null);
    setRcaError("");

    try {

      const response = await fetch(
        `${API_BASE_URL}/api/rca/${materialId}/${plantId}`
      );

      if (!response.ok) {
        throw new Error(
          `RCA API returned ${response.status}`
        );
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setRca(data);

    } catch (error) {

      console.error(error);

      setRcaError(
        "Unable to generate RCA for this exception."
      );

    } finally {

      setLoadingRca(false);

    }
  };

  const supplyRiskCount =
    exceptions.filter(
      (x) => x.exception_type === "SUPPLY_RISK"
    ).length;

  const transportRiskCount =
    exceptions.filter(
      (x) => x.exception_type === "TRANSPORT_RISK"
    ).length;

  const inventoryRiskCount =
    exceptions.filter(
      (x) => x.exception_type === "INVENTORY_RISK"
    ).length;

  const showMetrics = !loading && !apiError;

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        background: "#f5f7fa",
        minHeight: "100vh",
      }}
    >

      <h1>
        Supply Chain Control Tower
      </h1>

      <p>
        Enterprise Supply Chain Visibility Dashboard
      </p>

      {/* KPI SECTION */}

      <h2>
        Key Performance Indicators
      </h2>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginBottom: "30px",
          flexWrap: "wrap",
        }}
      >

        <KpiCard
          title="Total Exceptions"
          value={
            showMetrics
              ? exceptions.length
              : loading
              ? "..."
              : "—"
          }
        />

        <KpiCard
          title="Supply Risks"
          value={
            showMetrics
              ? supplyRiskCount
              : loading
              ? "..."
              : "—"
          }
        />

        <KpiCard
          title="Transport Risks"
          value={
            showMetrics
              ? transportRiskCount
              : loading
              ? "..."
              : "—"
          }
        />

        <KpiCard
          title="Inventory Risks"
          value={
            showMetrics
              ? inventoryRiskCount
              : loading
              ? "..."
              : "—"
          }
        />

      </div>

      {/* API ERROR */}

      {apiError && (

        <div
          style={{
            background: "#fff3f3",
            border: "1px solid #ffcccc",
            padding: "20px",
            marginBottom: "25px",
            borderRadius: "8px",
          }}
        >

          <strong>
            Dashboard connection problem
          </strong>

          <p>
            {apiError}
          </p>

          <button
            onClick={loadExceptions}
            style={{
              padding: "10px 16px",
              cursor: "pointer",
            }}
          >
            Retry Connection
          </button>

        </div>

      )}

      {/* EXCEPTIONS */}

      <h2>
        Supply Chain Exceptions
      </h2>

      {!apiError && (

        <div
          style={{
            background: "white",
            borderRadius: "8px",
            overflow: "auto",
          }}
        >

          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >

            <thead>

              <tr
                style={{
                  background: "#eef1f5",
                }}
              >

                <th style={cellStyle}>
                  Material
                </th>

                <th style={cellStyle}>
                  Plant
                </th>

                <th style={cellStyle}>
                  Exception
                </th>

                <th style={cellStyle}>
                  Status
                </th>

                <th style={cellStyle}>
                  Risk Score
                </th>

                <th style={cellStyle}>
                  RCA
                </th>

              </tr>

            </thead>

            <tbody>

              {exceptions.map(
                (exception, index) => (

                  <tr key={index}>

                    <td style={cellStyle}>
                      {exception.material_id}
                    </td>

                    <td style={cellStyle}>
                      {exception.plant_id}
                    </td>

                    <td style={cellStyle}>
                      {exception.exception_type}
                    </td>

                    <td style={cellStyle}>
                      {exception.exception_status}
                    </td>

                    <td style={cellStyle}>
                      {exception.risk_score}
                    </td>

                    <td style={cellStyle}>

                      <button
                        onClick={() =>
                          handleRca(
                            exception.material_id,
                            exception.plant_id
                          )
                        }
                        style={{
                          padding: "8px 14px",
                          cursor: "pointer",
                        }}
                      >
                        View RCA
                      </button>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

      {/* RCA LOADING */}

      {loadingRca && (

        <div
          style={{
            marginTop: "30px",
            padding: "25px",
            background: "white",
            borderRadius: "8px",
          }}
        >

          <h2>
            Generating RCA...
          </h2>

          <p>
            Analyzing supply-chain evidence.
          </p>

        </div>

      )}

      {/* RCA ERROR */}

      {rcaError && (

        <div
          style={{
            marginTop: "30px",
            padding: "20px",
            background: "#fff3f3",
            border: "1px solid #ffcccc",
            borderRadius: "8px",
          }}
        >

          {rcaError}

        </div>

      )}

      {/* RCA PANEL */}

      {rca && !loadingRca && (

        <div
          style={{
            marginTop: "30px",
            padding: "25px",
            background: "white",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >

          <h2>
            AI Root Cause Analysis
          </h2>

          <p>

            <strong>
              Analysis Status:
            </strong>{" "}

            {rca.ai_status === "available"
              ? "Gemini AI"
              : "Deterministic fallback"}

          </p>

          {rca.ai_message && (

            <p
              style={{
                color: "#9a6700",
              }}
            >
              {rca.ai_message}
            </p>

          )}

          <h3>
            {rca.rca?.headline}
          </h3>

          <p>
            <strong>
              Material:
            </strong>{" "}
            {rca.evidence?.material_id}
          </p>

          <p>
            <strong>
              Plant:
            </strong>{" "}
            {rca.evidence?.plant_id}
          </p>

          <p>
            <strong>
              Exception:
            </strong>{" "}
            {rca.evidence?.exception_type}
          </p>

          <p>
            <strong>
              Risk Score:
            </strong>{" "}
            {rca.evidence?.risk_score}
          </p>

          <hr />

          <h3>
            Root Cause
          </h3>

          <p>
            {rca.rca?.root_cause}
          </p>

          <h3>
            Evidence
          </h3>

          <ul>

            {rca.rca?.evidence?.map(
              (item, index) => (
                <li key={index}>
                  {item}
                </li>
              )
            )}

          </ul>

          <h3>
            Business Impact
          </h3>

          <p>
            {rca.rca?.business_impact}
          </p>

          <h3>
            Recommended Action
          </h3>

          <p>
            {rca.rca?.recommended_action}
          </p>

          <h3>
            Owner
          </h3>

          <p>
            {rca.rca?.owner}
          </p>

          <h3>
            Confidence
          </h3>

          <p>
            {rca.rca?.confidence}
          </p>

        </div>

      )}

    </div>
  );
}

function KpiCard({
  title,
  value,
}) {

  return (

    <div
      style={{
        background: "white",
        padding: "20px",
        minWidth: "180px",
        borderRadius: "8px",
        border: "1px solid #ddd",
      }}
    >

      <h3>
        {title}
      </h3>

      <p
        style={{
          fontSize: "28px",
          fontWeight: "bold",
          margin: 0,
        }}
      >
        {value}
      </p>

    </div>

  );
}

const cellStyle = {
  padding: "12px",
  borderBottom: "1px solid #ddd",
  textAlign: "left",
};

export default App;