'use client';

import { useState } from 'react';
import { findings, type Finding } from '@/lib/mock-data';

const severityConfig = {
  critical: { label: 'Critical', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200', dot: 'bg-rose-500', pill: 'bg-rose-100 text-rose-700 border-rose-200' },
  major: { label: 'Major', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-500', pill: 'bg-amber-100 text-amber-700 border-amber-200' },
  minor: { label: 'Minor', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200', dot: 'bg-blue-500', pill: 'bg-blue-100 text-blue-700 border-blue-200' },
  info: { label: 'Info', color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200', dot: 'bg-slate-400', pill: 'bg-slate-100 text-slate-600 border-slate-200' },
};

const statusConfig: Record<Finding['status'], { color: string; bg: string }> = {
  Open: { color: 'text-amber-700', bg: 'bg-amber-50' },
  Resolved: { color: 'text-emerald-700', bg: 'bg-emerald-50' },
  Escalated: { color: 'text-rose-700', bg: 'bg-rose-50' },
  'False Positive': { color: 'text-slate-600', bg: 'bg-slate-100' },
};

function FindingCard({ finding }: { finding: Finding }) {
  const [expanded, setExpanded] = useState(false);
  const sev = severityConfig[finding.severity];
  const sts = statusConfig[finding.status];

  return (
    <div className={`glass rounded-xl p-5 border ${sev.border} hover:shadow-md transition-shadow`}>
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${sev.dot}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 mb-1">
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${sev.pill} flex-shrink-0`}>{sev.label}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${sts.bg} ${sts.color} font-medium flex-shrink-0`}>{finding.status}</span>
          </div>
          <h3 className="text-sm font-semibold text-slate-800 leading-snug">{finding.title}</h3>
        </div>
        <div className="flex-shrink-0 text-right">
          <p className="text-xs text-slate-500 font-semibold">{finding.confidenceScore}%</p>
          <p className="text-xs text-slate-400">confidence</p>
        </div>
      </div>

      <p className="text-xs text-slate-500 leading-relaxed line-clamp-2 mb-3">{finding.description}</p>

      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div><p className="text-slate-400">Document</p><p className="text-slate-700 truncate font-medium">{finding.documentName}</p></div>
        <div><p className="text-slate-400">Agent</p><p className="text-slate-700 truncate">{finding.agentSource}</p></div>
        <div><p className="text-slate-400">Regulation</p><p className="text-slate-700 truncate">{finding.regulatoryReference}</p></div>
        <div><p className="text-slate-400">Category</p><p className="text-slate-700 truncate">{finding.category}</p></div>
      </div>

      <button onClick={() => setExpanded(!expanded)}
        className="text-xs text-[#0057A8] hover:text-[#003087] transition-colors flex items-center gap-1 font-medium">
        <svg className={`w-3 h-3 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        {expanded ? 'Hide' : 'Show'} remediation
      </button>

      {expanded && (
        <div className="mt-3 p-3 rounded-lg bg-blue-50 border border-blue-100">
          <p className="text-xs text-slate-500 font-semibold mb-1">Suggested Remediation</p>
          <p className="text-xs text-slate-700 leading-relaxed">{finding.suggestedRemediation}</p>
        </div>
      )}
    </div>
  );
}

export default function FindingsPage() {
  const [severityFilter, setSeverityFilter] = useState<string>('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [search, setSearch] = useState('');

  const filtered = findings.filter(f => {
    const matchSev = severityFilter === 'All' || f.severity === severityFilter.toLowerCase();
    const matchSts = statusFilter === 'All' || f.status === statusFilter;
    const matchSearch = search === '' || f.title.toLowerCase().includes(search.toLowerCase()) || f.documentName.toLowerCase().includes(search.toLowerCase());
    return matchSev && matchSts && matchSearch;
  });

  const counts = {
    critical: findings.filter(f => f.severity === 'critical').length,
    major: findings.filter(f => f.severity === 'major').length,
    minor: findings.filter(f => f.severity === 'minor').length,
    info: findings.filter(f => f.severity === 'info').length,
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Findings</h1>
        <p className="text-slate-500 text-sm mt-1">{findings.length} total findings across all studies</p>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {[
          { key: 'All', label: 'All', count: findings.length },
          { key: 'Critical', label: 'Critical', count: counts.critical },
          { key: 'Major', label: 'Major', count: counts.major },
          { key: 'Minor', label: 'Minor', count: counts.minor },
          { key: 'Info', label: 'Info', count: counts.info },
        ].map(item => {
          const active = severityFilter === item.key;
          const sev = item.key !== 'All' ? severityConfig[item.key.toLowerCase() as keyof typeof severityConfig] : null;
          return (
            <button key={item.key} onClick={() => setSeverityFilter(item.key)}
              className={`text-xs px-3 py-1.5 rounded-full transition-colors border font-medium ${
                active ? (sev ? `${sev.pill}` : 'bg-[#0057A8] text-white border-[#0057A8]') : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'
              }`}>
              {item.label} <span className="ml-1 opacity-70">{item.count}</span>
            </button>
          );
        })}
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Search findings..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg text-sm text-slate-700 placeholder-slate-400 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white" />
        </div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="px-4 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
          {['All', 'Open', 'Resolved', 'Escalated', 'False Positive'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="glass rounded-xl p-16 text-center"><p className="text-slate-400">No findings match your filters.</p></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map(f => <FindingCard key={f.id} finding={f} />)}
        </div>
      )}
    </div>
  );
}
