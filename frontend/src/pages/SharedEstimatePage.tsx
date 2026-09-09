import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import type { EstimateResult } from '@/types';
import { RISK_COLORS } from '@/lib/risk';

type SharedEstimate = Pick<EstimateResult, 'project_name' | 'version' | 'created_at' | 'inputs' | 'outputs'>;

export default function SharedEstimatePage() {
  const { token } = useParams<{ token: string }>();
  const [estimate, setEstimate] = useState<SharedEstimate | null>(null);
  const [password, setPassword] = useState('');
  const [needsPassword, setNeedsPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setEstimate(null);
    setLoading(true);
    setNeedsPassword(false);
    setError('');
    fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/shared/${encodeURIComponent(token || '')}`, {
      signal: controller.signal, cache: 'no-store', referrerPolicy: 'no-referrer',
    }).then(async response => {
      if (response.status === 401) { setNeedsPassword(true); return; }
      if (!response.ok) throw new Error('This share link has expired or is unavailable.');
      setEstimate(await response.json());
    }).catch(reason => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Unable to load estimate.');
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [token]);

  async function unlock(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/shared/${encodeURIComponent(token || '')}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }), cache: 'no-store', referrerPolicy: 'no-referrer',
      });
      if (!response.ok) throw new Error(response.status === 401 ? 'Incorrect password.' : 'This share link is unavailable.');
      setEstimate(await response.json());
      setNeedsPassword(false);
      setPassword('');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load estimate.');
    } finally { setLoading(false); }
  }

  const money = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  return <main style={{ maxWidth: 900, margin: 'auto', padding: '2rem', color: 'var(--text-primary)' }}>
    <Link to="/">Predictify</Link>
    <p>Shared estimate · Read only</p>
    {loading && <p role="status">Loading estimate…</p>}
    {error && <p role="alert">{error}</p>}
    {needsPassword && <form onSubmit={unlock}>
      <label htmlFor="share-password">Share password</label>
      <input id="share-password" type="password" autoComplete="current-password" value={password} maxLength={72} required onChange={event => setPassword(event.target.value)} />
      <button className="btn-primary" disabled={loading} type="submit">Open estimate</button>
    </form>}
    {estimate && <>
      <h1>{estimate.project_name}</h1>
      <p>Version {estimate.version} · {new Date(estimate.created_at).toLocaleDateString()}</p>
      <h2>{money(estimate.outputs.cost_likely_usd)}</h2>
      <p>Estimated cost range: {money(estimate.outputs.cost_min_usd)}–{money(estimate.outputs.cost_max_usd)}</p>
      <p>Effort: {estimate.outputs.effort_likely_hours.toLocaleString()} hours · Timeline: {estimate.outputs.timeline_likely_weeks} weeks</p>
      <p style={{ color: RISK_COLORS[estimate.outputs.risk_level] }}>Risk: {estimate.outputs.risk_level}</p>
      <p>Heuristic confidence: {estimate.outputs.confidence_pct}%. This score and effort range are not calibrated probabilities.</p>
      <h2>Project inputs</h2>
      <p>{estimate.inputs.project_type} · {estimate.inputs.team_size} people · {estimate.inputs.duration_months} months · {estimate.inputs.complexity} complexity</p>
      <p>{estimate.inputs.tech_stack.join(', ')}</p>
      <h2>Risk factors</h2>
      <ul>{estimate.outputs.top_risks.map(risk => <li key={risk.name}><strong>{risk.name} ({risk.severity})</strong>: {risk.description}</li>)}</ul>
      <p>{estimate.outputs.model_explanation}</p>
      <p>{estimate.outputs.benchmark_comparison}</p>
    </>}
  </main>;
}
