"use client";

import React, { useState, useEffect } from "react";

export default function DrishtiDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [metrics, setMetrics] = useState<any>(null);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [responses, setResponses] = useState<any[]>([]);
  const [mlopsRuns, setMlopsRuns] = useState<any[]>([]);
  const [mlopsStatus, setMlopsStatus] = useState<any>(null);
  const [predictInput, setPredictInput] = useState("ERROR: Database connection timeout");
  const [predictResult, setPredictResult] = useState<any>(null);
  const [predicting, setPredicting] = useState(false);
  const [taxiInput, setTaxiInput] = useState({ trip_distance: 3.5, passenger_count: 1, pickup_hour: 14 });
  const [taxiResult, setTaxiResult] = useState<any>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const refreshData = async () => {
    try {
      const [m, a, h, r, mr, ms] = await Promise.all([
        fetch(`${API_BASE}/incidents/stats`).then(res => res.json()).catch(() => ({})),
        fetch(`${API_BASE}/alerts`).then(res => res.json()).catch(() => ({ alerts: [] })),
        fetch(`${API_BASE}/incidents/history`).then(res => res.json()).catch(() => ({ history: [] })),
        fetch(`${API_BASE}/responses`).then(res => res.json()).catch(() => ({ actions: [] })),
        fetch(`${API_BASE}/mlops/runs`).then(res => res.json()).catch(() => ({ runs: [] })),
        fetch(`${API_BASE}/mlops/model-status`).then(res => res.json()).catch(() => ({})),
      ]);
      setMetrics(m);
      setIncidents(a.alerts || []);
      setHistory(h.history || []);
      setResponses(r.actions || []);
      setMlopsRuns(mr.runs || []);
      setMlopsStatus(ms);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    refreshData();
    const iv = setInterval(refreshData, 5000);
    return () => clearInterval(iv);
  }, []);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: predictInput }),
      });
      const data = await res.json();
      setPredictResult(data);
      refreshData();
    } catch (err: any) {
      alert("Prediction error: " + err.message);
    } finally {
      setPredicting(false);
    }
  };

  const handleResolve = async (id: string) => {
    await fetch(`${API_BASE}/alerts/${id}/resolve`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resolution_notes: "Resolved via Next.js Dashboard" }),
    });
    refreshData();
  };

  const handleTaxiPredict = async () => {
    const res = await fetch(`${API_BASE}/mlops/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taxiInput),
    });
    const d = await res.json();
    setTaxiResult(d);
  };

  const tabs = [
    { id: "overview", name: "Overview Dashboard" },
    { id: "logs", name: "Log Monitoring" },
    { id: "anomaly", name: "Anomaly Detection" },
    { id: "incidents", name: "Incident Management" },
    { id: "responses", name: "Automated Responses" },
    { id: "mlops", name: "Model Performance & MLOps" },
    { id: "health", name: "System Health" },
  ];

  return (
    <div className="flex h-screen bg-[#0b0f19] text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-[#0f172a] border-r border-gray-800 p-4 flex flex-col justify-between">
        <div>
          <div className="p-3 mb-4 flex items-center space-x-3">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center font-bold">D</div>
            <div>
              <div className="font-bold text-sm">DRISHTI AI</div>
              <div className="text-[10px] text-indigo-400 font-mono">MLOps & AIOps Platform</div>
            </div>
          </div>
          <nav className="space-y-1">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`w-full text-left px-3 py-2 rounded text-xs font-medium transition ${
                  activeTab === t.id
                    ? "bg-indigo-600/30 text-indigo-400 border border-indigo-500/40"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
              >
                {t.name}
              </button>
            ))}
          </nav>
        </div>
        <div className="text-[11px] text-gray-500 p-2 border-t border-gray-800">
          Backend: {API_BASE}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 space-y-6">
        <header className="flex justify-between items-center border-b border-gray-800 pb-4">
          <h1 className="text-xl font-bold">{tabs.find((t) => t.id === activeTab)?.name}</h1>
          <button
            onClick={refreshData}
            className="px-3 py-1.5 bg-indigo-600 text-xs rounded hover:bg-indigo-500"
          >
            Refresh
          </button>
        </header>

        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
                <div className="text-xs text-gray-400">Total Incidents</div>
                <div className="text-2xl font-bold mt-1">{metrics?.total_incidents || 0}</div>
              </div>
              <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
                <div className="text-xs text-red-400">Open Incidents</div>
                <div className="text-2xl font-bold text-red-400 mt-1">{metrics?.open_incidents || 0}</div>
              </div>
              <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
                <div className="text-xs text-emerald-400">Resolved Incidents</div>
                <div className="text-2xl font-bold text-emerald-400 mt-1">{metrics?.resolved_incidents || 0}</div>
              </div>
              <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
                <div className="text-xs text-indigo-400">Automated Responses</div>
                <div className="text-2xl font-bold text-indigo-400 mt-1">{responses.length}</div>
              </div>
            </div>

            <div className="p-6 rounded-xl bg-[#111827] border border-gray-800 space-y-3">
              <h2 className="text-sm font-semibold">Live Log Anomaly Detector</h2>
              <form onSubmit={handlePredict} className="flex gap-2">
                <input
                  type="text"
                  value={predictInput}
                  onChange={(e) => setPredictInput(e.target.value)}
                  className="flex-1 bg-[#0b0f19] border border-gray-700 rounded px-3 py-2 text-xs font-mono"
                />
                <button
                  type="submit"
                  disabled={predicting}
                  className="px-4 py-2 bg-indigo-600 rounded text-xs font-semibold"
                >
                  {predicting ? "Analyzing..." : "Analyze Log"}
                </button>
              </form>
              {predictResult && (
                <div className="p-3 rounded bg-[#0b0f19] border border-gray-800 text-xs font-mono">
                  Result: <span className={predictResult.result === "ANOMALY" ? "text-red-400" : "text-emerald-400"}>{predictResult.result}</span> | Features: {predictResult.features_used}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "incidents" && (
          <div className="p-6 rounded-xl bg-[#111827] border border-gray-800">
            <h2 className="text-sm font-semibold mb-4">Incident Queue</h2>
            <table className="w-full text-xs font-mono text-left">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500">
                  <th className="p-2">ID</th>
                  <th className="p-2">Severity</th>
                  <th className="p-2">Message</th>
                  <th className="p-2">Occurrences</th>
                  <th className="p-2">Status</th>
                  <th className="p-2">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {incidents.map((i) => (
                  <tr key={i.id}>
                    <td className="p-2 text-indigo-400">#{i.id}</td>
                    <td className="p-2">{i.severity}</td>
                    <td className="p-2 truncate max-w-xs">{i.message}</td>
                    <td className="p-2">{i.occurrence_count || 1}x</td>
                    <td className="p-2">{i.status}</td>
                    <td className="p-2">
                      {i.status !== "RESOLVED" && (
                        <button
                          onClick={() => handleResolve(i.id)}
                          className="px-2 py-1 bg-emerald-700 text-white rounded text-[10px]"
                        >
                          Resolve
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "mlops" && (
          <div className="p-6 rounded-xl bg-[#111827] border border-gray-800 space-y-4">
            <h2 className="text-sm font-semibold">MLflow Model Serving (Taxi Fare Predictor)</h2>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-gray-400">Distance (mi)</label>
                <input
                  type="number"
                  value={taxiInput.trip_distance}
                  onChange={(e) => setTaxiInput({ ...taxiInput, trip_distance: parseFloat(e.target.value) || 1 })}
                  className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400">Passengers</label>
                <input
                  type="number"
                  value={taxiInput.passenger_count}
                  onChange={(e) => setTaxiInput({ ...taxiInput, passenger_count: parseInt(e.target.value) || 1 })}
                  className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400">Pickup Hour</label>
                <input
                  type="number"
                  value={taxiInput.pickup_hour}
                  onChange={(e) => setTaxiInput({ ...taxiInput, pickup_hour: parseInt(e.target.value) || 12 })}
                  className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs"
                />
              </div>
            </div>
            <button
              onClick={handleTaxiPredict}
              className="px-4 py-2 bg-indigo-600 rounded text-xs font-semibold"
            >
              Predict Trip Duration
            </button>
            {taxiResult && (
              <div className="p-3 rounded bg-[#0b0f19] border border-gray-800 text-xs font-mono space-y-1">
                <div>Predicted Duration: <span className="text-indigo-400">{taxiResult.predicted_duration_minutes} min</span></div>
                <div>Estimated Fare: <span className="text-emerald-400">${taxiResult.estimated_fare_usd}</span></div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

