"""
DRISHTI AI - Professional Multi-Project Dark-Themed Observability Dashboard
Single Page Application powered by React 18, Tailwind CSS, Lucide icons, and Chart.js.
Supports dynamic project selection, universal telemetry inspection, accuracy drift tracking,
and end-to-end incident lifecycle management.
Served directly by FastAPI at /dashboard for instant, zero-dependency local execution.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DRISHTI AI — Universal MLOps & AIOps Platform</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 50: '#eef2ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' },
            dark: { 900: '#0b0f19', 800: '#111827', 700: '#1f2937', 600: '#374151' }
          }
        }
      }
    }
  </script>
  <!-- React 18 & ReactDOM -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <!-- Babel Standalone for JSX -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    body { font-family: 'Inter', sans-serif; background-color: #0b0f19; color: #f3f4f6; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #111827; }
    ::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
  </style>
</head>
<body class="bg-[#0b0f19] text-gray-100 min-h-screen">
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect } = React;

    function SeverityBadge({ severity }) {
      const colors = {
        CRITICAL: "bg-purple-900/40 text-purple-300 border-purple-500/40",
        ERROR: "bg-red-900/40 text-red-300 border-red-500/40",
        WARNING: "bg-amber-900/40 text-amber-300 border-amber-500/40",
        INFO: "bg-blue-900/40 text-blue-300 border-blue-500/40"
      };
      return (
        <span className={`px-2 py-0.5 text-xs font-semibold rounded border ${colors[severity] || colors.INFO}`}>
          {severity || "INFO"}
        </span>
      );
    }

    function StatusBadge({ status }) {
      const colors = {
        OPEN: "bg-red-950/60 text-red-400 border-red-800",
        INVESTIGATING: "bg-amber-950/60 text-amber-400 border-amber-800",
        MITIGATING: "bg-indigo-950/60 text-indigo-400 border-indigo-800",
        RESOLVED: "bg-emerald-950/60 text-emerald-400 border-emerald-800",
        CLOSED: "bg-gray-800 text-gray-400 border-gray-700"
      };
      return (
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${colors[status] || colors.OPEN}`}>
          {status}
        </span>
      );
    }

    function App() {
      const [activeTab, setActiveTab] = useState("overview");
      const [projects, setProjects] = useState([]);
      const [selectedProject, setSelectedProject] = useState("all");
      const [metrics, setMetrics] = useState(null);
      const [incidents, setIncidents] = useState([]);
      const [history, setHistory] = useState([]);
      const [responses, setResponses] = useState([]);
      const [mlopsRuns, setMlopsRuns] = useState([]);
      const [mlopsStatus, setMlopsStatus] = useState(null);
      const [keepStatus, setKeepStatus] = useState(null);
      const [telemetry, setTelemetry] = useState([]);
      const [driftData, setDriftData] = useState(null);
      const [bannerMessage, setBannerMessage] = useState(null);

      // Interactive test states
      const [predictInput, setPredictInput] = useState("ERROR: Database connection timeout");
      const [predictResult, setPredictResult] = useState(null);
      const [predicting, setPredicting] = useState(false);
      const [resolvingId, setResolvingId] = useState(null);
      const [resolveNotes, setResolveNotes] = useState("");
      const [taxiInput, setTaxiInput] = useState({ trip_distance: 3.5, passenger_count: 1, pickup_hour: 14 });
      const [taxiResult, setTaxiResult] = useState(null);
      const [trainingMlops, setTrainingMlops] = useState(false);

      // Project creation modal state
      const [showRegisterModal, setShowRegisterModal] = useState(false);
      const [newProject, setNewProject] = useState({ project_id: "", name: "", description: "", model_type: "regression", framework: "scikit-learn" });
      const [registeredKey, setRegisteredKey] = useState(null);

      const showNotification = (msg) => {
        setBannerMessage(msg);
        setTimeout(() => setBannerMessage(null), 4000);
      };

      const refreshData = async () => {
        try {
          const pParam = selectedProject !== "all" ? `?project_id=${selectedProject}` : "";
          const [projsRes, mRes, aRes, hRes, rRes, mrRes, msRes] = await Promise.all([
            fetch('/projects').then(r => r.json()).catch(() => ({ projects: [] })),
            fetch(`/system/stats${pParam}`).then(r => r.json()).catch(() => ({})),
            fetch(`/alerts${pParam}`).then(r => r.json()).catch(() => ({ alerts: [] })),
            fetch(`/incidents/history${pParam}`).then(r => r.json()).catch(() => ({ history: [] })),
            fetch(`/responses${pParam}`).then(r => r.json()).catch(() => ({ actions: [] })),
            fetch('/mlops/runs').then(r => r.json()).catch(() => ({ runs: [] })),
            fetch('/mlops/model-status').then(r => r.json()).catch(() => ({}))
          ]);

          setProjects(projsRes.projects || []);
          setMetrics(mRes.metrics || {});
          setIncidents(aRes.alerts || []);
          setHistory(hRes.history || []);
          setResponses(rRes.actions || []);
          setMlopsRuns(mrRes.runs || []);
          setMlopsStatus(msRes);
          setKeepStatus(mRes.incidents?.keep_status);

          if (selectedProject !== "all") {
            const [tRes, dRes] = await Promise.all([
              fetch(`/telemetry/${selectedProject}?limit=50`).then(r => r.json()).catch(() => ({ records: [] })),
              fetch(`/telemetry/${selectedProject}/drift`).then(r => r.json()).catch(() => null)
            ]);
            setTelemetry(tRes.records || []);
            setDriftData(dRes);
          } else {
            setTelemetry([]);
            setDriftData(null);
          }
        } catch (err) {
          console.error("Refresh error:", err);
        }
      };

      useEffect(() => {
        refreshData();
        const interval = setInterval(refreshData, 5000);
        return () => clearInterval(interval);
      }, [selectedProject]);

      // Handle Project Registration
      const handleRegisterProject = async (e) => {
        e.preventDefault();
        try {
          const res = await fetch('/projects/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newProject)
          });
          const data = await res.json();
          if (res.ok) {
            setRegisteredKey(data.api_key);
            showNotification(`Project '${data.project.project_id}' registered successfully!`);
            refreshData();
          } else {
            alert(data.detail || "Registration failed");
          }
        } catch (err) {
          alert("Error: " + err.message);
        }
      };

      // Handler for prediction
      const handlePredict = async (e) => {
        e?.preventDefault();
        if (!predictInput.trim()) return;
        setPredicting(true);
        try {
          const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: predictInput, project_id: selectedProject !== 'all' ? selectedProject : 'default' })
          });
          const data = await res.json();
          setPredictResult(data);
          refreshData();
          showNotification(data.result === "ANOMALY" ? "⚠️ Anomaly detected! Incident and safe response created." : "✅ Normal event processed.");
        } catch (err) {
          showNotification("Prediction failed: " + err.message);
        } finally {
          setPredicting(false);
        }
      };

      // Handler for resolving incident
      const handleResolve = async (id) => {
        try {
          const res = await fetch(`/alerts/${id}/resolve`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resolution_notes: resolveNotes || "Resolved from DRISHTI AI Dashboard" })
          });
          if (res.ok) {
            setResolvingId(null);
            setResolveNotes("");
            showNotification(`Incident ${id} successfully resolved.`);
            refreshData();
          }
        } catch (err) {
          showNotification("Resolve error: " + err.message);
        }
      };

      // Handler for triggering remediation
      const handleTriggerRemediation = async (id) => {
        try {
          const res = await fetch(`/responses/trigger/${id}`, { method: 'POST' });
          const data = await res.json();
          showNotification(`Remediation executed: ${data.action.action_name}`);
          refreshData();
        } catch (err) {
          showNotification("Remediation error: " + err.message);
        }
      };

      // Handler for Taxi Fare Predict
      const handleTaxiPredict = async () => {
        try {
          const res = await fetch('/mlops/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taxiInput)
          });
          const data = await res.json();
          setTaxiResult(data);
        } catch (err) {
          showNotification("MLOps predict error: " + err.message);
        }
      };

      const handleRetrain = async () => {
        setTrainingMlops(true);
        try {
          const res = await fetch('/mlops/train', { method: 'POST' });
          const data = await res.json();
          showNotification(`MLOps Model retrained! Run ID: ${data.run_id.slice(0, 8)}`);
          refreshData();
        } catch (err) {
          showNotification("Retrain error: " + err.message);
        } finally {
          setTrainingMlops(false);
        }
      };

      const handlePromote = async () => {
        try {
          const res = await fetch('/mlops/promote', { method: 'POST' });
          const data = await res.json();
          showNotification(data.promoted ? `Model v${data.version} promoted to Production!` : data.reason);
          refreshData();
        } catch (err) {
          showNotification("Promote error: " + err.message);
        }
      };

      const tabs = [
        { id: "overview", name: "Overview Dashboard", icon: "📊" },
        { id: "telemetry", name: "Project Telemetry", icon: "📡" },
        { id: "logs", name: "Log Monitoring", icon: "📑" },
        { id: "anomaly", name: "Anomaly Detection", icon: "🔍" },
        { id: "incidents", name: "Incident Management", icon: "🚨" },
        { id: "responses", name: "Automated Responses", icon: "⚡" },
        { id: "mlops", name: "MLOps & Experiments", icon: "🧠" },
        { id: "health", name: "System Health", icon: "💚" }
      ];

      return (
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 bg-[#0f172a] border-r border-gray-800 flex flex-col justify-between shrink-0">
            <div>
              <div className="px-6 py-5 border-b border-gray-800 flex items-center space-x-3">
                <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/30">
                  D
                </div>
                <div>
                  <h1 className="font-bold text-base tracking-wide text-white">DRISHTI AI</h1>
                  <p className="text-[10px] text-indigo-400 font-mono uppercase tracking-wider">Universal ML Observability</p>
                </div>
              </div>

              {/* Project Selector */}
              <div className="p-3 border-b border-gray-800 bg-[#0b0f19]/40">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Active Workspace</label>
                  <button
                    onClick={() => { setShowRegisterModal(true); setRegisteredKey(null); }}
                    className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    + New Project
                  </button>
                </div>
                <select
                  value={selectedProject}
                  onChange={e => setSelectedProject(e.target.value)}
                  className="w-full bg-[#111827] border border-gray-700 rounded-lg p-2 text-xs font-mono text-gray-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="all">🌐 All Projects (Platform Wide)</option>
                  {projects.map(p => (
                    <option key={p.project_id} value={p.project_id}>
                      📁 {p.name} ({p.project_id})
                    </option>
                  ))}
                </select>
              </div>

              <nav className="p-3 space-y-1">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-semibold"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-gray-800 text-xs text-gray-500 space-y-2">
              <div className="flex items-center justify-between">
                <span>FastAPI Backend</span>
                <span className="flex items-center text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block mr-1.5 animate-pulse"></span>
                  Active v1.1.0
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Keep Adapter</span>
                <span className={keepStatus?.is_connected ? "text-emerald-400 font-mono" : "text-amber-400 font-mono text-[11px]"}>
                  {keepStatus?.is_connected ? "Connected" : "Local Fallback"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Projects Count</span>
                <span className="text-gray-300 font-mono">{projects.length}</span>
              </div>
              <div className="pt-2 text-[10px] text-gray-600 border-t border-gray-800/60 text-center">
                DRISHTI AI • Universal ML Platform
              </div>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 overflow-y-auto bg-[#0b0f19] flex flex-col">
            {/* Header */}
            <header className="h-16 border-b border-gray-800/80 px-8 flex items-center justify-between bg-[#0f172a]/60 backdrop-blur sticky top-0 z-20">
              <div className="flex items-center space-x-4">
                <h2 className="text-lg font-semibold text-white capitalize">{tabs.find(t => t.id === activeTab)?.name}</h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-indigo-900/40 text-indigo-300 border border-indigo-700/50">
                  {selectedProject === "all" ? "All Projects Scope" : `Project: ${selectedProject}`}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <a
                  href="/metrics"
                  target="_blank"
                  className="px-3 py-1.5 rounded-md text-xs font-mono bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700 flex items-center space-x-1"
                >
                  <span>📈</span>
                  <span>Prometheus /metrics</span>
                </a>
                <button
                  onClick={refreshData}
                  className="px-3 py-1.5 rounded-md text-xs bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-sm"
                >
                  Refresh Data
                </button>
              </div>
            </header>

            {/* Notification Banner */}
            {bannerMessage && (
              <div className="bg-indigo-600/90 text-white px-6 py-2.5 text-sm font-medium flex items-center justify-between shadow-lg">
                <span>{bannerMessage}</span>
                <button onClick={() => setBannerMessage(null)} className="text-indigo-200 hover:text-white">✕</button>
              </div>
            )}

            {/* Content Body */}
            <div className="p-8 space-y-6 flex-1">
              {/* TAB 1: OVERVIEW */}
              {activeTab === "overview" && (
                <div className="space-y-6">
                  {/* KPI Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-gray-400 font-medium">Logs / Requests</p>
                      <p className="text-2xl font-bold text-white mt-1">{metrics?.total_logs_processed || 0}</p>
                      <span className="text-[11px] text-gray-500">Evaluated events</span>
                    </div>
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-red-400 font-medium">Anomalies Detected</p>
                      <p className="text-2xl font-bold text-red-400 mt-1">{metrics?.total_anomalies_detected || 0}</p>
                      <span className="text-[11px] text-gray-500">Rate: {metrics?.anomaly_rate_percent || 0}%</span>
                    </div>
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-amber-400 font-medium">Prediction Errors</p>
                      <p className="text-2xl font-bold text-amber-400 mt-1">{metrics?.prediction_errors_total || 0}</p>
                      <span className="text-[11px] text-gray-500">Error Rate: {metrics?.error_rate_percent || 0}%</span>
                    </div>
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-purple-400 font-medium">Avg Latency</p>
                      <p className="text-2xl font-bold text-purple-400 mt-1">{metrics?.avg_prediction_latency_ms || 0} ms</p>
                      <span className="text-[11px] text-gray-500">P95: {metrics?.p95_prediction_latency_ms || 0} ms</span>
                    </div>
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-red-400 font-medium">Open Incidents</p>
                      <p className="text-2xl font-bold text-red-400 mt-1">{metrics?.open_incidents || 0}</p>
                      <span className="text-[11px] text-gray-500">Resolved: {metrics?.resolved_incidents || 0}</span>
                    </div>
                    <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl">
                      <p className="text-xs text-indigo-400 font-medium">Automated Responses</p>
                      <p className="text-2xl font-bold text-indigo-400 mt-1">{responses.length}</p>
                      <span className="text-[11px] text-gray-500">Safe playbooks run</span>
                    </div>
                  </div>

                  {/* Dual Panel: Live Test & Project Telemetry Summary */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Live Log Anomaly Tester */}
                    <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                      <h3 className="text-base font-semibold text-white mb-2 flex items-center justify-between">
                        <span>Live Operational Anomaly Tester</span>
                        <span className="text-xs font-mono text-indigo-400">POST /predict</span>
                      </h3>
                      <p className="text-xs text-gray-400 mb-4">
                        Test any log or telemetry string. Operational anomalies trigger project-scoped incidents and automated safe remediation.
                      </p>
                      <form onSubmit={handlePredict} className="space-y-3">
                        <textarea
                          rows="3"
                          value={predictInput}
                          onChange={e => setPredictInput(e.target.value)}
                          className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg p-3 text-sm font-mono text-gray-200 focus:outline-none focus:border-indigo-500"
                          placeholder="Enter log event or telemetry message..."
                        ></textarea>
                        <div className="flex items-center justify-between">
                          <div className="space-x-2">
                            <button
                              type="button"
                              onClick={() => setPredictInput("ERROR: Database connection timeout")}
                              className="text-[11px] text-gray-400 hover:text-white bg-gray-800 px-2 py-1 rounded border border-gray-700"
                            >
                              DB Timeout
                            </button>
                            <button
                              type="button"
                              onClick={() => setPredictInput("CRITICAL: Memory usage exceeded limit")}
                              className="text-[11px] text-gray-400 hover:text-white bg-gray-800 px-2 py-1 rounded border border-gray-700"
                            >
                              Memory Leak
                            </button>
                            <button
                              type="button"
                              onClick={() => setPredictInput("INFO: Prediction request completed")}
                              className="text-[11px] text-gray-400 hover:text-white bg-gray-800 px-2 py-1 rounded border border-gray-700"
                            >
                              Normal Event
                            </button>
                          </div>
                          <button
                            type="submit"
                            disabled={predicting}
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow"
                          >
                            {predicting ? "Classifying..." : "Analyze"}
                          </button>
                        </div>
                      </form>

                      {predictResult && (
                        <div className={`mt-4 p-4 rounded-lg border text-sm font-mono ${
                          predictResult.result === "ANOMALY"
                            ? "bg-red-950/40 border-red-800/80 text-red-300"
                            : "bg-emerald-950/40 border-emerald-800/80 text-emerald-300"
                        }`}>
                          <div className="flex items-center justify-between font-bold">
                            <span>Result: {predictResult.result}</span>
                            <span className="text-xs text-gray-400">Score: {predictResult.prediction}</span>
                          </div>
                          <p className="text-xs text-gray-400 mt-1">Project: {predictResult.project_id} | Features: {predictResult.features_used} dims</p>
                          {predictResult.alert && (
                            <p className="text-xs text-amber-300 mt-2">
                              🚨 Incident Created: #{predictResult.alert.id} ({predictResult.alert.severity})
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Active Project Details & Accuracy Card */}
                    <div className="bg-[#111827] border border-gray-800 rounded-xl p-6 flex flex-col justify-between">
                      <div>
                        <h3 className="text-base font-semibold text-white mb-2">Project Metadata & Model Drift</h3>
                        <p className="text-xs text-gray-400 mb-4">Ground-truth validation and accuracy metrics for the active workspace.</p>

                        {selectedProject === "all" ? (
                          <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800 text-xs text-gray-400 space-y-2">
                            <p className="text-white font-medium">Platform Wide View</p>
                            <p>Showing aggregated telemetry across all {projects.length} registered projects.</p>
                            <p className="text-indigo-400 font-mono">Select a specific project from the left sidebar to inspect isolated drift metrics, ground truth comparisons, and API tokens.</p>
                          </div>
                        ) : (
                          <div className="space-y-3">
                            <div className="grid grid-cols-2 gap-3 text-xs">
                              <div className="p-3 rounded-lg bg-[#0b0f19] border border-gray-800">
                                <span className="text-gray-500">Project ID</span>
                                <p className="font-mono text-white font-semibold mt-0.5">{selectedProject}</p>
                              </div>
                              <div className="p-3 rounded-lg bg-[#0b0f19] border border-gray-800">
                                <span className="text-gray-500">Framework</span>
                                <p className="font-mono text-indigo-400 font-semibold mt-0.5">
                                  {projects.find(p => p.project_id === selectedProject)?.framework || "custom"}
                                </p>
                              </div>
                            </div>

                            {/* Drift / Accuracy Telemetry */}
                            <div className="p-3.5 rounded-lg bg-[#0b0f19] border border-gray-800 space-y-2 text-xs font-mono">
                              <div className="flex items-center justify-between text-gray-400">
                                <span>Ground-Truth Samples:</span>
                                <span className="text-white font-bold">{driftData?.sample_size || 0}</span>
                              </div>
                              <div className="flex items-center justify-between text-gray-400">
                                <span>Mean Absolute Error (MAE):</span>
                                <span className={driftData?.evaluation_available ? "text-emerald-400 font-bold" : "text-gray-500"}>
                                  {driftData?.evaluation_available ? driftData.mae : "Not available (no ground truth)"}
                                </span>
                              </div>
                              <div className="flex items-center justify-between text-gray-400">
                                <span>Root Mean Squared Error (RMSE):</span>
                                <span className={driftData?.evaluation_available ? "text-indigo-400 font-bold" : "text-gray-500"}>
                                  {driftData?.evaluation_available ? driftData.rmse : "Not available"}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="mt-4 pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-500">
                        <span>Python SDK: drishti_sdk.DrishtiClient</span>
                        <span className="font-mono text-emerald-400">Integration Ready</span>
                      </div>
                    </div>
                  </div>

                  {/* Recent Audit & Activity Stream */}
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-4">Recent Audit & Incident Activity</h3>
                    <div className="space-y-2.5">
                      {history.slice(-6).reverse().map((h, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#0b0f19] border border-gray-800/80 text-xs font-mono">
                          <div className="flex items-center space-x-3">
                            <span className="text-indigo-400 font-semibold">{h.action}</span>
                            <span className="text-gray-400">#{h.incident_id}</span>
                            <span className="text-gray-500 font-sans">{h.details}</span>
                          </div>
                          <div className="text-gray-500 text-[11px] shrink-0">{h.timestamp}</div>
                        </div>
                      ))}
                      {history.length === 0 && (
                        <p className="text-gray-500 text-xs italic">No system activity events recorded yet.</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: PROJECT TELEMETRY */}
              {activeTab === "telemetry" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-base font-semibold text-white">Universal Ingested Telemetry Feed</h3>
                        <p className="text-xs text-gray-400">Predictions, inputs, confidence scores, errors, and system metrics submitted via drishti_sdk.</p>
                      </div>
                      <div className="text-xs font-mono text-gray-400">
                        {selectedProject === "all" ? "Select a project to view telemetry" : `Project: ${selectedProject}`}
                      </div>
                    </div>

                    {selectedProject === "all" ? (
                      <div className="p-8 text-center text-gray-400 text-xs bg-[#0b0f19] rounded-lg border border-gray-800">
                        Please select a specific project from the top of the left sidebar to inspect its isolated telemetry stream.
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs font-mono">
                          <thead className="bg-[#0b0f19] text-gray-400 uppercase border-b border-gray-800">
                            <tr>
                              <th className="p-3">Time</th>
                              <th className="p-3">Type</th>
                              <th className="p-3">Model</th>
                              <th className="p-3">Prediction</th>
                              <th className="p-3">Ground Truth</th>
                              <th className="p-3">Latency</th>
                              <th className="p-3">Anomaly</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-800">
                            {telemetry.map((t) => (
                              <tr key={t.telemetry_id} className="hover:bg-gray-800/40">
                                <td className="p-3 text-gray-400">{t.timestamp}</td>
                                <td className="p-3 text-indigo-400 font-semibold">{t.event_type}</td>
                                <td className="p-3 text-gray-300">{t.model_name || "N/A"}</td>
                                <td className="p-3 text-white font-bold">{t.prediction !== null && t.prediction !== undefined ? JSON.stringify(t.prediction) : "Not available"}</td>
                                <td className="p-3 text-emerald-400">{t.ground_truth !== null && t.ground_truth !== undefined ? JSON.stringify(t.ground_truth) : "Not available"}</td>
                                <td className="p-3 text-purple-400">{t.latency_ms ? `${t.latency_ms} ms` : "Not available"}</td>
                                <td className="p-3">
                                  {t.is_anomaly ? (
                                    <span className="px-2 py-0.5 rounded bg-red-900/40 text-red-300 border border-red-700/50">ANOMALY</span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded bg-emerald-900/40 text-emerald-300 border border-emerald-700/50">NORMAL</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                            {telemetry.length === 0 && (
                              <tr>
                                <td colSpan="7" className="p-4 text-center text-gray-500 italic">No telemetry events logged for this project yet. Use drishti_sdk to submit data.</td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 3: LOG MONITORING */}
              {activeTab === "logs" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-2">Live Application Log Ingestion</h3>
                    <p className="text-xs text-gray-400 mb-4">Submit raw application log strings. The system parses them, extracts 16 numerical features, and sends them through the Loglizer detector.</p>
                    <form onSubmit={handlePredict} className="flex gap-3">
                      <input
                        type="text"
                        value={predictInput}
                        onChange={e => setPredictInput(e.target.value)}
                        placeholder="e.g. 2026-11-19 21:00:00 | ERROR: Database connection timeout"
                        className="flex-1 bg-[#0b0f19] border border-gray-700 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-200 focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        type="submit"
                        disabled={predicting}
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shrink-0"
                      >
                        Ingest & Evaluate
                      </button>
                    </form>
                  </div>

                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-4">Evaluated Incident Stream</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-[#0b0f19] text-gray-400 uppercase border-b border-gray-800">
                          <tr>
                            <th className="p-3">Timestamp</th>
                            <th className="p-3">Project</th>
                            <th className="p-3">Severity</th>
                            <th className="p-3">Category</th>
                            <th className="p-3">Log Message</th>
                            <th className="p-3">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                          {incidents.map((inc, i) => (
                            <tr key={i} className="hover:bg-gray-800/40">
                              <td className="p-3 text-gray-400">{inc.created_at}</td>
                              <td className="p-3 text-indigo-400 font-bold">{inc.project_id || "default"}</td>
                              <td className="p-3"><SeverityBadge severity={inc.severity} /></td>
                              <td className="p-3 text-indigo-300">{inc.category}</td>
                              <td className="p-3 text-gray-200 font-sans max-w-md truncate">{inc.message}</td>
                              <td className="p-3"><StatusBadge status={inc.status} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: ANOMALY DETECTION */}
              {activeTab === "anomaly" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-2">Loglizer IsolationForest Anomaly Engine</h3>
                    <p className="text-xs text-gray-400 mb-6">
                      DRISHTI AI uses Loglizer's actual unsupervised IsolationForest implementation. Telemetry from any ML model is mapped into a 16-dimensional numerical vector capturing severity levels, subsystem category one-hot encodings, and problem indicator flags.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500 font-medium">Model Architecture</p>
                        <p className="text-lg font-bold text-white mt-1">Isolation Forest</p>
                        <p className="text-[11px] text-gray-500">Loglizer Unsupervised</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500 font-medium">Contamination Threshold</p>
                        <p className="text-lg font-bold text-indigo-400 mt-1">0.20 (20%)</p>
                        <p className="text-[11px] text-gray-500">Expected anomaly ratio</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500 font-medium">Ensemble Estimators</p>
                        <p className="text-lg font-bold text-purple-400 mt-1">100 Trees</p>
                        <p className="text-[11px] text-gray-500">Randomized partitions</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500 font-medium">Artifact Location</p>
                        <p className="text-sm font-bold text-gray-300 mt-1 font-mono truncate">models/log_anomaly_detector.joblib</p>
                        <p className="text-[11px] text-emerald-400">Active & Ready</p>
                      </div>
                    </div>

                    <h4 className="text-sm font-semibold text-gray-200 mb-3">16-Dimensional Feature Extraction Schema</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
                      {[
                        "severity_INFO", "severity_WARNING", "severity_ERROR", "severity_CRITICAL",
                        "event_database", "event_prediction", "event_memory", "event_inference",
                        "event_latency", "event_authentication", "event_model", "event_api",
                        "event_other", "is_timeout", "is_failed", "is_high_usage"
                      ].map((feat, i) => (
                        <div key={i} className="p-2.5 rounded bg-[#0b0f19] border border-gray-800 flex items-center justify-between">
                          <span className="text-gray-400">{i+1}. {feat}</span>
                          <span className="text-indigo-400 text-[10px]">float</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: INCIDENT MANAGEMENT */}
              {activeTab === "incidents" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-base font-semibold text-white">Project-Scoped Incident Queue</h3>
                        <p className="text-xs text-gray-400">Track, deduplicate, and resolve operational anomalies per project.</p>
                      </div>
                      <div className="text-xs font-mono text-gray-400">
                        Active: {incidents.filter(i => i.status !== "RESOLVED" && i.status !== "CLOSED").length}
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-[#0b0f19] text-gray-400 uppercase border-b border-gray-800">
                          <tr>
                            <th className="p-3">ID</th>
                            <th className="p-3">Project</th>
                            <th className="p-3">Severity</th>
                            <th className="p-3">Title & Message</th>
                            <th className="p-3">Occurrences</th>
                            <th className="p-3">Status</th>
                            <th className="p-3">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                          {incidents.map((inc) => (
                            <tr key={inc.id} className="hover:bg-gray-800/40">
                              <td className="p-3 text-indigo-400 font-bold">#{inc.id}</td>
                              <td className="p-3 text-gray-300">{inc.project_id || "default"}</td>
                              <td className="p-3"><SeverityBadge severity={inc.severity} /></td>
                              <td className="p-3 text-gray-200 font-sans max-w-sm">
                                <div className="font-semibold text-white">{inc.title}</div>
                                <div className="text-xs text-gray-400 truncate">{inc.message}</div>
                                {inc.resolution_notes && (
                                  <div className="text-[11px] text-emerald-400 mt-0.5">Notes: {inc.resolution_notes}</div>
                                )}
                              </td>
                              <td className="p-3 text-center">
                                <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-200 border border-gray-700">
                                  {inc.occurrence_count || 1}x
                                </span>
                              </td>
                              <td className="p-3"><StatusBadge status={inc.status} /></td>
                              <td className="p-3">
                                {inc.status !== "RESOLVED" ? (
                                  <div className="flex space-x-2">
                                    <button
                                      onClick={() => setResolvingId(inc.id)}
                                      className="px-2.5 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded text-[11px] font-sans transition-colors"
                                    >
                                      Resolve
                                    </button>
                                    <button
                                      onClick={() => handleTriggerRemediation(inc.id)}
                                      className="px-2.5 py-1 bg-indigo-700 hover:bg-indigo-600 text-white rounded text-[11px] font-sans transition-colors"
                                    >
                                      Remediate
                                    </button>
                                  </div>
                                ) : (
                                  <span className="text-[11px] text-emerald-400">Resolved</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Resolve Modal */}
                  {resolvingId && (
                    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                      <div className="bg-[#111827] border border-gray-700 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
                        <h4 className="text-base font-bold text-white">Resolve Incident #{resolvingId}</h4>
                        <p className="text-xs text-gray-400">Record operational resolution notes and close this incident.</p>
                        <textarea
                          rows="3"
                          value={resolveNotes}
                          onChange={e => setResolveNotes(e.target.value)}
                          placeholder="e.g. Database connection pool recycled, latency stabilized to 12ms."
                          className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
                        ></textarea>
                        <div className="flex justify-end space-x-3">
                          <button
                            onClick={() => setResolvingId(null)}
                            className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 text-xs font-medium"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleResolve(resolvingId)}
                            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium"
                          >
                            Confirm Resolution
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 6: AUTOMATED RESPONSES */}
              {activeTab === "responses" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-2">Safe Automated Incident Response Engine</h3>
                    <p className="text-xs text-gray-400 mb-6">
                      Executes deterministic, non-destructive automated remediation actions when critical operational anomalies occur. Every action and duration is logged.
                    </p>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-[#0b0f19] text-gray-400 uppercase border-b border-gray-800">
                          <tr>
                            <th className="p-3">Action ID</th>
                            <th className="p-3">Project</th>
                            <th className="p-3">Incident</th>
                            <th className="p-3">Action Type</th>
                            <th className="p-3">Duration</th>
                            <th className="p-3">Status</th>
                            <th className="p-3">Remediation Details</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                          {responses.map((act) => (
                            <tr key={act.action_id} className="hover:bg-gray-800/40">
                              <td className="p-3 text-indigo-400 font-bold">#{act.action_id}</td>
                              <td className="p-3 text-gray-300 font-bold">{act.project_id || "default"}</td>
                              <td className="p-3 text-gray-400">#{act.incident_id}</td>
                              <td className="p-3 text-white font-semibold">{act.action_name}</td>
                              <td className="p-3 text-emerald-400">{act.execution_duration_ms} ms</td>
                              <td className="p-3">
                                <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800 text-[10px]">
                                  {act.status}
                                </span>
                              </td>
                              <td className="p-3 text-gray-400 font-sans text-[11px] max-w-md">
                                {act.description}
                              </td>
                            </tr>
                          ))}
                          {responses.length === 0 && (
                            <tr>
                              <td colSpan="7" className="p-4 text-center text-gray-500 italic">No automated actions executed yet.</td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 7: MLOPS & EXPERIMENTS */}
              {activeTab === "mlops" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                      <div>
                        <h3 className="text-base font-semibold text-white">MLflow Model Registry & Experiment Tracking</h3>
                        <p className="text-xs text-gray-400">Demonstration model lifecycle tracking for the NYC Taxi Fare predictor.</p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={handlePromote}
                          className="px-3.5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-medium transition-colors"
                        >
                          Promote to Production
                        </button>
                        <button
                          onClick={handleRetrain}
                          disabled={trainingMlops}
                          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors shadow"
                        >
                          {trainingMlops ? "Training..." : "Retrain MLOps Model"}
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500">Registered Model</p>
                        <p className="text-lg font-bold text-white mt-1">{mlopsStatus?.model_name || "taxi_fare_predictor"}</p>
                        <p className="text-[11px] text-gray-500">GradientBoosting / XGBoost</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500">Production Version</p>
                        <p className="text-lg font-bold text-emerald-400 mt-1">v{mlopsStatus?.production_version || 1}</p>
                        <p className="text-[11px] text-emerald-500">Serving Live Requests</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500">Staging Version</p>
                        <p className="text-lg font-bold text-amber-400 mt-1">
                          {mlopsStatus?.staging_version ? `v${mlopsStatus.staging_version}` : "None"}
                        </p>
                        <p className="text-[11px] text-gray-500">Awaiting Promotion</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#0b0f19] border border-gray-800">
                        <p className="text-xs text-gray-500">Tracking Store</p>
                        <p className="text-sm font-bold text-gray-300 mt-1 font-mono truncate">mlflow.db (SQLite)</p>
                        <p className="text-[11px] text-gray-500">Local Tracking Active</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                      <h4 className="text-sm font-semibold text-white mb-3">MLflow Experiment Runs</h4>
                      <div className="space-y-2.5">
                        {mlopsRuns.map((r, i) => (
                          <div key={i} className="p-3 rounded-lg bg-[#0b0f19] border border-gray-800 text-xs font-mono">
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-indigo-400 font-bold">{r.run_name}</span>
                              <span className="text-gray-500 text-[11px]">ID: {r.run_id.slice(0, 8)}</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-gray-300 text-[11px]">
                              <div>RMSE: <span className="text-emerald-400 font-semibold">{r.metrics?.rmse}</span></div>
                              <div>MAE: <span className="text-indigo-300 font-semibold">{r.metrics?.mae}</span></div>
                              <div>R²: <span className="text-amber-400 font-semibold">{r.metrics?.r2}</span></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                      <h4 className="text-sm font-semibold text-white mb-2">Live Demonstration Model Inference</h4>
                      <p className="text-xs text-gray-400 mb-4">NYC Taxi Duration & Fare prediction endpoint.</p>

                      <div className="grid grid-cols-3 gap-3 mb-4">
                        <div>
                          <label className="text-xs text-gray-400 block mb-1">Distance (mi)</label>
                          <input
                            type="number"
                            step="0.5"
                            value={taxiInput.trip_distance}
                            onChange={e => setTaxiInput({ ...taxiInput, trip_distance: parseFloat(e.target.value) || 1.0 })}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs font-mono text-white"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-400 block mb-1">Passengers</label>
                          <input
                            type="number"
                            min="1"
                            max="6"
                            value={taxiInput.passenger_count}
                            onChange={e => setTaxiInput({ ...taxiInput, passenger_count: parseInt(e.target.value) || 1 })}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs font-mono text-white"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-400 block mb-1">Pickup Hour</label>
                          <input
                            type="number"
                            min="0"
                            max="23"
                            value={taxiInput.pickup_hour}
                            onChange={e => setTaxiInput({ ...taxiInput, pickup_hour: parseInt(e.target.value) || 12 })}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs font-mono text-white"
                          />
                        </div>
                      </div>

                      <button
                        onClick={handleTaxiPredict}
                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors"
                      >
                        Run Taxi Duration Inference
                      </button>

                      {taxiResult && (
                        <div className="mt-4 p-4 rounded-lg bg-[#0b0f19] border border-indigo-700/50 text-xs font-mono space-y-1">
                          <p className="text-indigo-300 font-bold">Predicted Duration: {taxiResult.predicted_duration_minutes} mins</p>
                          <p className="text-emerald-400 font-bold">Estimated Fare: ${taxiResult.estimated_fare_usd}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 8: SYSTEM HEALTH */}
              {activeTab === "health" && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-base font-semibold text-white mb-2">DRISHTI AI End-to-End System Topology</h3>
                    <p className="text-xs text-gray-400 mb-6">
                      Integrated dual-loop architecture uniting operational log intelligence (AIOps) with continuous machine learning lifecycle management (MLOps).
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-5 rounded-xl bg-[#0b0f19] border border-gray-800 space-y-3">
                        <div className="text-xs font-bold uppercase tracking-wider text-indigo-400">Loop 1: AIOps Incident Intelligence</div>
                        <div className="space-y-2 text-xs font-mono text-gray-300">
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">1. Log Generation & Ingestion (generate_logs.py)</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">2. 16-Feature Extraction (log_processor.py)</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">3. Loglizer IsolationForest Anomaly Engine</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">4. Alert Deduplication & Correlation (alert_manager.py)</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">5. Automated Safe Remediation (response_engine.py)</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">6. Prometheus Telemetry & Audit History</div>
                        </div>
                      </div>

                      <div className="p-5 rounded-xl bg-[#0b0f19] border border-gray-800 space-y-3">
                        <div className="text-xs font-bold uppercase tracking-wider text-amber-400">Loop 2: MLOps Model Lifecycle</div>
                        <div className="space-y-2 text-xs font-mono text-gray-300">
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">1. NYC Taxi Dataset Download & Split</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">2. Scikit-learn ColumnTransformer Preprocessor</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">3. Model Training & MLflow Run Tracking</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">4. Threshold Validation & Evaluation</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">5. MLflow Model Registry Staging / Production Promotion</div>
                          <div className="p-2.5 rounded bg-gray-900 border border-gray-800">6. Real-time FastAPI Model Serving</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </main>

          {/* Project Registration Modal */}
          {showRegisterModal && (
            <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
              <div className="bg-[#111827] border border-gray-700 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
                <h3 className="text-base font-bold text-white">Register External ML Project</h3>
                <p className="text-xs text-gray-400">Connect any independent ML application (House Price, Fraud, NLP, Churn) to DRISHTI AI.</p>

                {registeredKey ? (
                  <div className="space-y-4 p-4 rounded-lg bg-[#0b0f19] border border-emerald-600/50">
                    <p className="text-xs text-emerald-400 font-bold">✓ Project Created Successfully!</p>
                    <p className="text-xs text-gray-400">Copy this secure API key now. It is hashed on the server and cannot be viewed again.</p>
                    <div className="p-3 bg-gray-900 border border-gray-700 rounded font-mono text-xs text-indigo-300 break-all select-all">
                      {registeredKey}
                    </div>
                    <div className="flex justify-end">
                      <button
                        onClick={() => { setShowRegisterModal(false); setRegisteredKey(null); }}
                        className="px-4 py-2 bg-indigo-600 text-white rounded text-xs font-semibold"
                      >
                        Done & Close
                      </button>
                    </div>
                  </div>
                ) : (
                  <form onSubmit={handleRegisterProject} className="space-y-3">
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Project ID (unique, lowercase)</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. house-price-predictor"
                        value={newProject.project_id}
                        onChange={e => setNewProject({ ...newProject, project_id: e.target.value })}
                        className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs font-mono text-white"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Project Name</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. House Price Valuation Engine"
                        value={newProject.name}
                        onChange={e => setNewProject({ ...newProject, name: e.target.value })}
                        className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Model Type</label>
                      <select
                        value={newProject.model_type}
                        onChange={e => setNewProject({ ...newProject, model_type: e.target.value })}
                        className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs text-white"
                      >
                        <option value="regression">Regression (e.g. Price, Duration)</option>
                        <option value="classification">Classification (e.g. Churn, Fraud)</option>
                        <option value="nlp">Natural Language Processing (NLP)</option>
                        <option value="computer_vision">Computer Vision (CV)</option>
                        <option value="recommendation">Recommendation System</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Description</label>
                      <textarea
                        rows="2"
                        placeholder="Appraisal estimation model for real estate portfolio"
                        value={newProject.description}
                        onChange={e => setNewProject({ ...newProject, description: e.target.value })}
                        className="w-full bg-[#0b0f19] border border-gray-700 rounded p-2 text-xs text-white"
                      />
                    </div>
                    <div className="flex justify-end space-x-3 pt-2">
                      <button
                        type="button"
                        onClick={() => setShowRegisterModal(false)}
                        className="px-4 py-2 rounded bg-gray-800 text-gray-300 text-xs"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                      >
                        Generate API Key & Register
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>
          )}
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
"""
