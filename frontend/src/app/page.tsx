"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";

// --- LOGTAIL OUTLINE ICONS ---
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
  )
};

export default function LogtailDashboard() {
  const [activeNav, setActiveNav] = useState("livetail");
  const [selectedProject, setSelectedProject] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [timeFilter, setTimeFilter] = useState("Last 3 hours");
  const [selectedLog, setSelectedLog] = useState<any>(null);
  const [isAutoScroll, setIsAutoScroll] = useState(true);

  const [projects, setProjects] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [mlopsRuns, setMlopsRuns] = useState<any[]>([]);
  const [driftData, setDriftData] = useState<any>(null);

  const terminalRef = useRef<HTMLDivElement>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const fetchData = async () => {
    try {
      const pParam = selectedProject !== "all" ? `?project_id=${selectedProject}` : "";
      const [projsRes, alertsRes, runsRes] = await Promise.all([
        fetch(`${API_BASE}/projects`).then(r => r.json()).catch(() => ({ projects: [] })),
        fetch(`${API_BASE}/alerts${pParam}`).then(r => r.json()).catch(() => ({ alerts: [] })),
        fetch(`${API_BASE}/mlops/runs`).then(r => r.json()).catch(() => ({ runs: [] }))
      ]);

      setProjects(projsRes.projects || []);
      setIncidents(alertsRes.alerts || []);
      setMlopsRuns(runsRes.runs || []);

      if (selectedProject !== "all") {
        const [tRes, dRes] = await Promise.all([
          fetch(`${API_BASE}/telemetry/${selectedProject}?limit=120`).then(r => r.json()).catch(() => ({ records: [] })),
          fetch(`${API_BASE}/telemetry/${selectedProject}/drift`).then(r => r.json()).catch(() => null)
        ]);
        setTelemetry(tRes.records || []);
        setDriftData(dRes);
      } else {
        const allPromises = (projsRes.projects || []).map((p: any) =>
          fetch(`${API_BASE}/telemetry/${p.project_id}?limit=60`).then(r => r.json()).catch(() => ({ records: [] }))
        );
        const allRes = await Promise.all(allPromises);
        const combined = allRes.flatMap((r: any) => r.records || []);
        combined.sort((a: any, b: any) => (b.timestamp || "").localeCompare(a.timestamp || ""));
        setTelemetry(combined);
        setDriftData(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [selectedProject]);

  useEffect(() => {
    if (isAutoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [telemetry, isAutoScroll]);

  const BASELINE_LOGS = [
    { id: "base_01", timestamp: "2021-12-29T10:39:24.865711689Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=38y2 class=EndpointCheckWorker jid=e8749afcdb6dfaf1f90fc0f elapsed=1.15 INFO: done" },
    { id: "base_02", timestamp: "2021-12-29T10:39:24.876526383Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=5zp2 class=EndpointCheckWorker jid=70b413957933fdae7dec2d0e elapsed=2.313 INFO: done" },
    { id: "base_03", timestamp: "2021-12-29T10:39:24.886492938Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3cey class=EndpointCheckWorker jid=57e968ea65eced9c1053403 elapsed=0.875 INFO: done" },
    { id: "base_04", timestamp: "2021-12-29T10:39:24.900355798Z", dotColor: null, appPill: "app[repeatable_backup.1]:", content: "pid=240 tid=3akk class=EndpointCheckWorker jid=2b0b0916b30ddf0b7ff36f01 elapsed=1.227 INFO: done" },
    { id: "base_05", timestamp: "2021-12-29T10:39:24.908874753Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3az6 class=EndpointCheckWorker jid=545fa64fe59e6c75db2004eb elapsed=0.361 INFO: done" },
    { id: "base_06", timestamp: "2021-12-29T10:39:24.901369287Z", dotColor: null, appPill: "app[repeatable.3]:", content: "pid=240 tid=3gt8 class=EndpointCheckWorker jid=e2507edbc53a65b9a771a333 elapsed=2.574 INFO: done" },
    { id: "base_07", timestamp: "2021-12-29T10:39:24.917024488Z", dotColor: "#e6b45c", appPill: "app[repeatable.1]:", content: "'Redis#exists(key)' will return an Integer in redis-rb 4.3. 'exists?' returns a boolean, you should use it instead. To opt-in to the new behavior now you can set Redis.exists_returns_integer = true. (/app/vendor/bundle/ruby/2.7.0/gems/sidekiq-6.0.7/lib/sidekiq/launcher.rb:160:in 'block (2 levels) in <top>')" },
    { id: "base_08", timestamp: "2021-12-29T10:39:24.929351079Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3rm2 class=EndpointCheckWorker jid=a00249aa96e6bf73a6e1ae03 elapsed=1.114 INFO: done" },
    { id: "base_09", timestamp: "2021-12-29T10:39:24.958132169Z", dotColor: "#e6b45c", appPill: "app[repeatable.3]:", content: "pid=238 tid=3iqa class=EndpointCheckWorker jid=d92e86d93d6cf044eecf2956 elapsed=2.431 INFO: done" },
    { id: "base_10", timestamp: "2021-12-29T10:39:24.972964706Z", dotColor: "#e6b45c", appPill: "app[analytics.1]:", content: "pid=238 tid=6jxa class=Report::IncidentWorker jid=e1a308b236505d46bee9d07a1 INFO: start" },
    { id: "base_11", timestamp: "2021-12-29T10:39:24.974833363Z", dotColor: null, appPill: "app[repeatable_backup.4]:", content: "pid=237 tid=4ygl class=EndpointCheckWorker jid=2e9aecb6da5a70dfd4aceb4d elapsed=2.485 INFO: done" },
    { id: "base_12", timestamp: "2021-12-29T10:39:24.979285611Z", dotColor: null, appPill: "app[analytics.1]:", content: "pid=238 tid=6jxa class=Report::IncidentWorker jid=e1a308b236505d46bee9d07a1 elapsed=0.005 INFO: done" },
    { id: "base_13", timestamp: "2021-12-29T10:39:24.982135345Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3tti class=EndpointCheckWorker jid=e42dc2d6d1e41b42de768d1b3 elapsed=9.067 INFO: done" },
    { id: "base_14", timestamp: "2021-12-29T10:39:24.995899668Z", dotColor: "#8b5cf6", appPill: "app[repeatable_backup.3]:", content: "pid=238 tid=3cjy class=EndpointCheckWorker jid=67201d5ff43b6f624e0b6a6bb elapsed=8.292 INFO: done" },
    { id: "base_15", timestamp: "2021-12-29T10:39:25.002565733Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=3tg2 class=EndpointCheckWorker jid=fa7694ae3b0e481cf76c0d714be elapsed=8.224 INFO: done" },
    { id: "base_16", timestamp: "2021-12-29T10:39:25.004137648Z", dotColor: null, appPill: "app[chung.1]:", content: "2020-12-29 10:39:25 +0000: running: EndpointCheckWorker.perform_all_30s" },
    { id: "base_17", timestamp: "2021-12-29T10:39:25.010639292Z", dotColor: null, appPill: "app[repeatable.3]:", content: "pid=238 tid=3tru class=EndpointCheckWorker jid=33a0a6ea701902f02cfef521 elapsed=9.242 INFO: done" },
    { id: "base_18", timestamp: "2021-12-29T10:39:25.046682785Z", dotColor: null, appPill: "app[repeatable_backup.3]:", content: "pid=238 tid=3bgq class=Endpoint::PingUptimeReportWorker jid=d00cb0b37f9fc532973718c2a INFO: start" },
    { id: "base_19", timestamp: "2021-12-29T10:39:25.056024213Z", dotColor: null, appPill: "app[repeatable_backup.3]:", content: "pid=238 tid=3bgq class=Endpoint::PingUptimeReportWorker jid=d00cb0b37f9fc532973718c2a elapsed=0.01 INFO: done" },
    { id: "base_20", timestamp: "2021-12-29T10:39:25.065721448Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3cin class=EndpointCheckWorker jid=0ffe96b955f8aa9cd537be1e elapsed=8.263 INFO: done" },
    { id: "base_21", timestamp: "2021-12-29T10:39:25.071807612Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=3bpq class=EndpointCheckWorker jid=3a709f518aa3d381b66a91d8 elapsed=9.147 INFO: done" },
    { id: "base_22", timestamp: "2021-12-29T10:39:25.082834821Z", dotColor: null, appPill: "app[repeatable.3]:", content: "pid=238 tid=3b0e class=EndpointCheckWorker jid=5ef01254cee91b638b08365df elapsed=8.296 INFO: done" },
    { id: "base_23", timestamp: "2021-12-29T10:39:25.097375634Z", dotColor: "#e6b45c", appPill: "app[repeatable_backup.1]:", content: "pid=240 tid=3e30 class=Endpoint::PingUptimeReportWorker jid=d035ee8b7332125feck95323 INFO: start" },
    { id: "base_24", timestamp: "2021-12-29T10:39:25.104028881Z", dotColor: null, appPill: "app[repeatable.4]:", content: "pid=238 tid=47za class=EndpointCheckWorker jid=c32427ca82dcd60157d6ff40 elapsed=2.266 INFO: done" },
    { id: "base_25", timestamp: "2021-12-29T10:39:25.121712204Z", dotColor: null, appPill: "app[worker.1]:", content: "2020-12-29 10:39:25.121 UTC [235] LOG stats: 7 xacts/s, 0 queries/s, in 5882 B/s, out 14003 B/s, xact 6342 us, query 5861 us, wait 0 us" },
    { id: "base_26", timestamp: "2021-12-29T10:39:25.125348926Z", dotColor: null, appPill: "app[repeatable.4]:", content: "pid=238 tid=3gxa class=EndpointCheckWorker jid=d9b221bd1af4603626464baa elapsed=9.193 INFO: done" },
    { id: "base_27", timestamp: "2021-12-29T10:39:25.135534444Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=3r2m class=EndpointCheckWorker jid=69958079a225e772608e46d8 elapsed=8.346 INFO: done" },
    { id: "base_28", timestamp: "2021-12-29T10:39:25.140470216Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=31v2 class=EndpointCheckWorker jid=4fa26bc27307fa3fc220ab33 elapsed=5.252 INFO: done" },
    { id: "base_29", timestamp: "2021-12-29T10:39:25.149318413Z", dotColor: null, appPill: "app[repeatable.4]:", content: "pid=237 tid=47kh class=Endpoint::PingUptimeReportWorker jid=479dd5d0ddbe4b51775d3d9b INFO: start" },
    { id: "base_30", timestamp: "2021-12-29T10:39:25.154987952Z", dotColor: null, appPill: "app[analytics.1]:", content: "'toadhopper' not available, safely cannot use the Hoptoad stategy 'toadhopper' not available, safely" },
    { id: "base_31", timestamp: "2021-12-29T10:39:25.164318385Z", dotColor: null, appPill: "app[repeatable.5]:", content: "pid=238 tid=3g2a class=EndpointCheckWorker jid=c27f797e391df5b557231e9d elapsed=2.428 INFO: done" },
    { id: "base_32", timestamp: "2021-12-29T10:39:25.180540825Z", dotColor: null, appPill: "app[repeatable_backup.1]:", content: "pid=238 tid=3c9a class=EndpointCheckWorker jid=76a11a51630867c539598a59c elapsed=1.884 INFO: done" },
    { id: "base_33", timestamp: "2021-12-29T10:39:25.196389758Z", dotColor: "#67b8d9", appPill: "app[repeatable.2]:", content: "pid=238 tid=3bb6 class=EndpointCheckWorker jid=aae21a406bf8cdbe51096 elapsed=0.557 INFO: done" },
    { id: "base_34", timestamp: "2021-12-29T10:39:25.198284772Z", dotColor: null, appPill: "app[repeatable_backup.5]:", content: "pid=237 tid=31c9 class=EndpointCheckWorker jid=89c08dbu0fc42f0829db11a5 elapsed=3.493 INFO: done" },
    { id: "base_35", timestamp: "2021-12-29T10:39:25.199708609Z", dotColor: null, appPill: "app[analytics.1]:", content: "pid=236 tid=5wxy class=Report::IncidentWorker jid=37d09ea95d1e66eaf0c956 INFO: start" },
    { id: "base_36", timestamp: "2021-12-29T10:39:25.223545945Z", dotColor: null, appPill: "app[repeatable.1]:", content: "pid=238 tid=3j0y class=EndpointCheckWorker jid=b03bf6b16a7ef79fec837c62 elapsed=1.644 INFO: done" },
    { id: "base_37", timestamp: "2021-12-29T10:39:25.234447970Z", dotColor: null, appPill: "app[repeatable.2]:", content: "pid=238 tid=6bqe class=EndpointCheckWorker jid=6aa743jf25742cfel1ca425a elapsed=9.32 INFO: done" },
    { id: "base_38", timestamp: "2021-12-29T10:39:25.243063731Z", dotColor: null, appPill: "app[repeatable_backup.3]:", content: "2020-12-29 10:39:25.243 UTC [235] LOG C-0+7f66cad96030: dbl/postgres@127.0.0.1:35284 closing because: client disconnected" }
  ];

  const terminalLogs = useMemo(() => {
    const lines: any[] = [...BASELINE_LOGS];
    telemetry.forEach((t, idx) => {
      const isErr = t.is_anomaly || t.event_type === "ERROR" || t.error_type;
      const isWarn = t.severity === "WARNING" || t.severity === "WARN";
      const dotColor = isErr ? "#e16d79" : (isWarn ? "#e6b45c" : (t.prediction !== undefined ? "#67b8d9" : null));
      const appPill = t.error_type ? "app[error.handler]:" : (t.is_anomaly ? "app[anomaly.detector]:" : `app[${t.project_id || 'repeatable.1'}]:`);
      
      let lineContent = `pid=238 tid=${t.telemetry_id?.slice(0, 4) || '38y2'} class=${t.model_name || 'EndpointCheckWorker'} jid=${t.telemetry_id || 'e8749a'}`;
      if (t.latency_ms) lineContent += ` elapsed=${(t.latency_ms / 1000).toFixed(3)}s`;
      if (t.prediction !== undefined) lineContent += ` pred=${JSON.stringify(t.prediction)}`;
      if (t.ground_truth !== undefined) lineContent += ` actual=${JSON.stringify(t.ground_truth)}`;
      if (t.log_message || t.error_message) {
        lineContent += ` ${t.severity || (isErr ? 'ERROR' : 'INFO')}: ${t.error_message || t.log_message}`;
      } else {
        lineContent += ` INFO: done`;
      }

      lines.push({
        id: t.telemetry_id || `line_${idx}`,
        timestamp: t.timestamp ? `${t.timestamp.replace('Z', '')}Z` : '2026-11-20T01:30:24.865711689Z',
        dotColor,
        appPill,
        content: lineContent,
        raw: t
      });
    });

    lines.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    return lines;
  }, [telemetry]);

  const filteredLogs = useMemo(() => {
    if (!searchQuery.trim()) return terminalLogs;
    const q = searchQuery.toLowerCase();
    return terminalLogs.filter(l => l.content.toLowerCase().includes(q) || l.timestamp.includes(q));
  }, [terminalLogs, searchQuery]);

  return (
    <div className="w-screen h-screen bg-[#0c0f17] flex items-center justify-center p-2 sm:p-4 md:p-6 overflow-hidden select-none">
      <div className="w-full h-full max-w-[1780px] max-h-[960px] bg-[#1e293b] rounded-2xl border border-[#39445a]/60 shadow-2xl flex overflow-hidden text-[#e2e8f0]">
        
        {/* 1. LEFT SIDEBAR */}
        <aside className="w-56 bg-[#30394d] border-r border-[#303b50] flex flex-col justify-between shrink-0">
          <div>
            <div className="h-13 px-4 py-3.5 flex items-center space-x-2.5 border-b border-[#303b50]/60">
              <Icons.Logo />
              <span className="font-bold text-sm tracking-wide text-white">Logtail</span>
              <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-[#8b5cf6]/30 text-[#8b5cf6] border border-[#8b5cf6]/40 ml-1">AI</span>
            </div>

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
                      active ? "bg-[#252d3d] text-white font-semibold border border-[#39445a]/50" : "text-[#a3adbf] hover:text-white hover:bg-[#273247]/50"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className={active ? "text-[#8b5cf6]" : "text-[#718096]"}><Icon /></span>
                      <span>{item.label}</span>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-3 border-t border-[#303b50]/60 text-xs space-y-2">
            <button className="flex items-center space-x-2.5 text-[#a3adbf] hover:text-white px-2 py-1">
              <Icons.Help />
              <span>Help & Support</span>
            </button>
            <div className="pt-2 border-t border-[#303b50]/40 flex items-center space-x-2.5 px-2">
              <div className="w-7 h-7 rounded-full bg-[#8b5cf6]/30 border border-[#8b5cf6] text-[11px] font-bold text-white flex items-center justify-center">
                D
              </div>
              <div className="truncate text-left leading-tight">
                <div className="text-[10px] text-[#718096] uppercase font-mono">Team</div>
                <div className="text-xs font-semibold text-white truncate">Wallmine Core</div>
              </div>
            </div>
          </div>
        </aside>

        {/* 2. CENTRAL WORKSPACE */}
        <div className="flex-1 flex flex-col min-w-0 bg-[#20283a] overflow-hidden">
          <header className="h-13 bg-[#1e293b] border-b border-[#39445a]/60 px-4 flex items-center justify-between shrink-0 text-xs">
            <div className="flex items-center space-x-3 flex-1 max-w-2xl">
              <div className="relative">
                <select
                  value={selectedProject}
                  onChange={e => setSelectedProject(e.target.value)}
                  className="appearance-none bg-[#273247] hover:bg-[#303b52] border border-[#39445a] rounded-md pl-7 pr-7 py-1.5 text-xs text-white font-medium focus:outline-none cursor-pointer"
                >
                  <option value="all">⚡ All Sources (Core Firehose)</option>
                  {projects.map((p: any) => (
                    <option key={p.project_id} value={p.project_id}>
                      ⚡ {p.name}
                    </option>
                  ))}
                </select>
                <div className="absolute left-2.5 top-2.5 pointer-events-none"><Icons.Zap /></div>
                <div className="absolute right-2.5 top-2.5 pointer-events-none"><Icons.ChevronDown /></div>
              </div>

              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search your logs..."
                  className="w-full bg-[#273247] border border-[#39445a] rounded-md pl-8 pr-3 py-1.5 text-xs text-white placeholder-[#718096] focus:outline-none focus:border-[#8b5cf6]"
                />
                <div className="absolute left-2.5 top-2.5 pointer-events-none"><Icons.Search /></div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button className="flex items-center space-x-1.5 bg-[#273247] border border-[#39445a] px-2.5 py-1.5 rounded-md text-[#a3adbf] hover:text-white">
                <span>{timeFilter}</span>
                <Icons.ChevronDown />
              </button>
              <div className="flex items-center space-x-2 pl-2 border-l border-[#39445a]/60">
                <div className="w-6 h-6 rounded-full bg-[#67b8d9]/30 border border-[#67b8d9] text-[10px] text-[#67b8d9] flex items-center justify-center font-bold">LW</div>
                <span className="font-medium text-xs text-white">Lillia Walker</span>
              </div>
            </div>
          </header>

          {/* Log Stream */}
          <div className="flex-1 relative flex overflow-hidden">
            <div
              ref={terminalRef}
              className="flex-1 overflow-y-auto p-3 font-mono text-[11px] leading-[18px] text-[#e2e8f0] space-y-1 select-text"
            >
              {filteredLogs.map((log: any) => (
                <div
                  key={log.id}
                  onClick={() => setSelectedLog(log)}
                  className={`flex items-start space-x-2 px-2 py-0.5 rounded cursor-pointer transition-colors ${
                    selectedLog?.id === log.id ? "bg-[#6689e8]/15 border-l-2 border-[#8b5cf6]" : "hover:bg-[#252f44]"
                  }`}
                >
                  <div className="w-2.5 flex justify-center pt-1 shrink-0">
                    {log.dotColor && <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ backgroundColor: log.dotColor }}></span>}
                  </div>
                  <span className="text-[#64748b] shrink-0">{log.timestamp}</span>
                  <span className="text-[#6689e8] shrink-0 font-semibold">{log.appPill}</span>
                  <span className="text-[#cbd5e1] break-all flex-1">{log.content}</span>
                </div>
              ))}
            </div>

            {/* Floating Jump to Live Tail Button */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
              <button
                onClick={() => {
                  setIsAutoScroll(true);
                  if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
                }}
                className="px-3 py-1.5 rounded-full bg-[#1b2230] hover:bg-[#252f44] border border-[#39445a] text-[#a3adbf] hover:text-white font-mono text-[11px] flex items-center space-x-1.5 shadow-xl"
              >
                <Icons.ArrowDown />
                <span>Jump to live tail</span>
              </button>
            </div>
          </div>
        </div>

        {/* 3. RIGHT NARROW TIMELINE HISTOGRAM */}
        <aside className="w-48 bg-[#1e293b] border-l border-[#39445a]/60 flex flex-col justify-between shrink-0 font-mono text-[11px]">
          <div className="p-3 border-b border-[#39445a]/60 text-right">
            <div className="font-bold text-white font-mono text-xs">{(75432 + terminalLogs.length - 38).toLocaleString()} Results</div>
            <div className="text-[10px] text-[#718096]">3 hours</div>
          </div>

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
                <span className="text-[9px] text-[#718096] shrink-0">{bucket.time}</span>
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

            {/* Purple Selection Overlay Box */}
            <div
              className="absolute left-1 right-1 p-2 rounded bg-[#2a244d]/90 border border-[#8b5cf6] shadow-xl"
              style={{ top: '36%' }}
            >
              <div className="text-[9px] text-white font-bold leading-tight">Tue Dec 29 12:54:00 pm</div>
              <div className="text-[9px] text-[#cbd5e1] font-bold leading-tight">+ Tue Dec 29 12:58:00 pm</div>
              <div className="text-[10px] text-[#8b5cf6] font-bold mt-1">
                8,321 Results
              </div>
              <div className="relative w-full h-1 bg-[#8b5cf6] rounded-full mt-1.5">
                <span className="absolute -top-1 right-3 w-3 h-3 rounded-full bg-[#8b5cf6] border-2 border-white shadow-md"></span>
              </div>
            </div>
          </div>

          <div className="p-2 border-t border-[#39445a]/60 text-[9px] text-[#718096] text-center">
            DRISHTI Tail Engine // 8001
          </div>
        </aside>

      </div>
    </div>
  );
}
