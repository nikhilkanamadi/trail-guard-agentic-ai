'use client';

import { useState } from 'react';
import { studies, type Study } from '@/lib/mock-data';

const statusConfig: Record<Study['status'], { color: string; bg: string; border: string }> = {
  Active: { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200' },
  Completed: { color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200' },
  'On Hold': { color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200' },
  Archived: { color: 'text-slate-600', bg: 'bg-slate-100', border: 'border-slate-200' },
};

const phaseColor: Record<string, string> = {
  'Phase I': 'text-cyan-700 bg-cyan-50',
  'Phase II': 'text-blue-700 bg-blue-50',
  'Phase III': 'text-violet-700 bg-violet-50',
  'Phase IV': 'text-fuchsia-700 bg-fuchsia-50',
};

function ScoreRing({ score }: { score: number }) {
  const r = 20;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 95 ? '#059669' : score >= 85 ? '#0057A8' : score >= 70 ? '#D97706' : '#DC2626';
  return (
    <div className="relative w-14 h-14 flex-shrink-0">
      <svg className="w-14 h-14 -rotate-90" viewBox="0 0 48 48">
        <circle cx="24" cy="24" r={r} fill="none" stroke="#E2E8F0" strokeWidth="4" />
        <circle cx="24" cy="24" r={r} fill="none" stroke={color} strokeWidth="4"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-slate-800">
        {score.toFixed(0)}
      </span>
    </div>
  );
}

function StudyCard({ study }: { study: Study }) {
  const cfg = statusConfig[study.status];
  const phaseClass = phaseColor[study.phase] ?? 'text-slate-600 bg-slate-100';
  return (
    <div className="glass gradient-border rounded-xl p-5 flex flex-col gap-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-400 font-mono mb-1">{study.protocolNumber}</p>
          <p className="text-sm font-semibold text-slate-800 leading-snug line-clamp-2">{study.title}</p>
          <p className="text-xs text-slate-500 mt-1">{study.sponsor}</p>
        </div>
        <ScoreRing score={study.complianceScore} />
      </div>

      <div className="flex flex-wrap gap-2">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.bg} ${cfg.color} border ${cfg.border}`}>
          {study.status}
        </span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${phaseClass}`}>
          {study.phase}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
          {study.therapeuticArea}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100">
        <div className="text-center">
          <p className="text-base font-bold text-slate-900">{study.documents}</p>
          <p className="text-xs text-slate-400">Docs</p>
        </div>
        <div className="text-center">
          <p className="text-base font-bold text-slate-900">{study.sites}</p>
          <p className="text-xs text-slate-400">Sites</p>
        </div>
        <div className="text-center">
          <p className="text-base font-bold text-slate-900">{study.enrolledPatients.toLocaleString()}</p>
          <p className="text-xs text-slate-400">Patients</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>PI: {study.principalInvestigator}</span>
        <span>{study.indication}</span>
      </div>
    </div>
  );
}

export default function StudiesPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('All');

  const filtered = studies.filter(s => {
    const matchSearch = s.title.toLowerCase().includes(search.toLowerCase()) ||
      s.protocolNumber.toLowerCase().includes(search.toLowerCase()) ||
      s.sponsor.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'All' || s.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Clinical Studies</h1>
          <p className="text-slate-500 text-sm mt-1">{studies.length} studies · {studies.filter(s => s.status === 'Active').length} active</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search studies..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 glass rounded-lg text-sm text-slate-700 placeholder-slate-400 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-4 py-2.5 glass rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white"
        >
          {['All', 'Active', 'Completed', 'On Hold', 'Archived'].map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="flex gap-2 mb-6">
        {(['All', 'Active', 'Completed', 'On Hold', 'Archived'] as const).map(s => {
          const count = s === 'All' ? studies.length : studies.filter(st => st.status === s).length;
          const active = statusFilter === s;
          return (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`text-xs px-3 py-1 rounded-full transition-colors border ${active
                ? 'bg-[#0057A8] text-white border-[#0057A8]'
                : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'}`}
            >
              {s} {count}
            </button>
          );
        })}
      </div>

      {filtered.length === 0 ? (
        <div className="glass rounded-xl p-16 text-center">
          <p className="text-slate-400">No studies match your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(study => <StudyCard key={study.id} study={study} />)}
        </div>
      )}
    </div>
  );
}
