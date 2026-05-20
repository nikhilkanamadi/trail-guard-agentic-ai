'use client';

import { useState } from 'react';
import { validationRuns, documents, type ValidationRun } from '@/lib/mock-data';

const statusConfig: Record<ValidationRun['status'], { color: string; bg: string; border: string }> = {
  Completed: { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200' },
  Running: { color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200' },
  Pending: { color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200' },
  Failed: { color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200' },
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function ValidationPage() {
  const [showModal, setShowModal] = useState(false);
  const [modalDoc, setModalDoc] = useState('');
  const [runType, setRunType] = useState<'FULL' | 'INCREMENTAL'>('FULL');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => { setShowModal(false); setSubmitted(false); setModalDoc(''); }, 1500);
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Validation Queue</h1>
          <p className="text-slate-500 text-sm mt-1">7-agent validation pipeline status</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-lg text-white text-sm font-medium transition-colors flex items-center gap-2"
          style={{ background: '#0057A8' }}
          onMouseOver={e => (e.currentTarget.style.background = '#003087')}
          onMouseOut={e => (e.currentTarget.style.background = '#0057A8')}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Trigger Validation
        </button>
      </div>

      <div className="flex gap-3 mb-6">
        {(['Completed', 'Running', 'Pending', 'Failed'] as const).map(s => {
          const cfg = statusConfig[s];
          const count = validationRuns.filter(r => r.status === s).length;
          return (
            <div key={s} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${cfg.border} ${cfg.bg}`}>
              <span className={`text-xs font-semibold ${cfg.color}`}>{s}</span>
              <span className="text-xs text-slate-500">{count}</span>
            </div>
          );
        })}
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                {['Document', 'Study', 'Status', 'Progress', 'Duration', 'Findings', 'Started'].map(h => (
                  <th key={h} className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {validationRuns.map((run, i) => {
                const cfg = statusConfig[run.status];
                const pct = Math.round((run.agentsCompleted / run.totalAgents) * 100);
                return (
                  <tr key={run.id} className={`border-b border-slate-50 transition-colors ${run.status === 'Running' ? 'bg-blue-50/40' : i % 2 === 1 ? 'bg-slate-50/40' : ''} hover:bg-slate-50`}>
                    <td className="px-5 py-4">
                      <p className="text-slate-800 font-medium text-sm leading-snug max-w-[220px] truncate">{run.documentName}</p>
                      <p className="text-slate-400 text-xs font-mono mt-0.5">{run.id}</p>
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-500 font-mono whitespace-nowrap">{run.studyId}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {run.status === 'Running' && <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse flex-shrink-0" />}
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.bg} ${cfg.color} whitespace-nowrap`}>{run.status}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 min-w-[140px]">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full progress-bar ${pct === 100 ? 'bg-emerald-500' : 'bg-[#0057A8]'}`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-xs text-slate-500 whitespace-nowrap">{run.agentsCompleted}/{run.totalAgents}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-500 whitespace-nowrap">{run.duration}</td>
                    <td className="px-5 py-4">
                      {run.findingsCount > 0 ? (
                        <span className="text-xs font-semibold text-rose-600">{run.findingsCount}</span>
                      ) : <span className="text-xs text-slate-300">—</span>}
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400 whitespace-nowrap">{formatDate(run.startedAt)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={() => setShowModal(false)} />
          <div className="relative bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl animate-slide-up border border-slate-200">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-semibold text-slate-900">Trigger New Validation</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {submitted ? (
              <div className="text-center py-6">
                <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="text-emerald-700 font-medium">Validation queued</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-xs text-slate-500 mb-1 block font-medium">Document *</label>
                  <select required value={modalDoc} onChange={e => setModalDoc(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
                    <option value="">Select document...</option>
                    {documents.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-2 block font-medium">Run Type</label>
                  <div className="grid grid-cols-2 gap-2">
                    {(['FULL', 'INCREMENTAL'] as const).map(t => (
                      <button key={t} type="button" onClick={() => setRunType(t)}
                        className={`py-2.5 rounded-lg text-sm font-medium transition-colors border ${
                          runType === t ? 'text-white border-[#0057A8]' : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'
                        }`}
                        style={runType === t ? { background: '#0057A8' } : {}}
                      >{t}</button>
                    ))}
                  </div>
                </div>
                <button type="submit" className="w-full py-2.5 rounded-lg text-white text-sm font-medium transition-colors mt-2"
                  style={{ background: '#0057A8' }}
                  onMouseOver={e => (e.currentTarget.style.background = '#003087')}
                  onMouseOut={e => (e.currentTarget.style.background = '#0057A8')}
                >Start Validation</button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
