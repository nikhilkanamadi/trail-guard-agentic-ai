'use client';

import { useState, useRef } from 'react';
import { documents, studies, type Document } from '@/lib/mock-data';

const docStatusConfig: Record<Document['status'], { color: string; bg: string }> = {
  Validated: { color: 'text-emerald-700', bg: 'bg-emerald-50' },
  Pending: { color: 'text-amber-700', bg: 'bg-amber-50' },
  'In Review': { color: 'text-blue-700', bg: 'bg-blue-50' },
  Failed: { color: 'text-rose-700', bg: 'bg-rose-50' },
};

const tmfZones = Array.from({ length: 11 }, (_, i) => i + 1);
const docTypes = [
  'Protocol', 'Informed Consent Form', 'Investigator Brochure', 'Case Report Form',
  'Statistical Analysis Plan', 'Clinical Study Report', 'Monitoring Report',
  'SAE Report', 'IRB Approval', 'DSMB Charter', 'Regulatory Submission',
];

export default function DocumentsPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success'>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [form, setForm] = useState({ studyId: '', documentType: '', tmfZone: '', title: '', version: '1.0' });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) setSelectedFile(file);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUploadState('uploading');
    setTimeout(() => setUploadState('success'), 2000);
    setTimeout(() => { setUploadState('idle'); setSelectedFile(null); }, 5000);
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
        <p className="text-slate-500 text-sm mt-1">Upload and manage clinical trial documents</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 mb-8">
        {/* Upload Panel */}
        <div className="xl:col-span-2 glass rounded-xl p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Upload Document</h2>

          {uploadState === 'success' ? (
            <div className="text-center py-10">
              <div className="w-14 h-14 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto mb-3">
                <svg className="w-7 h-7 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-emerald-700 font-medium">Upload successful</p>
              <p className="text-slate-400 text-sm mt-1">Document queued for validation</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                  dragActive ? 'border-[#0057A8] bg-blue-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                }`}
                onDragOver={e => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.doc,.docx,.txt,.csv"
                  onChange={e => setSelectedFile(e.target.files?.[0] ?? null)} />
                <svg className="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                {selectedFile ? (
                  <p className="text-[#0057A8] text-sm font-medium">{selectedFile.name}</p>
                ) : (
                  <>
                    <p className="text-slate-500 text-sm">Drop file here or click to browse</p>
                    <p className="text-slate-400 text-xs mt-1">PDF, DOCX, TXT, CSV · Max 100 MB</p>
                  </>
                )}
              </div>

              <div>
                <label className="text-xs text-slate-500 mb-1 block font-medium">Study *</label>
                <select required value={form.studyId} onChange={e => setForm(f => ({ ...f, studyId: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
                  <option value="">Select study...</option>
                  {studies.map(s => <option key={s.id} value={s.id}>{s.id} — {s.sponsor}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block font-medium">Document Type *</label>
                <select required value={form.documentType} onChange={e => setForm(f => ({ ...f, documentType: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
                  <option value="">Select type...</option>
                  {docTypes.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1 block font-medium">TMF Zone *</label>
                  <select required value={form.tmfZone} onChange={e => setForm(f => ({ ...f, tmfZone: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white">
                    <option value="">Zone</option>
                    {tmfZones.map(z => <option key={z} value={z}>Zone {z}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1 block font-medium">Version</label>
                  <input type="text" value={form.version} onChange={e => setForm(f => ({ ...f, version: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white" placeholder="1.0" />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block font-medium">Title *</label>
                <input type="text" required value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white" placeholder="Document title" />
              </div>

              <button type="submit" disabled={!selectedFile || uploadState === 'uploading'}
                className="w-full py-2.5 rounded-lg text-white text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
                style={{ background: '#0057A8' }}
                onMouseOver={e => (e.currentTarget.style.background = '#003087')}
                onMouseOut={e => (e.currentTarget.style.background = '#0057A8')}
              >
                {uploadState === 'uploading' ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Uploading...
                  </>
                ) : 'Upload & Queue Validation'}
              </button>
            </form>
          )}
        </div>

        {/* Documents Table */}
        <div className="xl:col-span-3 glass rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h2 className="text-base font-semibold text-slate-800">All Documents</h2>
            <p className="text-xs text-slate-400 mt-0.5">{documents.length} documents</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50">
                  {['Name', 'Type', 'Status', 'Ver.', 'Uploaded By', 'Findings'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {documents.map((doc, i) => {
                  const cfg = docStatusConfig[doc.status];
                  return (
                    <tr key={doc.id} className={`border-b border-slate-50 hover:bg-slate-50 transition-colors ${i % 2 === 1 ? 'bg-slate-50/50' : ''}`}>
                      <td className="px-4 py-3">
                        <p className="text-slate-800 font-medium text-xs leading-snug max-w-[200px] truncate">{doc.name}</p>
                        <p className="text-slate-400 text-xs">{doc.size} · {doc.language}</p>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">{doc.type}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.color} font-medium whitespace-nowrap`}>{doc.status}</span>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-500">v{doc.version}</td>
                      <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">{doc.uploadedBy}</td>
                      <td className="px-4 py-3">
                        {doc.findings > 0 ? (
                          <span className="text-xs font-semibold text-rose-600">{doc.findings}</span>
                        ) : (
                          <span className="text-xs text-slate-300">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
