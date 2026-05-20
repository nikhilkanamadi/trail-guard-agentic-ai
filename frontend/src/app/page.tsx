'use client';

import { studies, findings, validationRuns, agentStatuses, tmfZones } from '@/lib/mock-data';

const severityConfig = {
  critical: { label: 'Critical', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200' },
  major: { label: 'Major', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200' },
  minor: { label: 'Minor', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200' },
  info: { label: 'Info', color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200' },
};

const runStatusConfig = {
  Completed: { color: 'text-emerald-700', bg: 'bg-emerald-50', dot: 'bg-emerald-500' },
  Running: { color: 'text-blue-700', bg: 'bg-blue-50', dot: 'bg-blue-500' },
  Pending: { color: 'text-amber-700', bg: 'bg-amber-50', dot: 'bg-amber-500' },
  Failed: { color: 'text-rose-700', bg: 'bg-rose-50', dot: 'bg-rose-500' },
};

const agentStatusConfig = {
  running: { color: 'text-emerald-700', bg: 'bg-emerald-50', dot: 'bg-emerald-500' },
  idle: { color: 'text-slate-600', bg: 'bg-slate-100', dot: 'bg-slate-400' },
  error: { color: 'text-rose-700', bg: 'bg-rose-50', dot: 'bg-rose-500' },
  completed: { color: 'text-blue-700', bg: 'bg-blue-50', dot: 'bg-blue-500' },
};

function StatCard({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent: string }) {
  return (
    <div className={`glass rounded-xl p-6 border-l-4 ${accent} animate-slide-up`}>
      <p className="text-slate-500 text-sm font-medium">{label}</p>
      <p className="text-3xl font-bold text-slate-900 mt-1">{value}</p>
      {sub && <p className="text-slate-400 text-xs mt-1">{sub}</p>}
    </div>
  );
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function Dashboard() {
  const activeStudies = studies.filter(s => s.status === 'Active').length;
  const criticalCount = findings.filter(f => f.severity === 'critical').length;
  const avgScore = (studies.reduce((sum, s) => sum + s.complianceScore, 0) / studies.length).toFixed(1);
  const activeRuns = validationRuns.filter(r => r.status === 'Running').length;

  const recentRuns = [...validationRuns].slice(0, 5);
  const criticalFindings = findings.filter(f => f.severity === 'critical' || f.severity === 'major').slice(0, 5);

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Clinical Operations — TrialGuard AI Platform</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Studies" value={String(studies.length)} sub={`${activeStudies} active`} accent="border-l-[#0057A8]" />
        <StatCard label="Active Validations" value={String(activeRuns)} sub="in pipeline" accent="border-l-blue-400" />
        <StatCard label="Critical Findings" value={String(criticalCount)} sub="require action" accent="border-l-rose-500" />
        <StatCard label="Avg Compliance Score" value={`${avgScore}%`} sub="across all studies" accent="border-l-emerald-500" />
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        {/* Recent Runs */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Recent Validation Runs</h2>
          <div className="space-y-2">
            {recentRuns.map(run => {
              const cfg = runStatusConfig[run.status];
              return (
                <div key={run.id} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot} ${run.status === 'Running' ? 'animate-pulse' : ''}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-700 truncate">{run.documentName}</p>
                    <p className="text-xs text-slate-400">{formatDate(run.startedAt)} · {run.duration}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.color} font-medium`}>{run.status}</span>
                    {run.findingsCount > 0 && (
                      <span className="text-xs font-medium text-rose-600">{run.findingsCount} findings</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Critical & Major Findings */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Critical & Major Findings</h2>
          <div className="space-y-2">
            {criticalFindings.map(f => {
              const cfg = severityConfig[f.severity];
              return (
                <div key={f.id} className={`p-3 rounded-lg border ${cfg.border} ${cfg.bg}`}>
                  <div className="flex items-start gap-2">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full bg-white/60 ${cfg.color} flex-shrink-0 mt-0.5`}>
                      {cfg.label}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-800 font-medium leading-snug">{f.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">{f.documentName}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full bg-white/60 flex-shrink-0 ${f.status === 'Escalated' ? 'text-rose-600' : 'text-slate-500'}`}>
                      {f.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* TMF Completeness */}
      <div className="glass rounded-xl p-6 mb-8">
        <h2 className="text-base font-semibold text-slate-800 mb-4">TMF Completeness by Zone</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {tmfZones.map(zone => {
            const pct = zone.completeness;
            const color = pct >= 95 ? 'bg-emerald-500' : pct >= 85 ? 'bg-[#0057A8]' : pct >= 70 ? 'bg-amber-500' : 'bg-rose-500';
            const textColor = pct >= 95 ? 'text-emerald-600' : pct >= 85 ? 'text-[#0057A8]' : pct >= 70 ? 'text-amber-600' : 'text-rose-600';
            return (
              <div key={zone.id} className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-slate-600 font-medium">Zone {zone.zoneNumber}</p>
                  <span className={`text-xs font-bold ${textColor}`}>{pct}%</span>
                </div>
                <p className="text-xs text-slate-400 mb-2 truncate">{zone.name}</p>
                <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full progress-bar ${color}`} style={{ width: `${pct}%` }} />
                </div>
                <p className="text-xs text-slate-400 mt-1">{zone.completedArtifacts}/{zone.totalArtifacts} artifacts</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Agent Status Row */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-base font-semibold text-slate-800 mb-4">Agent Pipeline Status</h2>
        <div className="flex flex-wrap gap-2">
          {agentStatuses.map(agent => {
            const cfg = agentStatusConfig[agent.status];
            return (
              <div key={agent.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 ${cfg.bg}`}>
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot} ${agent.status === 'running' ? 'animate-pulse' : ''}`} />
                <span className="text-xs text-slate-700 font-medium">{agent.name}</span>
                <span className={`text-xs ${cfg.color}`}>{agent.status}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
