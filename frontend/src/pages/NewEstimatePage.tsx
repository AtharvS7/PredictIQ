import { useTheme } from '@/components/ThemeProvider';
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useToast } from '@/App';
import { useAuthStore } from '@/store/authStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { uploadDocumentFile, analyzeEstimate, createManualEstimate, extractDocumentParams } from '@/lib/api';
import {
  Upload,
  FileText,
  Check,
  ArrowLeft,
  Loader2,
  X,
  Brain,
  Zap,
} from 'lucide-react';

const PROJECT_TYPES = [
  'Web App',
  'Mobile App',
  'API/Backend',
  'ML/AI System',
  'Data Platform',
  'Enterprise Software',
  'Other',
];

const COMPLEXITIES = ['Low', 'Medium', 'High', 'Very High'];
const METHODOLOGIES = ['Agile', 'Waterfall', 'Hybrid'];

const ACCEPTED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

/* ── shared inline-style helpers ──────────────────────── */

const fieldStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: 8,
  border: '1px solid var(--border-color)',
  background: 'var(--bg-surface)',
  color: 'var(--text-primary)',
  fontSize: '0.875rem',
  transition: 'border-color 0.15s',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: 6,
};

const hintStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: 'var(--text-tertiary)',
  marginTop: 4,
};

