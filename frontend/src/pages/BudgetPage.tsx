import { useEffect, useState, type FormEvent } from 'react';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import { listBudgets, saveBudget, type BudgetTask, type SavedBudget } from '@/lib/budgets';
import { useAuthStore } from '@/store/authStore';
import './BudgetPage.css';

const emptyTask = () => ({ key: crypto.randomUUID(), name: '', low_hours: '', likely_hours: '', high_hours: '', hourly_rate_usd: '' });
const money = (value: string) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value));
const numericFields = [
  ['low_hours', 'Low hours', 100000], ['likely_hours', 'Likely hours', 100000],
  ['high_hours', 'High hours', 100000], ['hourly_rate_usd', 'Rate (USD/hour)', 10000],
] as const;

export default function BudgetPage() {
  const [project, setProject] = useState('');
  const [contingency, setContingency] = useState('0');
  const [tasks, setTasks] = useState([emptyTask()]);
  const [saved, setSaved] = useState<SavedBudget[]>([]);
  const [selected, setSelected] = useState<SavedBudget | null>(null);
  const [error, setError] = useState('');
  const [listError, setListError] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [reload, setReload] = useState(0);
  const role = useAuthStore(state => state.role);
  const canWrite = role !== 'viewer';

  useEffect(() => {
    let cancelled = false;
    listBudgets(offset).then(rows => {
      if (!cancelled) { setSaved(rows); setListError(''); }
    }).catch(() => { if (!cancelled) setListError('Saved budgets could not be loaded. Please retry.'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [offset, reload]);

  const changeTask = (key: string, field: keyof BudgetTask, value: string) => {
    setTasks(current => current.map(task => task.key === key ? { ...task, [field]: value } : task));
    setSelected(null);
  };
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setError('');
    if (!project.trim() || tasks.some(task => !task.name.trim())) {
      setError('Enter a project name and a name for every task.'); return;
    }
    if (tasks.some(task => Number(task.low_hours) > Number(task.likely_hours) || Number(task.likely_hours) > Number(task.high_hours))) {
      setError('For every task, low hours must be no greater than likely hours, and likely hours no greater than high hours.'); return;
    }
    setBusy(true);
    try {
      const result = await saveBudget({ project_name: project, contingency_pct: contingency,
        tasks: tasks.map(({ name, low_hours, likely_hours, high_hours, hourly_rate_usd }) => ({ name, low_hours, likely_hours, high_hours, hourly_rate_usd })) });
      setSelected(result);
      setOffset(0); setLoading(true); setReload(value => value + 1);
    } catch {
      setError('The budget could not be saved. Your inputs are still here. Check your connection and inputs, then retry.');
    } finally { setBusy(false); }
  };

  return <div className="budget-page">
    <SEOHead title="Budget planner" description="Plan project costs from your own task hours and rates." />
    <Navbar />
    <div className="budget-workspace"><Sidebar /><main className="budget-main">
      <header><p className="budget-eyebrow">MANUAL PLANNING</p><h1>Build a budget you can explain.</h1>
        <p>Break the work into tasks. Supply your hours and rates, then save a transparent cost range.</p>
        <p className="budget-notice">This is a calculation from your assumptions, not an AI prediction or a statistically calibrated range. Taxes and non-labour expenses are excluded.</p>
      </header>
      {!canWrite && <p role="status">Your account has read-only access. You can open saved budgets below.</p>}
      {canWrite && <form onSubmit={submit} className="budget-form">
        <fieldset disabled={busy}>
          <legend>Planning assumptions</legend>
          <div className="budget-project-fields">
            <label>Project name<input required maxLength={200} value={project} onChange={e => { setProject(e.target.value); setSelected(null); }} /></label>
            <label>Contingency (%)<input type="number" required min="0" max="100" step="0.01" value={contingency} onChange={e => { setContingency(e.target.value); setSelected(null); }} /></label>
          </div>
          <p>Contingency increases all cost scenarios by your chosen percentage; it does not change effort hours.</p>
          {tasks.map((task, index) => <fieldset className="budget-task" key={task.key}>
            <legend>Task {index + 1}</legend>
            <label>Task name<input required maxLength={200} value={task.name} onChange={e => changeTask(task.key, 'name', e.target.value)} /></label>
            <div className="budget-task-numbers">{numericFields.map(([field, label, max]) => <label key={field}>{label}
              <input type="number" required min="0" max={max} step="0.01" value={task[field]} onChange={e => changeTask(task.key, field, e.target.value)} />
            </label>)}</div>
            <button type="button" className="btn btn-secondary" disabled={tasks.length === 1} aria-label={`Remove task ${index + 1}`}
              onClick={() => { setTasks(current => current.filter(item => item.key !== task.key)); setSelected(null); }}>Remove task</button>
          </fieldset>)}
          <div className="budget-actions">
            <button type="button" className="btn btn-secondary" disabled={tasks.length >= 100} onClick={() => { setTasks(current => [...current, emptyTask()]); setSelected(null); }}>Add task</button>
            <button type="submit" className="btn btn-primary">{busy ? 'Saving budget…' : 'Calculate and save budget'}</button>
          </div>
        </fieldset>
        {error && <p role="alert" className="budget-notice">{error}</p>}
      </form>}
      {selected && <section className="budget-result" aria-label="Saved budget result" aria-live="polite">
        <h2>{selected.inputs.project_name}</h2><p>Saved {new Date(selected.created_at).toLocaleString()} · Manual task budget</p>
        <div className="budget-scenarios">{(['low', 'likely', 'high'] as const).map(scenario => <div key={scenario}>
          <h3>{scenario === 'likely' ? 'Likely scenario' : `${scenario === 'low' ? 'Low' : 'High'} scenario`}</h3>
          <strong>{money(selected.totals[`${scenario}_cost_usd`])}</strong><p>{selected.totals[`${scenario}_hours`]} effort hours</p>
        </div>)}</div>
        <p>Sum of task hours × task rates, plus {selected.inputs.contingency_pct}% contingency. Rounded once to cents. Effort hours are not a calendar schedule.</p>
        <details><summary>View saved assumptions</summary><ul>{selected.inputs.tasks.map((task, index) => <li key={index}>
          {task.name}: {task.low_hours} / {task.likely_hours} / {task.high_hours} hours at {money(task.hourly_rate_usd)}/hour
        </li>)}</ul></details>
      </section>}
      <section className="budget-history" aria-label="Saved budgets"><h2>Saved budgets</h2>
        {loading ? <p role="status">Loading saved budgets…</p> : listError ? <div role="alert"><p>{listError}</p>
          <button className="btn btn-secondary" onClick={() => { setLoading(true); setReload(value => value + 1); }}>Retry loading budgets</button></div> : <>
          {!saved.length && <p>No budgets on this page.</p>}
          <ul>{saved.map(budget => <li key={budget.id}><button type="button" onClick={() => setSelected(budget)}>
            <span>{budget.inputs.project_name}</span><span>{money(budget.totals.likely_cost_usd)} · {new Date(budget.created_at).toLocaleDateString()}</span>
          </button></li>)}</ul>
        </>}
        <div className="budget-actions">
          <button className="btn btn-secondary" disabled={offset === 0 || loading} onClick={() => { setLoading(true); setOffset(value => Math.max(0, value - 20)); }}>Previous</button>
          <button className="btn btn-secondary" disabled={saved.length < 20 || loading || !!listError} onClick={() => { setLoading(true); setOffset(value => value + 20); }}>Next</button>
        </div>
      </section>
    </main></div>
  </div>;
}
