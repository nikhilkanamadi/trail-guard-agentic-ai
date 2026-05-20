'use client';

import { useState } from 'react';

export default function SettingsPage() {
  const [apiKey] = useState('tg-sk-••••••••••••••••••••••••••••••4f2a');
  const [copied, setCopied] = useState(false);
  const [agentTimeout, setAgentTimeout] = useState(300);
  const [maxConcurrent, setMaxConcurrent] = useState(5);
  const [emailCritical, setEmailCritical] = useState(true);
  const [emailComplete, setEmailComplete] = useState(false);
  const [saved, setSaved] = useState(false);

  const [frameworks, setFrameworks] = useState({
    'ICH-GCP E6(R2)': true,
    'FDA 21 CFR Part 11': true,
    'EU CTR 536/2014': true,
    'HIPAA': true,
    'GDPR': false,
  });

  const handleCopy = () => {
    navigator.clipboard.writeText('tg-sk-example-key').catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const toggleFramework = (key: string) => {
    setFrameworks(f => ({ ...f, [key]: !f[key as keyof typeof f] }));
  };

  return (
    <div className="animate-fade-in max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 text-sm mt-1">Platform configuration for TrialGuard AI</p>
      </div>

      <div className="space-y-6">
        {/* API Configuration */}
        <section className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">API Configuration</h2>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">API Key</label>
            <div className="flex gap-2">
              <input
                readOnly
                value={apiKey}
                className="flex-1 px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 bg-white font-mono focus:outline-none"
              />
              <button
                onClick={handleCopy}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${copied ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'}`}
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-1">Use this key to authenticate backend API requests.</p>
          </div>
        </section>

        {/* Agent Configuration */}
        <section className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Agent Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Agent Timeout (seconds)</label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min={30}
                  max={600}
                  value={agentTimeout}
                  onChange={e => setAgentTimeout(Number(e.target.value))}
                  className="w-28 px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white"
                />
                <span className="text-xs text-slate-500">{agentTimeout}s · max 600s</span>
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Max Concurrent Validations</label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={maxConcurrent}
                  onChange={e => setMaxConcurrent(Number(e.target.value))}
                  className="w-28 px-3 py-2 rounded-lg text-sm text-slate-700 border border-slate-200 focus:outline-none focus:border-[#0057A8] bg-white"
                />
                <span className="text-xs text-slate-500">parallel pipeline executions</span>
              </div>
            </div>
          </div>
        </section>

        {/* Notification Preferences */}
        <section className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Notification Preferences</h2>
          <div className="space-y-3">
            {[
              { label: 'Email on Critical Finding', sub: 'Immediate alert when a critical finding is detected', value: emailCritical, set: setEmailCritical },
              { label: 'Email on Validation Complete', sub: 'Notify when a validation pipeline run finishes', value: emailComplete, set: setEmailComplete },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-lg">
                <div>
                  <p className="text-sm text-slate-700">{item.label}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{item.sub}</p>
                </div>
                <button
                  onClick={() => item.set(!item.value)}
                  className={`relative w-10 h-6 rounded-full transition-colors ${item.value ? '' : 'bg-slate-200'}`}
                  style={item.value ? { background: '#0057A8' } : {}}
                >
                  <span className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${item.value ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Regulatory Frameworks */}
        <section className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-800 mb-4">Regulatory Frameworks</h2>
          <p className="text-xs text-slate-500 mb-3">Select the frameworks to enable for compliance validation.</p>
          <div className="space-y-2">
            {Object.entries(frameworks).map(([key, enabled]) => (
              <label key={key} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={() => toggleFramework(key)}
                  className="w-4 h-4 cursor-pointer accent-[#0057A8]"
                />
                <span className="text-sm text-slate-700">{key}</span>
              </label>
            ))}
          </div>
        </section>

        {/* Save button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-lg text-white text-sm font-medium transition-colors"
            style={{ background: '#0057A8' }}
            onMouseOver={e => (e.currentTarget.style.background = '#003087')}
            onMouseOut={e => (e.currentTarget.style.background = '#0057A8')}
          >
            Save Settings
          </button>
          {saved && (
            <span className="text-sm text-emerald-600 flex items-center gap-1.5 animate-fade-in">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Settings saved
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
