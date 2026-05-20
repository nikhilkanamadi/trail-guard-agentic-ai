'use client';

import { useState } from 'react';

const reportTypes = [
  {
    id: 'compliance',
    title: 'Compliance Summary Report',
    description: 'Aggregated ICH-GCP, FDA 21 CFR Part 11, and EU CTR compliance scores across all active studies. Includes finding breakdown by agent and severity.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
      </svg>
    ),
    accent: 'text-blue-700 bg-blue-50 border-blue-200',
  },
  {
    id: 'tmf',
    title: 'TMF Completeness Report',
    description: 'Trial Master File completeness analysis across all 11 DIA Reference Model zones. Highlights missing artifacts and unvalidated documents per zone.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 00-1.883 2.542l.857 6a2.25 2.25 0 002.227 1.932H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-1.883-2.542m-16.5 0V6A2.25 2.25 0 016 3.75h3.879a1.5 1.5 0 011.06.44l2.122 2.12a1.5 1.5 0 001.06.44H18A2.25 2.25 0 0120.25 9v.776" />
      </svg>
    ),
    accent: 'text-violet-700 bg-violet-50 border-violet-200',
  },
  {
    id: 'findings',
    title: 'Findings Export',
    description: 'Full export of all validation findings with severity classifications, regulatory references, remediation guidance, and current resolution status.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
    accent: 'text-amber-700 bg-amber-50 border-amber-200',
  },
];

export default function ReportsPage() {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [generatedReports, setGeneratedReports] = useState<string[]>([]);

  const handleGenerate = (id: string) => {
    setLoadingId(id);
    setTimeout(() => {
      setLoadingId(null);
      setGeneratedReports(prev => prev.includes(id) ? prev : [...prev, id]);
    }, 2000);
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Compliance Reports</h1>
        <p className="text-slate-500 text-sm mt-1">Generate PDF reports for sponsor and regulatory submissions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {reportTypes.map(report => {
          const isLoading = loadingId === report.id;
          const isGenerated = generatedReports.includes(report.id);
          return (
            <div key={report.id} className={`glass gradient-border rounded-xl p-6 border ${report.accent.split(' ')[2]}`}>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${report.accent.split(' ').slice(1).join(' ')}`}>
                <span className={report.accent.split(' ')[0]}>{report.icon}</span>
              </div>
              <h3 className="text-sm font-semibold text-slate-800 mb-2">{report.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-5">{report.description}</p>
              <button
                onClick={() => handleGenerate(report.id)}
                disabled={isLoading}
                className={`w-full py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                  isGenerated
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200 disabled:opacity-50'
                }`}
              >
                {isLoading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Generating...
                  </>
                ) : isGenerated ? (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    Download PDF
                  </>
                ) : (
                  'Generate Report'
                )}
              </button>
            </div>
          );
        })}
      </div>

      {generatedReports.length === 0 && (
        <div className="glass rounded-xl p-12 text-center border border-slate-200">
          <svg className="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <p className="text-slate-400 font-medium">No reports generated yet</p>
          <p className="text-slate-400 text-sm mt-1">PDF export powered by your document generation pipeline</p>
        </div>
      )}

      {generatedReports.length > 0 && (
        <div className="glass rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-800 mb-3">Generated Reports</h2>
          <div className="space-y-2">
            {generatedReports.map(id => {
              const r = reportTypes.find(rt => rt.id === id)!;
              return (
                <div key={id} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center">
                      <svg className="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-slate-700">{r.title}</p>
                      <p className="text-xs text-slate-500">Generated just now · PDF</p>
                    </div>
                  </div>
                  <button className="text-xs text-[#0057A8] hover:text-[#003087] transition-colors">Download</button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
