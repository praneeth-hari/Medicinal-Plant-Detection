import React, { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Activity,
  Cpu,
  Coins,
  GitBranch,
  Play,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Database,
  Sparkles,
  Clock,
  Server,
  Terminal,
  RefreshCw,
  Sliders,
  Check,
  Cloud,
  ExternalLink,
  UploadCloud,
} from 'lucide-react';
import { getSettings, updateSettings, getStats, getAuditLogs } from '../api/controlTower';
import { useToast } from '../hooks/useToast';
import apiClient from '../api/client';

export default function ControlTower() {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState('visibility');
  const [settings, setSettings] = useState({
    pii_masking: false,
    dosage_disclaimer: true,
    toxicity_guardrail: true,
    source_verification: true,
  });
  const [stats, setStats] = useState({
    cpu_usage: 0,
    memory_usage: 0,
    active_sessions: 0,
    db_health: 'Healthy',
    ollama_availability: 'Available',
    total_queries: 0,
    avg_latency_ms: 0,
    latency_history: [],
    token_history: [],
  });
  const [auditLogs, setAuditLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Visibility simulation logs
  const [simLogs, setSimLogs] = useState([
    { time: new Date().toLocaleTimeString(), type: 'system', message: 'AI Control Tower dashboard initialized' },
    { time: new Date().toLocaleTimeString(), type: 'info', message: 'All 5 active agents report nominal status' },
  ]);

  // CMDB state
  const [cmdbCIs, setCmdbCIs]             = useState([]);
  const [cmdbConnected, setCmdbConnected] = useState(false);
  const [cmdbSyncing, setCmdbSyncing]     = useState(false);
  const [cmdbLoading, setCmdbLoading]     = useState(false);
  const [cmdbLastSync, setCmdbLastSync]   = useState('');
  const [cmdbError, setCmdbError]         = useState('');

  const loadCmdb = async () => {
    setCmdbLoading(true);
    setCmdbError('');
    try {
      const res = await apiClient.get('/cmdb/status');
      setCmdbConnected(res.data.connected);
      setCmdbCIs(res.data.cis || []);
      if (!res.data.connected) setCmdbError(res.data.error || 'Not connected');
    } catch (e) {
      setCmdbConnected(false);
      setCmdbError('Failed to reach CMDB endpoint');
    } finally {
      setCmdbLoading(false);
    }
  };

  const handleCmdbSync = async () => {
    setCmdbSyncing(true);
    try {
      const res = await apiClient.post('/cmdb/sync');
      if (res.data.success) {
        addToast(`Synced ${res.data.synced}/${res.data.total} CIs to ServiceNow`, 'success');
        setCmdbLastSync(new Date().toLocaleTimeString());
        await loadCmdb();
      } else {
        addToast(res.data.error || 'Sync failed', 'error');
      }
    } catch (e) {
      addToast('ServiceNow sync failed', 'error');
    } finally {
      setCmdbSyncing(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'cmdb') loadCmdb();
  }, [activeTab]);

  // Projected Requests Slider state
  const [projectedRequests, setProjectedRequests] = useState(5000);

  // Coordination tab state
  const [flowStep, setFlowStep] = useState(0);
  const [flowLog, setFlowLog] = useState([]);
  const [isPlayingFlow, setIsPlayingFlow] = useState(false);

  // Load stats, settings, audit logs
  const loadData = async () => {
    try {
      setIsLoading(true);
      const [settingsData, statsData, logsData] = await Promise.all([
        getSettings(),
        getStats(),
        getAuditLogs(),
      ]);
      setSettings(settingsData);
      setStats(statsData);
      setAuditLogs(logsData);
    } catch (err) {
      console.error('Error fetching Control Tower data:', err);
      addToast('Failed to connect to Control Tower backend', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Poll stats and audit logs every 8 seconds when dashboard is open
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const [statsData, logsData] = await Promise.all([
          getStats(),
          getAuditLogs(),
        ]);
        setStats(statsData);
        setAuditLogs(logsData);
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  // Live simulation log append (Visibility tab)
  useEffect(() => {
    const logInterval = setInterval(() => {
      if (activeTab !== 'visibility') return;
      const agents = [
        'Image Classifier Agent',
        'RAG Retriever Agent',
        'PII Sanitization Agent',
        'Toxicity Guardrail',
        'Dosage Disclaimer Verifier',
      ];
      const messages = [
        'Heartbeat checked: Status NOMINAL',
        'Verified index node list. Clean (147 vectors)',
        'Cache hits: 92% latency coverage',
        'Inspecting compliance policies... Pass',
        'Processed client request. No toxicity flags triggered',
        'System resources within baseline ranges',
      ];
      const randomAgent = agents[Math.floor(Math.random() * agents.length)];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      setSimLogs((prev) => [
        { time: new Date().toLocaleTimeString(), type: 'agent', message: `[${randomAgent}] ${randomMessage}` },
        ...prev.slice(0, 19),
      ]);
    }, 4000);
    return () => clearInterval(logInterval);
  }, [activeTab]);

  const handleToggle = async (policyKey) => {
    const updated = {
      ...settings,
      [policyKey]: !settings[policyKey],
    };
    setSettings(updated);
    try {
      setIsSaving(true);
      await updateSettings(updated);
      addToast(`Policy "${policyKey.replace('_', ' ').toUpperCase()}" updated`, 'success');
      // reload audit logs to see any quick adjustments
      const logsData = await getAuditLogs();
      setAuditLogs(logsData);
    } catch (err) {
      console.error(err);
      addToast('Failed to save settings changes', 'error');
      // Rollback
      setSettings(settings);
    } finally {
      setIsSaving(false);
    }
  };

  // Coordination: Step-by-step dry run animation
  const runCoordinationTest = () => {
    if (isPlayingFlow) return;
    setIsPlayingFlow(true);
    setFlowStep(1);
    setFlowLog(['[1] Initiating flow test client request...']);

    const steps = [
      'PII sanitization & toxicity filters run on message text...',
      'Retrieving semantically matched plant information nodes from Vector Store...',
      'Injecting retrieved plant text and history into LLM prompt synthesizer...',
      'Applying clinical safety and dosage validation policies...',
      'Flow test response successfully compiled! Generating payload.',
    ];

    let current = 1;
    const interval = setInterval(() => {
      current += 1;
      setFlowStep(current);
      setFlowLog((prev) => [...prev, `[${current}] ${steps[current - 2]}`]);

      if (current === 6) {
        clearInterval(interval);
        setIsPlayingFlow(false);
        addToast('Agent workflow pipeline simulation completed successfully!', 'success');
      }
    }, 2000);
  };

  // Slider optimization metrics calculations
  const calculateCosts = () => {
    const localCost = 10; // Hardware/power flat rate
    // Gemini cost structure: 0.0035 average per RAG query (both tokens included)
    const geminiCost = Number((projectedRequests * 0.0035).toFixed(2));
    const tokenThroughput = projectedRequests * 380; // Avg 380 tokens per message
    return { localCost, geminiCost, tokenThroughput };
  };

  const { localCost, geminiCost, tokenThroughput } = calculateCosts();

  const getOptimizationAdvice = () => {
    if (projectedRequests < 3000) {
      return {
        level: 'Ollama cost-effective',
        advice: 'Ollama is highly cost-effective at this level. Turn on local prompt caching to reduce startup overhead by 40%.',
        cachingAction: 'Apply Local Prompt Cache',
      };
    } else if (projectedRequests >= 3000 && projectedRequests < 15000) {
      return {
        level: 'Hybrid Recommended',
        advice: 'Moderate workload detects local queues. We suggest Hybrid Routing (use local Ollama for basic queries, route complex cases to Gemini API).',
        cachingAction: 'Apply Hybrid Router Config',
      };
    } else {
      return {
        level: 'Cloud Escalation Warning',
        advice: 'CRITICAL: High volume creates heavy queue bottlenecks on local hardware. Cloud Gemini API with redis vector cache is recommended to ensure <500ms latency.',
        cachingAction: 'Provision Redis Vector Cache',
      };
    }
  };

  const adviceObj = getOptimizationAdvice();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh]">
        <RefreshCw className="w-10 h-10 text-primary-500 animate-spin mb-4" />
        <p className="text-surface-600 dark:text-surface-400 font-medium animate-pulse">Loading AI Control Tower telemetry...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-2">
      {/* Header Banner */}
      <div className="relative glass p-6 rounded-3xl overflow-hidden border border-white/10 dark:border-white/5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Decorative background glow */}
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-primary-500/10 to-accent-500/5 blur-3xl -z-10" />

        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-primary-500/10 dark:bg-primary-500/20 border border-primary-500/30 flex items-center justify-center text-primary-600 dark:text-primary-400">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-650 to-accent-500 bg-clip-text text-transparent">AI Control Tower</h1>
            <p className="text-sm text-surface-600 dark:text-surface-400 mt-0.5">
              Multi-agent coordination, governance toggles, real-time query compliance audits, and performance telemetry.
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 border border-white/10 dark:border-white/5 bg-white/5 hover:bg-white/10 rounded-xl text-sm font-semibold transition-all hover:scale-[1.02]"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Stats
        </button>
      </div>

      {/* Control Tabs Pill Selector */}
      <div className="flex flex-wrap gap-2 p-1.5 glass rounded-2xl border border-white/10 dark:border-white/5 max-w-2xl">
        {[
          { id: 'visibility', label: 'Visibility', icon: Activity },
          { id: 'governance', label: 'Governance', icon: Shield },
          { id: 'monitoring', label: 'Monitoring', icon: Cpu },
          { id: 'optimization', label: 'Optimization', icon: Coins },
          { id: 'coordination', label: 'Coordination', icon: GitBranch },
          { id: 'cmdb', label: 'CMDB', icon: Cloud },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-xl transition-all duration-300 ${
                activeTab === tab.id
                  ? 'bg-primary-500/20 text-primary-700 dark:text-primary-300 shadow-glow-sm border border-primary-500/20'
                  : 'text-surface-600 dark:text-surface-400 hover:bg-white/5 hover:text-surface-800 dark:hover:text-surface-250'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div className="transition-all duration-300">
        
        {/* ==================== TAB 1: VISIBILITY ==================== */}
        {activeTab === 'visibility' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Grid of registered Agents */}
            <div className="lg:col-span-2 space-y-6">
              <div className="glass-card">
                <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 mb-4 flex items-center gap-2">
                  <Server className="w-5 h-5 text-primary-500" />
                  Active AI Agents Registry
                </h3>
                <div className="space-y-4">
                  {[
                    { name: 'RAG Knowledge Synthesizer', desc: 'Queries FAISS vector db and formats clinical answers using local Llama 3 context.', role: 'Response Generator', status: 'Active' },
                    { name: 'Image Classification Core', desc: 'Identifies medicinal plant family, class, and features from client uploaded photos.', role: 'ML Pipeline', status: 'Active' },
                    { name: 'Toxicity Guardrail Agent', desc: 'Evaluates questions against abuse taxonomy list and triggers automated block.', role: 'Safety Filter', status: 'Active' },
                    { name: 'PII Sanitization Gateway', desc: 'Recognizes phone numbers, emails, and patient ids to mask before prompt indexing.', role: 'Compliance filter', status: 'Active' },
                    { name: 'Dosage Policy Auditor', desc: 'Appends strict clinical cautions when preparing home remedies is requested.', role: 'Safety Audit', status: 'Idle' },
                  ].map((agent, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-xl border border-white/5 bg-white/5 dark:bg-white/3 flex items-start justify-between gap-4 hover:border-primary-500/30 transition-all duration-200"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-surface-800 dark:text-surface-150">{agent.name}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-white/10 dark:bg-white/5 text-surface-500">{agent.role}</span>
                        </div>
                        <p className="text-xs text-surface-550 dark:text-surface-400 leading-relaxed">{agent.desc}</p>
                      </div>
                      
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={`w-2.5 h-2.5 rounded-full ${agent.status === 'Active' ? 'bg-emerald-500 animate-ping' : 'bg-amber-500'}`} />
                        <span className="text-xs font-bold text-surface-600 dark:text-surface-400">{agent.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Live activity log terminal */}
            <div className="glass-card flex flex-col h-[520px]">
              <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 mb-3 flex items-center gap-2">
                <Terminal className="w-5 h-5 text-accent-500" />
                Live Agent Operations Stream
              </h3>
              <p className="text-xs text-surface-650 dark:text-surface-400 mb-4">
                Real-time activity logs streaming from the active agent pipelines in the background.
              </p>

              <div className="flex-1 bg-neutral-950/80 rounded-xl p-4 font-mono text-xs text-emerald-400 overflow-y-auto space-y-2.5 border border-white/5 shadow-inner">
                {simLogs.map((log, index) => (
                  <div key={index} className="flex items-start gap-2 animate-fadeIn">
                    <span className="text-neutral-600 font-semibold flex-shrink-0">{log.time}</span>
                    <span className={`px-1.5 py-0.2 rounded text-[10px] uppercase font-bold flex-shrink-0 ${log.type === 'system' ? 'bg-neutral-800 text-neutral-400' : 'bg-primary-900/60 text-primary-300'}`}>
                      {log.type}
                    </span>
                    <span className="text-neutral-200 leading-relaxed break-all">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* ==================== TAB 2: GOVERNANCE ==================== */}
        {activeTab === 'governance' && (
          <div className="space-y-6">
            
            {/* Policy Toggles Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { key: 'pii_masking', label: 'PII Masking', desc: 'Masks emails, mobile contacts, and health record Patient IDs to protect client privacy in vector store prompts.', badge: 'Input safety' },
                { key: 'dosage_disclaimer', label: 'Dosage Disclaimer', desc: 'Automatically appends legal healthcare disclaimers to answers detailing plant preparation recipes.', badge: 'Liability protect' },
                { key: 'toxicity_guardrail', label: 'Toxicity Guardrail', desc: 'Stops malicious queries (e.g. poison, abuse instructions) and yields a safe blocked system alert.', badge: 'Abuse prevent' },
                { key: 'source_verification', label: 'Source Verification', desc: 'Flags responses generated by the model if they contain no cited references or scientific documents.', badge: 'Fact-checking' },
              ].map((policy) => (
                <div key={policy.key} className="glass p-5 rounded-2xl flex flex-col justify-between border border-white/10 dark:border-white/5 space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-primary-500 bg-primary-500/10 px-2 py-0.5 rounded-full">{policy.badge}</span>
                      {isSaving && <RefreshCw className="w-3.5 h-3.5 text-neutral-400 animate-spin" />}
                    </div>
                    <h4 className="font-bold text-surface-800 dark:text-surface-150">{policy.label}</h4>
                    <p className="text-xs text-surface-600 dark:text-surface-400 leading-relaxed">{policy.desc}</p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-white/5">
                    <span className="text-xs font-bold text-surface-650 dark:text-surface-450">
                      {settings[policy.key] ? 'ENABLED' : 'DISABLED'}
                    </span>
                    <button
                      onClick={() => handleToggle(policy.key)}
                      disabled={isSaving}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-250 ease-in-out focus:outline-none ${
                        settings[policy.key] ? 'bg-primary-500' : 'bg-neutral-600 dark:bg-neutral-800'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-250 ease-in-out ${
                          settings[policy.key] ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Audit Logs Table */}
            <div className="glass-card">
              <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <div>
                  <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-primary-500" />
                    Query Compliance Audit Trail
                  </h3>
                  <p className="text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                    Logging client RAG queries and showing policy enforcement audits in real-time.
                  </p>
                </div>
                <div className="text-xs font-semibold px-3 py-1 bg-white/10 dark:bg-white/5 rounded-lg text-surface-600 dark:text-surface-450 border border-white/5">
                  Total Audited: {auditLogs.length} entries
                </div>
              </div>

              <div className="overflow-x-auto rounded-xl border border-white/5">
                <table className="min-w-full divide-y divide-white/5 bg-white/3 text-left">
                  <thead className="bg-white/5 text-xs font-bold text-surface-700 dark:text-surface-300 uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-4">Timestamp</th>
                      <th className="px-6 py-4">User Query</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Policies Checked</th>
                      <th className="px-6 py-4">Compliance Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-xs text-surface-800 dark:text-surface-350 font-medium">
                    {auditLogs.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="px-6 py-12 text-center text-surface-600 dark:text-surface-450 font-semibold">
                          No query audit records found. Ask the RAG assistant a question to populate this trail.
                        </td>
                      </tr>
                    ) : (
                      auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-white/3 transition-colors duration-150">
                          <td className="px-6 py-4 text-surface-600 dark:text-surface-400 whitespace-nowrap">
                            {new Date(log.timestamp).toLocaleTimeString()}{' '}
                            <span className="text-[10px] block opacity-70">
                              {new Date(log.timestamp).toLocaleDateString()}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-mono max-w-xs truncate" title={log.user_query}>
                            {log.masked_query ? (
                              <span className="text-primary-600 dark:text-primary-450" title={`Original: ${log.user_query}`}>
                                🛡️ {log.masked_query}
                              </span>
                            ) : (
                              log.user_query
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                                log.compliance_status === 'PASSED'
                                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                                  : log.compliance_status === 'WARNING'
                                  ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                                  : 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20'
                              }`}
                            >
                              {log.compliance_status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1.5">
                              {log.policies_applied.map((p, index) => (
                                <span key={index} className="px-2 py-0.5 bg-white/10 dark:bg-white/5 rounded text-[10px] text-surface-650 dark:text-surface-400">
                                  {p}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-surface-650 dark:text-surface-400 leading-normal max-w-sm truncate" title={log.details || 'Passed checks'}>
                            {log.details || '✓ Compliant with safety policies.'}
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

        {/* ==================== TAB 3: MONITORING ==================== */}
        {activeTab === 'monitoring' && (
          <div className="space-y-6">
            
            {/* System Resource Gauges */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              <div className="glass-card flex flex-col items-center justify-center text-center p-8 space-y-4">
                <h4 className="font-bold text-surface-700 dark:text-surface-200">CPU Usage Baseline</h4>
                <div className="relative w-36 h-36 flex items-center justify-center">
                  {/* SVG Circle Gauge */}
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="72" cy="72" r="58" strokeWidth="8" stroke="rgba(255,255,255,0.05)" fill="transparent" />
                    <circle
                      cx="72"
                      cy="72"
                      r="58"
                      strokeWidth="8"
                      stroke="url(#cpuGrad)"
                      fill="transparent"
                      strokeDasharray={364}
                      strokeDashoffset={364 - (364 * stats.cpu_usage) / 100}
                      className="transition-all duration-1000 ease-out"
                    />
                    <defs>
                      <linearGradient id="cpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22c55e" />
                        <stop offset="100%" stopColor="#84cc16" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-extrabold text-surface-850 dark:text-white">{stats.cpu_usage}%</span>
                    <span className="text-[10px] text-surface-500 font-bold uppercase tracking-wider">Active load</span>
                  </div>
                </div>
                <p className="text-xs text-surface-600 dark:text-surface-450 leading-normal">
                  Real-time processing footprint across core backend servers.
                </p>
              </div>

              <div className="glass-card flex flex-col items-center justify-center text-center p-8 space-y-4">
                <h4 className="font-bold text-surface-700 dark:text-surface-200">System Memory Alloc</h4>
                <div className="relative w-36 h-36 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="72" cy="72" r="58" strokeWidth="8" stroke="rgba(255,255,255,0.05)" fill="transparent" />
                    <circle
                      cx="72"
                      cy="72"
                      r="58"
                      strokeWidth="8"
                      stroke="url(#memGrad)"
                      fill="transparent"
                      strokeDasharray={364}
                      strokeDashoffset={364 - (364 * stats.memory_usage) / 100}
                      className="transition-all duration-1000 ease-out"
                    />
                    <defs>
                      <linearGradient id="memGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22c55e" />
                        <stop offset="100%" stopColor="#06b6d4" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-extrabold text-surface-850 dark:text-white">{stats.memory_usage}%</span>
                    <span className="text-[10px] text-surface-500 font-bold uppercase tracking-wider">Allocated RAM</span>
                  </div>
                </div>
                <p className="text-xs text-surface-600 dark:text-surface-450 leading-normal">
                  Vector cache footprint and inference weights in RAM buffer.
                </p>
              </div>

              {/* Service Health Grid */}
              <div className="glass p-6 rounded-2xl flex flex-col justify-between border border-white/10 dark:border-white/5 space-y-4">
                <h4 className="font-bold text-surface-800 dark:text-surface-150">Subservice Connectivity</h4>
                <div className="space-y-3 flex-1 flex flex-col justify-center">
                  {[
                    { name: 'SQLite DB Server', health: stats.db_health === 'Healthy', latency: '2ms' },
                    { name: 'Ollama Pipeline', health: stats.ollama_availability === 'Available', latency: '24ms' },
                    { name: 'FAISS Vectors Index', health: true, latency: '1ms' },
                    { name: 'FastAPI Web Core', health: true, latency: '14ms' },
                  ].map((srv, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 border border-white/3 text-xs">
                      <div className="flex items-center gap-2 font-semibold text-surface-800 dark:text-surface-200">
                        {srv.health ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-500" />
                        )}
                        {srv.name}
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white/10 text-surface-600 dark:text-surface-400">
                        {srv.latency}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Performance charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* SVG latency chart */}
              <div className="glass-card space-y-4">
                <div>
                  <h4 className="font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-primary-500" />
                    Average Chat Latency (ms)
                  </h4>
                  <p className="text-[10px] text-surface-550 dark:text-surface-400 mt-0.5">
                    Live system latency (ms) per query exchange (recent history).
                  </p>
                </div>
                
                <div className="h-44 w-full relative">
                  {stats.latency_history.length > 0 ? (
                    <svg className="w-full h-full" viewBox="0 0 100 35" preserveAspectRatio="none">
                      {/* Grid lines */}
                      <line x1="0" y1="10" x2="100" y2="10" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      <line x1="0" y1="20" x2="100" y2="20" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      <line x1="0" y1="30" x2="100" y2="30" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      
                      {/* Latency line */}
                      <path
                        d={`M ${stats.latency_history.map((val, idx) => `${(idx * 100) / 9} ${35 - (val * 30) / 600}`).join(' L ')}`}
                        fill="none"
                        stroke="#22c55e"
                        strokeWidth="1.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      
                      {/* Gradient area */}
                      <path
                        d={`M 0 35 L ${stats.latency_history.map((val, idx) => `${(idx * 100) / 9} ${35 - (val * 30) / 600}`).join(' L ')} L 100 35 Z`}
                        fill="url(#latencyAreaGrad)"
                      />
                      
                      <defs>
                        <linearGradient id="latencyAreaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#22c55e" stopOpacity="0.2" />
                          <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
                        </linearGradient>
                      </defs>
                    </svg>
                  ) : (
                    <div className="flex items-center justify-center h-full text-xs text-neutral-500 font-semibold">No telemetry history</div>
                  )}
                </div>
                <div className="flex justify-between items-center text-[10px] text-surface-500 font-bold border-t border-white/5 pt-2">
                  <span>Current: {stats.avg_latency_ms}ms</span>
                  <span>Baseline: 340ms</span>
                </div>
              </div>

              {/* SVG token chart */}
              <div className="glass-card space-y-4">
                <div>
                  <h4 className="font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-accent-500" />
                    Model Token Throughput
                  </h4>
                  <p className="text-[10px] text-surface-550 dark:text-surface-400 mt-0.5">
                    Count of prompt & answer tokens synthesized per chat turn.
                  </p>
                </div>
                
                <div className="h-44 w-full relative">
                  {stats.token_history.length > 0 ? (
                    <svg className="w-full h-full" viewBox="0 0 100 35" preserveAspectRatio="none">
                      <line x1="0" y1="10" x2="100" y2="10" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      <line x1="0" y1="20" x2="100" y2="20" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      <line x1="0" y1="30" x2="100" y2="30" stroke="rgba(255,255,255,0.05)" strokeWidth="0.2" />
                      
                      {/* Token throughput bar chart */}
                      {stats.token_history.map((val, idx) => (
                        <rect
                          key={idx}
                          x={(idx * 100) / 10 + 2}
                          y={35 - (val * 30) / 500}
                          width="5"
                          height={(val * 30) / 500}
                          fill="url(#tokenBarGrad)"
                          rx="1"
                        />
                      ))}
                      
                      <defs>
                        <linearGradient id="tokenBarGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#06b6d4" />
                          <stop offset="100%" stopColor="#22c55e" />
                        </linearGradient>
                      </defs>
                    </svg>
                  ) : (
                    <div className="flex items-center justify-center h-full text-xs text-neutral-500 font-semibold">No telemetry history</div>
                  )}
                </div>
                <div className="flex justify-between items-center text-[10px] text-surface-500 font-bold border-t border-white/5 pt-2">
                  <span>Peak turn: 420 tokens</span>
                  <span>Monthly Accum: {(stats.total_queries * 380).toLocaleString()} tokens</span>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ==================== TAB 4: OPTIMIZATION ==================== */}
        {activeTab === 'optimization' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Projected request calculator */}
            <div className="lg:col-span-2 space-y-6">
              <div className="glass-card space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                    <Sliders className="w-5 h-5 text-primary-500" />
                    Query Volume Optimizer & Price Calculator
                  </h3>
                  <p className="text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                    Adjust the monthly traffic volume slider to project infrastructure costs and view model recommendations.
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-surface-700 dark:text-surface-300">Projected Queries / Month</span>
                    <span className="text-xl font-extrabold text-primary-600 dark:text-primary-400">{projectedRequests.toLocaleString()} queries</span>
                  </div>
                  <input
                    type="range"
                    min="100"
                    max="50000"
                    step="100"
                    value={projectedRequests}
                    onChange={(e) => setProjectedRequests(Number(e.target.value))}
                    className="w-full accent-primary-500 bg-neutral-250 dark:bg-neutral-800 h-2 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-surface-500 font-bold">
                    <span>100 q/mo</span>
                    <span>10,000 q/mo</span>
                    <span>25,000 q/mo</span>
                    <span>50,000 q/mo</span>
                  </div>
                </div>

                {/* Costs Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-white/5">
                  <div className="p-4 rounded-xl bg-white/5 border border-white/3 text-center">
                    <span className="text-[10px] font-bold text-surface-500 uppercase">Token Throughput</span>
                    <h4 className="text-lg font-extrabold text-surface-800 dark:text-surface-150 mt-1">{tokenThroughput.toLocaleString()}</h4>
                    <p className="text-[10px] text-surface-600 dark:text-surface-400 mt-1">tokens projected / mo</p>
                  </div>
                  
                  <div className="p-4 rounded-xl bg-white/5 border border-white/3 text-center">
                    <span className="text-[10px] font-bold text-surface-500 uppercase">Local Ollama setup</span>
                    <h4 className="text-lg font-extrabold text-emerald-500 mt-1">${localCost} / mo</h4>
                    <p className="text-[10px] text-surface-600 dark:text-surface-400 mt-1">Flat hardware power cost</p>
                  </div>

                  <div className="p-4 rounded-xl bg-white/5 border border-white/3 text-center">
                    <span className="text-[10px] font-bold text-surface-500 uppercase">Cloud Gemini API</span>
                    <h4 className="text-lg font-extrabold text-cyan-500 mt-1">${geminiCost} / mo</h4>
                    <p className="text-[10px] text-surface-600 dark:text-surface-400 mt-1">Pay-as-you-go billing</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Advice panel */}
            <div className="glass-card flex flex-col justify-between space-y-6">
              <div className="space-y-4">
                <span className="text-xs font-bold text-primary-500 bg-primary-500/10 px-2 py-0.5 rounded-full inline-block">
                  {adviceObj.level}
                </span>
                <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-500" />
                  Efficiency Optimizer Suggestions
                </h3>
                <p className="text-xs text-surface-600 dark:text-surface-400 leading-relaxed">
                  {adviceObj.advice}
                </p>
              </div>

              <div className="space-y-3 pt-4 border-t border-white/5">
                <button
                  onClick={() => {
                    addToast(`Optimization applied: ${adviceObj.cachingAction}`, 'success');
                  }}
                  className="w-full btn-primary text-xs py-3 flex items-center justify-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  {adviceObj.cachingAction}
                </button>
                <p className="text-[10px] text-center text-surface-500 font-bold leading-normal">
                  Reduces processing overhead and keeps tokens/second throughput nominal.
                </p>
              </div>
            </div>

          </div>
        )}

        {/* ==================== TAB 5: COORDINATION ==================== */}
        {activeTab === 'coordination' && (
          <div className="space-y-6">
            
            {/* Visual flowchart canvas */}
            <div className="glass-card space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="text-lg font-bold text-surface-800 dark:text-surface-100 flex items-center gap-2">
                    <GitBranch className="w-5 h-5 text-primary-500" />
                    Agent Workflow Orchestrator (Pipeline)
                  </h3>
                  <p className="text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                    Interactive pipeline flow path mapping user query ingestion, database vector retrievals, guardrail logic, and LLM text synthesizer.
                  </p>
                </div>

                <button
                  onClick={runCoordinationTest}
                  disabled={isPlayingFlow}
                  className="btn-primary text-xs py-2 flex items-center gap-2 transition-all hover:scale-[1.02]"
                >
                  <Play className="w-3.5 h-3.5" />
                  {isPlayingFlow ? 'Running flow test...' : 'Run Flow Test'}
                </button>
              </div>

              {/* Graphical nodes */}
              <div className="p-8 bg-neutral-950/40 rounded-2xl border border-white/5 flex flex-col md:flex-row items-center justify-between gap-6 overflow-x-auto relative min-h-[160px]">
                
                {/* Visual Connection line highlight */}
                {isPlayingFlow && (
                  <div
                    className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-emerald-500 via-accent-500 to-cyan-500 rounded-full transition-all duration-1000 -translate-y-1/2 -z-10 shadow-glow"
                    style={{
                      width: `${((flowStep - 1) * 100) / 4}%`,
                      maxWidth: '100%',
                    }}
                  />
                )}

                {[
                  { step: 1, label: 'User Query Ingest', icon: Terminal, color: 'border-neutral-500 text-neutral-400' },
                  { step: 2, label: 'Governance Guardrails', icon: Shield, color: 'border-primary-500 text-primary-500' },
                  { step: 3, label: 'Vector DB Search', icon: Database, color: 'border-emerald-500 text-emerald-500' },
                  { step: 4, label: 'LLM Response Synthesize', icon: Sparkles, color: 'border-cyan-500 text-cyan-500' },
                  { step: 5, label: 'Final Output Client', icon: CheckCircle2, color: 'border-lime-500 text-lime-500' },
                ].map((node) => {
                  const NodeIcon = node.icon;
                  const isCurrent = flowStep === node.step;
                  const isCompleted = flowStep > node.step;
                  
                  return (
                    <div
                      key={node.step}
                      className={`relative z-10 flex flex-col items-center text-center p-4 rounded-xl border-2 glass bg-neutral-900/90 w-44 transition-all duration-300 ${
                        isCurrent
                          ? 'border-primary-500 shadow-glow scale-[1.06] bg-primary-950/20'
                          : isCompleted
                          ? 'border-emerald-500 shadow-glow-sm'
                          : 'border-white/10 opacity-70'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 border-dashed mb-2 ${
                        isCurrent ? 'animate-bounce border-primary-500' : isCompleted ? 'border-emerald-500 text-emerald-500' : 'border-white/20'
                      }`}>
                        <NodeIcon className="w-5 h-5" />
                      </div>
                      <span className="text-xs font-bold text-surface-200">{node.label}</span>
                      <span className="text-[10px] text-surface-500 font-bold uppercase mt-1">
                        {isCurrent ? 'PROCESSING' : isCompleted ? 'SUCCESS' : 'PENDING'}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Coordination dry-run steps logging console */}
              <div className="bg-neutral-950/75 rounded-xl p-4 border border-white/5 h-44 overflow-y-auto space-y-2">
                <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest block mb-2">Workflow Trace Log</span>
                {flowLog.length === 0 ? (
                  <p className="text-xs text-neutral-500 font-medium">Click "Run Flow Test" above to trigger and trace the workflow execution steps.</p>
                ) : (
                  flowLog.map((logStr, i) => (
                    <p key={i} className="text-xs font-mono text-emerald-400 animate-fadeIn">{logStr}</p>
                  ))
                )}
              </div>
            </div>

          </div>
        )}

        {/* ==================== TAB 6: CMDB ==================== */}
        {activeTab === 'cmdb' && (
          <div className="space-y-6">

            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-surface-900 dark:text-white flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-primary-500" /> ServiceNow CMDB Integration
                </h2>
                <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">
                  Instance: <span className="font-mono text-primary-600 dark:text-primary-400">https://dev390109.service-now.com</span>
                </p>
              </div>
              <div className="flex items-center gap-3">
                {cmdbLastSync && (
                  <span className="text-[10px] text-surface-400 font-mono">Last sync: {cmdbLastSync}</span>
                )}
                <button
                  onClick={loadCmdb}
                  disabled={cmdbLoading}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold border border-surface-200 dark:border-white/10 hover:bg-surface-100 dark:hover:bg-white/5 text-surface-600 dark:text-surface-300 transition-all"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${cmdbLoading ? 'animate-spin' : ''}`} /> Refresh
                </button>
                <button
                  onClick={handleCmdbSync}
                  disabled={cmdbSyncing}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-primary-500 hover:bg-primary-600 text-white shadow-glow transition-all disabled:opacity-60"
                >
                  <UploadCloud className={`w-3.5 h-3.5 ${cmdbSyncing ? 'animate-bounce' : ''}`} />
                  {cmdbSyncing ? 'Syncing...' : 'Sync to ServiceNow'}
                </button>
              </div>
            </div>

            {/* Connection Status */}
            <div className={`flex items-center gap-3 p-4 rounded-2xl border ${
              cmdbConnected
                ? 'bg-emerald-500/5 border-emerald-500/20'
                : 'bg-red-500/5 border-red-500/20'
            }`}>
              <div className={`w-3 h-3 rounded-full ${cmdbConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
              <div>
                <p className="text-xs font-bold text-surface-900 dark:text-white">
                  {cmdbConnected ? 'Connected to ServiceNow' : 'Not Connected'}
                </p>
                {cmdbError && <p className="text-[10px] text-red-500 mt-0.5">{cmdbError}</p>}
              </div>
              {cmdbConnected && (
                <a
                  href="https://dev390109.service-now.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-auto flex items-center gap-1 text-[10px] text-primary-600 dark:text-primary-400 font-bold hover:underline"
                >
                  Open ServiceNow <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>

            {/* CI Table */}
            {cmdbLoading ? (
              <div className="flex items-center justify-center py-16">
                <RefreshCw className="w-6 h-6 text-primary-500 animate-spin mr-2" />
                <span className="text-xs text-surface-400">Loading CIs from ServiceNow...</span>
              </div>
            ) : cmdbCIs.length === 0 ? (
              <div className="text-center py-16 space-y-3">
                <Database className="w-10 h-10 text-surface-400 mx-auto opacity-40" />
                <p className="text-sm font-bold text-surface-600 dark:text-surface-400">No CIs registered yet</p>
                <p className="text-xs text-surface-400">Click "Sync to ServiceNow" to register MediPlant components as Configuration Items.</p>
              </div>
            ) : (
              <div className="overflow-hidden rounded-2xl border border-surface-200 dark:border-white/10">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-surface-100 dark:bg-white/5 border-b border-surface-200 dark:border-white/10">
                      <th className="text-left px-4 py-3 font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">CI Name</th>
                      <th className="text-left px-4 py-3 font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">Description</th>
                      <th className="text-left px-4 py-3 font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">Version</th>
                      <th className="text-left px-4 py-3 font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">Status</th>
                      <th className="text-left px-4 py-3 font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">Last Updated</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-200 dark:divide-white/5">
                    {cmdbCIs.map((ci) => (
                      <tr key={ci.sys_id} className="hover:bg-surface-50 dark:hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3 font-bold text-surface-900 dark:text-white">{ci.name}</td>
                        <td className="px-4 py-3 text-surface-500 dark:text-surface-400 max-w-[200px] truncate">{ci.description}</td>
                        <td className="px-4 py-3 font-mono text-surface-600 dark:text-surface-300">{ci.version}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                            ci.status === 'Operational'
                              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-400'
                              : 'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400'
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${ci.status === 'Operational' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                            {ci.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-surface-400 font-mono text-[10px]">{ci.last_updated || '—'}</td>
                        <td className="px-4 py-3">
                          <a
                            href={ci.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
                          >
                            View <ExternalLink className="w-3 h-3" />
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Registered CIs info */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { name: 'MediPlant AI App', key: 'mediplant_app' },
                { name: 'FastAPI Backend', key: 'fastapi_backend' },
                { name: 'ML Classifier', key: 'ml_classifier' },
                { name: 'SQLite Database', key: 'sqlite_db' },
                { name: 'ChromaDB Vector Store', key: 'chromadb' },
                { name: 'Groq LLM Integration', key: 'groq_api' },
              ].map((item) => {
                const registered = cmdbCIs.some(ci => ci.key === item.key);
                return (
                  <div key={item.key} className={`p-3 rounded-xl border flex items-center gap-2 ${
                    registered
                      ? 'border-emerald-500/20 bg-emerald-500/5'
                      : 'border-surface-200 dark:border-white/10 bg-surface-50 dark:bg-white/[0.02]'
                  }`}>
                    {registered
                      ? <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      : <XCircle className="w-4 h-4 text-surface-400 flex-shrink-0" />
                    }
                    <span className="text-xs font-semibold text-surface-700 dark:text-surface-300">{item.name}</span>
                  </div>
                );
              })}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
