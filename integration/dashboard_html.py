"""
DRISHTI AI — Terminal-Inspired Intelligent MLOps & AIOps Observability Platform
Redesigned with a high-density, professional developer-workstation aesthetic.
Color Palette:
- Canvas/Main: #090D18
- Sidebar: #101625
- Content: #0D1321
- Card: #141C2D
- Elevated: #192338
- Borders: #273247
- Accents: Purple #8B5CF6 / #A78BFA, Blue #60A5FA, Green #22C55E, Amber #F59E0B, Red #EF4444
- Typography: Inter (UI) & JetBrains Mono (Terminal, Logs, Metas)
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DRISHTI AI — Intelligent MLOps & AIOps Platform</title>
  
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            canvas: '#090D18',
            sidebar: '#101625',
            content: '#0D1321',
            card: '#141C2D',
            elevated: '#192338',
            border: '#273247',
            brand: {
              purple: '#8B5CF6',
              secondary: '#A78BFA',
              blue: '#60A5FA',
              dark: '#6D28D9'
            },
            status: {
              success: '#22C55E',
              warning: '#F59E0B',
              error: '#EF4444',
              critical: '#DC2626',
              info: '#60A5FA'
            },
            txt: {
              primary: '#E5E7EB',
              secondary: '#94A3B8',
              muted: '#64748B'
            }
          },
          fontFamily: {
            sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace']
          }
        }
      }
    }
  </script>

  <!-- React 18, ReactDOM, and Babel -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <style>
    body {
      background-color: #090D18;
      color: #E5E7EB;
      font-family: 'Inter', sans-serif;
      overflow: hidden;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }
    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: #090D18;
    }
    ::-webkit-scrollbar-thumb {
      background: #273247;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #8B5CF6;
    }
    /* Subtle Glow Effects */
    .purple-glow {
      box-shadow: 0 0 25px -5px rgba(139, 92, 246, 0.18);
    }
    .purple-glow-sm {
      box-shadow: 0 0 12px -2px rgba(139, 92, 246, 0.25);
    }
    /* Terminal Line Selected */
    .terminal-row-active {
      background-color: rgba(139, 92, 246, 0.12);
      border-left: 3px solid #8B5CF6;
    }
    /* Pulse animations */
    @keyframes pulse-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    .animate-pulse-dot {
      animation: pulse-dot 2s infinite ease-in-out;
    }
  </style>
</head>
<body class="bg-canvas text-txt-primary select-none">
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef, useMemo } = React;

    // --- REUSABLE ICONS (SVG) ---
    const Icons = {
      Logo: () => (
        <svg className="w-5 h-5 text-brand-purple" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M3 12h1m8-9v1m8 8h1m-9 8v1M5.6 5.6l.7.7m12.1-.7l-.7.7m0 11.4l.7.7m-12.1-.7l-.7.7" />
          <path d="M12 2a10 10 0 1 0 10 10" strokeDasharray="3 3" />
        </svg>
      ),
      Terminal: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="4 17 10 11 4 5" /><line x1="12" y1="19" x2="20" y2="19" />
        </svg>
      ),
      Overview: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="9" /><rect x="14" y="3" width="7" height="5" /><rect x="14" y="12" width="7" height="9" /><rect x="3" y="16" width="7" height="5" />
        </svg>
      ),
      Telemetry: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2 12h5l2 8 5-16 2 8h6" />
        </svg>
      ),
      Metrics: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      ),
      Anomaly: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 2 22 22 22" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      ),
      Models: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      ),
      Drift: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><path d="m14 10-4 4" /><path d="m10 10 4 4" />
        </svg>
      ),
      Incidents: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      ),
      Playbooks: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      ),
      History: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 14 14" />
        </svg>
      ),
      Projects: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
        </svg>
      ),
      Integrations: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
        </svg>
      ),
      Settings: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      ),
      Search: () => (
        <svg className="w-3.5 h-3.5 text-txt-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      ),
      Copy: () => (
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      ),
      Check: () => (
        <svg className="w-3.5 h-3.5 text-status-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ),
      Refresh: () => (
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
      ),
      PanelToggle: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="15" y1="3" x2="15" y2="21" />
        </svg>
      ),
      Play: () => (
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
      ),
      Pause: () => (
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" />
        </svg>
      ),
      ChevronDown: () => (
        <svg className="w-3 h-3 text-txt-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      ),
      Plus: () => (
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      )
    };

    // --- BADGES & CHIPS ---
    function LevelChip({ level }) {
      const styles = {
        CRITICAL: "bg-status-critical/15 text-status-critical border-status-critical/30",
        ERROR: "bg-status-error/15 text-status-error border-status-error/30",
        WARN: "bg-status-warning/15 text-status-warning border-status-warning/30",
        WARNING: "bg-status-warning/15 text-status-warning border-status-warning/30",
        INFO: "bg-status-info/15 text-status-info border-status-info/30",
        DEBUG: "bg-txt-muted/15 text-txt-secondary border-txt-muted/30"
      };
      const clean = (level || "INFO").toUpperCase();
      return (
        <span className={`px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded border uppercase tracking-wider ${styles[clean] || styles.INFO}`}>
          {clean}
        </span>
      );
    }

    function StatusBadge({ status }) {
      const styles = {
        OPEN: "bg-status-error/15 text-status-error border-status-error/40",
        INVESTIGATING: "bg-status-warning/15 text-status-warning border-status-warning/40",
        MITIGATING: "bg-brand-purple/20 text-brand-secondary border-brand-purple/40",
        RESOLVED: "bg-status-success/15 text-status-success border-status-success/40",
        CLOSED: "bg-card text-txt-muted border-border"
      };
      const clean = (status || "OPEN").toUpperCase();
      return (
        <span className={`px-2 py-0.5 text-[11px] font-mono font-semibold rounded-full border ${styles[clean] || styles.OPEN}`}>
          {clean}
        </span>
      );
    }

    // --- MAIN APPLICATION SHELL ---
    function App() {
      // Navigation & Layout State
      const [activeTab, setActiveTab] = useState("logs"); // Live Logs is signature screen!
      const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
      const [rightPanelOpen, setRightPanelOpen] = useState(true);
      const [selectedProject, setSelectedProject] = useState("all");
      const [timeRange, setTimeRange] = useState("1h");
      const [isStreaming, setIsStreaming] = useState(true);
      const [autoScroll, setAutoScroll] = useState(true);

      // Selected item for contextual inspector
      const [selectedItem, setSelectedItem] = useState(null);

      // Filter State for Logs
      const [logFilterLevel, setLogFilterLevel] = useState("ALL");
      const [logSearchQuery, setLogSearchQuery] = useState("");

      // Backend Data State
      const [projects, setProjects] = useState([]);
      const [metrics, setMetrics] = useState({});
      const [incidents, setIncidents] = useState([]);
      const [history, setHistory] = useState([]);
      const [responses, setResponses] = useState([]);
      const [mlopsRuns, setMlopsRuns] = useState([]);
      const [mlopsStatus, setMlopsStatus] = useState(null);
      const [telemetry, setTelemetry] = useState([]);
      const [driftData, setDriftData] = useState(null);
      const [backendStatus, setBackendStatus] = useState("CONNECTING");

      // Modals and notifications
      const [showRegisterModal, setShowRegisterModal] = useState(false);
      const [registeredApiKey, setRegisteredApiKey] = useState(null);
      const [toast, setToast] = useState(null);

      // Diagnostic Playground State
      const [diagMessage, setDiagMessage] = useState("Feature store connection timeout to Redis cluster");
      const [diagSeverity, setDiagSeverity] = useState("ERROR");
      const [diagResult, setDiagResult] = useState(null);
      const [diagRunning, setDiagRunning] = useState(false);

      // Log terminal auto-scroll ref
      const logContainerRef = useRef(null);

      const notify = (text, type = "info") => {
        setToast({ text, type });
        setTimeout(() => setToast(null), 3500);
      };

      // Fetch all platform telemetry & state
      const fetchData = async () => {
        try {
          const pParam = selectedProject !== "all" ? `?project_id=${selectedProject}` : "";
          const [projsRes, statsRes, alertsRes, histRes, respRes, runsRes, mlopsRes] = await Promise.all([
            fetch('/projects').then(r => r.json()).catch(() => ({ projects: [] })),
            fetch(`/system/stats${pParam}`).then(r => r.json()).catch(() => ({})),
            fetch(`/alerts${pParam}`).then(r => r.json()).catch(() => ({ alerts: [] })),
            fetch(`/incidents/history${pParam}`).then(r => r.json()).catch(() => ({ history: [] })),
            fetch(`/responses${pParam}`).then(r => r.json()).catch(() => ({ actions: [] })),
            fetch('/mlops/runs').then(r => r.json()).catch(() => ({ runs: [] })),
            fetch('/mlops/model-status').then(r => r.json()).catch(() => ({}))
          ]);

          setProjects(projsRes.projects || []);
          setMetrics(statsRes.metrics || {});
          setIncidents(alertsRes.alerts || []);
          setHistory(histRes.history || []);
          setResponses(respRes.actions || []);
          setMlopsRuns(runsRes.runs || []);
          setMlopsStatus(mlopsRes);
          setBackendStatus("HEALTHY");

          // Fetch telemetry records
          if (selectedProject !== "all") {
            const [tRes, dRes] = await Promise.all([
              fetch(`/telemetry/${selectedProject}?limit=150`).then(r => r.json()).catch(() => ({ records: [] })),
              fetch(`/telemetry/${selectedProject}/drift`).then(r => r.json()).catch(() => null)
            ]);
            setTelemetry(tRes.records || []);
            setDriftData(dRes);
          } else {
            // Fetch telemetry across all known projects and combine
            const allTelemetryPromises = (projsRes.projects || []).map(p =>
              fetch(`/telemetry/${p.project_id}?limit=60`).then(r => r.json()).catch(() => ({ records: [] }))
            );
            const allTResults = await Promise.all(allTelemetryPromises);
            const combined = allTResults.flatMap(r => r.records || []);
            combined.sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""));
            setTelemetry(combined);
            setDriftData(null);
          }
        } catch (err) {
          console.error("Data fetch error:", err);
          setBackendStatus("DISCONNECTED");
        }
      };

      useEffect(() => {
        fetchData();
        const interval = setInterval(() => {
          if (isStreaming) {
            fetchData();
          }
        }, 3000);
        return () => clearInterval(interval);
      }, [selectedProject, isStreaming]);

      // Auto-scroll terminal logs if enabled
      useEffect(() => {
        if (autoScroll && logContainerRef.current) {
          logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
      }, [telemetry, autoScroll]);

      // Synthesized unified terminal logs from real telemetry and events
      const unifiedLogs = useMemo(() => {
        const stream = [];

        // 1. Add Telemetry Ingestion Events
        telemetry.forEach(t => {
          const isErr = t.event_type === "ERROR" || t.is_anomaly || t.error_type;
          const sev = t.severity || (isErr ? "ERROR" : "INFO");
          stream.push({
            id: t.telemetry_id || Math.random().toString(36).substr(2, 8),
            timestamp: t.timestamp ? t.timestamp.split("T")[1]?.replace("Z", "") || t.timestamp : "12:00:00.000",
            fullTimestamp: t.timestamp,
            level: sev,
            source: t.error_type ? "model.runtime" : (t.is_anomaly ? "anomaly.iforest" : "telemetry.api"),
            model: t.model_name || t.project_id,
            project_id: t.project_id,
            message: t.log_message || t.error_message || (t.prediction !== undefined ? `Inference completed: pred=${JSON.stringify(t.prediction)}` : `Telemetry recorded`),
            latency: t.latency_ms ? `${parseFloat(t.latency_ms).toFixed(1)}ms` : null,
            prediction: t.prediction,
            confidence: t.confidence,
            ground_truth: t.ground_truth,
            inputs: t.inputs,
            error_type: t.error_type,
            features_extracted: t.features_extracted,
            raw: t
          });
        });

        // 2. Add Incident Lifecycle Events
        history.forEach(h => {
          stream.push({
            id: `hist_${h.incident_id || Math.random().toString(36).substr(2, 6)}`,
            timestamp: h.timestamp ? h.timestamp.split("T")[1]?.replace("Z", "") || h.timestamp : "12:00:00.000",
            fullTimestamp: h.timestamp,
            level: "WARN",
            source: "incident.mgr",
            model: h.project_id || "core",
            project_id: h.project_id,
            message: `[${h.action}] Incident #${h.incident_id} ${h.details || ""}`,
            latency: null,
            raw: h
          });
        });

        // 3. Add Automated Remediation Playbooks
        responses.forEach(r => {
          stream.push({
            id: `resp_${Math.random().toString(36).substr(2, 6)}`,
            timestamp: r.timestamp ? r.timestamp.split("T")[1]?.replace("Z", "") || r.timestamp : "12:00:00.000",
            fullTimestamp: r.timestamp,
            level: "INFO",
            source: "playbook.exec",
            model: r.project_id || "core",
            project_id: r.project_id,
            message: `[PLAYBOOK] ${r.playbook} -> ${r.action_taken} (${r.status})`,
            latency: r.execution_latency_ms ? `${parseFloat(r.execution_latency_ms).toFixed(1)}ms` : null,
            raw: r
          });
        });

        // Sort descending by timestamp
        stream.sort((a, b) => (b.fullTimestamp || "").localeCompare(a.fullTimestamp || ""));
        return stream;
      }, [telemetry, history, responses]);

      // Filtered logs for terminal viewer
      const filteredLogs = useMemo(() => {
        return unifiedLogs.filter(log => {
          const matchLevel = logFilterLevel === "ALL" || log.level.toUpperCase() === logFilterLevel;
          const q = logSearchQuery.toLowerCase();
          const matchQuery = !q ||
            log.message.toLowerCase().includes(q) ||
            log.id.toLowerCase().includes(q) ||
            log.source.toLowerCase().includes(q) ||
            (log.model && log.model.toLowerCase().includes(q));
          return matchLevel && matchQuery;
        });
      }, [unifiedLogs, logFilterLevel, logSearchQuery]);

      // Calculate operational distribution stats
      const streamStats = useMemo(() => {
        const counts = { INFO: 0, WARN: 0, ERROR: 0, CRITICAL: 0 };
        let totalLat = 0;
        let latCount = 0;
        let p95Lat = 0;
        const latList = [];

        unifiedLogs.forEach(l => {
          const lvl = l.level.toUpperCase();
          if (counts[lvl] !== undefined) counts[lvl]++;
          if (l.latency) {
            const val = parseFloat(l.latency);
            if (!isNaN(val)) {
              totalLat += val;
              latCount++;
              latList.push(val);
            }
          }
        });

        latList.sort((a, b) => a - b);
        if (latList.length > 0) {
          p95Lat = latList[Math.floor(latList.length * 0.95)] || latList[latList.length - 1];
        }

        const avgLat = latCount > 0 ? (totalLat / latCount).toFixed(1) : "0.0";
        const errCount = (counts.ERROR || 0) + (counts.CRITICAL || 0);
        const errRate = unifiedLogs.length > 0 ? ((errCount / unifiedLogs.length) * 100).toFixed(1) : "0.0";

        return {
          counts,
          total: unifiedLogs.length,
          avgLatency: avgLat,
          p95Latency: p95Lat.toFixed(1),
          errorRate: errRate,
          anomalies: telemetry.filter(t => t.is_anomaly).length,
          openIncidents: incidents.filter(i => i.status !== "RESOLVED" && i.status !== "CLOSED").length
        };
      }, [unifiedLogs, telemetry, incidents]);

      // Handle resolving an incident
      const handleResolveIncident = async (id) => {
        try {
          const res = await fetch(`/alerts/${id}/resolve`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resolution_notes: "Resolved via Operator Terminal Console" })
          });
          if (res.ok) {
            notify(`Incident #${id} resolved successfully!`, "success");
            fetchData();
          }
        } catch (e) {
          notify(`Failed to resolve incident: ${e.message}`, "error");
        }
      };

      // Handle running diagnostic test
      const handleRunDiagnostic = async () => {
        setDiagRunning(true);
        try {
          const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              log_message: diagMessage,
              severity: diagSeverity,
              project_id: selectedProject !== "all" ? selectedProject : "default"
            })
          });
          const data = await res.json();
          setDiagResult(data);
          notify(`Diagnostic scored: ${data.result} (Anomaly: ${data.is_anomaly})`, data.is_anomaly ? "error" : "success");
          fetchData();
        } catch (e) {
          notify(`Diagnostic error: ${e.message}`, "error");
        } finally {
          setDiagRunning(false);
        }
      };

      // Navigation Hierarchy
      const navSections = [
        {
          group: "OBSERVABILITY",
          items: [
            { id: "overview", label: "Live Overview", icon: Icons.Overview },
            { id: "logs", label: "Live Logs", icon: Icons.Terminal, badge: streamStats.total > 0 ? streamStats.total : null },
            { id: "telemetry", label: "Telemetry Feed", icon: Icons.Telemetry },
            { id: "metrics", label: "Prometheus Metrics", icon: Icons.Metrics }
          ]
        },
        {
          group: "INTELLIGENCE",
          items: [
            { id: "anomaly", label: "Anomaly Detection", icon: Icons.Anomaly, badge: streamStats.anomalies > 0 ? streamStats.anomalies : null, badgeColor: "text-status-error bg-status-error/10" },
            { id: "models", label: "Model Monitoring", icon: Icons.Models },
            { id: "drift", label: "Drift Analysis", icon: Icons.Drift }
          ]
        },
        {
          group: "OPERATIONS",
          items: [
            { id: "incidents", label: "Alerts & Incidents", icon: Icons.Incidents, badge: streamStats.openIncidents > 0 ? streamStats.openIncidents : null, badgeColor: "text-status-warning bg-status-warning/10" },
            { id: "playbooks", label: "Automated Playbooks", icon: Icons.Playbooks },
            { id: "history", label: "Event Audit Trail", icon: Icons.History }
          ]
        },
        {
          group: "MANAGEMENT",
          items: [
            { id: "projects", label: "Projects & Apps", icon: Icons.Projects },
            { id: "integrations", label: "SDK & API Keys", icon: Icons.Integrations },
            { id: "settings", label: "System Diagnostics", icon: Icons.Settings }
          ]
        }
      ];

      return (
        <div className="flex h-screen w-screen overflow-hidden bg-canvas text-txt-primary">
          {/* TOAST NOTIFICATION */}
          {toast && (
            <div className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded-lg border text-xs font-mono flex items-center space-x-2.5 purple-glow-sm shadow-xl transition-all ${
              toast.type === "error" ? "bg-status-error/15 text-status-error border-status-error/40" :
              toast.type === "success" ? "bg-status-success/15 text-status-success border-status-success/40" :
              "bg-elevated text-txt-primary border-brand-purple/40"
            }`}>
              {toast.type === "success" ? <Icons.Check /> : <Icons.Terminal />}
              <span>{toast.text}</span>
            </div>
          )}

          {/* ========================================================================= */}
          {/* A. LEFT NAVIGATION SIDEBAR                                                */}
          {/* ========================================================================= */}
          <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-sidebar border-r border-border flex flex-col justify-between shrink-0 transition-all duration-200 z-20`}>
            <div>
              {/* Header: Logo & Branding */}
              <div className="h-14 border-b border-border flex items-center justify-between px-3.5">
                <div className="flex items-center space-x-2.5 overflow-hidden">
                  <div className="w-8 h-8 rounded-lg bg-card border border-brand-purple/40 flex items-center justify-center purple-glow-sm shrink-0">
                    <Icons.Logo />
                  </div>
                  {!sidebarCollapsed && (
                    <div className="leading-tight truncate">
                      <div className="font-mono font-bold text-xs tracking-wider text-txt-primary flex items-center space-x-1.5">
                        <span>DRISHTI</span>
                        <span className="text-[10px] px-1 py-0.2 bg-brand-purple/20 text-brand-secondary rounded border border-brand-purple/30">AI</span>
                      </div>
                      <span className="text-[10px] font-mono text-txt-muted tracking-tight">MLOps & AIOps Platform</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                  className="p-1 rounded hover:bg-card text-txt-muted hover:text-txt-primary transition-colors"
                  title="Toggle Sidebar"
                >
                  <Icons.PanelToggle />
                </button>
              </div>

              {/* Workspace / Project Selector */}
              {!sidebarCollapsed && (
                <div className="p-3 border-b border-border bg-canvas/40">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono font-semibold text-txt-muted uppercase tracking-wider">Active Workspace</span>
                    <button
                      onClick={() => setShowRegisterModal(true)}
                      className="text-[10px] font-mono text-brand-secondary hover:text-brand-purple font-medium flex items-center space-x-0.5"
                    >
                      <Icons.Plus />
                      <span>New</span>
                    </button>
                  </div>
                  <div className="relative">
                    <select
                      value={selectedProject}
                      onChange={e => setSelectedProject(e.target.value)}
                      className="w-full bg-card border border-border rounded-md px-2.5 py-1.5 text-xs font-mono text-txt-primary focus:outline-none focus:border-brand-purple appearance-none cursor-pointer"
                    >
                      <option value="all">🌐 All Projects (Platform Firehose)</option>
                      {projects.map(p => (
                        <option key={p.project_id} value={p.project_id}>
                          📁 {p.name} ({p.project_id})
                        </option>
                      ))}
                    </select>
                    <div className="absolute right-2.5 top-2.5 pointer-events-none">
                      <Icons.ChevronDown />
                    </div>
                  </div>
                </div>
              )}

              {/* Grouped Navigation Links */}
              <nav className="p-2 space-y-4 overflow-y-auto max-h-[calc(100vh-230px)]">
                {navSections.map(sec => (
                  <div key={sec.group}>
                    {!sidebarCollapsed && (
                      <h4 className="px-2 mb-1 text-[9px] font-mono font-bold text-txt-muted tracking-widest uppercase">
                        {sec.group}
                      </h4>
                    )}
                    <div className="space-y-0.5">
                      {sec.items.map(item => {
                        const Icon = item.icon;
                        const active = activeTab === item.id;
                        return (
                          <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-mono transition-colors ${
                              active
                                ? "bg-elevated text-brand-secondary border border-brand-purple/30 font-semibold purple-glow-sm"
                                : "text-txt-secondary hover:text-txt-primary hover:bg-card/60"
                            }`}
                            title={item.label}
                          >
                            <div className="flex items-center space-x-2.5 truncate">
                              <span className={active ? "text-brand-secondary" : "text-txt-muted"}>
                                <Icon />
                              </span>
                              {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                            </div>
                            {!sidebarCollapsed && item.badge !== undefined && item.badge !== null && (
                              <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-bold border ${item.badgeColor || 'bg-card text-txt-muted border-border'}`}>
                                {item.badge}
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </nav>
            </div>

            {/* Bottom Status & Diagnostics */}
            <div className="p-3 border-t border-border bg-canvas/30 text-xs font-mono">
              {!sidebarCollapsed ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-txt-muted">Telemetry Node:</span>
                    <span className="text-txt-secondary">{typeof window !== 'undefined' ? (window.location.host || '127.0.0.1:8001') : '127.0.0.1:8001'}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-txt-muted">Stream Pulse:</span>
                    <div className="flex items-center space-x-1.5">
                      <span className={`w-2 h-2 rounded-full ${backendStatus === "HEALTHY" ? "bg-status-success animate-pulse-dot" : "bg-status-error"}`}></span>
                      <span className={backendStatus === "HEALTHY" ? "text-status-success font-semibold" : "text-status-error"}>
                        {backendStatus}
                      </span>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-border/60 flex items-center justify-between text-[10px] text-txt-muted">
                    <span>DRISHTI Core v1.4.0</span>
                    <a href="/docs" target="_blank" className="text-brand-secondary hover:underline">API Docs ↗</a>
                  </div>
                </div>
              ) : (
                <div className="flex justify-center">
                  <span className={`w-2.5 h-2.5 rounded-full ${backendStatus === "HEALTHY" ? "bg-status-success animate-pulse-dot" : "bg-status-error"}`} title={`Status: ${backendStatus}`}></span>
                </div>
              )}
            </div>
          </aside>

          {/* ========================================================================= */}
          {/* B. CENTRAL WORKSPACE (MAIN ENGINE)                                         */}
          {/* ========================================================================= */}
          <main className="flex-1 flex flex-col min-w-0 bg-content overflow-hidden">
            {/* Topbar: Technical Controls, Streaming Status & Filters */}
            <header className="h-14 border-b border-border bg-canvas/70 px-4 flex items-center justify-between shrink-0">
              {/* Left: Breadcrumbs & Active Project */}
              <div className="flex items-center space-x-3 overflow-hidden">
                <span className="text-xs font-mono text-txt-muted uppercase">SYS //</span>
                <h2 className="text-sm font-mono font-bold text-txt-primary truncate">
                  {activeTab.toUpperCase().replace("_", " ")}
                </h2>
                <div className="hidden md:flex items-center space-x-2">
                  <span className="text-xs text-border font-mono">|</span>
                  <span className="px-2 py-0.5 rounded bg-card border border-border text-[11px] font-mono text-brand-secondary">
                    {selectedProject === "all" ? "🌐 ALL_PROJECTS" : `📁 ${selectedProject}`}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-status-success/15 border border-status-success/30 text-[10px] font-mono text-status-success font-bold">
                    PROD_NODE_01
                  </span>
                </div>
              </div>

              {/* Right: Streaming Controls, Time Range & Contextual Drawer Toggle */}
              <div className="flex items-center space-x-2 font-mono text-xs">
                {/* Time Range Selector */}
                <div className="hidden sm:flex items-center bg-card border border-border rounded-md p-0.5">
                  {["15m", "1h", "6h", "24h"].map(tr => (
                    <button
                      key={tr}
                      onClick={() => setTimeRange(tr)}
                      className={`px-2 py-1 rounded text-[11px] ${timeRange === tr ? "bg-elevated text-brand-secondary font-bold" : "text-txt-muted hover:text-txt-primary"}`}
                    >
                      {tr}
                    </button>
                  ))}
                </div>

                {/* Pause/Resume Live Stream */}
                <button
                  onClick={() => {
                    setIsStreaming(!isStreaming);
                    notify(isStreaming ? "Stream paused" : "Stream resumed", "info");
                  }}
                  className={`px-2.5 py-1 rounded-md border flex items-center space-x-1.5 text-xs transition-colors ${
                    isStreaming
                      ? "bg-card border-border text-status-success hover:bg-elevated"
                      : "bg-status-warning/20 border-status-warning/40 text-status-warning"
                  }`}
                  title={isStreaming ? "Pause Live Stream" : "Resume Live Stream"}
                >
                  {isStreaming ? <Icons.Pause /> : <Icons.Play />}
                  <span className="text-[11px] hidden sm:inline">{isStreaming ? "LIVE" : "PAUSED"}</span>
                </button>

                {/* Auto Scroll Toggle (for Live Logs) */}
                {activeTab === "logs" && (
                  <button
                    onClick={() => setAutoScroll(!autoScroll)}
                    className={`px-2 py-1 rounded-md border text-[11px] ${
                      autoScroll ? "bg-brand-purple/20 border-brand-purple/40 text-brand-secondary font-semibold" : "bg-card border-border text-txt-muted"
                    }`}
                    title="Toggle Terminal Auto-Scroll"
                  >
                    ⬇ AUTO-SCROLL
                  </button>
                )}

                {/* Refresh Trigger */}
                <button
                  onClick={() => { fetchData(); notify("Refreshed operational telemetry", "info"); }}
                  className="p-1.5 rounded-md bg-card border border-border hover:bg-elevated text-txt-muted hover:text-txt-primary"
                  title="Force Reload Data"
                >
                  <Icons.Refresh />
                </button>

                {/* Toggle Right Contextual Panel */}
                <button
                  onClick={() => setRightPanelOpen(!rightPanelOpen)}
                  className={`p-1.5 rounded-md border transition-colors ${
                    rightPanelOpen ? "bg-elevated border-brand-purple/40 text-brand-secondary purple-glow-sm" : "bg-card border-border text-txt-muted hover:text-txt-primary"
                  }`}
                  title="Toggle Analytics & Inspection Drawer"
                >
                  <Icons.PanelToggle />
                </button>
              </div>
            </header>

            {/* Dynamic Screen Content Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">

              {/* ================================================================= */}
              {/* TAB 1: LIVE LOGS — THE SIGNATURE SCREEN                          */}
              {/* ================================================================= */}
              {activeTab === "logs" && (
                <div className="h-full flex flex-col space-y-3">
                  {/* Search and Filter Terminal Toolbar */}
                  <div className="bg-card border border-border rounded-lg p-2.5 flex flex-wrap items-center justify-between gap-2.5 font-mono text-xs">
                    {/* Search Input */}
                    <div className="relative flex-1 min-w-[260px]">
                      <div className="absolute left-2.5 top-2.5 pointer-events-none">
                        <Icons.Search />
                      </div>
                      <input
                        type="text"
                        value={logSearchQuery}
                        onChange={e => setLogSearchQuery(e.target.value)}
                        placeholder="Search logs by keyword, model, correlation ID, error type..."
                        className="w-full bg-content border border-border rounded-md pl-8 pr-3 py-1.5 text-xs text-txt-primary placeholder-txt-muted focus:outline-none focus:border-brand-purple"
                      />
                      {logSearchQuery && (
                        <button
                          onClick={() => setLogSearchQuery("")}
                          className="absolute right-2.5 top-2 text-txt-muted hover:text-txt-primary"
                        >
                          ✕
                        </button>
                      )}
                    </div>

                    {/* Level Filter Chips */}
                    <div className="flex items-center space-x-1 bg-content border border-border rounded-md p-1">
                      {["ALL", "INFO", "WARN", "ERROR", "CRITICAL"].map(lvl => (
                        <button
                          key={lvl}
                          onClick={() => setLogFilterLevel(lvl)}
                          className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                            logFilterLevel === lvl
                              ? "bg-brand-purple text-white shadow"
                              : "text-txt-muted hover:text-txt-primary"
                          }`}
                        >
                          {lvl}
                        </button>
                      ))}
                    </div>

                    {/* Quick Clear Filter */}
                    {(logSearchQuery || logFilterLevel !== "ALL") && (
                      <button
                        onClick={() => { setLogSearchQuery(""); setLogFilterLevel("ALL"); }}
                        className="text-[11px] text-txt-muted hover:text-brand-secondary underline"
                      >
                        Reset Filters
                      </button>
                    )}

                    <div className="text-[11px] text-txt-muted">
                      Showing <span className="text-txt-primary font-bold">{filteredLogs.length}</span> of {unifiedLogs.length} events
                    </div>
                  </div>

                  {/* Terminal Log Stream Window */}
                  <div className="flex-1 bg-content border border-border rounded-lg flex flex-col overflow-hidden purple-glow-sm">
                    {/* Terminal Header Bar */}
                    <div className="bg-canvas border-b border-border px-3 py-2 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1.5">
                          <span className="w-2.5 h-2.5 rounded-full bg-status-error/80 inline-block"></span>
                          <span className="w-2.5 h-2.5 rounded-full bg-status-warning/80 inline-block"></span>
                          <span className="w-2.5 h-2.5 rounded-full bg-status-success/80 inline-block"></span>
                        </div>
                        <span className="text-txt-muted text-[11px] ml-2">drishti-tail -f /var/log/telemetry.stream</span>
                      </div>
                      <div className="flex items-center space-x-3 text-[11px] text-txt-muted">
                        <span>Buffer: <span className="text-txt-primary">{filteredLogs.length} rows</span></span>
                        <span>Encoding: <span className="text-txt-primary">UTF-8 / JSONL</span></span>
                      </div>
                    </div>

                    {/* Scrollable Monospace Log Region */}
                    <div
                      ref={logContainerRef}
                      className="flex-1 overflow-y-auto p-2 font-mono text-[11.5px] space-y-0.5 divide-y divide-border/20 select-text"
                    >
                      {filteredLogs.length === 0 ? (
                        <div className="h-64 flex flex-col items-center justify-center text-txt-muted space-y-2">
                          <Icons.Terminal />
                          <p>No log events match your current filter criteria.</p>
                          <button
                            onClick={() => { setLogSearchQuery(""); setLogFilterLevel("ALL"); }}
                            className="text-xs text-brand-secondary hover:underline"
                          >
                            Reset filters
                          </button>
                        </div>
                      ) : (
                        filteredLogs.map((log, idx) => {
                          const isSelected = selectedItem && selectedItem.id === log.id;
                          return (
                            <div
                              key={log.id + idx}
                              onClick={() => {
                                setSelectedItem(log);
                                if (!rightPanelOpen) setRightPanelOpen(true);
                              }}
                              className={`group px-2 py-1.5 rounded cursor-pointer flex items-baseline space-x-2.5 transition-colors ${
                                isSelected
                                  ? "terminal-row-active"
                                  : "hover:bg-card/70 text-txt-secondary hover:text-txt-primary"
                              }`}
                            >
                              {/* 1. Timestamp */}
                              <span className="text-txt-muted text-[11px] shrink-0 font-normal">{log.timestamp}</span>

                              {/* 2. Severity Level Badge */}
                              <LevelChip level={log.level} />

                              {/* 3. Service / Component Source */}
                              <span className="text-brand-secondary text-[11px] shrink-0 font-medium">[{log.source}]</span>

                              {/* 4. Event / Correlation ID */}
                              <span className="text-txt-muted text-[11px] shrink-0">#{log.id.slice(0, 8)}</span>

                              {/* 5. Model / App Tag */}
                              {log.model && (
                                <span className="px-1.5 py-0.2 rounded bg-card border border-border text-[10px] text-accent-blue shrink-0">
                                  {log.model}
                                </span>
                              )}

                              {/* 6. Message Body */}
                              <span className="flex-1 truncate text-txt-primary font-normal">
                                {log.message}
                              </span>

                              {/* 7. Latency (if reported) */}
                              {log.latency && (
                                <span className="text-brand-purple text-[11px] shrink-0 font-semibold">
                                  {log.latency}
                                </span>
                              )}

                              {/* Hover Quick Action: Copy */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigator.clipboard.writeText(JSON.stringify(log.raw || log, null, 2));
                                  notify(`Copied event #${log.id.slice(0, 8)} to clipboard`, "success");
                                }}
                                className="opacity-0 group-hover:opacity-100 text-txt-muted hover:text-txt-primary p-0.5 rounded shrink-0"
                                title="Copy event JSON"
                              >
                                <Icons.Copy />
                              </button>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 2: LIVE OVERVIEW CONTROL CENTER                               */}
              {/* ================================================================= */}
              {activeTab === "overview" && (
                <div className="space-y-4">
                  {/* System Operational Status Banner */}
                  <div className="bg-card border border-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 purple-glow-sm">
                    <div className="flex items-center space-x-3.5">
                      <div className="w-10 h-10 rounded-lg bg-elevated border border-brand-purple/40 flex items-center justify-center text-brand-secondary purple-glow">
                        <Icons.Overview />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-sm font-mono font-bold text-txt-primary">DRISHTI AI GUARDIAN CLUSTER</h3>
                          <span className="px-2 py-0.5 rounded-full bg-status-success/15 border border-status-success/30 text-[10px] font-mono text-status-success font-bold">
                            ONLINE // NORMAL
                          </span>
                        </div>
                        <p className="text-xs font-mono text-txt-muted mt-0.5">
                          Autonomous MLOps monitoring, Loglizer IsolationForest detection, and active incident response.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 font-mono text-xs">
                      <div>
                        <span className="text-txt-muted block text-[10px]">ACTIVE PROJECT:</span>
                        <span className="text-brand-secondary font-bold">{selectedProject.toUpperCase()}</span>
                      </div>
                      <div>
                        <span className="text-txt-muted block text-[10px]">STREAM VELOCITY:</span>
                        <span className="text-txt-primary font-bold">{unifiedLogs.length} EVENTS</span>
                      </div>
                    </div>
                  </div>

                  {/* 6 Compact KPI Panels */}
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">Total Predictions</div>
                      <div className="text-xl font-bold text-txt-primary mt-1">{streamStats.total}</div>
                      <div className="text-[10px] text-status-success mt-0.5">↑ Ingestion Active</div>
                    </div>
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">Avg Latency</div>
                      <div className="text-xl font-bold text-brand-purple mt-1">{streamStats.avgLatency} ms</div>
                      <div className="text-[10px] text-txt-muted mt-0.5">P50 benchmark</div>
                    </div>
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">P95 Latency</div>
                      <div className="text-xl font-bold text-accent-blue mt-1">{streamStats.p95Latency} ms</div>
                      <div className="text-[10px] text-txt-muted mt-0.5">95th percentile</div>
                    </div>
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">Error Rate</div>
                      <div className={`text-xl font-bold mt-1 ${parseFloat(streamStats.errorRate) > 5 ? 'text-status-error' : 'text-status-success'}`}>
                        {streamStats.errorRate}%
                      </div>
                      <div className="text-[10px] text-txt-muted mt-0.5">Operational errors</div>
                    </div>
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">Anomalies</div>
                      <div className="text-xl font-bold text-status-warning mt-1">{streamStats.anomalies}</div>
                      <div className="text-[10px] text-txt-muted mt-0.5">IsolationForest flags</div>
                    </div>
                    <div className="bg-card border border-border rounded-lg p-3">
                      <div className="text-[10px] text-txt-muted uppercase">Open Incidents</div>
                      <div className={`text-xl font-bold mt-1 ${streamStats.openIncidents > 0 ? 'text-status-error' : 'text-status-success'}`}>
                        {streamStats.openIncidents}
                      </div>
                      <div className="text-[10px] text-txt-muted mt-0.5">Triage queue</div>
                    </div>
                  </div>

                  {/* Dual Grid: Real-Time Diagnostic Test & Ground Truth Accuracy */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Panel 1: Live Diagnostic Playground */}
                    <div className="bg-card border border-border rounded-xl p-4 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-xs font-mono font-bold text-txt-primary flex items-center space-x-2">
                            <Icons.Terminal />
                            <span>LOGLIZER ANOMALY DETECTOR PLAYGROUND</span>
                          </h4>
                          <span className="text-[10px] font-mono text-txt-muted">100 Trees // iForest</span>
                        </div>
                        <p className="text-xs text-txt-muted mb-3">
                          Test real-time 16-feature vectorization and IsolationForest anomaly inference on arbitrary logs.
                        </p>

                        <div className="space-y-2.5 font-mono text-xs">
                          <div>
                            <label className="text-[10px] text-txt-muted uppercase">Input Log Message:</label>
                            <input
                              type="text"
                              value={diagMessage}
                              onChange={e => setDiagMessage(e.target.value)}
                              className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1 focus:outline-none focus:border-brand-purple"
                            />
                          </div>

                          <div className="flex items-center space-x-3">
                            <div>
                              <label className="text-[10px] text-txt-muted uppercase">Severity:</label>
                              <select
                                value={diagSeverity}
                                onChange={e => setDiagSeverity(e.target.value)}
                                className="bg-content border border-border rounded px-2.5 py-1 text-xs text-txt-primary ml-2"
                              >
                                <option value="INFO">INFO</option>
                                <option value="WARNING">WARNING</option>
                                <option value="ERROR">ERROR</option>
                                <option value="CRITICAL">CRITICAL</option>
                              </select>
                            </div>
                            <button
                              onClick={handleRunDiagnostic}
                              disabled={diagRunning}
                              className="px-4 py-1.5 rounded bg-brand-purple hover:bg-brand-dark text-white font-bold text-xs purple-glow-sm transition-all"
                            >
                              {diagRunning ? "Scoring..." : "Execute Test"}
                            </button>
                          </div>
                        </div>

                        {diagResult && (
                          <div className="mt-3 p-3 rounded bg-content border border-border font-mono text-xs space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="text-txt-muted">Inference Outcome:</span>
                              <span className={`font-bold ${diagResult.is_anomaly ? "text-status-error" : "text-status-success"}`}>
                                {diagResult.result} ({diagResult.is_anomaly ? "ANOMALY DETECTED" : "NORMAL PATTERN"})
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-txt-muted text-[11px]">
                              <span>Latency: {diagResult.latency_ms}ms</span>
                              <span>Incident Triggered: {diagResult.alert ? "YES" : "NO"}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Panel 2: Ground-Truth Accuracy & Model Drift */}
                    <div className="bg-card border border-border rounded-xl p-4 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-xs font-mono font-bold text-txt-primary flex items-center space-x-2">
                            <Icons.Drift />
                            <span>GROUND-TRUTH DRIFT & ACCURACY TRACKER</span>
                          </h4>
                          <span className="text-[10px] font-mono text-brand-secondary">{selectedProject}</span>
                        </div>
                        <p className="text-xs text-txt-muted mb-3">
                          Evaluates production prediction accuracy vs reported ground-truth outcomes.
                        </p>

                        {selectedProject === "all" ? (
                          <div className="p-4 rounded-lg bg-content border border-border text-xs font-mono text-txt-muted space-y-2">
                            <p className="text-txt-primary font-bold">Platform-Wide Aggregate View</p>
                            <p>Showing global telemetry across {projects.length} projects.</p>
                            <p className="text-brand-secondary">
                              Select a specific project from the left sidebar to inspect isolated drift metrics (MAE, RMSE, Ground-Truth count).
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-3 font-mono text-xs">
                            <div className="grid grid-cols-2 gap-3">
                              <div className="p-3 rounded bg-content border border-border">
                                <span className="text-[10px] text-txt-muted uppercase">Verified Samples</span>
                                <div className="text-lg font-bold text-txt-primary mt-0.5">
                                  {driftData?.sample_size !== undefined ? driftData.sample_size : (telemetry.filter(t => t.ground_truth !== null && t.ground_truth !== undefined).length)}
                                </div>
                              </div>
                              <div className="p-3 rounded bg-content border border-border">
                                <span className="text-[10px] text-txt-muted uppercase">Health Status</span>
                                <div className="text-lg font-bold text-status-success mt-0.5">
                                  {driftData?.status || "HEALTHY"}
                                </div>
                              </div>
                            </div>

                            <div className="p-3 rounded bg-content border border-border space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className="text-txt-muted">Mean Absolute Error (MAE):</span>
                                <span className="text-status-success font-bold">
                                  {driftData?.evaluation_available ? (typeof driftData.mae === 'number' ? driftData.mae.toFixed(4) : driftData.mae) : "Available with ground truth"}
                                </span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-txt-muted">Root Mean Squared Error (RMSE):</span>
                                <span className="text-accent-blue font-bold">
                                  {driftData?.evaluation_available ? (typeof driftData.rmse === 'number' ? driftData.rmse.toFixed(4) : driftData.rmse) : "Available with ground truth"}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 3: TELEMETRY FEED                                             */}
              {/* ================================================================= */}
              {activeTab === "telemetry" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-txt-primary">UNIVERSAL INGESTED TELEMETRY STREAM</h3>
                      <p className="text-xs text-txt-muted">Predictions, inputs, confidence scores, and ground truth isolated per project.</p>
                    </div>
                    <span className="text-xs text-brand-secondary">Count: {telemetry.length}</span>
                  </div>

                  <div className="overflow-x-auto border border-border rounded-lg">
                    <table className="w-full text-left divide-y divide-border text-[11.5px]">
                      <thead className="bg-canvas text-txt-muted uppercase text-[10px]">
                        <tr>
                          <th className="p-2.5">Timestamp</th>
                          <th className="p-2.5">Event</th>
                          <th className="p-2.5">Model</th>
                          <th className="p-2.5">Prediction</th>
                          <th className="p-2.5">Confidence</th>
                          <th className="p-2.5">Ground Truth</th>
                          <th className="p-2.5">Latency</th>
                          <th className="p-2.5">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40 bg-content">
                        {telemetry.length === 0 ? (
                          <tr>
                            <td colSpan="8" className="p-6 text-center text-txt-muted">
                              No telemetry records found for this workspace. Use drishti_sdk to stream data.
                            </td>
                          </tr>
                        ) : (
                          telemetry.map((t, idx) => (
                            <tr
                              key={idx}
                              onClick={() => { setSelectedItem(t); if (!rightPanelOpen) setRightPanelOpen(true); }}
                              className="hover:bg-card/70 cursor-pointer transition-colors"
                            >
                              <td className="p-2.5 text-txt-muted">{t.timestamp ? t.timestamp.split("T")[1]?.slice(0, 12) : "-"}</td>
                              <td className="p-2.5 text-accent-blue font-semibold">{t.event_type}</td>
                              <td className="p-2.5 text-txt-primary">{t.model_name || t.project_id}</td>
                              <td className="p-2.5 text-txt-primary font-bold">{t.prediction !== undefined && t.prediction !== null ? JSON.stringify(t.prediction) : "-"}</td>
                              <td className="p-2.5 text-brand-purple">{t.confidence !== undefined && t.confidence !== null ? t.confidence : "-"}</td>
                              <td className="p-2.5 text-status-success font-semibold">{t.ground_truth !== undefined && t.ground_truth !== null ? JSON.stringify(t.ground_truth) : "-"}</td>
                              <td className="p-2.5 text-txt-muted">{t.latency_ms ? `${parseFloat(t.latency_ms).toFixed(1)}ms` : "-"}</td>
                              <td className="p-2.5">
                                {t.is_anomaly ? (
                                  <span className="px-1.5 py-0.5 rounded bg-status-error/15 text-status-error border border-status-error/30 text-[10px] font-bold">
                                    ANOMALY
                                  </span>
                                ) : (
                                  <span className="px-1.5 py-0.5 rounded bg-status-success/15 text-status-success border border-status-success/30 text-[10px] font-bold">
                                    NORMAL
                                  </span>
                                )}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 4: ANOMALY DETECTION INVESTIGATION                            */}
              {/* ================================================================= */}
              {activeTab === "anomaly" && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Anomaly />
                        <span>LOGLIZER ISOLATION FOREST DETECTOR</span>
                      </h3>
                      <span className="px-2 py-0.5 rounded bg-brand-purple/20 text-brand-secondary border border-brand-purple/30 text-[10px] font-bold">
                        ACTIVE INFERENCE
                      </span>
                    </div>
                    <p className="text-xs text-txt-muted mb-4">
                      Unsupervised machine learning model inspecting 16-dimensional numerical features extracted from log messages.
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                      <div className="p-3 rounded bg-content border border-border">
                        <span className="text-[10px] text-txt-muted">ESTIMATORS</span>
                        <div className="text-base font-bold text-txt-primary mt-1">100 Trees</div>
                      </div>
                      <div className="p-3 rounded bg-content border border-border">
                        <span className="text-[10px] text-txt-muted">CONTAMINATION</span>
                        <div className="text-base font-bold text-brand-purple mt-1">0.20 (20%)</div>
                      </div>
                      <div className="p-3 rounded bg-content border border-border">
                        <span className="text-[10px] text-txt-muted">MODEL ARTIFACT</span>
                        <div className="text-[11px] font-bold text-txt-secondary mt-1 truncate">models/log_anomaly_detector.joblib</div>
                      </div>
                      <div className="p-3 rounded bg-content border border-border">
                        <span className="text-[10px] text-txt-muted">ANOMALY FLAGS</span>
                        <div className="text-base font-bold text-status-warning mt-1">{streamStats.anomalies} Total</div>
                      </div>
                    </div>

                    <h4 className="text-[11px] font-bold text-txt-secondary mb-2 uppercase">16-Dimensional Normalization Schema:</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px]">
                      {[
                        "severity_INFO", "severity_WARNING", "severity_ERROR", "severity_CRITICAL",
                        "event_database", "event_prediction", "event_memory", "event_inference",
                        "event_latency", "event_authentication", "event_model", "event_api",
                        "event_other", "is_timeout", "is_failed", "is_high_usage"
                      ].map((feat, i) => (
                        <div key={i} className="p-2 rounded bg-content border border-border flex items-center justify-between">
                          <span className="text-txt-muted">{i+1}. {feat}</span>
                          <span className="text-brand-secondary">float</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 5: ALERTS & INCIDENTS                                         */}
              {/* ================================================================= */}
              {activeTab === "incidents" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Incidents />
                        <span>PROJECT-SCOPED INCIDENT QUEUE</span>
                      </h3>
                      <p className="text-xs text-txt-muted">MD5 fingerprint deduplication, severity triage, and operational lifecycle tracking.</p>
                    </div>
                    <span className="text-xs text-status-warning">Active Incidents: {streamStats.openIncidents}</span>
                  </div>

                  <div className="overflow-x-auto border border-border rounded-lg">
                    <table className="w-full text-left divide-y divide-border text-[11.5px]">
                      <thead className="bg-canvas text-txt-muted uppercase text-[10px]">
                        <tr>
                          <th className="p-2.5">ID</th>
                          <th className="p-2.5">Project</th>
                          <th className="p-2.5">Severity</th>
                          <th className="p-2.5">Incident Title & Details</th>
                          <th className="p-2.5">Hits</th>
                          <th className="p-2.5">Status</th>
                          <th className="p-2.5">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40 bg-content">
                        {incidents.length === 0 ? (
                          <tr>
                            <td colSpan="7" className="p-6 text-center text-status-success font-bold">
                              ✓ All operational systems nominal. No open incidents.
                            </td>
                          </tr>
                        ) : (
                          incidents.map((inc) => (
                            <tr key={inc.id} className="hover:bg-card/70 transition-colors">
                              <td className="p-2.5 text-txt-muted">#{inc.id}</td>
                              <td className="p-2.5 text-accent-blue font-semibold">{inc.project_id || "default"}</td>
                              <td className="p-2.5"><LevelChip level={inc.severity} /></td>
                              <td className="p-2.5 text-txt-primary max-w-md truncate">{inc.message}</td>
                              <td className="p-2.5 text-brand-purple font-bold">{inc.occurrences || 1}</td>
                              <td className="p-2.5"><StatusBadge status={inc.status} /></td>
                              <td className="p-2.5">
                                {inc.status !== "RESOLVED" && (
                                  <button
                                    onClick={() => handleResolveIncident(inc.id)}
                                    className="px-2.5 py-1 rounded bg-status-success/20 hover:bg-status-success text-status-success hover:text-white border border-status-success/40 text-[10px] font-bold transition-all"
                                  >
                                    Resolve
                                  </button>
                                )}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 6: AUTOMATED PLAYBOOKS                                        */}
              {/* ================================================================= */}
              {activeTab === "playbooks" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Playbooks />
                        <span>AUTOMATED REMEDIATION PLAYBOOKS</span>
                      </h3>
                      <p className="text-xs text-txt-muted">Non-destructive automated response actions triggered by operational anomalies.</p>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-status-warning/15 text-status-warning border border-status-warning/30 text-[10px] font-bold">
                      SIMULATED REMEDIATION
                    </span>
                  </div>

                  <div className="space-y-2">
                    {responses.length === 0 ? (
                      <p className="p-6 text-center text-txt-muted">No automated remediation actions executed yet.</p>
                    ) : (
                      responses.map((resp, i) => (
                        <div key={i} className="p-3 rounded-lg bg-content border border-border flex items-center justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <span className="font-bold text-brand-secondary">{resp.playbook}</span>
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-card text-txt-muted">Project: {resp.project_id || "core"}</span>
                            </div>
                            <p className="text-txt-primary text-[11px]">{resp.action_taken}</p>
                          </div>
                          <div className="text-right text-[11px]">
                            <span className="text-status-success font-bold">{resp.status}</span>
                            <div className="text-txt-muted text-[10px] mt-0.5">{resp.timestamp?.split("T")[1]?.slice(0, 8)}</div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 7: MODEL MONITORING & MLOps                                   */}
              {/* ================================================================= */}
              {activeTab === "models" && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Models />
                        <span>MLFLOW EXPERIMENT TRACKING & MODEL REGISTRY</span>
                      </h3>
                      <span className="text-xs text-brand-secondary">Store: sqlite:///mlflow.db</span>
                    </div>
                    <p className="text-xs text-txt-muted mb-4">
                      Integrated MLOps lifecycle tracking hyperparameters, metric curves, model artifacts, and stage promotion.
                    </p>

                    <div className="overflow-x-auto border border-border rounded-lg">
                      <table className="w-full text-left divide-y divide-border text-[11px]">
                        <thead className="bg-canvas text-txt-muted uppercase text-[10px]">
                          <tr>
                            <th className="p-2.5">Run ID</th>
                            <th className="p-2.5">Experiment</th>
                            <th className="p-2.5">RMSE</th>
                            <th className="p-2.5">MAE</th>
                            <th className="p-2.5">R² Score</th>
                            <th className="p-2.5">Stage</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/40 bg-content">
                          {mlopsRuns.length === 0 ? (
                            <tr>
                              <td colSpan="6" className="p-4 text-center text-txt-muted">No MLflow runs recorded.</td>
                            </tr>
                          ) : (
                            mlopsRuns.map((r, i) => (
                              <tr key={i} className="hover:bg-card/70">
                                <td className="p-2.5 text-brand-secondary font-bold truncate max-w-[120px]">{r.run_id}</td>
                                <td className="p-2.5 text-txt-primary">{r.run_name || "taxi_fare_pipeline"}</td>
                                <td className="p-2.5 text-status-success font-bold">{r.metrics?.rmse ? r.metrics.rmse.toFixed(4) : "-"}</td>
                                <td className="p-2.5 text-accent-blue">{r.metrics?.mae ? r.metrics.mae.toFixed(4) : "-"}</td>
                                <td className="p-2.5 text-brand-purple">{r.metrics?.r2 ? r.metrics.r2.toFixed(4) : "-"}</td>
                                <td className="p-2.5">
                                  <span className="px-2 py-0.5 rounded bg-status-success/15 text-status-success border border-status-success/30 text-[10px] font-bold">
                                    PRODUCTION
                                  </span>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 8: PROJECTS & INTEGRATIONS                                    */}
              {activeTab === "projects" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Projects />
                        <span>REGISTERED WORKSPACES & APPLICATIONS</span>
                      </h3>
                      <p className="text-xs text-txt-muted">Multi-project isolation, cryptographic key management, and schema mappings.</p>
                    </div>
                    <button
                      onClick={() => setShowRegisterModal(true)}
                      className="px-3 py-1.5 rounded bg-brand-purple hover:bg-brand-dark text-white font-bold text-xs purple-glow-sm flex items-center space-x-1.5"
                    >
                      <Icons.Plus />
                      <span>Register New Project</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {projects.map(p => (
                      <div key={p.project_id} className="p-3.5 rounded-lg bg-content border border-border space-y-2 hover:border-brand-purple/40 transition-colors">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-txt-primary">{p.name}</span>
                          <span className="px-1.5 py-0.2 rounded bg-card text-[10px] text-accent-blue border border-border">{p.framework}</span>
                        </div>
                        <div className="text-[11px] text-txt-muted">ID: <span className="text-brand-secondary font-mono">{p.project_id}</span></div>
                        <div className="text-[10px] text-txt-muted truncate">{p.description || "Machine learning application model"}</div>
                        <div className="pt-2 border-t border-border/40 flex items-center justify-between text-[10px]">
                          <span className="text-txt-muted">API Token:</span>
                          <span className="font-mono text-txt-secondary">{p.api_key_masked || "dr_live_••••••"}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 9: SDK & API KEYS                                             */}
              {activeTab === "integrations" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-4">
                  <div>
                    <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                      <Icons.Integrations />
                      <span>DEVELOPER INTEGRATION & UNIVERSAL SDK</span>
                    </h3>
                    <p className="text-xs text-txt-muted">Integrate any external ML application into DRISHTI AI in under 5 lines of code.</p>
                  </div>

                  <div className="space-y-3">
                    <div className="p-3.5 rounded-lg bg-content border border-border space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-accent-blue">Option 1: Python SDK (`drishti_sdk`)</span>
                        <button
                          onClick={() => {
                            const port = window.location.port || '8001';
                            navigator.clipboard.writeText(`from drishti_sdk import DrishtiClient\\n\\nclient = DrishtiClient(project_id="${selectedProject}", api_key="YOUR_KEY", endpoint="http://${window.location.hostname || 'localhost'}:${port}")\\nclient.log_prediction(model_name="my-model", prediction=1, latency_ms=18.5)`);
                            notify("Python code snippet copied!", "success");
                          }}
                          className="text-xs text-brand-secondary hover:underline flex items-center space-x-1"
                        >
                          <Icons.Copy />
                          <span>Copy Code</span>
                        </button>
                      </div>
                      <pre className="p-3 rounded bg-canvas text-txt-primary text-[11px] overflow-x-auto leading-relaxed">
{`from drishti_sdk import DrishtiClient

# 1. Connect client to DRISHTI AI
client = DrishtiClient(
    project_id="${selectedProject !== 'all' ? selectedProject : 'house-price-prediction'}",
    api_key="dr_live_••••••••••••••••••••••••••••••••",
    endpoint="http://127.0.0.1:8001"
)

# 2. Log inference predictions & latencies
client.log_prediction(
    model_name="random-forest-v1",
    prediction=685000.0,
    confidence=0.94,
    latency_ms=18.5,
    ground_truth=690000.0  # Optional: when verified sale price arrives
)`}
                      </pre>
                    </div>

                    <div className="p-3.5 rounded-lg bg-content border border-border space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-brand-secondary">Option 2: Universal HTTP REST API</span>
                        <button
                          onClick={() => {
                            const port = window.location.port || '8001';
                            navigator.clipboard.writeText(`curl -X POST http://${window.location.hostname || '127.0.0.1'}:${port}/telemetry/ingest -H "Content-Type: application/json" -H "X-API-Key: YOUR_KEY" -d '{"project_id": "${selectedProject}", "record": {"prediction": 1, "latency_ms": 18.5}}'`);
                            notify("cURL snippet copied!", "success");
                          }}
                          className="text-xs text-brand-secondary hover:underline flex items-center space-x-1"
                        >
                          <Icons.Copy />
                          <span>Copy cURL</span>
                        </button>
                      </div>
                      <pre className="p-3 rounded bg-canvas text-txt-primary text-[11px] overflow-x-auto leading-relaxed">
{`curl -X POST "http://127.0.0.1:8001/telemetry/ingest" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: dr_live_••••••••••••••••••••••••••••••••" \\
  -d '{
    "project_id": "${selectedProject !== 'all' ? selectedProject : 'house-price-prediction'}",
    "record": {
      "event_type": "prediction",
      "model_name": "model-v1",
      "prediction": 685000.0,
      "latency_ms": 18.5
    }
  }'`}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 10: PROMETHEUS METRICS                                        */}
              {activeTab === "metrics" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                        <Icons.Metrics />
                        <span>STANDARDS-COMPLIANT PROMETHEUS METRICS</span>
                      </h3>
                      <p className="text-xs text-txt-muted">Exposed directly at `/metrics` (Prometheus text format v0.0.4).</p>
                    </div>
                    <a
                      href="/metrics"
                      target="_blank"
                      className="px-2.5 py-1 rounded bg-elevated border border-border hover:border-brand-purple text-brand-secondary"
                    >
                      Open Raw /metrics ↗
                    </a>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 rounded bg-content border border-border">
                      <span className="text-[10px] text-txt-muted">drishti_logs_processed_total</span>
                      <div className="text-lg font-bold text-txt-primary mt-1">{streamStats.total}</div>
                    </div>
                    <div className="p-3 rounded bg-content border border-border">
                      <span className="text-[10px] text-txt-muted">drishti_anomalies_detected_total</span>
                      <div className="text-lg font-bold text-status-warning mt-1">{streamStats.anomalies}</div>
                    </div>
                    <div className="p-3 rounded bg-content border border-border">
                      <span className="text-[10px] text-txt-muted">drishti_prediction_latency_seconds_sum</span>
                      <div className="text-lg font-bold text-accent-blue mt-1">{(parseFloat(streamStats.avgLatency) * streamStats.total / 1000).toFixed(2)}s</div>
                    </div>
                    <div className="p-3 rounded bg-content border border-border">
                      <span className="text-[10px] text-txt-muted">drishti_incidents_active</span>
                      <div className="text-lg font-bold text-status-error mt-1">{streamStats.openIncidents}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* ================================================================= */}
              {/* TAB 11: SYSTEM SETTINGS & DIAGNOSTICS                             */}
              {activeTab === "settings" && (
                <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-4">
                  <div>
                    <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                      <Icons.Settings />
                      <span>SYSTEM DIAGNOSTICS & RUNTIME CONFIGURATION</span>
                    </h3>
                    <p className="text-xs text-txt-muted">Local filesystem paths, active dependencies, and model weights integrity.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px]">
                    <div className="p-3 rounded bg-content border border-border space-y-1.5">
                      <div className="text-txt-muted uppercase font-bold text-[10px]">Paths & Directories:</div>
                      <div>Telemetry Partitions: <span className="text-txt-primary">data/telemetry/*.jsonl</span></div>
                      <div>Project Registry: <span className="text-txt-primary">data/projects.json</span></div>
                      <div>Incident Storage: <span className="text-txt-primary">alerts/incidents.json</span></div>
                      <div>Remediation Audit: <span className="text-txt-primary">alerts/remediation_audit.json</span></div>
                    </div>
                    <div className="p-3 rounded bg-content border border-border space-y-1.5">
                      <div className="text-txt-muted uppercase font-bold text-[10px]">Model Weights & Runtimes:</div>
                      <div>Loglizer IsolationForest: <span className="text-status-success font-bold">LOADED</span></div>
                      <div>FastAPI Gateway: <span className="text-status-success font-bold">ACTIVE (127.0.0.1:8001)</span></div>
                      <div>Prometheus Engine: <span className="text-status-success font-bold">EXPOSING (v0.0.4)</span></div>
                      <div>Keep AIOps Orchestrator: <span className="text-txt-muted">LOCAL FALLBACK ACTIVE</span></div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </main>

          {/* ========================================================================= */}
          {/* C. RIGHT CONTEXTUAL DRAWER (ANALYTICS & LOG INSPECTOR)                    */}
          {/* ========================================================================= */}
          {rightPanelOpen && (
            <aside className="w-80 bg-sidebar border-l border-border flex flex-col justify-between shrink-0 transition-all z-10 text-xs font-mono">
              {/* Drawer Header */}
              <div className="h-14 border-b border-border px-3.5 flex items-center justify-between bg-canvas/40">
                <span className="font-bold text-[11px] text-txt-primary tracking-wider uppercase flex items-center space-x-2">
                  <Icons.Metrics />
                  <span>{selectedItem ? "INSPECTOR // EVENT" : "TELEMETRY METRICS"}</span>
                </span>
                <div className="flex items-center space-x-1">
                  {selectedItem && (
                    <button
                      onClick={() => setSelectedItem(null)}
                      className="px-2 py-0.5 rounded bg-card hover:bg-elevated text-[10px] text-txt-muted hover:text-txt-primary border border-border"
                    >
                      Clear
                    </button>
                  )}
                  <button
                    onClick={() => setRightPanelOpen(false)}
                    className="p-1 rounded text-txt-muted hover:text-txt-primary"
                    title="Collapse Panel"
                  >
                    ✕
                  </button>
                </div>
              </div>

              {/* Drawer Content */}
              <div className="flex-1 overflow-y-auto p-3.5 space-y-4">
                {/* 1. SELECTED LOG / TELEMETRY INSPECTOR */}
                {selectedItem ? (
                  <div className="space-y-3">
                    <div className="p-2.5 rounded bg-content border border-border space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-txt-muted text-[10px]">EVENT IDENTIFIER:</span>
                        <LevelChip level={selectedItem.level} />
                      </div>
                      <div className="text-sm font-bold text-brand-secondary break-all">#{selectedItem.id}</div>
                    </div>

                    <div className="space-y-1.5 text-[11px]">
                      <div className="flex items-center justify-between text-txt-muted">
                        <span>Timestamp:</span>
                        <span className="text-txt-primary">{selectedItem.timestamp}</span>
                      </div>
                      <div className="flex items-center justify-between text-txt-muted">
                        <span>Source:</span>
                        <span className="text-accent-blue">{selectedItem.source}</span>
                      </div>
                      {selectedItem.model && (
                        <div className="flex items-center justify-between text-txt-muted">
                          <span>Model Name:</span>
                          <span className="text-txt-primary font-bold">{selectedItem.model}</span>
                        </div>
                      )}
                      {selectedItem.latency && (
                        <div className="flex items-center justify-between text-txt-muted">
                          <span>Latency:</span>
                          <span className="text-brand-purple font-bold">{selectedItem.latency}</span>
                        </div>
                      )}
                    </div>

                    {/* Prediction & Ground Truth Details */}
                    {(selectedItem.prediction !== undefined || selectedItem.ground_truth !== undefined) && (
                      <div className="p-2.5 rounded bg-content border border-border space-y-1 text-[11px]">
                        <div className="text-txt-muted text-[10px] uppercase font-bold">Inference Telemetry:</div>
                        {selectedItem.prediction !== undefined && (
                          <div className="flex items-center justify-between">
                            <span className="text-txt-muted">Prediction:</span>
                            <span className="text-txt-primary font-bold">{JSON.stringify(selectedItem.prediction)}</span>
                          </div>
                        )}
                        {selectedItem.confidence !== undefined && (
                          <div className="flex items-center justify-between">
                            <span className="text-txt-muted">Confidence:</span>
                            <span className="text-brand-purple font-bold">{selectedItem.confidence}</span>
                          </div>
                        )}
                        {selectedItem.ground_truth !== undefined && (
                          <div className="flex items-center justify-between">
                            <span className="text-txt-muted">Ground Truth:</span>
                            <span className="text-status-success font-bold">{JSON.stringify(selectedItem.ground_truth)}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Inputs Payload JSON */}
                    {selectedItem.inputs && (
                      <div className="space-y-1">
                        <span className="text-txt-muted text-[10px] uppercase font-bold">Input Features:</span>
                        <pre className="p-2.5 rounded bg-content border border-border text-[10px] text-txt-primary overflow-x-auto max-h-32">
                          {JSON.stringify(selectedItem.inputs, null, 2)}
                        </pre>
                      </div>
                    )}

                    {/* Message Body */}
                    <div className="space-y-1">
                      <span className="text-txt-muted text-[10px] uppercase font-bold">Log Message:</span>
                      <p className="p-2.5 rounded bg-content border border-border text-[11px] text-txt-primary break-words">
                        {selectedItem.message}
                      </p>
                    </div>

                    {/* Raw JSON Copy Button */}
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(selectedItem.raw || selectedItem, null, 2));
                        notify(`Copied full payload to clipboard`, "success");
                      }}
                      className="w-full py-1.5 rounded bg-card hover:bg-elevated border border-border hover:border-brand-purple text-brand-secondary text-[11px] font-bold flex items-center justify-center space-x-1.5 transition-colors"
                    >
                      <Icons.Copy />
                      <span>Copy Complete JSON Record</span>
                    </button>
                  </div>
                ) : (
                  /* 2. REAL-TIME STREAM DISTRIBUTION & VOLUME METRICS */
                  <div className="space-y-4">
                    {/* Log Level Breakdown Bar & Counters */}
                    <div className="p-3 rounded-lg bg-content border border-border space-y-2.5">
                      <div className="text-[10px] text-txt-muted uppercase font-bold">Severity Distribution</div>
                      <div className="space-y-2">
                        <div>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-status-info font-bold">INFO</span>
                            <span className="text-txt-primary font-bold">{streamStats.counts.INFO || 0}</span>
                          </div>
                          <div className="w-full h-1.5 bg-canvas rounded-full overflow-hidden mt-1">
                            <div
                              className="h-full bg-status-info"
                              style={{ width: `${streamStats.total ? (streamStats.counts.INFO / streamStats.total) * 100 : 0}%` }}
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-status-warning font-bold">WARN</span>
                            <span className="text-txt-primary font-bold">{streamStats.counts.WARN || 0}</span>
                          </div>
                          <div className="w-full h-1.5 bg-canvas rounded-full overflow-hidden mt-1">
                            <div
                              className="h-full bg-status-warning"
                              style={{ width: `${streamStats.total ? (streamStats.counts.WARN / streamStats.total) * 100 : 0}%` }}
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-status-error font-bold">ERROR</span>
                            <span className="text-txt-primary font-bold">{streamStats.counts.ERROR || 0}</span>
                          </div>
                          <div className="w-full h-1.5 bg-canvas rounded-full overflow-hidden mt-1">
                            <div
                              className="h-full bg-status-error"
                              style={{ width: `${streamStats.total ? (streamStats.counts.ERROR / streamStats.total) * 100 : 0}%` }}
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="text-status-critical font-bold">CRITICAL</span>
                            <span className="text-txt-primary font-bold">{streamStats.counts.CRITICAL || 0}</span>
                          </div>
                          <div className="w-full h-1.5 bg-canvas rounded-full overflow-hidden mt-1">
                            <div
                              className="h-full bg-status-critical"
                              style={{ width: `${streamStats.total ? (streamStats.counts.CRITICAL / streamStats.total) * 100 : 0}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Operational Health Checklist */}
                    <div className="p-3 rounded-lg bg-content border border-border space-y-2 text-[11px]">
                      <div className="text-[10px] text-txt-muted uppercase font-bold">Operational Checklist</div>
                      <div className="flex items-center justify-between">
                        <span className="text-txt-muted">Log Ingestion:</span>
                        <span className="text-status-success font-bold">ACTIVE</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-txt-muted">Anomaly Detector:</span>
                        <span className="text-status-success font-bold">HEALTHY</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-txt-muted">Auto-Remediation:</span>
                        <span className="text-brand-purple font-bold">ARMED</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-txt-muted">Prometheus Exporter:</span>
                        <span className="text-status-success font-bold">ONLINE</span>
                      </div>
                    </div>

                    {/* Contextual Quick Tip */}
                    <div className="p-3 rounded-lg bg-canvas border border-border text-[11px] text-txt-muted leading-relaxed">
                      💡 <span className="text-txt-primary font-bold">Terminal Tip:</span> Click on any row in the <span className="text-brand-secondary">Live Logs</span> terminal or <span className="text-accent-blue">Telemetry Feed</span> to inspect its extracted 16-feature vector and payload metadata.
                    </div>
                  </div>
                )}
              </div>

              {/* Drawer Footer */}
              <div className="p-3 border-t border-border bg-canvas/30 text-[10px] text-txt-muted flex items-center justify-between">
                <span>Buffer Rate: ~{Math.min(unifiedLogs.length, 120)}/min</span>
                <span className="text-brand-purple">DRISHTI AIOps</span>
              </div>
            </aside>
          )}

          {/* ========================================================================= */}
          {/* MODAL: REGISTER NEW PROJECT                                               */}
          {/* ========================================================================= */}
          {showRegisterModal && (
            <div className="fixed inset-0 bg-canvas/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-card border border-brand-purple/40 rounded-xl p-5 w-full max-w-md font-mono text-xs space-y-4 purple-glow">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <h3 className="text-sm font-bold text-txt-primary flex items-center space-x-2">
                    <Icons.Projects />
                    <span>REGISTER NEW ML WORKSPACE</span>
                  </h3>
                  <button onClick={() => { setShowRegisterModal(false); setRegisteredApiKey(null); }} className="text-txt-muted hover:text-txt-primary">
                    ✕
                  </button>
                </div>

                {registeredApiKey ? (
                  <div className="space-y-3">
                    <div className="p-3 rounded bg-status-success/15 border border-status-success/30 text-status-success font-bold text-center">
                      ✓ Project Registered Successfully!
                    </div>
                    <div className="space-y-1">
                      <span className="text-[10px] text-txt-muted uppercase">Secret API Key (Save it now; won't be shown again):</span>
                      <div className="p-2.5 rounded bg-content border border-brand-purple text-brand-secondary font-mono text-xs break-all select-all">
                        {registeredApiKey}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(registeredApiKey);
                        notify("API Key copied to clipboard!", "success");
                        setShowRegisterModal(false);
                        setRegisteredApiKey(null);
                        fetchData();
                      }}
                      className="w-full py-2 rounded bg-brand-purple hover:bg-brand-dark text-white font-bold transition-all"
                    >
                      Copy Key & Close
                    </button>
                  </div>
                ) : (
                  <form
                    onSubmit={async (e) => {
                      e.preventDefault();
                      const form = e.target;
                      const payload = {
                        project_id: form.project_id.value,
                        name: form.name.value,
                        description: form.description.value,
                        model_type: form.model_type.value,
                        framework: form.framework.value,
                        schema_mapping: {
                          latency_field: "latency_ms",
                          prediction_field: "prediction"
                        }
                      };
                      try {
                        const res = await fetch('/projects/register', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify(payload)
                        });
                        const data = await res.json();
                        if (res.ok) {
                          setRegisteredApiKey(data.api_key);
                        } else {
                          notify(data.detail || "Registration failed", "error");
                        }
                      } catch (err) {
                        notify(err.message, "error");
                      }
                    }}
                    className="space-y-3"
                  >
                    <div>
                      <label className="text-[10px] text-txt-muted uppercase">Project Identifier (Slug):</label>
                      <input
                        name="project_id"
                        required
                        placeholder="e.g. churn-risk-model"
                        className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1 focus:outline-none focus:border-brand-purple"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] text-txt-muted uppercase">Project Display Name:</label>
                      <input
                        name="name"
                        required
                        placeholder="e.g. Customer Churn Risk Engine"
                        className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1 focus:outline-none focus:border-brand-purple"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-txt-muted uppercase">Model Type:</label>
                        <select name="model_type" className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1">
                          <option value="binary_classification">Binary Classification</option>
                          <option value="regression">Regression</option>
                          <option value="multiclass">Multiclass Classification</option>
                          <option value="nlp">Natural Language Processing</option>
                          <option value="computer_vision">Computer Vision</option>
                          <option value="recommendation">Recommendation System</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-[10px] text-txt-muted uppercase">Framework:</label>
                        <select name="framework" className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1">
                          <option value="scikit-learn">Scikit-Learn</option>
                          <option value="pytorch">PyTorch</option>
                          <option value="tensorflow">TensorFlow</option>
                          <option value="xgboost">XGBoost / LightGBM</option>
                          <option value="llm">LLM API / Custom</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] text-txt-muted uppercase">Description:</label>
                      <textarea
                        name="description"
                        rows="2"
                        placeholder="Operational description of model..."
                        className="w-full bg-content border border-border rounded p-2 text-txt-primary mt-1 focus:outline-none focus:border-brand-purple"
                      ></textarea>
                    </div>

                    <div className="pt-2 flex items-center justify-end space-x-2">
                      <button
                        type="button"
                        onClick={() => setShowRegisterModal(false)}
                        className="px-3 py-1.5 rounded bg-content border border-border text-txt-muted hover:text-txt-primary"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-1.5 rounded bg-brand-purple hover:bg-brand-dark text-white font-bold purple-glow-sm transition-all"
                      >
                        Generate API Key
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

    // Mount the Application
    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
"""
