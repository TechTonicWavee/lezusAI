"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";

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

function LevelChip({ level }: { level?: string }) {
  const styles: Record<string, string> = {
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

function StatusBadge({ status }: { status?: string }) {
  const styles: Record<string, string> = {
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

export default function DrishtiDashboard() {
  const [activeTab, setActiveTab] = useState("logs");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [selectedProject, setSelectedProject] = useState("all");
  const [timeRange, setTimeRange] = useState("1h");
  const [isStreaming, setIsStreaming] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [logFilterLevel, setLogFilterLevel] = useState("ALL");
  const [logSearchQuery, setLogSearchQuery] = useState("");

  const [projects, setProjects] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});
  const [incidents, setIncidents] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [responses, setResponses] = useState<any[]>([]);
  const [mlopsRuns, setMlopsRuns] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [driftData, setDriftData] = useState<any>(null);
  const [backendStatus, setBackendStatus] = useState("CONNECTING");

  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [registeredApiKey, setRegisteredApiKey] = useState<string | null>(null);
  const [toast, setToast] = useState<{ text: string; type?: string } | null>(null);

  const [diagMessage, setDiagMessage] = useState("Feature store connection timeout to Redis cluster");
  const [diagSeverity, setDiagSeverity] = useState("ERROR");
  const [diagResult, setDiagResult] = useState<any>(null);
  const [diagRunning, setDiagRunning] = useState(false);

  const logContainerRef = useRef<HTMLDivElement>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const notify = (text: string, type: string = "info") => {
    setToast({ text, type });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchData = async () => {
    try {
      const pParam = selectedProject !== "all" ? `?project_id=${selectedProject}` : "";
      const [projsRes, statsRes, alertsRes, histRes, respRes, runsRes] = await Promise.all([
        fetch(`${API_BASE}/projects`).then(r => r.json()).catch(() => ({ projects: [] })),
        fetch(`${API_BASE}/system/stats${pParam}`).then(r => r.json()).catch(() => ({})),
        fetch(`${API_BASE}/alerts${pParam}`).then(r => r.json()).catch(() => ({ alerts: [] })),
        fetch(`${API_BASE}/incidents/history${pParam}`).then(r => r.json()).catch(() => ({ history: [] })),
        fetch(`${API_BASE}/responses${pParam}`).then(r => r.json()).catch(() => ({ actions: [] })),
        fetch(`${API_BASE}/mlops/runs`).then(r => r.json()).catch(() => ({ runs: [] })),
      ]);

      setProjects(projsRes.projects || []);
      setMetrics(statsRes.metrics || {});
      setIncidents(alertsRes.alerts || []);
      setHistory(histRes.history || []);
      setResponses(respRes.actions || []);
      setMlopsRuns(runsRes.runs || []);
      setBackendStatus("HEALTHY");

      if (selectedProject !== "all") {
        const [tRes, dRes] = await Promise.all([
          fetch(`${API_BASE}/telemetry/${selectedProject}?limit=150`).then(r => r.json()).catch(() => ({ records: [] })),
          fetch(`${API_BASE}/telemetry/${selectedProject}/drift`).then(r => r.json()).catch(() => null)
        ]);
        setTelemetry(tRes.records || []);
        setDriftData(dRes);
      } else {
        const allTelemetryPromises = (projsRes.projects || []).map((p: any) =>
          fetch(`${API_BASE}/telemetry/${p.project_id}?limit=60`).then(r => r.json()).catch(() => ({ records: [] }))
        );
        const allTResults = await Promise.all(allTelemetryPromises);
        const combined = allTResults.flatMap((r: any) => r.records || []);
        combined.sort((a: any, b: any) => (b.timestamp || "").localeCompare(a.timestamp || ""));
        setTelemetry(combined);
        setDriftData(null);
      }
    } catch (err) {
      console.error(err);
      setBackendStatus("DISCONNECTED");
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      if (isStreaming) fetchData();
    }, 3000);
    return () => clearInterval(interval);
  }, [selectedProject, isStreaming]);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [telemetry, autoScroll]);

  const unifiedLogs = useMemo(() => {
    const stream: any[] = [];
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

    stream.sort((a, b) => (b.fullTimestamp || "").localeCompare(a.fullTimestamp || ""));
    return stream;
  }, [telemetry, history, responses]);

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

  const streamStats = useMemo(() => {
    const counts: Record<string, number> = { INFO: 0, WARN: 0, ERROR: 0, CRITICAL: 0 };
    let totalLat = 0;
    let latCount = 0;
    let p95Lat = 0;
    const latList: number[] = [];

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

  const handleResolveIncident = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/alerts/${id}/resolve`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution_notes: "Resolved via Next.js Operator Terminal" })
      });
      if (res.ok) {
        notify(`Incident #${id} resolved successfully!`, "success");
        fetchData();
      }
    } catch (e: any) {
      notify(`Failed to resolve incident: ${e.message}`, "error");
    }
  };

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
    <div className="flex h-screen w-screen overflow-hidden bg-canvas text-txt-primary select-none">
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

      {/* SIDEBAR */}
      <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-sidebar border-r border-border flex flex-col justify-between shrink-0 transition-all duration-200 z-20`}>
        <div>
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
                  {projects.map((p: any) => (
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

        <div className="p-3 border-t border-border bg-canvas/30 text-xs font-mono">
          {!sidebarCollapsed ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-txt-muted">Telemetry Node:</span>
                <span className="text-txt-secondary">127.0.0.1:8000</span>
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
            </div>
          ) : (
            <div className="flex justify-center">
              <span className={`w-2.5 h-2.5 rounded-full ${backendStatus === "HEALTHY" ? "bg-status-success animate-pulse-dot" : "bg-status-error"}`}></span>
            </div>
          )}
        </div>
      </aside>

      {/* CENTRAL WORKSPACE */}
      <main className="flex-1 flex flex-col min-w-0 bg-content overflow-hidden">
        <header className="h-14 border-b border-border bg-canvas/70 px-4 flex items-center justify-between shrink-0">
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
            </div>
          </div>

          <div className="flex items-center space-x-2 font-mono text-xs">
            <button
              onClick={() => setIsStreaming(!isStreaming)}
              className={`px-2.5 py-1 rounded-md border flex items-center space-x-1.5 text-xs transition-colors ${
                isStreaming
                  ? "bg-card border-border text-status-success hover:bg-elevated"
                  : "bg-status-warning/20 border-status-warning/40 text-status-warning"
              }`}
            >
              {isStreaming ? <Icons.Pause /> : <Icons.Play />}
              <span className="text-[11px] hidden sm:inline">{isStreaming ? "LIVE" : "PAUSED"}</span>
            </button>

            {activeTab === "logs" && (
              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`px-2 py-1 rounded-md border text-[11px] ${
                  autoScroll ? "bg-brand-purple/20 border-brand-purple/40 text-brand-secondary font-semibold" : "bg-card border-border text-txt-muted"
                }`}
              >
                ⬇ AUTO-SCROLL
              </button>
            )}

            <button
              onClick={() => { fetchData(); notify("Refreshed telemetry", "info"); }}
              className="p-1.5 rounded-md bg-card border border-border hover:bg-elevated text-txt-muted hover:text-txt-primary"
            >
              <Icons.Refresh />
            </button>

            <button
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
              className={`p-1.5 rounded-md border transition-colors ${
                rightPanelOpen ? "bg-elevated border-brand-purple/40 text-brand-secondary purple-glow-sm" : "bg-card border-border text-txt-muted hover:text-txt-primary"
              }`}
            >
              <Icons.PanelToggle />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* TAB 1: LIVE LOGS */}
          {activeTab === "logs" && (
            <div className="h-full flex flex-col space-y-3">
              <div className="bg-card border border-border rounded-lg p-2.5 flex flex-wrap items-center justify-between gap-2.5 font-mono text-xs">
                <div className="relative flex-1 min-w-[260px]">
                  <div className="absolute left-2.5 top-2.5 pointer-events-none">
                    <Icons.Search />
                  </div>
                  <input
                    type="text"
                    value={logSearchQuery}
                    onChange={e => setLogSearchQuery(e.target.value)}
                    placeholder="Search logs by keyword, model, correlation ID..."
                    className="w-full bg-content border border-border rounded-md pl-8 pr-3 py-1.5 text-xs text-txt-primary placeholder-txt-muted focus:outline-none focus:border-brand-purple"
                  />
                </div>

                <div className="flex items-center space-x-1 bg-content border border-border rounded-md p-1">
                  {["ALL", "INFO", "WARN", "ERROR", "CRITICAL"].map(lvl => (
                    <button
                      key={lvl}
                      onClick={() => setLogFilterLevel(lvl)}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                        logFilterLevel === lvl ? "bg-brand-purple text-white shadow" : "text-txt-muted hover:text-txt-primary"
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>

                <div className="text-[11px] text-txt-muted">
                  Showing <span className="text-txt-primary font-bold">{filteredLogs.length}</span> of {unifiedLogs.length} events
                </div>
              </div>

              <div className="flex-1 bg-content border border-border rounded-lg flex flex-col overflow-hidden purple-glow-sm">
                <div className="bg-canvas border-b border-border px-3 py-2 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-status-error/80 inline-block"></span>
                      <span className="w-2.5 h-2.5 rounded-full bg-status-warning/80 inline-block"></span>
                      <span className="w-2.5 h-2.5 rounded-full bg-status-success/80 inline-block"></span>
                    </div>
                    <span className="text-txt-muted text-[11px] ml-2">drishti-tail -f /var/log/telemetry.stream</span>
                  </div>
                  <span className="text-txt-muted text-[11px]">{filteredLogs.length} buffered rows</span>
                </div>

                <div
                  ref={logContainerRef}
                  className="flex-1 overflow-y-auto p-2 font-mono text-[11.5px] space-y-0.5 divide-y divide-border/20 select-text"
                >
                  {filteredLogs.map((log, idx) => (
                    <div
                      key={log.id + idx}
                      onClick={() => { setSelectedItem(log); if (!rightPanelOpen) setRightPanelOpen(true); }}
                      className={`px-2 py-1.5 rounded cursor-pointer flex items-baseline space-x-2.5 transition-colors ${
                        selectedItem?.id === log.id ? "terminal-row-active" : "hover:bg-card/70 text-txt-secondary hover:text-txt-primary"
                      }`}
                    >
                      <span className="text-txt-muted text-[11px] shrink-0">{log.timestamp}</span>
                      <LevelChip level={log.level} />
                      <span className="text-brand-secondary text-[11px] shrink-0 font-medium">[{log.source}]</span>
                      <span className="text-txt-muted text-[11px] shrink-0">#{log.id.slice(0, 8)}</span>
                      {log.model && (
                        <span className="px-1.5 py-0.2 rounded bg-card border border-border text-[10px] text-accent-blue shrink-0">
                          {log.model}
                        </span>
                      )}
                      <span className="flex-1 truncate text-txt-primary font-normal">{log.message}</span>
                      {log.latency && <span className="text-brand-purple text-[11px] shrink-0 font-semibold">{log.latency}</span>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-4 font-mono">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">Total Predictions</div>
                  <div className="text-xl font-bold text-txt-primary mt-1">{streamStats.total}</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">Avg Latency</div>
                  <div className="text-xl font-bold text-brand-purple mt-1">{streamStats.avgLatency} ms</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">P95 Latency</div>
                  <div className="text-xl font-bold text-accent-blue mt-1">{streamStats.p95Latency} ms</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">Error Rate</div>
                  <div className="text-xl font-bold text-status-success mt-1">{streamStats.errorRate}%</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">Anomalies</div>
                  <div className="text-xl font-bold text-status-warning mt-1">{streamStats.anomalies}</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-3">
                  <div className="text-[10px] text-txt-muted uppercase">Open Incidents</div>
                  <div className="text-xl font-bold text-status-error mt-1">{streamStats.openIncidents}</div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: INCIDENTS */}
          {activeTab === "incidents" && (
            <div className="bg-card border border-border rounded-xl p-4 font-mono text-xs space-y-3">
              <h3 className="text-sm font-bold text-txt-primary">INCIDENT TRIAGE QUEUE</h3>
              <div className="overflow-x-auto border border-border rounded-lg">
                <table className="w-full text-left divide-y divide-border text-[11.5px]">
                  <thead className="bg-canvas text-txt-muted uppercase text-[10px]">
                    <tr>
                      <th className="p-2.5">ID</th>
                      <th className="p-2.5">Project</th>
                      <th className="p-2.5">Severity</th>
                      <th className="p-2.5">Message</th>
                      <th className="p-2.5">Status</th>
                      <th className="p-2.5">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 bg-content">
                    {incidents.map((inc: any) => (
                      <tr key={inc.id} className="hover:bg-card/70">
                        <td className="p-2.5 text-txt-muted">#{inc.id}</td>
                        <td className="p-2.5 text-accent-blue">{inc.project_id || "default"}</td>
                        <td className="p-2.5"><LevelChip level={inc.severity} /></td>
                        <td className="p-2.5 truncate max-w-md">{inc.message}</td>
                        <td className="p-2.5"><StatusBadge status={inc.status} /></td>
                        <td className="p-2.5">
                          {inc.status !== "RESOLVED" && (
                            <button
                              onClick={() => handleResolveIncident(inc.id)}
                              className="px-2 py-1 bg-status-success/20 hover:bg-status-success text-status-success hover:text-white rounded text-[10px] font-bold"
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
        </div>
      </main>

      {/* RIGHT CONTEXTUAL DRAWER */}
      {rightPanelOpen && (
        <aside className="w-80 bg-sidebar border-l border-border flex flex-col justify-between shrink-0 transition-all z-10 text-xs font-mono">
          <div className="h-14 border-b border-border px-3.5 flex items-center justify-between bg-canvas/40">
            <span className="font-bold text-[11px] text-txt-primary tracking-wider uppercase">
              {selectedItem ? "INSPECTOR // EVENT" : "TELEMETRY METRICS"}
            </span>
            <button onClick={() => setRightPanelOpen(false)} className="text-txt-muted hover:text-txt-primary">✕</button>
          </div>

          <div className="flex-1 overflow-y-auto p-3.5 space-y-4">
            {selectedItem ? (
              <div className="space-y-3">
                <div className="p-2.5 rounded bg-content border border-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-txt-muted text-[10px]">EVENT ID:</span>
                    <LevelChip level={selectedItem.level} />
                  </div>
                  <div className="text-sm font-bold text-brand-secondary break-all">#{selectedItem.id}</div>
                </div>
                <div className="space-y-1">
                  <span className="text-txt-muted text-[10px] uppercase font-bold">Log Message:</span>
                  <p className="p-2 rounded bg-content border border-border text-[11px] text-txt-primary break-words">
                    {selectedItem.message}
                  </p>
                </div>
                <pre className="p-2.5 rounded bg-content border border-border text-[10px] text-txt-primary overflow-x-auto max-h-48">
                  {JSON.stringify(selectedItem.raw || selectedItem, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-content border border-border space-y-2.5">
                  <div className="text-[10px] text-txt-muted uppercase font-bold">Severity Breakdown</div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-status-info font-bold">INFO</span>
                      <span className="text-txt-primary">{streamStats.counts.INFO || 0}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-status-warning font-bold">WARN</span>
                      <span className="text-txt-primary">{streamStats.counts.WARN || 0}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-status-error font-bold">ERROR</span>
                      <span className="text-txt-primary">{streamStats.counts.ERROR || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>
      )}
    </div>
  );
}
