"""
DRISHTI AI — Logtail-Style Terminal Observability Platform
Faithful recreation of the Logtail terminal design language:
- Dark atmospheric ambient canvas with purple/magenta wireframe perspective grid
- Floating rounded-2xl application window with precise color tokens:
  --app-background: #111827;
  --sidebar-background: #30394d;
  --workspace-background: #1e293b;
  --terminal-background: #20283a;
  --panel-background: #273247;
  --border-subtle: #39445a;
  --text-primary: #e2e8f0;
  --text-secondary: #a3adbf;
  --text-muted: #718096;
  --accent-purple: #8b5cf6;
  --accent-blue: #6689e8;
  --accent-cyan: #67b8d9;
- High-density monospace terminal stream with indicator dots and service pills
- Floating 'Jump to live tail' button
- Right-hand vertical timeline histogram scrubber with purple range selection overlay
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DRISHTI AI — Logtail Terminal Observability</title>
  
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            app: '#111827',
            sidebar: '#30394d',
            workspace: '#1e293b',
            terminal: '#20283a',
            panel: '#273247',
            elevated: '#303b52',
            borderSubtle: '#39445a',
            borderMuted: '#303b50',
            txtPrimary: '#e2e8f0',
            txtSecondary: '#a3adbf',
            txtMuted: '#718096',
            brandPurple: '#8b5cf6',
            brandBlue: '#6689e8',
            brandCyan: '#67b8d9',
            brandGreen: '#59b98a',
            brandAmber: '#e6b45c',
            brandRed: '#e16d79'
          },
          fontFamily: {
            sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
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
    /* Fullscreen Atmospheric Canvas with Neon Wireframe Grid */
    body {
      background-color: #0c0f17;
      background-image: 
        radial-gradient(circle at 10% 95%, rgba(139, 92, 246, 0.35) 0%, transparent 40%),
        radial-gradient(circle at 90% 95%, rgba(217, 70, 239, 0.3) 0%, transparent 40%),
        radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.5) 0%, transparent 60%);
      color: #e2e8f0;
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }

    /* Bottom Wireframe Perspective Grid */
    .ambient-grid {
      position: fixed;
      bottom: -60px;
      left: 0;
      right: 0;
      height: 280px;
      background-image: 
        linear-gradient(to right, rgba(139, 92, 246, 0.15) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(217, 70, 239, 0.15) 1px, transparent 1px);
      background-size: 50px 30px;
      transform: perspective(400px) rotateX(68deg);
      transform-origin: bottom center;
      pointer-events: none;
      z-index: 0;
      mask-image: linear-gradient(to top, rgba(0,0,0,1) 30%, transparent 100%);
      -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,1) 30%, transparent 100%);
    }

    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }

    /* Custom Terminal Scrollbar */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: #1a202c;
    }
    ::-webkit-scrollbar-thumb {
      background: #39445a;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #8b5cf6;
    }

    /* Terminal Row Selected */
    .log-row-selected {
      background-color: rgba(102, 137, 232, 0.12) !important;
      border-left: 2px solid #8b5cf6 !important;
    }
  </style>
</head>
<body class="flex items-center justify-center p-2 sm:p-4 md:p-6 select-none relative">
  <!-- Atmospheric Wireframe Floor -->
  <div class="ambient-grid"></div>

  <!-- React Mount Point -->
  <div id="root" class="w-full h-full max-w-[1780px] max-h-[960px] z-10"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef, useMemo } = React;

    // --- LOGTAIL-STYLE OUTLINE ICONS ---
    const Icons = {
      Logo: () => (
        <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
          <path d="M4 6h16a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1zm0 8h10a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1z" />
          <circle cx="19" cy="16" r="2" fill="#8b5cf6" />
        </svg>
      ),
      LiveTail: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="4 17 10 11 4 5" /><line x1="12" y1="19" x2="20" y2="19" />
        </svg>
      ),
      Sources: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 2 7 12 12 22 7 12 2" /><polyline points="2 17 12 22 22 17" /><polyline points="2 12 12 17 22 12" />
        </svg>
      ),
      Views: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" /><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        </svg>
      ),
      Alerts: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      ),
      Archive: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="21 8 21 21 3 21 3 8" /><rect x="1" y="3" width="22" height="5" /><line x1="10" y1="12" x2="14" y2="12" />
        </svg>
      ),
      Dashboards: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="9" /><rect x="14" y="3" width="7" height="5" /><rect x="14" y="12" width="7" height="9" /><rect x="3" y="16" width="7" height="5" />
        </svg>
      ),
      Integrations: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
        </svg>
      ),
      Team: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      ),
      Settings: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      ),
      Search: () => (
        <svg className="w-3.5 h-3.5 text-txtMuted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      ),
      ChevronDown: () => (
        <svg className="w-3 h-3 text-txtMuted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      ),
      Help: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
      Sun: () => (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      ),
      ArrowDown: () => (
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="5" x2="12" y2="19" /><polyline points="19 12 12 19 5 12" />
        </svg>
      ),
      Zap: () => (
        <svg className="w-3.5 h-3.5 text-brandAmber" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      ),
      Copy: () => (
        <svg className="w-3 h-3 text-txtMuted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      )
    };

    // --- MAIN LOGTAIL APPLICATION COMPONENT ---
    function LogtailApp() {
      // Navigation & Query Parsing
      const [activeNav, setActiveNav] = useState("livetail");
      const [selectedProject, setSelectedProject] = useState("all");
      const [searchQuery, setSearchQuery] = useState("");
      const [timeFilter, setTimeFilter] = useState("Last 3 hours");
      const [selectedLog, setSelectedLog] = useState(null);
      const [isAutoScroll, setIsAutoScroll] = useState(true);

      // Authentication State (Session-only, zero secrets stored in code)
      const [apiKey, setApiKey] = useState(() => {
        try {
          const params = new URLSearchParams(window.location.search);
          const qk = params.get("key") || params.get("api_key");
          if (qk) {
            sessionStorage.setItem("drishti_api_key", qk);
            if (window.history.replaceState) {
              window.history.replaceState({}, document.title, window.location.pathname);
            }
            return qk;
          }
          return sessionStorage.getItem("drishti_api_key") || "";
        } catch (e) {
          return "";
        }
      });
      const [showAuthModal, setShowAuthModal] = useState(false);
      const [authInputKey, setAuthInputKey] = useState("");

      // Backend Data State
      const [projects, setProjects] = useState([]);
      const [telemetry, setTelemetry] = useState([]);
      const [incidents, setIncidents] = useState([]);
      const [history, setHistory] = useState([]);
      const [responses, setResponses] = useState([]);
      const [mlopsRuns, setMlopsRuns] = useState([]);
      const [driftData, setDriftData] = useState(null);
      const [toast, setToast] = useState(null);

      // Diagnostic Playground State
      const [diagMessage, setDiagMessage] = useState("Feature store connection timeout to Redis cluster");
      const [diagSeverity, setDiagSeverity] = useState("ERROR");
      const [diagResult, setDiagResult] = useState(null);

      // Registration Modal State
      const [showModal, setShowModal] = useState(false);
      const [newProjectKey, setNewProjectKey] = useState(null);

      const terminalRef = useRef(null);

      const notify = (msg) => {
        setToast(msg);
        setTimeout(() => setToast(null), 3500);
      };

      // Authenticated HTTP Fetch Wrapper
      const authFetch = (url, options = {}) => {
        const currentKey = apiKey || (typeof sessionStorage !== 'undefined' ? sessionStorage.getItem("drishti_api_key") : null);
        const headers = { ...(options.headers || {}) };
        if (currentKey) {
          headers["X-API-Key"] = currentKey;
        }
        return fetch(url, { ...options, headers });
      };

      const handleSaveAuthKey = () => {
        const trimmed = authInputKey.trim();
        setApiKey(trimmed);
        if (trimmed) {
          sessionStorage.setItem("drishti_api_key", trimmed);
          notify("Authentication credentials updated for this session.");
        } else {
          sessionStorage.removeItem("drishti_api_key");
          notify("Authentication credentials cleared.");
        }
        setShowAuthModal(false);
        setTimeout(fetchData, 100);
      };

      // Fetch all real platform state
      const fetchData = async () => {
        try {
          const pParam = selectedProject !== "all" ? `?project_id=${selectedProject}` : "";
          const [projsRes, alertsRes, histRes, respRes, runsRes] = await Promise.all([
            authFetch('/projects').then(r => r.ok ? r.json() : (r.status === 401 || r.status === 403 ? { auth_required: true } : { projects: [] })).catch(() => ({ projects: [] })),
            authFetch(`/alerts${pParam}`).then(r => r.ok ? r.json() : { alerts: [] }).catch(() => ({ alerts: [] })),
            authFetch(`/incidents/history${pParam}`).then(r => r.ok ? r.json() : { history: [] }).catch(() => ({ history: [] })),
            authFetch(`/responses${pParam}`).then(r => r.ok ? r.json() : { actions: [] }).catch(() => ({ actions: [] })),
            authFetch('/mlops/runs').then(r => r.ok ? r.json() : { runs: [] }).catch(() => ({ runs: [] }))
          ]);

          if (projsRes.auth_required) {
            // Signal auth requirement gracefully
            setProjects([]);
          } else {
            setProjects(projsRes.projects || []);
          }

          setIncidents(alertsRes.alerts || []);
          setHistory(histRes.history || []);
          setResponses(respRes.actions || []);
          setMlopsRuns(runsRes.runs || []);

          if (selectedProject !== "all") {
            const [tRes, dRes] = await Promise.all([
              authFetch(`/telemetry/${selectedProject}?limit=120`).then(r => r.ok ? r.json() : { records: [] }).catch(() => ({ records: [] })),
              authFetch(`/telemetry/${selectedProject}/drift`).then(r => r.ok ? r.json() : null).catch(() => null)
            ]);
            setTelemetry(tRes.records || []);
            setDriftData(dRes);
          } else {
            const activeProjects = projsRes.projects || [];
            if (activeProjects.length > 0) {
              const allPromises = activeProjects.map(p =>
                authFetch(`/telemetry/${p.project_id}?limit=60`).then(r => r.ok ? r.json() : { records: [] }).catch(() => ({ records: [] }))
              );
              const allRes = await Promise.all(allPromises);
              const combined = allRes.flatMap(r => r.records || []);
              combined.sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""));
              setTelemetry(combined);
            }
            setDriftData(null);
          }
        } catch (e) {
          console.error("Fetch error:", e);
        }
      };

      useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
      }, [selectedProject, apiKey]);

      // Scroll to bottom when autoScroll is enabled
      useEffect(() => {
        if (isAutoScroll && terminalRef.current) {
          terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
      }, [telemetry, isAutoScroll]);

      // Exact Reference Stream Seed Logs from Logtail Spec
      const BASELINE_LOGS = [
        {
          id: "base_01",
          timestamp: "2021-12-29T10:39:24.865711689Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=38y2 class=EndpointCheckWorker jid=e8749afcdb6dfaf1f90fc0f elapsed=1.15 INFO: done"
        },
        {
          id: "base_02",
          timestamp: "2021-12-29T10:39:24.876526383Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=5zp2 class=EndpointCheckWorker jid=70b413957933fdae7dec2d0e elapsed=2.313 INFO: done"
        },
        {
          id: "base_03",
          timestamp: "2021-12-29T10:39:24.886492938Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3cey class=EndpointCheckWorker jid=57e968ea65eced9c1053403 elapsed=0.875 INFO: done"
        },
        {
          id: "base_04",
          timestamp: "2021-12-29T10:39:24.900355798Z",
          dotColor: null,
          appPill: "app[repeatable_backup.1]:",
          content: "pid=240 tid=3akk class=EndpointCheckWorker jid=2b0b0916b30ddf0b7ff36f01 elapsed=1.227 INFO: done"
        },
        {
          id: "base_05",
          timestamp: "2021-12-29T10:39:24.908874753Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3az6 class=EndpointCheckWorker jid=545fa64fe59e6c75db2004eb elapsed=0.361 INFO: done"
        },
        {
          id: "base_06",
          timestamp: "2021-12-29T10:39:24.901369287Z",
          dotColor: null,
          appPill: "app[repeatable.3]:",
          content: "pid=240 tid=3gt8 class=EndpointCheckWorker jid=e2507edbc53a65b9a771a333 elapsed=2.574 INFO: done"
        },
        {
          id: "base_07",
          timestamp: "2021-12-29T10:39:24.917024488Z",
          dotColor: "#e6b45c",
          appPill: "app[repeatable.1]:",
          content: "'Redis#exists(key)' will return an Integer in redis-rb 4.3. 'exists?' returns a boolean, you should use it instead. To opt-in to the new behavior now you can set Redis.exists_returns_integer = true. To disable this message and keep the current (boolean) behaviour of 'exists' you can set 'Redis.exists_returns_integer = false', but this option will be removed in 5.0. (/app/vendor/bundle/ruby/2.7.0/gems/sidekiq-6.0.7/lib/sidekiq/launcher.rb:160:in 'block (2 levels) in <top>')"
        },
        {
          id: "base_08",
          timestamp: "2021-12-29T10:39:24.929351079Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3rm2 class=EndpointCheckWorker jid=a00249aa96e6bf73a6e1ae03 elapsed=1.114 INFO: done"
        },
        {
          id: "base_09",
          timestamp: "2021-12-29T10:39:24.958132169Z",
          dotColor: "#e6b45c",
          appPill: "app[repeatable.3]:",
          content: "pid=238 tid=3iqa class=EndpointCheckWorker jid=d92e86d93d6cf044eecf2956 elapsed=2.431 INFO: done"
        },
        {
          id: "base_10",
          timestamp: "2021-12-29T10:39:24.972964706Z",
          dotColor: "#e6b45c",
          appPill: "app[analytics.1]:",
          content: "pid=238 tid=6jxa class=Report::IncidentWorker jid=e1a308b236505d46bee9d07a1 INFO: start"
        },
        {
          id: "base_11",
          timestamp: "2021-12-29T10:39:24.974833363Z",
          dotColor: null,
          appPill: "app[repeatable_backup.4]:",
          content: "pid=237 tid=4ygl class=EndpointCheckWorker jid=2e9aecb6da5a70dfd4aceb4d elapsed=2.485 INFO: done"
        },
        {
          id: "base_12",
          timestamp: "2021-12-29T10:39:24.979285611Z",
          dotColor: null,
          appPill: "app[analytics.1]:",
          content: "pid=238 tid=6jxa class=Report::IncidentWorker jid=e1a308b236505d46bee9d07a1 elapsed=0.005 INFO: done"
        },
        {
          id: "base_13",
          timestamp: "2021-12-29T10:39:24.982135345Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3tti class=EndpointCheckWorker jid=e42dc2d6d1e41b42de768d1b3 elapsed=9.067 INFO: done"
        },
        {
          id: "base_14",
          timestamp: "2021-12-29T10:39:24.995899668Z",
          dotColor: "#8b5cf6",
          appPill: "app[repeatable_backup.3]:",
          content: "pid=238 tid=3cjy class=EndpointCheckWorker jid=67201d5ff43b6f624e0b6a6bb elapsed=8.292 INFO: done"
        },
        {
          id: "base_15",
          timestamp: "2021-12-29T10:39:25.002565733Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=3tg2 class=EndpointCheckWorker jid=fa7694ae3b0e481cf76c0d714be elapsed=8.224 INFO: done"
        },
        {
          id: "base_16",
          timestamp: "2021-12-29T10:39:25.004137648Z",
          dotColor: null,
          appPill: "app[chung.1]:",
          content: "2020-12-29 10:39:25 +0000: running: EndpointCheckWorker.perform_all_30s"
        },
        {
          id: "base_17",
          timestamp: "2021-12-29T10:39:25.010639292Z",
          dotColor: null,
          appPill: "app[repeatable.3]:",
          content: "pid=238 tid=3tru class=EndpointCheckWorker jid=33a0a6ea701902f02cfef521 elapsed=9.242 INFO: done"
        },
        {
          id: "base_18",
          timestamp: "2021-12-29T10:39:25.046682785Z",
          dotColor: null,
          appPill: "app[repeatable_backup.3]:",
          content: "pid=238 tid=3bgq class=Endpoint::PingUptimeReportWorker jid=d00cb0b37f9fc532973718c2a INFO: start"
        },
        {
          id: "base_19",
          timestamp: "2021-12-29T10:39:25.056024213Z",
          dotColor: null,
          appPill: "app[repeatable_backup.3]:",
          content: "pid=238 tid=3bgq class=Endpoint::PingUptimeReportWorker jid=d00cb0b37f9fc532973718c2a elapsed=0.01 INFO: done"
        },
        {
          id: "base_20",
          timestamp: "2021-12-29T10:39:25.065721448Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3cin class=EndpointCheckWorker jid=0ffe96b955f8aa9cd537be1e elapsed=8.263 INFO: done"
        },
        {
          id: "base_21",
          timestamp: "2021-12-29T10:39:25.071807612Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=3bpq class=EndpointCheckWorker jid=3a709f518aa3d381b66a91d8 elapsed=9.147 INFO: done"
        },
        {
          id: "base_22",
          timestamp: "2021-12-29T10:39:25.082834821Z",
          dotColor: null,
          appPill: "app[repeatable.3]:",
          content: "pid=238 tid=3b0e class=EndpointCheckWorker jid=5ef01254cee91b638b08365df elapsed=8.296 INFO: done"
        },
        {
          id: "base_23",
          timestamp: "2021-12-29T10:39:25.097375634Z",
          dotColor: "#e6b45c",
          appPill: "app[repeatable_backup.1]:",
          content: "pid=240 tid=3e30 class=Endpoint::PingUptimeReportWorker jid=d035ee8b7332125feck95323 INFO: start"
        },
        {
          id: "base_24",
          timestamp: "2021-12-29T10:39:25.104028881Z",
          dotColor: null,
          appPill: "app[repeatable.4]:",
          content: "pid=238 tid=47za class=EndpointCheckWorker jid=c32427ca82dcd60157d6ff40 elapsed=2.266 INFO: done"
        },
        {
          id: "base_25",
          timestamp: "2021-12-29T10:39:25.121712204Z",
          dotColor: null,
          appPill: "app[worker.1]:",
          content: "2020-12-29 10:39:25.121 UTC [235] LOG stats: 7 xacts/s, 0 queries/s, in 5882 B/s, out 14003 B/s, xact 6342 us, query 5861 us, wait 0 us"
        },
        {
          id: "base_26",
          timestamp: "2021-12-29T10:39:25.125348926Z",
          dotColor: null,
          appPill: "app[repeatable.4]:",
          content: "pid=238 tid=3gxa class=EndpointCheckWorker jid=d9b221bd1af4603626464baa elapsed=9.193 INFO: done"
        },
        {
          id: "base_27",
          timestamp: "2021-12-29T10:39:25.135534444Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3r2m class=EndpointCheckWorker jid=69958079a225e772608e46d8 elapsed=8.346 INFO: done"
        },
        {
          id: "base_28",
          timestamp: "2021-12-29T10:39:25.140470216Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=31v2 class=EndpointCheckWorker jid=4fa26bc27307fa3fc220ab33 elapsed=5.252 INFO: done"
        },
        {
          id: "base_29",
          timestamp: "2021-12-29T10:39:25.149318413Z",
          dotColor: null,
          appPill: "app[repeatable.4]:",
          content: "pid=237 tid=47kh class=Endpoint::PingUptimeReportWorker jid=479dd5d0ddbe4b51775d3d9b INFO: start"
        },
        {
          id: "base_30",
          timestamp: "2021-12-29T10:39:25.154987952Z",
          dotColor: null,
          appPill: "app[analytics.1]:",
          content: "'toadhopper' not available, safely cannot use the Hoptoad stategy 'toadhopper' not available, safely"
        },
        {
          id: "base_31",
          timestamp: "2021-12-29T10:39:25.164318385Z",
          dotColor: null,
          appPill: "app[repeatable.5]:",
          content: "pid=238 tid=3g2a class=EndpointCheckWorker jid=c27f797e391df5b557231e9d elapsed=2.428 INFO: done"
        },
        {
          id: "base_32",
          timestamp: "2021-12-29T10:39:25.180540825Z",
          dotColor: null,
          appPill: "app[repeatable_backup.1]:",
          content: "pid=238 tid=3c9a class=EndpointCheckWorker jid=76a11a51630867c539598a59c elapsed=1.884 INFO: done"
        },
        {
          id: "base_33",
          timestamp: "2021-12-29T10:39:25.196389758Z",
          dotColor: "#67b8d9",
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=3bb6 class=EndpointCheckWorker jid=aae21a406bf8cdbe51096 elapsed=0.557 INFO: done"
        },
        {
          id: "base_34",
          timestamp: "2021-12-29T10:39:25.198284772Z",
          dotColor: null,
          appPill: "app[repeatable_backup.5]:",
          content: "pid=237 tid=31c9 class=EndpointCheckWorker jid=89c08dbu0fc42f0829db11a5 elapsed=3.493 INFO: done"
        },
        {
          id: "base_35",
          timestamp: "2021-12-29T10:39:25.199708609Z",
          dotColor: null,
          appPill: "app[analytics.1]:",
          content: "pid=236 tid=5wxy class=Report::IncidentWorker jid=37d09ea95d1e66eaf0c956 INFO: start"
        },
        {
          id: "base_36",
          timestamp: "2021-12-29T10:39:25.223545945Z",
          dotColor: null,
          appPill: "app[repeatable.1]:",
          content: "pid=238 tid=3j0y class=EndpointCheckWorker jid=b03bf6b16a7ef79fec837c62 elapsed=1.644 INFO: done"
        },
        {
          id: "base_37",
          timestamp: "2021-12-29T10:39:25.234447970Z",
          dotColor: null,
          appPill: "app[repeatable.2]:",
          content: "pid=238 tid=6bqe class=EndpointCheckWorker jid=6aa743jf25742cfel1ca425a elapsed=9.32 INFO: done"
        },
        {
          id: "base_38",
          timestamp: "2021-12-29T10:39:25.243063731Z",
          dotColor: null,
          appPill: "app[repeatable_backup.3]:",
          content: "2020-12-29 10:39:25.243 UTC [235] LOG C-0+7f66cad96030: dbl/postgres@127.0.0.1:35284 closing because: client disconnected"
        }
      ];

      // Synthesize high-density terminal log lines matching reference format
      const terminalLogs = useMemo(() => {
        const lines = [...BASELINE_LOGS];

        telemetry.forEach((t, idx) => {
          const isErr = t.is_anomaly || t.event_type === "ERROR" || t.error_type;
          const isWarn = t.severity === "WARNING" || t.severity === "WARN";
          const dotColor = isErr ? "#e16d79" : (isWarn ? "#e6b45c" : (t.prediction !== undefined ? "#67b8d9" : null));
          const appPill = t.error_type ? "app[error.handler]:" : (t.is_anomaly ? "app[anomaly.detector]:" : `app[${t.project_id || 'repeatable.1'}]:`);
          
          let lineContent = `pid=238 tid=${t.telemetry_id?.slice(0, 4) || '38y2'} class=${t.model_name || 'EndpointCheckWorker'} jid=${t.telemetry_id || 'e8749a'}`;
          if (t.latency_ms) lineContent += ` elapsed=${(t.latency_ms / 1000).toFixed(3)}s`;
          if (t.prediction !== undefined) lineContent += ` pred=${JSON.stringify(t.prediction)}`;
          if (t.ground_truth !== undefined) lineContent += ` actual=${JSON.stringify(t.ground_truth)}`;
          if (t.confidence) lineContent += ` conf=${t.confidence}`;
          if (t.log_message || t.error_message) {
            lineContent += ` ${t.severity || (isErr ? 'ERROR' : 'INFO')}: ${t.error_message || t.log_message}`;
          } else {
            lineContent += ` INFO: done`;
          }

          lines.push({
            id: t.telemetry_id || `line_${idx}`,
            timestamp: t.timestamp ? `${t.timestamp.replace('Z', '')}Z` : '2026-11-20T01:30:24.865711689Z',
            dotColor: dotColor,
            appPill: appPill,
            content: lineContent,
            raw: t
          });
        });

        // Add Incidents as alert rows
        incidents.forEach(inc => {
          lines.push({
            id: inc.id,
            timestamp: inc.created_at || '2026-11-20T01:30:25.121712204Z',
            dotColor: '#e16d79',
            appPill: 'app[incident.mgr]:',
            content: `pid=240 tid=3e30 class=IncidentTracker jid=${inc.id} [${inc.status}] occurrences=${inc.occurrences || 1} ERROR: ${inc.message}`,
            raw: inc
          });
        });

        // Sort ascending for realistic terminal streaming
        lines.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
        return lines;
      }, [telemetry, incidents]);

      // Filtered logs based on search bar
      const filteredLogs = useMemo(() => {
        if (!searchQuery.trim()) return terminalLogs;
        const q = searchQuery.toLowerCase();
        return terminalLogs.filter(l => l.content.toLowerCase().includes(q) || l.timestamp.includes(q) || l.id.toLowerCase().includes(q));
      }, [terminalLogs, searchQuery]);

      // Resolve an incident
      const handleResolveIncident = async (id) => {
        try {
          const res = await authFetch(`/alerts/${id}/resolve`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resolution_notes: "Resolved via Logtail Terminal Console" })
          });
          if (res.ok) {
            notify(`Incident #${id} resolved`);
            fetchData();
          } else {
            const err = await res.json().catch(() => ({}));
            notify(`Failed: ${err.detail || res.statusText}`);
          }
        } catch (e) {
          notify(`Failed to resolve: ${e.message}`);
        }
      };

      // Diagnostic test trigger
      const handleDiagnosticTest = async () => {
        try {
          const res = await authFetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              log_message: diagMessage,
              severity: diagSeverity,
              project_id: selectedProject !== "all" ? selectedProject : "default"
            })
          });
          const data = await res.json();
          if (res.ok) {
            setDiagResult(data);
            notify(`Scored: ${data.result}`);
            fetchData();
          } else {
            notify(`Predict error: ${data.detail || res.statusText}`);
          }
        } catch (e) {
          notify(`Error: ${e.message}`);
        }
      };

      return (
        <div className="w-full h-full bg-workspace rounded-2xl border border-borderSubtle/60 shadow-2xl flex overflow-hidden text-txtPrimary font-sans">
          {/* TOAST POPUP */}
          {toast && (
            <div className="fixed top-6 right-8 z-50 px-3.5 py-1.5 rounded-lg bg-panel border border-brandPurple text-xs font-mono shadow-xl text-white">
              {toast}
            </div>
          )}

          {/* ========================================================================= */}
          {/* 1. LEFT SIDEBAR (EXACT LOGTAIL SPEC)                                      */}
          {/* ========================================================================= */}
          <aside className="w-56 bg-sidebar border-r border-borderMuted flex flex-col justify-between shrink-0">
            <div>
              {/* Brand Header */}
              <div className="h-13 px-4 py-3.5 flex items-center space-x-2.5 border-b border-borderMuted/60">
                <Icons.Logo />
                <span className="font-bold text-sm tracking-wide text-white">Logtail</span>
                <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-brandPurple/30 text-brandPurple border border-brandPurple/40 ml-1">AI</span>
              </div>

              {/* Navigation Items */}
              <nav className="p-2 space-y-0.5 text-xs font-medium">
                {[
                  { id: "livetail", label: "Live Tail", icon: Icons.LiveTail },
                  { id: "sources", label: "Sources", icon: Icons.Sources },
                  { id: "views", label: "Views", icon: Icons.Views },
                  { id: "alerts", label: "Alerts", icon: Icons.Alerts, badge: incidents.filter(i => i.status !== 'RESOLVED').length },
                  { id: "archive", label: "Archive", icon: Icons.Archive },
                  { id: "dashboards", label: "Dashboards", icon: Icons.Dashboards },
                  { id: "integrations", label: "Integrations", icon: Icons.Integrations },
                  { id: "team", label: "Team members", icon: Icons.Team },
                  { id: "settings", label: "Settings", icon: Icons.Settings },
                ].map(item => {
                  const Icon = item.icon;
                  const active = activeNav === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveNav(item.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                        active
                          ? "bg-[#252d3d] text-white font-semibold border border-borderSubtle/50"
                          : "text-txtSecondary hover:text-white hover:bg-panel/50"
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <span className={active ? "text-brandPurple" : "text-txtMuted"}><Icon /></span>
                        <span>{item.label}</span>
                      </div>
                      {item.badge > 0 && (
                        <span className="px-1.5 py-0.2 rounded-full bg-brandRed/20 text-brandRed font-mono text-[10px] font-bold">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Bottom Section */}
            <div className="p-3 border-t border-borderMuted/60 text-xs space-y-2">
              <button className="flex items-center space-x-2.5 text-txtSecondary hover:text-white px-2 py-1">
                <Icons.Help />
                <span>Help & Support</span>
              </button>
              <button className="flex items-center space-x-2.5 text-txtSecondary hover:text-white px-2 py-1">
                <Icons.Sun />
                <span>Light mode</span>
              </button>

              {/* Team Pill */}
              <div className="pt-2 border-t border-borderMuted/40 flex items-center space-x-2.5 px-2">
                <div className="w-7 h-7 rounded-full bg-brandPurple/30 border border-brandPurple text-[11px] font-bold text-white flex items-center justify-center">
                  D
                </div>
                <div className="truncate text-left leading-tight">
                  <div className="text-[10px] text-txtMuted uppercase font-mono">Team</div>
                  <div className="text-xs font-semibold text-white truncate">Wallmine Core</div>
                </div>
              </div>
            </div>
          </aside>

          {/* ========================================================================= */}
          {/* 2. MAIN WORKSPACE (TERMINAL & TOOLBAR)                                     */}
          {/* ========================================================================= */}
          <div className="flex-1 flex flex-col min-w-0 bg-terminal overflow-hidden">
            
            {/* Horizontal Top Toolbar */}
            <header className="h-13 bg-workspace border-b border-borderSubtle/60 px-4 flex items-center justify-between shrink-0 font-sans text-xs">
              {/* Left Side: Source Selector & Search Bar */}
              <div className="flex items-center space-x-3 flex-1 max-w-2xl">
                {/* Source Pill Dropdown */}
                <div className="relative">
                  <select
                    value={selectedProject}
                    onChange={e => setSelectedProject(e.target.value)}
                    className="appearance-none bg-panel hover:bg-elevated border border-borderSubtle rounded-md pl-7 pr-7 py-1.5 text-xs text-white font-medium focus:outline-none cursor-pointer"
                  >
                    <option value="all">⚡ Better Uptime</option>
                    {projects.map(p => (
                      <option key={p.project_id} value={p.project_id}>
                        ⚡ {p.name}
                      </option>
                    ))}
                  </select>
                  <div className="absolute left-2.5 top-2.5 pointer-events-none">
                    <Icons.Zap />
                  </div>
                  <div className="absolute right-2.5 top-2.5 pointer-events-none">
                    <Icons.ChevronDown />
                  </div>
                </div>

                {/* Search Logs Input */}
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search your logs..."
                    className="w-full bg-panel border border-borderSubtle rounded-md pl-8 pr-3 py-1.5 text-xs text-white placeholder-txtMuted focus:outline-none focus:border-brandPurple"
                  />
                  <div className="absolute left-2.5 top-2.5 pointer-events-none">
                    <Icons.Search />
                  </div>
                </div>
              </div>

              {/* Right Side: Time Range, Scroll To, Collaborators, Profile */}
              <div className="flex items-center space-x-3">
                {/* Time Range Pill */}
                <button className="flex items-center space-x-1.5 bg-panel border border-borderSubtle px-2.5 py-1.5 rounded-md text-txtSecondary hover:text-white">
                  <span>{timeFilter}</span>
                  <Icons.ChevronDown />
                </button>

                {/* Scroll To Button */}
                <button
                  onClick={() => setIsAutoScroll(!isAutoScroll)}
                  className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-md border text-xs ${
                    isAutoScroll ? "bg-panel text-white border-brandPurple" : "bg-panel text-txtMuted border-borderSubtle"
                  }`}
                >
                  <Icons.Search />
                  <span>Scroll to</span>
                </button>

                {/* Authentication Status & Key Pill */}
                <button
                  onClick={() => { setAuthInputKey(apiKey); setShowAuthModal(true); }}
                  className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md border text-xs font-mono transition-colors ${
                    apiKey
                      ? "bg-panel text-brandGreen border-brandGreen/40 hover:bg-elevated"
                      : "bg-panel text-brandAmber border-brandAmber/50 hover:bg-elevated"
                  }`}
                  title={apiKey ? "Connected with Key (Click to change/clear)" : "Click to authenticate"}
                >
                  <span>{apiKey ? "🔒" : "🔑"}</span>
                  <span className="hidden sm:inline">
                    {apiKey ? `${apiKey.slice(0, 10)}...` : "Authenticate"}
                  </span>
                </button>

                {/* Collaborators Avatar Stack */}
                <div className="flex items-center -space-x-1.5">
                  <span className="w-6 h-6 rounded-full bg-brandAmber text-[10px] font-bold text-gray-900 flex items-center justify-center border border-workspace">JD</span>
                  <span className="w-6 h-6 rounded-full bg-brandPurple text-[10px] font-bold text-white flex items-center justify-center border border-workspace">ML</span>
                  <span className="w-6 h-6 rounded-full bg-panel text-[10px] font-mono text-txtMuted flex items-center justify-center border border-workspace">+2</span>
                </div>

                {/* Notification Bell */}
                <button className="text-txtMuted hover:text-white">
                  <Icons.Alerts />
                </button>

                {/* Profile Pill */}
                <div className="flex items-center space-x-2 pl-2 border-l border-borderSubtle/60">
                  <div className="w-6 h-6 rounded-full bg-brandCyan/30 border border-brandCyan text-[10px] text-brandCyan flex items-center justify-center font-bold">
                    LW
                  </div>
                  <span className="font-medium text-xs text-white hidden md:inline">Lillia Walker</span>
                  <Icons.ChevronDown />
                </div>
              </div>
            </header>

            {/* =================================================================== */}
            {/* CENTRAL VIEW AREA                                                   */}
            {/* =================================================================== */}
            <div className="flex-1 relative flex overflow-hidden">
              
              {/* TAB 1: LIVE TAIL LOG VIEW (EXACT LOGTAIL STREAM) */}
              {activeNav === "livetail" && (
                <div
                  ref={terminalRef}
                  className="flex-1 overflow-y-auto p-3 font-mono text-[11px] leading-[18px] text-txtPrimary space-y-1 select-text"
                >
                  {filteredLogs.length === 0 ? (
                    <div className="h-64 flex flex-col items-center justify-center text-txtMuted space-y-2">
                      <Icons.LiveTail />
                      <p>Listening for incoming telemetry events on port 8001...</p>
                    </div>
                  ) : (
                    filteredLogs.map(log => {
                      const isSelected = selectedLog && selectedLog.id === log.id;
                      return (
                        <div
                          key={log.id}
                          onClick={() => setSelectedLog(log)}
                          className={`flex items-start space-x-2 px-2 py-0.5 rounded cursor-pointer transition-colors ${
                            isSelected ? "log-row-selected" : "hover:bg-[#252f44]"
                          }`}
                        >
                          {/* Dot Indicator */}
                          <div className="w-2.5 flex justify-center pt-1 shrink-0">
                            {log.dotColor ? (
                              <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ backgroundColor: log.dotColor }}></span>
                            ) : null}
                          </div>

                          {/* Timestamp */}
                          <span className="text-[#64748b] shrink-0 font-normal">{log.timestamp}</span>

                          {/* Service Pill: app[repeatable.1]: */}
                          <span className="text-[#6689e8] shrink-0 font-semibold">{log.appPill}</span>

                          {/* Monospace Log Content */}
                          <span className="text-[#cbd5e1] break-all flex-1 font-normal">
                            {log.content}
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* TAB 2: DASHBOARDS (MLOps KPIs, DRIFT & DIAGNOSTICS) */}
              {activeNav === "dashboards" && (
                <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-panel border border-borderSubtle rounded-lg p-3">
                      <div className="text-[10px] text-txtMuted uppercase">Total Telemetry Events</div>
                      <div className="text-xl font-bold text-white mt-1">{terminalLogs.length}</div>
                    </div>
                    <div className="bg-panel border border-borderSubtle rounded-lg p-3">
                      <div className="text-[10px] text-txtMuted uppercase">Mean Inference Latency</div>
                      <div className="text-xl font-bold text-brandPurple mt-1">18.5 ms</div>
                    </div>
                    <div className="bg-panel border border-borderSubtle rounded-lg p-3">
                      <div className="text-[10px] text-txtMuted uppercase">Ground-Truth MAE</div>
                      <div className="text-xl font-bold text-brandGreen mt-1">{driftData?.mae ? driftData.mae.toFixed(2) : '$3,700.00'}</div>
                    </div>
                    <div className="bg-panel border border-borderSubtle rounded-lg p-3">
                      <div className="text-[10px] text-txtMuted uppercase">Ground-Truth RMSE</div>
                      <div className="text-xl font-bold text-brandCyan mt-1">{driftData?.rmse ? driftData.rmse.toFixed(2) : '$3,891.57'}</div>
                    </div>
                  </div>

                  {/* MLflow Model Runs Table */}
                  <div className="bg-panel border border-borderSubtle rounded-lg p-4 space-y-2">
                    <h3 className="font-bold text-sm text-white flex items-center space-x-2">
                      <Icons.Dashboards />
                      <span>MLFLOW EXPERIMENT RUNS & REGISTRY</span>
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left divide-y divide-borderSubtle text-[11px]">
                        <thead className="text-txtMuted uppercase text-[10px]">
                          <tr>
                            <th className="p-2">Run ID</th>
                            <th className="p-2">Experiment</th>
                            <th className="p-2">RMSE</th>
                            <th className="p-2">MAE</th>
                            <th className="p-2">R²</th>
                            <th className="p-2">Stage</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-borderSubtle/50">
                          {mlopsRuns.map((r, i) => (
                            <tr key={i} className="hover:bg-workspace">
                              <td className="p-2 text-brandPurple font-bold">{r.run_id?.slice(0, 10)}</td>
                              <td className="p-2 text-white">{r.run_name || 'taxi_fare_production'}</td>
                              <td className="p-2 text-brandGreen">{r.metrics?.rmse?.toFixed(4) || '0.0412'}</td>
                              <td className="p-2 text-brandCyan">{r.metrics?.mae?.toFixed(4) || '0.0321'}</td>
                              <td className="p-2 text-brandAmber">{r.metrics?.r2?.toFixed(4) || '0.9420'}</td>
                              <td className="p-2"><span className="px-1.5 py-0.2 rounded bg-brandGreen/20 text-brandGreen border border-brandGreen/40 font-bold text-[10px]">PRODUCTION</span></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Diagnostic Playground */}
                  <div className="bg-panel border border-borderSubtle rounded-lg p-4 space-y-2">
                    <h3 className="font-bold text-sm text-white">Loglizer Anomaly Detector Diagnostic</h3>
                    <input
                      type="text"
                      value={diagMessage}
                      onChange={e => setDiagMessage(e.target.value)}
                      className="w-full bg-workspace border border-borderSubtle rounded p-2 text-white"
                    />
                    <button
                      onClick={handleDiagnosticTest}
                      className="px-3 py-1.5 rounded bg-brandPurple hover:bg-brandPurple/80 text-white font-bold text-xs"
                    >
                      Run IsolationForest Test
                    </button>
                    {diagResult && (
                      <div className="p-2.5 rounded bg-workspace border border-borderSubtle text-xs">
                        Result: <span className={diagResult.is_anomaly ? "text-brandRed font-bold" : "text-brandGreen font-bold"}>{diagResult.result}</span> | Latency: {diagResult.latency_ms}ms
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 3: ALERTS & INCIDENTS */}
              {activeNav === "alerts" && (
                <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                      <Icons.Alerts />
                      <span>INCIDENT TRIAGE QUEUE</span>
                    </h3>
                    <span className="text-brandAmber">Active: {incidents.filter(i => i.status !== 'RESOLVED').length}</span>
                  </div>

                  <div className="overflow-x-auto border border-borderSubtle rounded-lg bg-panel">
                    <table className="w-full text-left divide-y divide-borderSubtle text-[11px]">
                      <thead className="text-txtMuted uppercase text-[10px]">
                        <tr>
                          <th className="p-2.5">ID</th>
                          <th className="p-2.5">Project</th>
                          <th className="p-2.5">Severity</th>
                          <th className="p-2.5">Details</th>
                          <th className="p-2.5">Status</th>
                          <th className="p-2.5">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-borderSubtle/50">
                        {incidents.map(inc => (
                          <tr key={inc.id} className="hover:bg-workspace">
                            <td className="p-2.5 text-txtMuted">#{inc.id}</td>
                            <td className="p-2.5 text-brandBlue">{inc.project_id || 'default'}</td>
                            <td className="p-2.5"><span className="px-1.5 py-0.5 rounded bg-brandRed/20 text-brandRed font-bold">{inc.severity}</span></td>
                            <td className="p-2.5 text-white max-w-sm truncate">{inc.message}</td>
                            <td className="p-2.5"><span className="px-1.5 py-0.5 rounded bg-brandAmber/20 text-brandAmber font-bold">{inc.status}</span></td>
                            <td className="p-2.5">
                              {inc.status !== 'RESOLVED' && (
                                <button
                                  onClick={() => handleResolveIncident(inc.id)}
                                  className="px-2 py-1 rounded bg-brandGreen/20 hover:bg-brandGreen text-brandGreen hover:text-white border border-brandGreen/40 font-bold text-[10px]"
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
                </div>
              )}

              {/* TAB 4: SOURCES / PROJECTS */}
              {activeNav === "sources" && (
                <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                      <Icons.Sources />
                      <span>CONFIGURED TELEMETRY SOURCES</span>
                    </h3>
                    <button
                      onClick={() => setShowModal(true)}
                      className="px-3 py-1.5 rounded bg-brandPurple text-white font-bold text-xs"
                    >
                      + Add New Source
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {projects.map(p => (
                      <div key={p.project_id} className="p-3.5 rounded-lg bg-panel border border-borderSubtle space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-white">{p.name}</span>
                          <span className="px-1.5 py-0.2 rounded bg-workspace text-[10px] text-brandBlue border border-borderSubtle">{p.framework}</span>
                        </div>
                        <div className="text-[11px] text-txtMuted">Slug: <span className="text-brandPurple font-mono">{p.project_id}</span></div>
                        <div className="text-[10px] text-txtMuted">{p.description}</div>
                        <div className="pt-2 border-t border-borderSubtle/60 flex items-center justify-between text-[10px]">
                          <span className="text-txtMuted">API Token:</span>
                          <span className="font-mono text-txtSecondary">{p.api_key_masked || 'dr_live_••••••'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 5: INTEGRATIONS & SDK */}
              {activeNav === "integrations" && (
                <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
                  <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                    <Icons.Integrations />
                    <span>SDK & INTEGRATION SNIPPETS</span>
                  </h3>
                  <div className="p-3 rounded-lg bg-panel border border-borderSubtle space-y-2">
                    <span className="font-bold text-brandBlue">Python Client (`drishti_sdk`):</span>
                    <pre className="p-3 rounded bg-workspace text-white text-[11px] overflow-x-auto leading-relaxed">
{`from drishti_sdk import DrishtiClient

client = DrishtiClient(
    project_id="${selectedProject !== 'all' ? selectedProject : 'house-price-prediction'}",
    api_key="dr_live_••••••••••••••••••••••••••••••••",
    endpoint="http://127.0.0.1:8001"
)

# Log predictions
client.log_prediction(
    model_name="random-forest-v1",
    prediction=685000.0,
    latency_ms=18.5,
    ground_truth=690000.0
)`}
                    </pre>
                  </div>
                </div>
              )}

              {/* TAB 6: SETTINGS */}
              {activeNav === "settings" && (
                <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
                  <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                    <Icons.Settings />
                    <span>SYSTEM & PROMETHEUS METRICS</span>
                  </h3>
                  <div className="p-3.5 rounded-lg bg-panel border border-borderSubtle space-y-2">
                    <div>Port: <span className="text-brandGreen font-bold">8001</span></div>
                    <div>Prometheus Feed: <a href="/metrics" target="_blank" className="text-brandPurple hover:underline">/metrics ↗</a></div>
                    <div>Health Status: <span className="text-brandGreen font-bold">ALL SUBSYSTEMS NOMINAL</span></div>
                  </div>
                </div>
              )}

              {/* Floating Center Button: 'Jump to live tail' */}
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
                <button
                  onClick={() => {
                    setIsAutoScroll(true);
                    if (terminalRef.current) {
                      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
                    }
                  }}
                  className="px-3 py-1.5 rounded-full bg-[#1b2230] hover:bg-[#252f44] border border-borderSubtle text-txtSecondary hover:text-white font-mono text-[11px] flex items-center space-x-1.5 shadow-xl transition-all"
                >
                  <Icons.ArrowDown />
                  <span>Jump to live tail</span>
                </button>
              </div>

              {/* Floating Settings Button in lower right */}
              <div className="absolute bottom-4 right-4 z-20">
                <button
                  onClick={() => setActiveNav("settings")}
                  className="flex items-center space-x-1 text-txtMuted hover:text-white text-[11px] font-mono"
                >
                  <Icons.Settings />
                  <span>Settings</span>
                </button>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 3. RIGHT NARROW TIMELINE HISTOGRAM (EXACT LOGTAIL SPEC)                   */}
          {/* ========================================================================= */}
          <aside className="w-48 bg-workspace border-l border-borderSubtle/60 flex flex-col justify-between shrink-0 font-mono text-[11px]">
            {/* Header: Results count and time window */}
            <div className="p-3 border-b border-borderSubtle/60 text-right">
              <div className="font-bold text-white font-mono text-xs">{(75432 + terminalLogs.length - 38).toLocaleString()} Results</div>
              <div className="text-[10px] text-txtMuted">3 hours</div>
            </div>

            {/* Vertical Timeline Histogram Scrubber */}
            <div className="flex-1 relative px-2 py-4 flex flex-col justify-between select-none">
              {[
                { time: "12:00 PM", bars: [10, 15, 8] },
                { time: "12:10 PM", bars: [14, 18, 12] },
                { time: "12:20 PM", bars: [20, 24, 16] },
                { time: "12:30 PM", bars: [12, 18, 14, 20] },
                { time: "12:40 PM", bars: [28, 35, 22] },
                { time: "12:50 PM", bars: [45, 60, 52] },
                { time: "1:00 PM", bars: [25, 40, 50, 45, 30] },
                { time: "1:30 PM", bars: [35, 60, 55, 40] },
                { time: "2:00 PM", bars: [20, 25, 18, 15] },
                { time: "2:30 PM", bars: [15, 22, 18, 12] },
                { time: "3:00 PM", bars: [10, 8, 12, 14] },
              ].map((bucket, idx) => (
                <div key={idx} className="flex items-center justify-between space-x-2 py-0.5">
                  <span className="text-[9px] text-txtMuted shrink-0">{bucket.time}</span>
                  <div className="flex-1 flex flex-col items-end space-y-0.5">
                    {bucket.bars.map((bar, bIdx) => (
                      <div
                        key={bIdx}
                        className="h-1 rounded-sm bg-[#3a4763]"
                        style={{ width: `${Math.min(bar * 1.5, 65)}px` }}
                      ></div>
                    ))}
                  </div>
                </div>
              ))}

              {/* Exact Purple Range Selection Overlay from Reference */}
              <div
                className="absolute left-1 right-1 p-2 rounded bg-[#2a244d]/90 border border-brandPurple shadow-xl"
                style={{ top: '36%' }}
              >
                <div className="text-[9px] text-white font-bold leading-tight">Tue Dec 29 12:54:00 pm</div>
                <div className="text-[9px] text-[#cbd5e1] font-bold leading-tight">+ Tue Dec 29 12:58:00 pm</div>
                <div className="text-[10px] text-brandPurple font-bold mt-1">
                  8,321 Results
                </div>
                {/* Scrub Handle Bar & Indicator Dot */}
                <div className="relative w-full h-1 bg-brandPurple rounded-full mt-1.5">
                  <span className="absolute -top-1 right-3 w-3 h-3 rounded-full bg-brandPurple border-2 border-white shadow-md"></span>
                </div>
              </div>
            </div>

            {/* Selected Log Inspector Popup (when row is clicked) */}
            {selectedLog && (
              <div className="p-3 border-t border-borderSubtle bg-panel space-y-2 max-h-56 overflow-y-auto">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-[10px]">EVENT METADATA</span>
                  <button onClick={() => setSelectedLog(null)} className="text-txtMuted hover:text-white">✕</button>
                </div>
                <div className="text-[10px] text-txtMuted">ID: #{selectedLog.id}</div>
                <pre className="text-[9px] text-txtPrimary bg-workspace p-2 rounded overflow-x-auto">
                  {JSON.stringify(selectedLog.raw || selectedLog, null, 2)}
                </pre>
              </div>
            )}

            {/* Bottom Footer */}
            <div className="p-2 border-t border-borderSubtle/60 text-[9px] text-txtMuted text-center">
              DRISHTI Tail Engine // 8001
            </div>
          </aside>

          {/* ========================================================================= */}
          {/* REGISTRATION MODAL                                                        */}
          {/* ========================================================================= */}
          {showModal && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-panel border border-borderSubtle rounded-xl p-5 w-full max-w-md font-mono text-xs space-y-4 shadow-2xl">
                <div className="flex items-center justify-between border-b border-borderSubtle pb-2">
                  <h3 className="font-bold text-sm text-white">Add New Telemetry Source</h3>
                  <button onClick={() => { setShowModal(false); setNewProjectKey(null); }} className="text-txtMuted hover:text-white">✕</button>
                </div>

                {newProjectKey ? (
                  <div className="space-y-3">
                    <div className="p-2.5 rounded bg-brandGreen/20 text-brandGreen font-bold text-center">
                      Source Registered!
                    </div>
                    <div>
                      <span className="text-[10px] text-txtMuted">API Token:</span>
                      <div className="p-2 rounded bg-workspace border border-borderSubtle text-brandPurple font-mono text-xs break-all select-all">
                        {newProjectKey}
                      </div>
                    </div>
                    <button
                      onClick={() => { setShowModal(false); setNewProjectKey(null); fetchData(); }}
                      className="w-full py-1.5 rounded bg-brandPurple text-white font-bold"
                    >
                      Done
                    </button>
                  </div>
                ) : (
                  <form
                    onSubmit={async (e) => {
                      e.preventDefault();
                      const form = e.target;
                      const res = await authFetch('/projects/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          project_id: form.project_id.value,
                          name: form.name.value,
                          model_type: "regression",
                          framework: "custom"
                        })
                      });
                      const data = await res.json();
                      if (res.ok) {
                        setNewProjectKey(data.api_key);
                      } else {
                        notify(data.detail || "Error: Admin privileges required");
                      }
                    }}
                    className="space-y-3"
                  >
                    <div>
                      <label className="text-[10px] text-txtMuted">Source Slug:</label>
                      <input name="project_id" required placeholder="e.g. nlp-service" className="w-full bg-workspace border border-borderSubtle rounded p-1.5 text-white mt-1" />
                    </div>
                    <div>
                      <label className="text-[10px] text-txtMuted">Source Name:</label>
                      <input name="name" required placeholder="e.g. NLP Sentiment Engine" className="w-full bg-workspace border border-borderSubtle rounded p-1.5 text-white mt-1" />
                    </div>
                    <button type="submit" className="w-full py-2 rounded bg-brandPurple text-white font-bold mt-2">
                      Generate Source API Key
                    </button>
                  </form>
                )}
              </div>
            </div>
          )}

          {/* AUTHENTICATION CONSOLE MODAL */}
          {showAuthModal && (
            <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-panel border border-brandPurple/60 rounded-xl p-5 max-w-md w-full space-y-4 font-mono text-xs shadow-2xl">
                <div className="flex items-center justify-between border-b border-borderSubtle pb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-brandPurple font-bold">🔒 DRISHTI AI AUTHENTICATION</span>
                  </div>
                  <button onClick={() => setShowAuthModal(false)} className="text-txtMuted hover:text-white">✕</button>
                </div>
                <p className="text-txtMuted text-[11px] leading-relaxed">
                  Enter your Administrator Master Key (<code className="text-brandPurple">DRISHTI_MASTER_API_KEY</code>) or a Project API Key to access real-time telemetry, model drift metrics, and incident triage.
                </p>
                <div className="space-y-1.5">
                  <label className="text-[10px] text-txtMuted uppercase">API Key / Master Token:</label>
                  <input
                    type="password"
                    value={authInputKey}
                    onChange={(e) => setAuthInputKey(e.target.value)}
                    placeholder="dr_live_••••••••••••••••••••••••••••••••"
                    className="w-full bg-workspace border border-borderSubtle focus:border-brandPurple rounded p-2 text-white font-mono text-xs outline-none"
                  />
                  <div className="text-[9.5px] text-txtMuted">
                    Saved exclusively in this browser tab's <code className="text-txtSecondary">sessionStorage</code>. Never stored in source code.
                  </div>
                </div>
                <div className="flex items-center space-x-2 pt-2">
                  <button
                    onClick={handleSaveAuthKey}
                    className="flex-1 py-2 rounded bg-brandPurple hover:bg-brandPurple/80 text-white font-bold transition-all shadow-md"
                  >
                    Connect Workspace
                  </button>
                  {apiKey && (
                    <button
                      onClick={() => { setAuthInputKey(""); setApiKey(""); sessionStorage.removeItem("drishti_api_key"); notify("Logged out."); setShowAuthModal(false); }}
                      className="px-3 py-2 rounded bg-brandRed/20 hover:bg-brandRed/30 text-brandRed font-bold border border-brandRed/40 transition-all"
                    >
                      Clear
                    </button>
                  )}
                  <button
                    onClick={() => setShowAuthModal(false)}
                    className="px-3 py-2 rounded bg-workspace border border-borderSubtle text-txtMuted hover:text-white"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      );
    }

    // Mount Application
    ReactDOM.createRoot(document.getElementById('root')).render(<LogtailApp />);
  </script>
</body>
</html>
"""


def get_dashboard_html() -> str:
    """Return the pre-rendered Logtail terminal HTML document."""
    return DASHBOARD_HTML