export default function NewEstimatePage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { user } = useAuthStore();

  const currency = useCurrencyStore((s) => s.currency);
  const getRate = useCurrencyStore((s) => s.getRate);

  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const [step, setStep] = useState(1);
  const [useManual, setUseManual] = useState(false);

  /* Step 1 — Upload */
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  /* Step 3 — Processing */
  const [processing, setProcessing] = useState(false);
  const [estimateError, setEstimateError] = useState<string | null>(null);
  const processingStep = 0;

  const processingSteps = [
    'Waiting for your estimate...',
  ];

  /* Step 2 — Parameters */
  const [params, setParams] = useState({
    project_name: '',
    project_type: 'Web App',
    team_size: 5,
    duration_months: 6,
    complexity: 'Medium',
    methodology: 'Agile',
    hourly_rate_usd: 75,
    tech_stack: '' as string,
    integration_count: 2,
    volatility_score: 3,
    team_experience: 2,
  });

  /* ── Handlers ───────────────────────────────────────── */

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);

      const droppedFile = e.dataTransfer.files[0];

      if (droppedFile && ACCEPTED_TYPES.includes(droppedFile.type)) {
        setFile(droppedFile);
      } else {
        addToast('error', 'Only PDF, DOCX, and TXT files are supported');
      }
    },
    [addToast]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];

    if (!selected) return;

    if (!ACCEPTED_TYPES.includes(selected.type)) {
      addToast('error', 'Only PDF, DOCX, and TXT files are supported');
      return;
    }

    if (selected.size > 10 * 1024 * 1024) {
      addToast('error', 'File must be under 10MB');
      return;
    }

    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file || !user) return;

    setUploading(true);
    setUploadProgress(0);

    const interval = setInterval(() => {
        setUploadProgress((p) => Math.min(p + 10, 60));
      }, 200);
    try {
      // Step 1: Upload the file
      const { data } = await uploadDocumentFile(file);

      clearInterval(interval);
      setUploadProgress(70);
      setDocumentId(data.id);

      // Step 2: Run NLP extraction to pre-fill parameters
      try {
        setUploadProgress(80);
        const extractRes = await extractDocumentParams(data.id);
        const nlp = extractRes.data;
        setUploadProgress(95);

        // Map NLP results to form fields
        const techArray: string[] = nlp.tech_stack || [];
        const expValue = nlp.team_experience;
        setParams({
          project_name: nlp.project_name || file.name.replace(/\.[^/.]+$/, ''),
          project_type: nlp.project_type || 'Web App',
          team_size: nlp.team_size || 5,
          duration_months: nlp.duration_months || 6,
          complexity: nlp.complexity || 'Medium',
          methodology: nlp.methodology || 'Agile',
          hourly_rate_usd: 75,
          tech_stack: techArray.join(', '),
          integration_count: nlp.integration_count ?? 2,
          volatility_score: nlp.volatility_score || 3,
          team_experience: typeof expValue === 'number' ? expValue : 2,
        });

        addToast('success', 'Document analyzed — parameters extracted!');
      } catch {
        setDocumentId(null);
        addToast('error', 'Document extraction failed. Try another document or choose manual entry.');
        return;
      }

      setUploadProgress(100);
      setStep(2);
    } catch {
      addToast('error', 'Upload failed');
    } finally {
      clearInterval(interval);
      setUploading(false);
    }
  };

  const handleEstimate = async () => {
    if (processing) return;
    setEstimateError(null);
    setStep(3);
    setProcessing(true);

    try {
      const techArray = params.tech_stack
        ? params.tech_stack.split(',').map((t) => t.trim()).filter(Boolean)
        : [];

      let response;

      if (documentId && !useManual) {
        response = await analyzeEstimate({
          document_id: documentId,
          overrides: { ...params, tech_stack: techArray },
        });
      } else {
        response = await createManualEstimate({
          ...params,
          tech_stack: techArray,
        });
      }

      addToast('success', 'Estimate generated!');
      navigate(`/estimate/${response.data.estimate_id}/results`);
    } catch (error: unknown) {
      const status = (error as { response?: { status?: number } })?.response?.status;
      const message = status === 503
        ? 'Prediction service is unavailable. Your inputs are preserved; try again after the service is restored.'
        : 'Could not generate the estimate. Check your inputs and try again.';
      setEstimateError(message);
      addToast('error', message);
      setStep(2);
    } finally {
      setProcessing(false);
    }
  };

  /* ── Button style (respects theme) ──────────────────── */

  const primaryBtnStyle: React.CSSProperties = {
    padding: '10px 18px',
    borderRadius: 8,
    background: isDark ? 'black' : 'white',
    color: isDark ? 'white' : 'black',
    border: isDark ? '1px solid white' : '1px solid black',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    fontWeight: 600,
    fontSize: '0.875rem',
    transition: 'all 0.2s ease',
  };

  const secondaryBtnStyle: React.CSSProperties = {
    ...primaryBtnStyle,
    background: 'transparent',
    color: 'var(--text-primary)',
    border: '1px solid var(--border-color)',
  };

  /* ── Render ─────────────────────────────────────────── */

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <SEOHead title="New Estimate" description="Create a new project cost estimate by uploading a document or entering parameters manually." />
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: '2rem',
            maxWidth: 820,
            margin: '0 auto',
            width: '100%',
          }}
        >
          {/* ── Progress Steps ─────────────────────────── */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 32,
              justifyContent: 'center',
            }}
          >
            {['Upload', 'Parameters', 'Generate'].map((label, i) => (
              <div
                key={i}
                className="estimate-step"
                aria-current={step === i + 1 ? 'step' : undefined}
                style={{ display: 'flex', alignItems: 'center', gap: 8 }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background:
                      step > i + 1
                        ? 'var(--color-success)'
                        : step === i + 1
                          ? isDark ? 'white' : 'black'
                          : 'var(--bg-elevated)',
                    color:
                      step > i + 1
                        ? 'white'
                        : step === i + 1
                          ? isDark ? 'black' : 'white'
                          : 'var(--text-tertiary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 600,
                    fontSize: '0.8125rem',
                    transition: 'all 0.3s',
                  }}
                >
                  {step > i + 1 ? <Check size={14} /> : i + 1}
                </div>

                <span
                  style={{
                    fontSize: '0.8125rem',
                    fontWeight: step === i + 1 ? 600 : 400,
                    color:
                      step === i + 1
                        ? 'var(--text-primary)'
                        : 'var(--text-tertiary)',
                  }}
                >
                  {label}
                </span>

                {i < 2 && (
                  <div
                    className="estimate-step-connector"
                    style={{
                      width: 40,
                      height: 1,
                      background: 'var(--border-color)',
                    }}
                  />
                )}
              </div>
            ))}
          </div>

          {/* ══════════════════════════════════════════════
              STEP 1 — Upload
             ══════════════════════════════════════════════ */}
          {step === 1 && (
            <div className="card" style={{ padding: 32 }}>
              <h2
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  marginBottom: 8,
                  textAlign: 'center',
                  color: 'var(--text-primary)',
                }}
              >
                Upload Your Project Document
              </h2>

              <p
                style={{
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  marginBottom: 24,
                  textAlign: 'center',
                }}
              >
                Drop a project spec, SRS, or proposal.
              </p>

              {/* Drag & Drop */}
              <div
                onDrop={handleDrop}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onClick={() =>
                  document.getElementById('file-input')?.click()
                }
                style={{
                  border: `2px dashed ${dragOver
                      ? 'var(--color-primary)'
                      : 'var(--border-color)'
                    }`,
                  borderRadius: 16,
                  padding: 48,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: 220,
                  flexDirection: 'column',
                  gap: 12,
                  textAlign: 'center',
                }}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
                <button type="button" style={{ ...secondaryBtnStyle, minHeight: 44 }}
                  onClick={(event) => { event.stopPropagation(); document.getElementById('file-input')?.click(); }}>
                  Choose document
                </button>

                {file ? (
                  <div>
                    <FileText size={40} />
                    <p
                      style={{
                        fontWeight: 600,
                        marginTop: 12,
                        color: 'var(--text-primary)',
                      }}
                    >
                      {file.name}
                    </p>
                    <p
                      style={{
                        fontSize: '0.8125rem',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                      style={{
                        marginTop: 12,
                        background: 'transparent',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                        padding: '6px 16px',
                        borderRadius: 8,
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        fontSize: '0.8125rem',
                      }}
                    >
                      <X size={14} /> Remove
                    </button>
                  </div>
                ) : (
                  <div>
                    <Upload size={40} />
                    <p
                      style={{
                        fontWeight: 500,
                        marginTop: 12,
                        color: 'var(--text-primary)',
                      }}
                    >
                      Drag & drop your file here
                    </p>
                    <p
                      style={{
                        fontSize: '0.8125rem',
                        color: 'var(--text-secondary)',
                        marginTop: 4,
                      }}
                    >
                      PDF, DOCX, or TXT • Max 10MB
                    </p>
                  </div>
                )}
              </div>

              {/* Upload Progress */}
              {uploading && (
                <div style={{ marginTop: 16 }}>
                  <div
                    style={{
                      height: 6,
                      background: 'var(--bg-elevated)',
                      borderRadius: 3,
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        background: isDark ? 'white' : 'black',
                        width: `${uploadProgress}%`,
                        borderRadius: 3,
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </div>
                  <p style={{ ...hintStyle, marginTop: 4 }}>
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div
                style={{
                  display: 'flex',
                  gap: 12,
                  marginTop: 24,
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <button
                  onClick={() => {
                    setUseManual(true);
                    setStep(2);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-primary)',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                  }}
                >
                  Skip — enter parameters manually →
                </button>

                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  style={{
                    ...primaryBtnStyle,
                    opacity: !file || uploading ? 0.5 : 1,
                  }}
                >
                  {uploading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Upload size={16} />
                  )}
                  Upload & Continue
                </button>
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════
              STEP 2 — Parameters
             ══════════════════════════════════════════════ */}
          {step === 2 && (
            <form className="card" style={{ padding: 32 }}
              onSubmit={(event) => { event.preventDefault(); void handleEstimate(); }}>
              {estimateError && <p role="alert" style={{ color: 'var(--color-danger)', marginBottom: 16 }}>{estimateError}</p>}
              <h2
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  marginBottom: 8,
                  textAlign: 'center',
                  color: 'var(--text-primary)',
                }}
              >
                {useManual
                  ? 'Enter Project Parameters'
                  : 'Confirm Extracted Parameters'}
              </h2>

              <p
                style={{
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  marginBottom: 24,
                  textAlign: 'center',
                }}
              >
                {useManual
                  ? 'Fill in the project details to generate your estimate.'
                  : 'Review and correct if needed. Fields are pre-filled from document analysis.'}
              </p>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 240px), 1fr))',
                  gap: 16,
                }}
              >
                {/* Project Name — full width */}
                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={labelStyle} htmlFor="estimate-project_name">Project Name</label>
                  <input
                    style={fieldStyle}
                    id="estimate-project_name" value={params.project_name}
                    onChange={(e) =>
                      setParams({ ...params, project_name: e.target.value })
                    }
                    placeholder="My Project"
                    required
                    maxLength={200}
                    pattern=".*\S.*"
                  />
                </div>

                {/* Project Type */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-project_type">Project Type</label>
                  <select
                    style={fieldStyle}
                    id="estimate-project_type" value={params.project_type}
                    onChange={(e) =>
                      setParams({ ...params, project_type: e.target.value })
                    }
                  >
                    {PROJECT_TYPES.map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </div>

                {/* Complexity */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-complexity">Complexity</label>
                  <select
                    style={fieldStyle}
                    id="estimate-complexity" value={params.complexity}
                    onChange={(e) =>
                      setParams({ ...params, complexity: e.target.value })
                    }
                  >
                    {COMPLEXITIES.map((c) => (
                      <option key={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Team Size */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-team_size">Team Size</label>
                  <input
                    type="number"
                    style={fieldStyle}
                    min={1}
                    max={100}
                    id="estimate-team_size" value={params.team_size}
                    onChange={(e) =>
                      setParams({ ...params, team_size: Number(e.target.value) })
                    }
                  />
                </div>

                {/* Duration */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-duration_months">Duration (months)</label>
                  <input
                    type="number"
                    style={fieldStyle}
                    min={1}
                    max={60}
                    step="any"
                    id="estimate-duration_months" value={params.duration_months}
                    onChange={(e) =>
                      setParams({
                        ...params,
                        duration_months: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Methodology */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-methodology">Methodology</label>
                  <select
                    style={fieldStyle}
                    id="estimate-methodology" value={params.methodology}
                    onChange={(e) =>
                      setParams({ ...params, methodology: e.target.value })
                    }
                  >
                    {METHODOLOGIES.map((m) => (
                      <option key={m}>{m}</option>
                    ))}
                  </select>
                </div>

                {/* Hourly Rate + Currency */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-rate">Hourly Rate ({currency}/hour)</label>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <input
                      type="number"
                      style={{ ...fieldStyle, flex: 1 }}
                      min={10 * getRate()}
                      max={500 * getRate()}
                      step="any"
                      required
                      id="estimate-rate" value={Number((params.hourly_rate_usd * getRate()).toFixed(2))}
                      onChange={(e) =>
                        setParams({
                          ...params,
                          hourly_rate_usd: Number(e.target.value) / getRate(),
                        })
                      }
                    />
                    <CurrencySelector compact />
                  </div>
                  {currency !== 'USD' && (
                    <p style={hintStyle}>
                      ≈ ${params.hourly_rate_usd.toFixed(2)} USD/hr
                    </p>
                  )}
                </div>

                {/* Technology Stack — full width */}
                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={labelStyle} htmlFor="estimate-tech">
                    Technology Stack (comma-separated)
                  </label>
                  <input
                    style={fieldStyle}
                    id="estimate-tech" value={params.tech_stack}
                    onChange={(e) =>
                      setParams({ ...params, tech_stack: e.target.value })
                    }
                    placeholder="React, FastAPI, PostgreSQL, Python"
                  />
                </div>

                {/* External Integrations */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-integration_count">External Integrations</label>
                  <input
                    type="number"
                    style={fieldStyle}
                    min={0}
                    max={15}
                    id="estimate-integration_count" value={params.integration_count}
                    onChange={(e) =>
                      setParams({
                        ...params,
                        integration_count: Number(e.target.value),
                      })
                    }
                  />
                  <p style={hintStyle}>
                    Third-party APIs, payment gateways, CRM integrations
                  </p>
                </div>

                {/* Requirements Volatility */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-volatility_score">Requirements Volatility</label>
                  <select
                    style={fieldStyle}
                    id="estimate-volatility_score" value={params.volatility_score}
                    onChange={(e) =>
                      setParams({
                        ...params,
                        volatility_score: Number(e.target.value),
                      })
                    }
                  >
                    <option value={1}>1 — Locked / Fixed Scope</option>
                    <option value={2}>2 — Mostly Stable</option>
                    <option value={3}>3 — Moderate Changes</option>
                    <option value={4}>4 — Evolving / Iterative</option>
                    <option value={5}>5 — Highly Volatile</option>
                  </select>
                </div>

                {/* Team Experience */}
                <div>
                  <label style={labelStyle} htmlFor="estimate-experience">Team Experience</label>
                  <select
                    style={fieldStyle}
                    id="estimate-experience" value={Math.round(params.team_experience)}
                    onChange={(e) =>
                      setParams({ ...params, team_experience: Number(e.target.value) })
                    }
                  >
                    <option value="1">Junior (0-2 yrs avg)</option>
                    <option value="2">Mixed (2-5 yrs avg)</option>
                    <option value="3">Senior (5-10 yrs avg)</option>
                    <option value="4">Expert (10+ yrs avg)</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginTop: 24,
                }}
              >
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  style={secondaryBtnStyle}
                >
                  <ArrowLeft size={16} /> Back
                </button>

                <button
                  type="submit"
                  disabled={processing || !params.project_name.trim()}
                  style={{
                    ...primaryBtnStyle,
                    opacity: !params.project_name ? 0.5 : 1,
                  }}
                >
                  Generate Estimate <Zap size={16} />
                </button>
              </div>
            </form>
          )}

          {/* ══════════════════════════════════════════════
              STEP 3 — Processing
             ══════════════════════════════════════════════ */}
          {step === 3 && (
            <div
              className="card"
              role="status"
              aria-live="polite"
              style={{ padding: 48, textAlign: 'center' }}
            >
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: '50%',
                  background: isDark
                    ? 'white'
                    : 'black',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 24px',
                }}
              >
                <Brain size={28} color={isDark ? 'black' : 'white'} />
              </div>

              <h2
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  marginBottom: 8,
                  color: 'var(--text-primary)',
                }}
              >
                Generating Your Estimate
              </h2>

              <p
                style={{
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  marginBottom: 32,
                }}
              >
                Our AI is analyzing your project parameters...
              </p>

              <div style={{ maxWidth: 400, margin: '0 auto' }}>
                {processingSteps.map((label, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '10px 0',
                      opacity: processingStep >= i ? 1 : 0.3,
                      transition: 'opacity 0.3s',
                    }}
                  >
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        background:
                          processingStep > i
                            ? 'var(--color-success)'
                            : processingStep === i
                              ? isDark ? 'white' : 'black'
                              : 'var(--bg-elevated)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {processingStep > i ? (
                        <Check size={12} color="white" />
                      ) : processingStep === i ? (
                        <div
                          style={{
                            width: 10,
                            height: 10,
                            border: `2px solid ${isDark ? 'black' : 'white'}`,
                            borderTopColor: 'transparent',
                            borderRadius: '50%',
                            animation: 'spin 0.8s linear infinite',
                          }}
                        />
                      ) : null}
                    </div>

                    <span
                      style={{
                        fontSize: '0.875rem',
                        fontWeight: processingStep === i ? 600 : 400,
                        color:
                          processingStep >= i
                            ? 'var(--text-primary)'
                            : 'var(--text-tertiary)',
                      }}
                    >
                      {label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
