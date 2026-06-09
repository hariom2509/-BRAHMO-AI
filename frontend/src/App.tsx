import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Settings, 
  RefreshCw, 
  RotateCcw, 
  Search, 
  Database, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface KnowledgeNode {
  id: string;
  org_id: string;
  type: 'CONSTRAINT' | 'DECISION' | 'ANTI_PATTERN' | 'FACT';
  title: string;
  content: string;
  importance: number;
  derivability_score: number;
  derivability_class: 'DERIVABLE' | 'PARTIALLY_DERIVABLE' | 'NON_DERIVABLE' | 'UNKNOWN';
  non_derivable_portion: string | null;
  expected_derivability: 'DERIVABLE' | 'PARTIALLY_DERIVABLE' | 'NON_DERIVABLE' | 'UNKNOWN';
  expected_score_range: string;
  department: string | null;
  tokens_full: number;
  tokens_delta: number;
  scoring_reason: string;
  type_floor_applied: boolean;
  never_exclude: boolean;
  confidence: string;
  created_at: string;
}

interface OrgConfig {
  derivability_threshold: number;
  type_floors: {
    CONSTRAINT: number;
    ANTI_PATTERN: number;
    DECISION: number;
    FACT: number;
  };
}

interface OrgInfo {
  id: string;
  name: string;
  config: OrgConfig;
}

