'use client';

import { useState } from 'react';
import { auditEntries } from '@/lib/mock-data';

const actionColors: Record<string, { color: string; bg: string }> = {
  'Upload Document': { color: 'text-blue-700', bg: 'bg-blue-50' },
  'Start Validation': { color: 'text-violet-700', bg: 'bg-violet-50' },
  'Complete Validation': { color: 'text-emerald-700', bg: 'bg-emerald-50' },
  'Escalate Finding': { color: 'text-rose-700', bg: 'bg-rose-50' },
  'Resolve Finding': { color: 'text-emerald-700', bg: 'bg-emerald-50' },
  'Agent Error': { color: 'text-rose-700', bg: 'bg-rose-50' },
  'Export Report': { color: 'text-cyan-700', bg: 'bg-cyan-50' },
  'Update Configuration': { color: 'text-amber-700', bg: 'bg-amber-50' },
  'Create Study': { color: 'text-blue-700', bg: 'bg-blue-50' },
  'Backup Complete': { color: 'text-emerald-700', bg: 'bg-emerald-50' },
};

const entityTypeColors: Record<string, string> = {
  Document: 'text-blue-700', Validation: 'text-violet-700', Finding: 'text-amber-700',
  Agent: 'text-cyan-700', Report: 'text-emerald-700', Study: 'text-fuchsia-700', System: 'text-slate-500',
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function AuditPage() {
  const [actionFilter, setActionFilter] = useState('All');
  const [entityFilter, setEntityFilter] = useState('All');

  const actions = ['All', ...Array.from(new Set(auditEntries.map(e => e.action)))];
  const entityTypes = ['All', ...Array.from(new Set(auditEntries.map(e => e.entityType)))];
  const filtered = auditEntries.filter(e => (actionFilter === 'All' || e.action === actionFilter) && (entityFilter === 'All' || e.entityType === entityFilter));

  return (
    <div className="animate-fade-in">
      <div className="mb-2">
        <h1 className="text-2xl font-bold text-slate-900">Audit Trail</h1>
        <p className="text-slate-500 text-sm mt-1">21 CFR Part 11 compliant audit log — all actions are immutable and timestamped</p>
      </div>
      <div className="flex items-center gap-2 mb-6 mt-4">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <p className="text-xs text-slate-400">Audit logging active · {auditEntries.length} entries</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <select value={actionFilter} onChange={e => setActionFilter(e.target.value)}
          className="px-4 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
          {actions.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select value={entityFilter} onChange={e => setEntityFilter(e.target.value)}
          className="px-4 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
          {entityTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <span className="text-xs text-slate-400 self-center">{filtered.length} entries</span>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                {['Timestamp', 'User', 'Action', 'Entity', 'Type', 'Details', 'IP Address'].map(h => (
                  <th key={h} className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry, i) => {
                const actCfg = actionColors[entry.action] ?? { color: 'text-slate-600', bg: 'bg-slate-100' };
                const entColor = entityTypeColors[entry.entityType] ?? 'text-slate-500';
                return (
                  <tr key={entry.id} className={`border-b border-slate-50 hover:bg-slate-50 transition-colors ${i % 2 === 1 ? 'bg-slate-50/50' : ''}`}>
                    <td className="px-5 py-3.5"><p className="text-xs text-slate-600 font-mono whitespace-nowrap">{formatDate(entry.timestamp)}</p></td>
                    <td className="px-5 py-3.5"><p className="text-xs text-slate-700 whitespace-nowrap">{entry.user}</p></td>
                    <td className="px-5 py-3.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap font-medium ${actCfg.bg} ${actCfg.color}`}>{entry.action}</span>
                    </td>
                    <td className="px-5 py-3.5"><p className="text-xs text-slate-700 max-w-[180px] truncate">{entry.entity}</p></td>
                    <td className="px-5 py-3.5"><span className={`text-xs font-semibold ${entColor}`}>{entry.entityType}</span></td>
                    <td className="px-5 py-3.5"><p className="text-xs text-slate-500 max-w-[280px] truncate">{entry.details}</p></td>
                    <td className="px-5 py-3.5"><p className="text-xs text-slate-400 font-mono whitespace-nowrap">{entry.ipAddress}</p></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
