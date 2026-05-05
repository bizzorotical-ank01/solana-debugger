import { useState } from "react";
import axios from "axios";

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const severityColor = {
    funds: "#ef4444",
    bug: "#f97316",
    config: "#eab308",
    cpi: "#8b5cf6",
  };

  async function handleDebug() {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await axios.post(
        "https://solana-debugger-production.up.railway.app/debug",
        {
          input: input.trim(),
        },
        { timeout: 60000 },
      );
      if (res.data.error) {
        setError(res.data.error);
      } else {
        setResult(res.data);
      }
    } catch (e) {
      if (e.code === "ECONNABORTED") {
        setError("Request timed out. Backend may be slow. Try again.");
      } else if (e.response?.status === 500) {
        setError("Backend error. Check your error format and try again.");
      } else {
        setError(
          "Could not connect to backend. Check your internet connection.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setInput("");
    setResult(null);
    setError(null);
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f0f0f",
        color: "#ffffff",
        fontFamily: "monospace",
        padding: "40px 20px",
      }}
    >
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        <h1 style={{ fontSize: "28px", marginBottom: "8px" }}>
          SolanaDebugger
        </h1>
        <p style={{ color: "#888", marginBottom: "32px" }}>
          Paste a failed transaction signature or error log → get an instant
          explanation
        </p>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste transaction signature or error logs here..."
          rows={5}
          style={{
            width: "100%",
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: "8px",
            color: "#fff",
            padding: "16px",
            fontSize: "14px",
            fontFamily: "monospace",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />

        <button
          onClick={handleDebug}
          disabled={loading}
          style={{
            marginTop: "12px",
            padding: "12px 32px",
            background: loading ? "#333" : "#9945ff",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontSize: "16px",
            cursor: loading ? "not-allowed" : "pointer",
            fontFamily: "monospace",
            marginRight: "8px",
          }}
        >
          {loading ? "Analyzing..." : "Debug Transaction →"}
        </button>

        {(result || error) && (
          <button
            onClick={handleClear}
            style={{
              marginTop: "12px",
              padding: "12px 32px",
              background: "#333",
              color: "#888",
              border: "1px solid #555",
              borderRadius: "8px",
              fontSize: "16px",
              cursor: "pointer",
              fontFamily: "monospace",
            }}
          >
            Clear
          </button>
        )}

        {error && (
          <div
            style={{
              marginTop: "24px",
              padding: "16px",
              background: "#1a0000",
              border: "1px solid #ef4444",
              borderRadius: "8px",
              color: "#ef4444",
            }}
          >
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: "32px" }}>
            <div
              style={{
                display: "inline-block",
                padding: "4px 12px",
                borderRadius: "20px",
                background:
                  severityColor[result.ai_explanation.severity] + "22",
                border: `1px solid ${severityColor[result.ai_explanation.severity]}`,
                color: severityColor[result.ai_explanation.severity],
                fontSize: "13px",
                marginBottom: "16px",
              }}
            >
              {result.ai_explanation.severity.toUpperCase()}
            </div>

            <div
              style={{
                background: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                padding: "20px",
                marginBottom: "16px",
              }}
            >
              <h3 style={{ color: "#9945ff", marginTop: 0 }}>
                What went wrong
              </h3>
              <p style={{ margin: 0, lineHeight: "1.6", color: "#ddd" }}>
                {result.ai_explanation.explanation}
              </p>
            </div>

            <div
              style={{
                background: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                padding: "20px",
                marginBottom: "16px",
              }}
            >
              <h3 style={{ color: "#9945ff", marginTop: 0 }}>Root cause</h3>
              <p style={{ margin: 0, color: "#ddd" }}>
                {result.ai_explanation.root_cause}
              </p>
            </div>

            <div
              style={{
                background: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                padding: "20px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <h3 style={{ color: "#9945ff", margin: 0 }}>How to fix it</h3>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(result.ai_explanation.fix);
                    alert("Copied to clipboard!");
                  }}
                  style={{
                    padding: "4px 12px",
                    background: "#333",
                    color: "#9945ff",
                    border: "1px solid #9945ff",
                    borderRadius: "4px",
                    fontSize: "12px",
                    cursor: "pointer",
                    fontFamily: "monospace",
                  }}
                >
                  Copy
                </button>
              </div>
              <pre
                style={{
                  margin: 0,
                  color: "#4ade80",
                  whiteSpace: "pre-wrap",
                  fontSize: "13px",
                }}
              >
                {result.ai_explanation.fix}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