export default function App() {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [org, setOrg] = useState<OrgInfo | null>(null);
  const [threshold, setThreshold] = useState<number>(0.7);
  const [algorithm, setAlgorithm] = useState<string>('hybrid');
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [classFilter, setClassFilter] = useState<string>('ALL');
  
  // Surprise test state
  const [surpriseContent, setSurpriseContent] = useState<string>('');
  const [surpriseType, setSurpriseType] = useState<string>('FACT');
  const [surpriseNeverExclude, setSurpriseNeverExclude] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testingNode, setTestingNode] = useState<boolean>(false);
  
  // UI toggles
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  // Use environment variable or fallback based on current origin (dev port 5173 -> local backend, other -> proxied relative path)
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 
    (window.location.origin.includes('localhost:5173') ? 'http://127.0.0.1:8000/api' : '/api');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Get org config
      const orgRes = await fetch(`${API_BASE}/org/supra`);
      if (!orgRes.ok) throw new Error("Failed to fetch organization settings");
      const orgData = await orgRes.json();
      setOrg(orgData);
      setThreshold(orgData.config.derivability_threshold);

      // Get knowledge nodes
      const nodesRes = await fetch(`${API_BASE}/nodes?org_id=supra`);
      if (!nodesRes.ok) throw new Error("Failed to fetch knowledge nodes");
      const nodesData = await nodesRes.json();
      setNodes(nodesData);
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleThresholdChange = async (val: number) => {
    setThreshold(val);
  };

  const handleThresholdRelease = async () => {
    if (!org) return;
    setActionLoading(true);
    try {
      // 1. Update config on backend
      const updateRes = await fetch(`${API_BASE}/org/supra/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          derivability_threshold: threshold,
          type_floors: org.config.type_floors
        })
      });
      if (!updateRes.ok) throw new Error("Failed to save config");

      // 2. Rescore all nodes automatically to reflect the new threshold
      const rescoreRes = await fetch(`${API_BASE}/rescore?org_id=supra`, {
        method: 'POST'
      });
      if (!rescoreRes.ok) throw new Error("Failed to rescore nodes");
      const updatedNodes = await rescoreRes.json();
      setNodes(updatedNodes);

      // 3. Update local org object
      setOrg(prev => prev ? {
        ...prev,
        config: { ...prev.config, derivability_threshold: threshold }
      } : null);

    } catch (err) {
      console.error("Error updating threshold:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRescore = async () => {
    setActionLoading(true);
    try {
      const res = await fetch(`${API_BASE}/rescore?org_id=supra`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error("Rescore failed");
      const updatedNodes = await res.json();
      setNodes(updatedNodes);
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async () => {
    setActionLoading(true);
    try {
      const seedRes = await fetch(`${API_BASE}/seed`, { method: 'POST' });
      if (!seedRes.ok) throw new Error("Seed failed");
      
      const rescoreRes = await fetch(`${API_BASE}/rescore?org_id=supra`, { method: 'POST' });
      const updatedNodes = await rescoreRes.json();
      
      const orgRes = await fetch(`${API_BASE}/org/supra`);
      const orgData = await orgRes.json();
      
      setOrg(orgData);
      setThreshold(orgData.config.derivability_threshold);
      setNodes(updatedNodes);
      setTestResult(null);
      setSurpriseContent('');
      setSurpriseNeverExclude(false);
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleTestSurpriseNode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!surpriseContent.trim()) return;
    setTestingNode(true);
    try {
      const res = await fetch(`${API_BASE}/test-node?org_id=supra`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: surpriseContent,
          type: surpriseType,
          never_exclude: surpriseNeverExclude
        })
      });
      if (!res.ok) throw new Error("Test failed");
      const data = await res.json();
      setTestResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setTestingNode(false);
    }
  };

  const toggleExpandNode = (id: string) => {
    setExpandedNodes(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // --- STATS CALCULATIONS ---
  const totalNodesCount = nodes.length;
  
  const tokenStats = nodes.reduce((acc, node) => {
    const full = node.tokens_full || 0;
    const delta = node.tokens_delta || 0;
    
    acc.total += full;
    
    if (node.derivability_class === 'DERIVABLE') {
      acc.saved += full;
      acc.included += 0;
      acc.derivableCount++;
    } else if (node.derivability_class === 'PARTIALLY_DERIVABLE') {
      acc.saved += (full - delta);
      acc.included += delta;
      acc.partialCount++;
    } else {
      acc.saved += 0;
      acc.included += full;
      acc.nonDerivableCount++;
    }
    
    return acc;
  }, { total: 0, saved: 0, included: 0, derivableCount: 0, partialCount: 0, nonDerivableCount: 0 });

  const savingsPercentage = tokenStats.total > 0 ? (tokenStats.saved / tokenStats.total) * 100 : 0;
  
  // Cost Saved per Session: assumes Claude 3.5 Sonnet / GPT-4o input cost is $15 per million tokens ($0.000015 / token)
  const costPerToken = 0.000015;
  const costSavedPerSession = tokenStats.saved * costPerToken;
  
  // Scale metrics: 500 engineers, 10 sessions/day, 250 working days/year (1.25M sessions/year)
  const scaleSessionsPerYear = 500 * 10 * 250;
  const annualSavings = costSavedPerSession * scaleSessionsPerYear;

  // --- VALIDATION MATRIX COMPUTATION ---
  // We evaluate against ground truth expected_derivability
  let truePositives = 0;   // Ground Truth: DERIVABLE & Scorer: DERIVABLE
  let falsePositives = 0;  // Ground Truth: NON_DERIVABLE & Scorer: DERIVABLE (CRITICAL FAIL)
  let trueNegatives = 0;   // Ground Truth: NON_DERIVABLE & Scorer: NON_DERIVABLE
  let falseNegatives = 0;  // Ground Truth: DERIVABLE & Scorer: NON_DERIVABLE (WASTED TOKENS)
  let truePartials = 0;    // Ground Truth: PARTIALLY_DERIVABLE & Scorer: PARTIALLY_DERIVABLE
  let borderlineCount = 0; // Other mismatches

  nodes.forEach(node => {
    const gt = node.expected_derivability;
    const computed = node.derivability_class;
    
    if (gt === 'DERIVABLE') {
      if (computed === 'DERIVABLE') truePositives++;
      else falseNegatives++;
    } else if (gt === 'NON_DERIVABLE') {
      if (computed === 'DERIVABLE') falsePositives++;
      else trueNegatives++;
    } else if (gt === 'PARTIALLY_DERIVABLE') {
      if (computed === 'PARTIALLY_DERIVABLE') truePartials++;
      else borderlineCount++;
    }
  });

  const precision = (truePositives + falsePositives) > 0 
    ? (truePositives / (truePositives + falsePositives)) * 100 
    : 100;
  
  const recall = (truePositives + falseNegatives) > 0 
    ? (truePositives / (truePositives + falseNegatives)) * 100 
    : 100;

  // --- FILTERS ---
  const filteredNodes = nodes.filter(node => {
    const matchesSearch = 
      node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      node.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      node.id.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesType = typeFilter === 'ALL' || node.type === typeFilter;
    const matchesClass = classFilter === 'ALL' || node.derivability_class === classFilter;
    
    return matchesSearch && matchesType && matchesClass;
  });

  const reviewNodes = nodes.filter(node => 
    !node.never_exclude && 
    (node.confidence === 'LOW' || (node.derivability_score >= 0.60 && node.derivability_score <= 0.80))
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* HEADER */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/10">
              <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center text-cyan-400 font-bold text-lg">
                B
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white">BRAHMO</h1>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
                  L2 rules engine check 5
                </span>
              </div>
              <p className="text-xs text-slate-400">Context Derivability Scorer • Healthcare Knowledge Infrastructure</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleRescore}
              disabled={actionLoading || loading}
              className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${actionLoading ? 'animate-spin' : ''}`} />
              Rescore All
            </button>
            <button
              onClick={handleReset}
              disabled={actionLoading || loading}
              className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg bg-slate-900 hover:bg-red-950/30 hover:text-red-400 text-slate-200 border border-slate-800 hover:border-red-900 disabled:opacity-50 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              Reset Seeding
            </button>
            <div className="h-6 w-[1px] bg-slate-800 mx-2" />
            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
              <Database className="h-3.5 w-3.5 text-emerald-500" />
              <span>DB: {loading ? '...' : (org ? 'Connected' : 'Disconnected')}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
        
        {/* TOP CONFIG BAR */}
        <section className="glass-panel rounded-2xl p-6 shadow-xl flex flex-col lg:flex-row items-center justify-between gap-8 border border-slate-900">
          <div className="flex-1 w-full flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <Settings className="h-4 w-4 text-cyan-400 animate-pulse" />
                Derivability Threshold
              </span>
              <span className="text-xl font-mono font-bold text-cyan-400 bg-cyan-950/30 px-3 py-1 rounded-lg border border-cyan-900/50">
                {threshold.toFixed(2)}
              </span>
            </div>
            <div className="flex items-center gap-4 w-full mt-2">
              <span className="text-xs text-slate-500 font-mono">0.0 (Exclude None)</span>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={threshold}
                onChange={(e) => handleThresholdChange(parseFloat(e.target.value))}
                onMouseUp={handleThresholdRelease}
                onTouchEnd={handleThresholdRelease}
                disabled={actionLoading}
                className="flex-1 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500 disabled:opacity-50"
              />
              <span className="text-xs text-slate-500 font-mono">1.0 (Exclude All)</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Nodes scoring above this threshold are classified as <b>DERIVABLE</b> and excluded from injected context, saving tokens.
            </p>
          </div>

          <div className="h-[1px] w-full lg:h-16 lg:w-[1px] bg-slate-900" />

          <div className="w-full lg:w-72 flex flex-col gap-2">
            <label className="text-sm font-semibold text-slate-300">Scoring Algorithm</label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="hybrid">(Recommended) Hybrid: Heuristics + TF-IDF</option>
              <option value="heuristics">Heuristics Only</option>
            </select>
            <p className="text-[10px] text-slate-500">
              Heuristic rules evaluate specific names, dates, metrics, and incident cases; TF-IDF checks similarity.
            </p>
          </div>
        </section>

        {/* METRICS & VALIDATION ROW */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* TOKEN SAVINGS SUMMARY */}
          <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-900 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-bold text-white tracking-wide flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-emerald-400" />
                  TOKEN SAVINGS SUMMARY
                </h2>
                <span className="text-xs px-2.5 py-1 rounded-lg bg-emerald-950/30 text-emerald-400 border border-emerald-900/40 font-semibold uppercase tracking-wider">
                  Active Stats
                </span>
              </div>

              {/* SAVINGS CIRCLE + KEY STATS */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center">
                
                {/* Visual Savings Percent */}
                <div className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-950 border border-slate-900 relative">
                  <span className="text-3xl font-mono font-black text-emerald-400">
                    {savingsPercentage.toFixed(1)}%
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase tracking-widest mt-1">Saved</span>
                  <div className="absolute inset-0 border border-emerald-500/10 rounded-xl pointer-events-none shadow-[inset_0_0_15px_rgba(16,185,129,0.02)]" />
                </div>
                
                {/* Text statistics */}
                <div className="sm:col-span-2 grid grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-900">
                    <p className="text-[10px] text-slate-400 uppercase tracking-wider">Total Context</p>
                    <p className="text-lg font-mono font-bold text-slate-200 mt-0.5">{tokenStats.total} tkn</p>
                  </div>
                  <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-900">
                    <p className="text-[10px] text-emerald-400 uppercase tracking-wider font-semibold">Tokens Saved</p>
                    <p className="text-lg font-mono font-bold text-emerald-400 mt-0.5">-{tokenStats.saved} tkn</p>
                  </div>
                </div>

              </div>

              {/* Node Classifications Breakdown */}
              <div className="mt-6 grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-lg bg-red-950/20 border border-red-900/30">
                  <span className="block text-red-400 font-bold text-sm">{tokenStats.derivableCount}</span>
                  <span className="text-[10px] text-slate-400 uppercase">Derivable</span>
                </div>
                <div className="p-2.5 rounded-lg bg-yellow-950/20 border border-yellow-900/30">
                  <span className="block text-yellow-400 font-bold text-sm">{tokenStats.partialCount}</span>
                  <span className="text-[10px] text-slate-400 uppercase">Partial</span>
                </div>
                <div className="p-2.5 rounded-lg bg-green-950/20 border border-green-900/30">
                  <span className="block text-green-400 font-bold text-sm">{tokenStats.nonDerivableCount}</span>
                  <span className="text-[10px] text-slate-400 uppercase">Non-Deriv</span>
                </div>
              </div>
            </div>

            {/* Financial Calculations */}
            <div className="mt-6 pt-6 border-t border-slate-900 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-400">Estimated Cost Saved / Session</p>
                <p className="text-xl font-bold font-mono text-emerald-400">${costSavedPerSession.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Annual Scaling Savings (500 Eng)</p>
                <p className="text-xl font-bold font-mono text-emerald-400">${annualSavings.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/yr</p>
              </div>
            </div>

          </div>

          {/* VALIDATION MATRIX */}
          <div className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-900 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-white tracking-wide flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  VALIDATION MATRIX (Accuracy Suite)
                </h2>
                <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 text-slate-400 border border-slate-800 font-mono">
                  30 Nodes Ground Truth
                </span>
              </div>

              {/* Warning about False Positives */}
              {falsePositives > 0 && (
                <div className="mb-4 p-3 bg-red-950/30 border border-red-900/50 rounded-xl flex items-start gap-3 text-xs text-red-400">
                  <AlertTriangle className="h-5 w-5 text-red-500 shrink-0 mt-0.5 animate-bounce" />
                  <div>
                    <span className="font-bold uppercase block mb-0.5">Critical Safety Hazard: {falsePositives} False Positive(s)</span>
                    The scorer classified organization-specific knowledge as DERIVABLE, which will exclude critical constraints. Recommend raising the threshold.
                  </div>
                </div>
              )}

              {/* Confusion Matrix Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-900">
                      <th className="py-2 text-slate-500 font-semibold">Predicted \ Actual</th>
                      <th className="py-2 text-red-400 font-semibold">GT: Derivable</th>
                      <th className="py-2 text-green-400 font-semibold">GT: Non-Derivable</th>
                      <th className="py-2 text-yellow-400 font-semibold">GT: Partial</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-900/50">
                      <td className="py-2.5 font-semibold text-slate-400">Scored DERIVABLE</td>
                      <td className="py-2.5">
                        <span className="text-emerald-400 font-mono font-bold">{truePositives}</span>
                        <span className="text-[10px] text-slate-500 block">True Pos (TP)</span>
                      </td>
                      <td className="py-2.5">
                        <span className={`font-mono font-bold ${falsePositives > 0 ? 'text-red-500' : 'text-slate-400'}`}>{falsePositives}</span>
                        <span className="text-[10px] text-slate-500 block">False Pos (FP)</span>
                      </td>
                      <td className="py-2.5 text-slate-500">Borderline</td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-semibold text-slate-400">Scored NON_DERIV/PART</td>
                      <td className="py-2.5">
                        <span className="text-slate-400 font-mono font-bold">{falseNegatives}</span>
                        <span className="text-[10px] text-slate-500 block">False Neg (FN)</span>
                      </td>
                      <td className="py-2.5">
                        <span className="text-emerald-400 font-mono font-bold">{trueNegatives}</span>
                        <span className="text-[10px] text-slate-500 block">True Neg (TN)</span>
                      </td>
                      <td className="py-2.5">
                        <span className="text-yellow-400 font-mono font-bold">{truePartials}</span>
                        <span className="text-[10px] text-slate-500 block">True Partial</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Metrics */}
            <div className="mt-6 pt-6 border-t border-slate-900 flex items-center justify-between gap-4">
              <div className="flex-1 p-3 bg-slate-900/50 rounded-xl border border-slate-900 flex flex-col items-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider">Precision (Target ≥85%)</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className={`text-lg font-bold font-mono ${precision >= 85 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {precision.toFixed(1)}%
                  </span>
                  {precision >= 85 ? <CheckCircle className="h-4 w-4 text-emerald-400" /> : <AlertTriangle className="h-4 w-4 text-red-500" />}
                </div>
              </div>
              <div className="flex-1 p-3 bg-slate-900/50 rounded-xl border border-slate-900 flex flex-col items-center">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider">Recall (Target ≥70%)</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className={`text-lg font-bold font-mono ${recall >= 70 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {recall.toFixed(1)}%
                  </span>
                  {recall >= 70 ? <CheckCircle className="h-4 w-4 text-emerald-400" /> : <AlertTriangle className="h-4 w-4 text-red-500" />}
                </div>
              </div>
            </div>

          </div>

        </section>

        {/* SURPRISE NODE TESTER */}
        <section className="glass-panel rounded-2xl p-6 shadow-xl border border-slate-900">
          <h2 className="font-bold text-white tracking-wide mb-4 flex items-center gap-2">
            <Info className="h-5 w-5 text-cyan-400" />
            LIVE SURPRISE NODE TESTER
          </h2>
          <form onSubmit={handleTestSurpriseNode} className="flex flex-col gap-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 flex flex-col gap-1.5">
                <label className="text-xs text-slate-400 uppercase tracking-wider">Node Content</label>
                <textarea
                  value={surpriseContent}
                  onChange={(e) => setSurpriseContent(e.target.value)}
                  placeholder="Paste a surprise node clinical content here (e.g. nurse documents: 'Patient Ramaiah's son keeps requesting Ibuprofen...')"
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 outline-none focus:border-cyan-500 transition-colors placeholder:text-slate-600 resize-none"
                />
              </div>
              <div className="w-full md:w-52 flex flex-col gap-1.5 justify-between">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs text-slate-400 uppercase tracking-wider">Node Type</label>
                  <select
                    value={surpriseType}
                    onChange={(e) => setSurpriseType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500 transition-colors"
                  >
                    <option value="FACT">FACT</option>
                    <option value="CONSTRAINT">CONSTRAINT</option>
                    <option value="DECISION">DECISION</option>
                    <option value="ANTI_PATTERN">ANTI_PATTERN</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 py-1">
                  <input
                    type="checkbox"
                    id="surpriseNeverExclude"
                    checked={surpriseNeverExclude}
                    onChange={(e) => setSurpriseNeverExclude(e.target.checked)}
                    className="rounded bg-slate-900 border-slate-800 text-cyan-500 focus:ring-cyan-500/20"
                  />
                  <label htmlFor="surpriseNeverExclude" className="text-xs text-slate-300 font-semibold cursor-pointer select-none">
                    Safety-Critical (Never Exclude)
                  </label>
                </div>
                <button
                  type="submit"
                  disabled={testingNode || !surpriseContent.trim()}
                  className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-900 disabled:text-slate-600 hover:shadow-lg hover:shadow-cyan-500/10 text-slate-950 font-bold px-4 py-2.5 rounded-xl border border-transparent disabled:border-slate-800 transition-all text-sm flex items-center justify-center gap-2"
                >
                  <RefreshCw className={`h-4 w-4 ${testingNode ? 'animate-spin' : ''}`} />
                  {testingNode ? 'Evaluating...' : 'Predict & Calculate'}
                </button>
              </div>
            </div>
          </form>

          {/* Test prediction result */}
          {testResult && (
            <div className="mt-6 p-4 bg-slate-900/50 border border-slate-900 rounded-xl grid grid-cols-1 md:grid-cols-3 gap-6">
              
              <div className="flex flex-col justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Predicted Score & Classification</span>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-3xl font-mono font-black text-cyan-400">{testResult.derivability_score.toFixed(2)}</span>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                      testResult.never_exclude ? 'bg-purple-950/30 text-purple-400 border-purple-900/50' :
                      testResult.derivability_class === 'DERIVABLE' ? 'bg-red-950/30 text-red-400 border-red-900/50' :
                      testResult.derivability_class === 'PARTIALLY_DERIVABLE' ? 'bg-yellow-950/30 text-yellow-400 border-yellow-900/50' :
                      'bg-green-950/30 text-green-400 border-green-900/50'
                    }`}>
                      {testResult.never_exclude ? 'OVERRIDDEN' : testResult.derivability_class}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                    {testResult.never_exclude && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-purple-900/20 text-purple-400 border border-purple-900/50 font-bold tracking-wider uppercase animate-pulse">
                        🛡️ Safety Override
                      </span>
                    )}
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${
                      testResult.confidence === 'HIGH' || testResult.confidence?.startsWith('HIGH') ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/40' :
                      testResult.confidence === 'MEDIUM' ? 'bg-blue-950/30 text-blue-400 border-blue-900/40' :
                      'bg-amber-950/30 text-amber-400 border-amber-900/40'
                    }`}>
                      Confidence: {testResult.confidence}
                    </span>
                  </div>
                </div>
                {testResult.type_floor_applied && !testResult.never_exclude && (
                  <div className="mt-2 text-xs text-amber-500 flex items-center gap-1.5 font-semibold">
                    <Shield className="h-3.5 w-3.5" />
                    Safety floor applied (Constraint cap)
                  </div>
                )}
              </div>

              <div className="md:col-span-2">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Decision Reason Breakdown</span>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-900 font-mono">
                  {testResult.scoring_reason || 'Node content is generic clinical knowledge, standard in corpus.'}
                </p>
                {testResult.derivability_class === 'PARTIALLY_DERIVABLE' && testResult.non_derivable_portion && (
                  <div className="mt-3">
                    <span className="text-[10px] text-yellow-500 font-semibold tracking-wider block">Extracted Non-Derivable Delta:</span>
                    <p className="text-xs text-yellow-200 mt-1 bg-yellow-950/10 p-2.5 rounded border border-yellow-900/20 italic">
                      "{testResult.non_derivable_portion}"
                    </p>
                  </div>
                )}
              </div>

            </div>
          )}
        </section>

        {/* CLINICIAN REVIEW QUEUE */}
        {reviewNodes.length > 0 && (
          <section className="glass-panel rounded-2xl p-6 shadow-xl border border-amber-900/20 bg-amber-950/5">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <h2 className="font-bold text-white tracking-wide flex items-center gap-2 text-amber-400">
                  <span className="text-lg">🩺</span> CLINICIAN REVIEW QUEUE
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Borderline automated scores (0.60–0.80) or LOW confidence flags require human clinical validation to prevent exclusion of patient directives.
                </p>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-lg bg-amber-950/30 text-amber-400 border border-amber-900/40 font-mono font-bold uppercase tracking-wider">
                {reviewNodes.length} Nodes Pending Review
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {reviewNodes.map(node => (
                <div key={node.id} className="bg-slate-950 border border-amber-900/30 rounded-xl p-4 flex flex-col justify-between gap-3 shadow-md hover:border-amber-700/50 transition-colors">
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-[10px] font-bold text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded">
                          {node.id}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 uppercase font-semibold">
                          {node.type}
                        </span>
                      </div>
                      <h4 className="font-bold text-xs text-white mt-1 leading-snug">{node.title}</h4>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-950/30 text-amber-400 border border-amber-900/50 font-mono">
                      Score: {node.derivability_score.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-300 italic line-clamp-2 bg-slate-900/50 p-2 rounded">
                    "{node.content}"
                  </p>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-red-400 font-semibold uppercase bg-red-950/25 px-2 py-0.5 rounded border border-red-950/50">
                      Confidence: {node.confidence}
                    </span>
                    <button
                      onClick={() => {
                        const el = document.getElementById(`node-card-${node.id}`);
                        if (el) {
                          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                          el.classList.add('ring-2', 'ring-amber-500');
                          setTimeout(() => el.classList.remove('ring-2', 'ring-amber-500'), 2000);
                        }
                      }}
                      className="text-cyan-400 hover:text-cyan-300 font-semibold hover:underline outline-none"
                    >
                      Audit Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* NODES LIST */}
        <section className="flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <h2 className="font-bold text-lg text-white tracking-wide flex items-center gap-2">
              <Database className="h-5 w-5 text-cyan-400" />
              KNOWLEDGE NODES ({totalNodesCount})
            </h2>
            
            {/* Search + Filters */}
            <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
              
              {/* Search bar */}
              <div className="relative flex-1 sm:w-60 min-w-44">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search nodes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 hover:border-slate-700 focus:border-cyan-500 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-200 outline-none transition-colors"
                />
              </div>

              {/* Type Filter */}
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Types</option>
                <option value="FACT">FACT</option>
                <option value="CONSTRAINT">CONSTRAINT</option>
                <option value="DECISION">DECISION</option>
                <option value="ANTI_PATTERN">ANTI_PATTERN</option>
              </select>

              {/* Class Filter */}
              <select
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Actions</option>
                <option value="DERIVABLE">DERIVABLE (Exclude)</option>
                <option value="PARTIALLY_DERIVABLE">PARTIAL (Delta)</option>
                <option value="NON_DERIVABLE">NON_DERIV (Full)</option>
              </select>

            </div>
          </div>

          {/* Cards List */}
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-4 text-slate-500">
              <RefreshCw className="h-8 w-8 animate-spin text-cyan-500" />
              <span>Loading Knowledge Base...</span>
            </div>
          ) : filteredNodes.length === 0 ? (
            <div className="py-20 border border-dashed border-slate-900 rounded-2xl flex flex-col items-center justify-center gap-2 text-slate-500">
              <Database className="h-8 w-8" />
              <span>No nodes found matching filters.</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredNodes.map(node => {
                const isExpanded = expandedNodes[node.id];
                const matchesGt = node.derivability_class === node.expected_derivability;
                
                return (
                  <div 
                    key={node.id} 
                    id={`node-card-${node.id}`}
                    className={`glass-panel rounded-xl p-5 border flex flex-col justify-between gap-4 transition-all duration-200 ${
                      node.never_exclude ? 'border-purple-900/50 shadow-[0_0_15px_rgba(168,85,247,0.05)] ring-1 ring-purple-500/20' :
                      node.derivability_class === 'DERIVABLE' ? 'border-red-900/30 shadow-[0_0_15px_rgba(239,68,68,0.02)]' :
                      node.derivability_class === 'PARTIALLY_DERIVABLE' ? 'border-yellow-900/30' :
                      'border-green-900/30'
                    }`}
                  >
                    
                    {/* Top Row: Title, ID & Classification */}
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs font-bold text-slate-500 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                            {node.id}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded bg-slate-900 text-slate-300 font-semibold uppercase tracking-wider">
                            {node.type}
                          </span>
                          {node.department && (
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-900 text-cyan-400 font-medium">
                              {node.department}
                            </span>
                          )}
                        </div>
                        <h3 className="font-bold text-white mt-1.5 tracking-wide leading-tight">{node.title}</h3>
                      </div>

                      <div className="flex flex-col items-end gap-1.5">
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase border ${
                          node.never_exclude ? 'bg-purple-950/30 text-purple-400 border-purple-900/50' :
                          node.derivability_class === 'DERIVABLE' ? 'bg-red-950/30 text-red-400 border-red-900/50' :
                          node.derivability_class === 'PARTIALLY_DERIVABLE' ? 'bg-yellow-950/30 text-yellow-400 border-yellow-900/50' :
                          'bg-green-950/30 text-green-400 border-green-900/50'
                        }`}>
                          {node.never_exclude ? 'OVERRIDDEN' : node.derivability_class}
                        </span>
                        {node.never_exclude && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-red-950/30 text-red-400 border border-red-900/30 font-bold uppercase tracking-wider animate-pulse">
                            🛡️ Safety Override
                          </span>
                        )}
                        <div className="flex items-center gap-1.5">
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${
                            node.confidence === 'HIGH' || node.confidence?.startsWith('HIGH') ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/40' :
                            node.confidence === 'MEDIUM' ? 'bg-blue-950/30 text-blue-400 border-blue-900/40' :
                            'bg-amber-950/30 text-amber-400 border-amber-900/40'
                          }`}>
                            Conf: {node.confidence}
                          </span>
                          <span className="text-xs font-mono text-slate-400 font-semibold bg-slate-900 px-2 py-0.5 rounded">
                            Score: {node.derivability_score.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Content Section */}
                    <p className="text-xs text-slate-300 leading-relaxed italic bg-slate-950/40 p-3 rounded-lg border border-slate-900">
                      "{node.content}"
                    </p>

                    {/* Reasons breakdown list */}
                    <div className="text-[11px] text-slate-400 font-mono bg-slate-950/20 p-2.5 rounded-lg border border-slate-900 flex flex-col gap-1">
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">Breakdown Rationale:</span>
                      {node.scoring_reason.split('; ').map((reason, idx) => (
                        <div key={idx} className="flex items-start gap-1">
                          <span className="text-cyan-500">•</span>
                          <span>{reason}</span>
                        </div>
                      ))}
                      {node.type_floor_applied && (
                        <div className="flex items-center gap-1.5 mt-1 text-amber-500 font-semibold">
                          <Shield className="h-3.5 w-3.5" />
                          <span>Type floor applied ({node.type} max constraint cap)</span>
                        </div>
                      )}
                    </div>

                    {/* Token savings detail */}
                    <div className="flex items-center justify-between text-xs bg-slate-900 px-3 py-2 rounded-lg border border-slate-800">
                      <div className="flex items-center gap-4">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Full Size</span>
                          <span className="font-mono font-bold text-slate-300">{node.tokens_full} tokens</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Injected Size</span>
                          <span className="font-mono font-bold text-slate-300">
                            {node.never_exclude ? node.tokens_full :
                             node.derivability_class === 'DERIVABLE' ? 0 : 
                             node.derivability_class === 'PARTIALLY_DERIVABLE' ? node.tokens_delta : 
                             node.tokens_full} tokens
                          </span>
                        </div>
                        <div className="h-6 w-[1px] bg-slate-800" />
                        <div>
                          <span className="text-[10px] text-emerald-400 uppercase font-semibold block">Tokens Saved</span>
                          <span className="font-mono font-bold text-emerald-400">
                            {node.never_exclude ? 0 :
                             node.derivability_class === 'DERIVABLE' ? node.tokens_full : 
                             node.derivability_class === 'PARTIALLY_DERIVABLE' ? (node.tokens_full - node.tokens_delta) : 
                             0} tokens
                          </span>
                        </div>
                      </div>

                      {/* Expandable toggle for partially derivable delta content */}
                      {node.derivability_class === 'PARTIALLY_DERIVABLE' && node.non_derivable_portion && (
                        <button
                          onClick={() => toggleExpandNode(node.id)}
                          className="text-xs text-yellow-400 flex items-center gap-1 hover:underline outline-none"
                        >
                          {isExpanded ? 'Hide Delta' : 'View Delta'}
                          {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                        </button>
                      )}
                    </div>

                    {/* Expandable delta portion block */}
                    {isExpanded && node.derivability_class === 'PARTIALLY_DERIVABLE' && node.non_derivable_portion && (
                      <div className="p-3 bg-yellow-950/10 border border-yellow-900/20 rounded-lg text-xs text-yellow-200">
                        <span className="font-semibold block mb-1">Non-Derivable Portion (Only this is injected):</span>
                        <p className="italic">"{node.non_derivable_portion}"</p>
                      </div>
                    )}

                    {/* Bottom Row: Validation vs Ground Truth */}
                    <div className="pt-3 border-t border-slate-900 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Expected (GT):</span>
                        <span className="font-bold text-slate-300">{node.expected_derivability}</span>
                      </div>
                      
                      {matchesGt ? (
                        <span className="text-emerald-400 font-semibold flex items-center gap-1">
                          <CheckCircle className="h-3.5 w-3.5" />
                          Scorer Correct
                        </span>
                      ) : (
                        <span className="text-amber-500 font-semibold flex items-center gap-1">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          Misclassified (Safety FN/Borderline)
                        </span>
                      )}
                    </div>

                  </div>
                );
              })}
            </div>
          )}
        </section>

      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4">
          <p>© {new Date().getFullYear()} BRAHMO Systems (USPTO #74841377). Built for Astroum AI Technical Assessment.</p>
          <p className="mt-1 text-[10px] text-slate-600">Lead Full-Stack Developer Take-Home Solution • Calibrated Scoring Engine</p>
        </div>
      </footer>

    </div>
  );
}
