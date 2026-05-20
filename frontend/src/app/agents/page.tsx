'use client';

import { agentStatuses, type AgentStatus } from '@/lib/mock-data';

const statusConfig = {
  running: { label: 'Running', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-500' },
  idle: { label: 'Idle', color: 'text-slate-600', bg: 'bg-slate-100', border: 'border-slate-200', dot: 'bg-slate-400' },
  error: { label: 'Error', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200', dot: 'bg-rose-500' },
  completed: { label: 'Completed', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200', dot: 'bg-blue-500' },
};

const circuitColors = {
  closed: 'text-emerald-700 bg-emerald-50 border border-emerald-200',
  open: 'text-rose-700 bg-rose-50 border border-rose-200',
  'half-open': 'text-amber-700 bg-amber-50 border border-amber-200',
};

function Sparkline({ data }: { data: number[] }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 80; const h = 32;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-20 h-8" preserveAspectRatio="none">
      <polyline points={points} fill="none" stroke="#0057A8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.7" />
    </svg>
  );
}

function AgentCard({ agent }: { agent: AgentStatus }) {
  const cfg = statusConfig[agent.status];
  const errColor = agent.errorRate > 2 ? 'text-rose-600 font-semibold' : agent.errorRate > 1 ? 'text-amber-600 font-semibold' : 'text-emerald-600 font-semibold';
  const circuitClass = circuitColors[agent.circuitBreaker];

  return (
    <div className={`glass gradient-border rounded-xl p-5 border ${cfg.border} hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot} ${agent.status === 'running' ? 'animate-pulse' : ''}`} />
            <span className={`text-xs font-semibold ${cfg.color}`}>{cfg.label}</span>
          </div>
          <h3 className="text-sm font-semibold text-slate-800 leading-snug">{agent.name}</h3>
        </div>
        <Sparkline data={agent.sparklineData} />
      </div>

      <p className="text-xs text-slate-500 leading-relaxed mb-4">{agent.description}</p>

      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
          <p className="text-slate-400">Tasks Completed</p>
          <p className="text-slate-800 font-bold text-sm">{agent.tasksCompleted.toLocaleString()}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
          <p className="text-slate-400">Avg Time</p>
          <p className="text-slate-800 font-bold text-sm">{agent.avgProcessingTime}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
          <p className="text-slate-400">Error Rate</p>
          <p className={`text-sm ${errColor}`}>{agent.errorRate}%</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2 border border-slate-100">
          <p className="text-slate-400">Queue Depth</p>
          <p className="text-slate-800 font-bold text-sm">{agent.queueDepth}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400">Uptime</span>
          <span className="text-emerald-600 font-semibold">{agent.uptime}</span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${circuitClass}`}>
          CB: {agent.circuitBreaker}
        </span>
      </div>
    </div>
  );
}

export default function AgentsPage() {
  const running = agentStatuses.filter(a => a.status === 'running').length;
  const errors = agentStatuses.filter(a => a.status === 'error').length;
  const totalTasks = agentStatuses.reduce((sum, a) => sum + a.tasksCompleted, 0);
  const avgUptime = (agentStatuses.reduce((sum, a) => sum + parseFloat(a.uptime), 0) / agentStatuses.length).toFixed(2);

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Agent Pipeline Monitor</h1>
        <p className="text-slate-500 text-sm mt-1">Real-time status of the 7-agent validation pipeline</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Agents', value: String(agentStatuses.length), color: 'border-l-[#0057A8]' },
          { label: 'Running', value: String(running), color: 'border-l-emerald-500' },
          { label: 'Errors', value: String(errors), color: errors > 0 ? 'border-l-rose-500' : 'border-l-slate-300' },
          { label: 'Total Tasks · ' + avgUptime + '% avg', value: totalTasks.toLocaleString(), color: 'border-l-[#0057A8]' },
        ].map(card => (
          <div key={card.label} className={`glass rounded-xl p-4 text-center border-l-4 ${card.color}`}>
            <p className="text-2xl font-bold text-slate-900">{card.value}</p>
            <p className="text-xs text-slate-400 mt-1">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {agentStatuses.map(agent => <AgentCard key={agent.id} agent={agent} />)}
      </div>
    </div>
  );
}
