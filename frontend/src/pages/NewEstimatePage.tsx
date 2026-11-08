import { useTheme } from '@/components/ThemeProvider';
import { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useToast } from '@/App';
import { useAuthStore } from '@/store/authStore';
import { useCurrencyStore } from '@/store/currencyStore';
import {
  uploadDocumentFile,
  analyzeEstimate,
  createManualEstimate,
  extractDocumentParams,
  exportPDF,
  exportJSON,
  createShareLink,
  duplicateEstimate,
} from '@/lib/api';
import {
  Upload,
  FileText,
  Check,
  ArrowLeft,
  Loader2,
  X,
  Sparkles,
  Layers,
  Target,
  Zap,
  ArrowRight,
  Shield,
  HelpCircle,
} from 'lucide-react';
import type { EstimateResult } from '@/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { Heading, Text } from '@/components/shared/Typography';
import { FunctionalSizeCard } from '@/components/estimate/FunctionalSizeCard';
import { PlanningCapacityCard } from '@/components/estimate/PlanningCapacityCard';
import { EstimationResultView } from '@/components/estimate/EstimationResultView';

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

/* ── Shared style helpers ────────────────────────────── */
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

  const currency = useCurrencyStore((s) => s.currency) || 'USD';
  const rawGetRate = useCurrencyStore((s) => s.getRate);
  const getRate = typeof rawGetRate === 'function' ? rawGetRate : () => 1;
  const rawSymbol = useCurrencyStore((s) => s.symbol);
  const currencySymbol = typeof rawSymbol === 'function' ? rawSymbol() : '$';

  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const [step, setStep] = useState(1);
  const stepHeading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    stepHeading.current?.focus();
  }, [step]);

  const [useManual, setUseManual] = useState(false);

  /* Step 1 — Upload & Functional Size */
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [featureCount, setFeatureCount] = useState<number>(12);

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
    size_fp: undefined as number | undefined,
  });

  /* Step 3 — Processing & Calibrated Result View */
  const [processing, setProcessing] = useState(false);
  const [estimateError, setEstimateError] = useState<string | null>(null);
  const [generatedResult, setGeneratedResult] = useState<EstimateResult | null>(null);

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
        const extractedFeatures = nlp.feature_count ?? 15;
        const extractedIntegrations = nlp.integration_count ?? 2;

        setFeatureCount(extractedFeatures);
        setParams({
          project_name: nlp.project_name || file.name.replace(/\.[^/.]+$/, ''),
          project_type: nlp.project_type || 'Web App',
          team_size: nlp.team_size || 5,
          duration_months: nlp.duration_months || 6,
          complexity: nlp.complexity || 'Medium',
          methodology: nlp.methodology || 'Agile',
          hourly_rate_usd: 75,
          tech_stack: techArray.join(', '),
          integration_count: extractedIntegrations,
          volatility_score: nlp.volatility_score || 3,
          team_experience: typeof expValue === 'number' ? expValue : 2,
          size_fp: nlp.size_fp ?? undefined,
        });

        addToast('success', 'Document analyzed — functional parameters extracted!');
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
    setProcessing(true);

    try {
      const techArray = params.tech_stack
        ? params.tech_stack.split(',').map((t) => t.trim()).filter(Boolean)
        : [];

      let response;

      if (documentId && !useManual) {
        response = await analyzeEstimate({
          document_id: documentId,
          overrides: { ...params, tech_stack: techArray, feature_count: featureCount },
        });
      } else {
        response = await createManualEstimate({
          ...params,
          tech_stack: techArray,
        });
      }

      addToast('success', 'Calibrated estimate generated!');
      setGeneratedResult(response.data as EstimateResult);
      setStep(3);
    } catch (error: unknown) {
      const status = (error as { response?: { status?: number } })?.response?.status;
      const message =
        status === 503
          ? 'Prediction service is unavailable. Your inputs are preserved; try again after the service is restored.'
          : 'Could not generate the estimate. Check your inputs and try again.';
      setEstimateError(message);
      addToast('error', message);
      setStep(2);
    } finally {
      setProcessing(false);
    }
  };

  /* ── Export Handlers for Step 3 ──────────────────────── */
  const handleExportPDF = async () => {
    if (!generatedResult) return;
    try {
      const currencyCode = useCurrencyStore.getState().currency;
      const response = await exportPDF(generatedResult.estimate_id, currencyCode);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `PredictIQ_Estimate_${generatedResult.estimate_id.slice(0, 8)}_${currencyCode}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast('success', 'PDF exported!');
    } catch {
      addToast('error', 'PDF export failed');
    }
  };

  const handleExportJSON = async () => {
    if (!generatedResult) return;
    try {
      let exportData: unknown = generatedResult;
      try {
        const response = await exportJSON(generatedResult.estimate_id);
        if (response?.data) exportData = response.data;
      } catch {
        // Fallback to generatedResult in memory
      }
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PredictIQ_Estimate_${generatedResult.estimate_id.slice(0, 8)}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast('success', 'JSON exported!');
    } catch {
      addToast('error', 'JSON export failed');
    }
  };

  const handleShare = async () => {
    if (!generatedResult) return;
    try {
      const { data } = await createShareLink(generatedResult.estimate_id, { expires_in_days: 7 });
      await navigator.clipboard.writeText(window.location.origin + data.share_url);
      addToast('success', 'Share link copied to clipboard!');
    } catch {
      addToast('error', 'Failed to create share link');
    }
  };

  const handleDuplicate = async () => {
    if (!generatedResult) return;
    try {
      await duplicateEstimate(generatedResult.estimate_id);
      addToast('success', 'Estimate duplicated');
    } catch {
      addToast('error', 'Duplication failed');
    }
  };

  /* ── Button styles ─────────────────────────────────── */
  const primaryBtnStyle: React.CSSProperties = {
    padding: '10px 18px',
    borderRadius: 8,
    background: isDark ? 'white' : 'black',
    color: isDark ? 'black' : 'white',
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

  /* ── Step definitions ───────────────────────────────── */
  const wizardSteps = [
    { title: 'Requirements & Functional Size', desc: 'Scope calibration' },
    { title: 'Planning Parameters', desc: 'Target constraints' },
    { title: 'Calibrated Results', desc: 'Conformal ranges' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <SEOHead
        title="New Estimate Wizard"
        description="Create a calibrated project estimate with PredictIQ v2.0 Monotone Power-Law with Mondrian Split-Conformal Prediction & Empirical Bayes Shrinkage."
      />
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: '2rem 1.5rem',
            maxWidth: 900,
            margin: '0 auto',
            width: '100%',
          }}
        >
          {/* ── Modern Step Progress Header ──────────────── */}
          <div className="mb-8">
            <div className="flex items-center justify-between gap-2 max-w-xl mx-auto">
              {wizardSteps.map((s, i) => {
                const stepNum = i + 1;
                const isCurrent = step === stepNum;
                const isDone = step > stepNum;

                return (
                  <div
                    key={i}
                    className="flex-1 flex flex-col items-center relative text-center"
                    aria-current={isCurrent ? 'step' : undefined}
                  >
                    <div className="flex items-center w-full justify-center relative">
                      {i > 0 && (
                        <div
                          className={`absolute right-1/2 left-0 -translate-y-1/2 top-4 h-0.5 transition-colors ${
                            isDone ? 'bg-emerald-500' : 'bg-[var(--border-color)]'
                          }`}
                        />
                      )}
                      {i < wizardSteps.length - 1 && (
                        <div
                          className={`absolute left-1/2 right-0 -translate-y-1/2 top-4 h-0.5 transition-colors ${
                            step > stepNum ? 'bg-emerald-500' : 'bg-[var(--border-color)]'
                          }`}
                        />
                      )}

                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold z-10 transition-all ${
                          isDone
                            ? 'bg-emerald-500 text-white shadow-sm'
                            : isCurrent
                            ? isDark
                              ? 'bg-white text-black ring-4 ring-blue-500/20'
                              : 'bg-black text-white ring-4 ring-blue-500/20'
                            : 'bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-color)]'
                        }`}
                      >
                        {isDone ? <Check size={14} className="stroke-[3]" /> : stepNum}
                      </div>
                    </div>

                    <span
                      className={`text-xs mt-2 font-semibold transition-colors px-1 break-words leading-tight ${
                        isCurrent
                          ? 'text-[var(--text-primary)]'
                          : isDone
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-[var(--text-tertiary)]'
                      }`}
                    >
                      {s.title}
                    </span>
                    <span className="text-[10px] text-[var(--text-tertiary)] hidden sm:block">
                      {s.desc}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ══════════════════════════════════════════════
              STEP 1 — Scope & Functional Size Estimation
             ══════════════════════════════════════════════ */}
          {step === 1 && (
            <div className="space-y-6">
              {/* Functional Size & Transparency Feedback Card */}
              <FunctionalSizeCard
                featureCount={featureCount}
                integrationCount={params.integration_count}
                customFp={params.size_fp}
                onFeatureChange={(c) => setFeatureCount(c)}
                onIntegrationChange={(ic) => setParams({ ...params, integration_count: ic })}
                source={useManual ? 'manual' : file ? 'upload' : 'manual'}
              />

              {/* Upload Dropzone Container */}
              <Card variant="elevated" padding="lg">
                <CardHeader className="text-center pb-2">
                  <CardTitle as="h2" ref={stepHeading} tabIndex={-1} className="text-xl sm:text-2xl font-bold">
                    Upload Specification or Enter Requirements
                  </CardTitle>
                  <CardDescription className="text-sm">
                    Drop a project specification, SRS, or architecture document to auto-extract parameters, or enter scope directly.
                  </CardDescription>
                </CardHeader>

                <CardContent className="mt-4">
                  {/* Drag & Drop Area */}
                  <div
                    onDrop={handleDrop}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setDragOver(true);
                    }}
                    onDragLeave={() => setDragOver(false)}
                    onClick={() => document.getElementById('file-input')?.click()}
                    style={{
                      border: `2px dashed ${dragOver ? 'var(--color-primary)' : 'var(--border-color)'}`,
                      borderRadius: 16,
                      padding: '36px 24px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: 200,
                      flexDirection: 'column',
                      gap: 12,
                      textAlign: 'center',
                      background: dragOver ? 'var(--bg-elevated)' : 'transparent',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <input
                      id="file-input"
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                    />

                    <button
                      type="button"
                      style={{ ...secondaryBtnStyle, minHeight: 40 }}
                      onClick={(event) => {
                        event.stopPropagation();
                        document.getElementById('file-input')?.click();
                      }}
                    >
                      Choose document
                    </button>

                    {file ? (
                      <div className="text-center">
                        <FileText size={36} className="mx-auto text-blue-600 dark:text-blue-400" />
                        <p className="font-semibold text-sm mt-2 text-[var(--text-primary)]">{file.name}</p>
                        <p className="text-xs text-[var(--text-secondary)]">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setFile(null);
                          }}
                          className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs text-rose-600 hover:text-rose-700 border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40"
                        >
                          <X size={12} /> Remove file
                        </button>
                      </div>
                    ) : (
                      <div>
                        <Upload size={36} className="mx-auto text-[var(--text-secondary)] opacity-70" />
                        <p className="font-semibold text-sm mt-2 text-[var(--text-primary)]">
                          Drag &amp; drop project document here
                        </p>
                        <p className="text-xs text-[var(--text-tertiary)] mt-1">
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
                      <p style={{ ...hintStyle, marginTop: 4 }}>Analyzing document... {uploadProgress}%</p>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex items-center justify-between gap-4 mt-6 flex-wrap">
                    <button
                      type="button"
                      onClick={() => {
                        setUseManual(true);
                        setStep(2);
                      }}
                      className="text-xs font-semibold text-[var(--color-primary)] hover:underline inline-flex items-center gap-1"
                    >
                      Skip — enter parameters manually <ArrowRight size={14} />
                    </button>

                    <button
                      type="button"
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
                      Upload &amp; Continue
                    </button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* ══════════════════════════════════════════════
              STEP 2 — Planning Parameters & Capacity
             ══════════════════════════════════════════════ */}
          {step === 2 && (
            <div className="space-y-6">
              {/* Real-time Reactive Planning Capacity Card */}
              <PlanningCapacityCard
                teamSize={params.team_size}
                durationMonths={params.duration_months}
                hourlyRateUsd={params.hourly_rate_usd}
                currencySymbol={currencySymbol}
                currencyRate={getRate()}
                currencyCode={currency}
              />

              <form
                className="card"
                style={{ padding: 'clamp(1.25rem, 3.5vw, 2rem)' }}
                onSubmit={(event) => {
                  event.preventDefault();
                  void handleEstimate();
                }}
              >
                {estimateError && (
                  <p role="alert" style={{ color: 'var(--color-danger)', marginBottom: 16 }}>
                    {estimateError}
                  </p>
                )}

                <h2
                  ref={stepHeading}
                  tabIndex={-1}
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    marginBottom: 8,
                    textAlign: 'center',
                    color: 'var(--text-primary)',
                  }}
                >
                  {useManual ? 'Enter Project Parameters' : 'Confirm Extracted Parameters'}
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
                    ? 'Define your project scope and target delivery constraints.'
                    : 'Review and adjust parameters extracted from your document analysis.'}
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
                    <label style={labelStyle} htmlFor="estimate-project_name">
                      Project Name
                    </label>
                    <input
                      style={fieldStyle}
                      id="estimate-project_name"
                      value={params.project_name}
                      onChange={(e) => setParams({ ...params, project_name: e.target.value })}
                      placeholder="e.g. NextGen Mobile Platform"
                      required
                      maxLength={200}
                      pattern=".*\S.*"
                    />
                  </div>

                  {/* Project Type */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-project_type">
                      Project Type
                    </label>
                    <select
                      style={fieldStyle}
                      id="estimate-project_type"
                      value={params.project_type}
                      onChange={(e) => setParams({ ...params, project_type: e.target.value })}
                    >
                      {PROJECT_TYPES.map((t) => (
                        <option key={t}>{t}</option>
                      ))}
                    </select>
                  </div>

                  {/* Complexity */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-complexity">
                      Complexity
                    </label>
                    <select
                      style={fieldStyle}
                      id="estimate-complexity"
                      value={params.complexity}
                      onChange={(e) => setParams({ ...params, complexity: e.target.value })}
                    >
                      {COMPLEXITIES.map((c) => (
                        <option key={c}>{c}</option>
                      ))}
                    </select>
                  </div>

                  {/* Team Size */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-team_size">
                      Team Size
                    </label>
                    <input
                      type="number"
                      style={fieldStyle}
                      min={1}
                      max={100}
                      id="estimate-team_size"
                      value={params.team_size}
                      onChange={(e) => setParams({ ...params, team_size: Number(e.target.value) })}
                    />
                    <p style={hintStyle}>Staffing capacity indicator (Brooks&apos; Law: does not shorten effort)</p>
                  </div>

                  {/* Planned Target Duration */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-duration_months">
                      Planned Target Duration (months)
                    </label>
                    <input
                      type="number"
                      style={fieldStyle}
                      min={1}
                      max={60}
                      step="any"
                      id="estimate-duration_months"
                      value={params.duration_months}
                      onChange={(e) =>
                        setParams({
                          ...params,
                          duration_months: Number(e.target.value),
                        })
                      }
                    />
                    <p style={hintStyle}>Target planning horizon (effort depends strictly on functional size)</p>
                  </div>

                  {/* Methodology */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-methodology">
                      Methodology
                    </label>
                    <select
                      style={fieldStyle}
                      id="estimate-methodology"
                      value={params.methodology}
                      onChange={(e) => setParams({ ...params, methodology: e.target.value })}
                    >
                      {METHODOLOGIES.map((m) => (
                        <option key={m}>{m}</option>
                      ))}
                    </select>
                  </div>

                  {/* Hourly Rate + Currency */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-rate">
                      Hourly Rate ({currency}/hour)
                    </label>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <input
                        type="number"
                        style={{ ...fieldStyle, flex: 1 }}
                        min={10 * getRate()}
                        max={500 * getRate()}
                        step="any"
                        required
                        id="estimate-rate"
                        value={Number((params.hourly_rate_usd * getRate()).toFixed(2))}
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
                      <p style={hintStyle}>≈ ${params.hourly_rate_usd.toFixed(2)} USD/hr</p>
                    )}
                  </div>

                  {/* Technology Stack — full width */}
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle} htmlFor="estimate-tech">
                      Technology Stack (comma-separated)
                    </label>
                    <input
                      style={fieldStyle}
                      id="estimate-tech"
                      value={params.tech_stack}
                      onChange={(e) => setParams({ ...params, tech_stack: e.target.value })}
                      placeholder="React, FastAPI, PostgreSQL, Python"
                    />
                  </div>

                  {/* External Integrations */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-integration_count">
                      External Integrations
                    </label>
                    <input
                      type="number"
                      style={fieldStyle}
                      min={0}
                      max={15}
                      id="estimate-integration_count"
                      value={params.integration_count}
                      onChange={(e) =>
                        setParams({
                          ...params,
                          integration_count: Number(e.target.value),
                        })
                      }
                    />
                    <p style={hintStyle}>Third-party APIs, payment gateways, CRM integrations</p>
                  </div>

                  {/* Requirements Volatility */}
                  <div>
                    <label style={labelStyle} htmlFor="estimate-volatility_score">
                      Requirements Volatility
                    </label>
                    <select
                      style={fieldStyle}
                      id="estimate-volatility_score"
                      value={params.volatility_score}
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
                    <label style={labelStyle} htmlFor="estimate-experience">
                      Team Experience
                    </label>
                    <select
                      style={fieldStyle}
                      id="estimate-experience"
                      value={Math.round(params.team_experience)}
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
                    flexWrap: 'wrap',
                    gap: 12,
                  }}
                >
                  <button type="button" onClick={() => setStep(1)} style={secondaryBtnStyle}>
                    <ArrowLeft size={16} /> Back
                  </button>

                  <button
                    type="submit"
                    disabled={processing || !params.project_name.trim()}
                    style={{
                      ...primaryBtnStyle,
                      opacity: !params.project_name || processing ? 0.5 : 1,
                    }}
                  >
                    {processing ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        Generate Estimate <Zap size={16} />
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* ══════════════════════════════════════════════
              STEP 3 — Result View
             ══════════════════════════════════════════════ */}
          {step === 3 && generatedResult && (
            <div className="space-y-6">
              <EstimationResultView
                estimate={generatedResult}
                onExportPDF={handleExportPDF}
                onExportJSON={handleExportJSON}
                onShare={handleShare}
                onDuplicate={handleDuplicate}
                currencySymbol={currencySymbol}
                currencyRate={getRate()}
                currencyCode={currency}
                showExtendedBreakdown={false}
              />

              {/* Navigation Options Footer */}
              <div className="flex items-center justify-between gap-4 pt-4 border-t border-[var(--border-color)] flex-wrap">
                <button
                  type="button"
                  onClick={() => {
                    setGeneratedResult(null);
                    setStep(1);
                  }}
                  style={secondaryBtnStyle}
                >
                  <ArrowLeft size={15} /> Create Another Estimate
                </button>

                <button
                  type="button"
                  onClick={() => navigate(`/estimate/${generatedResult.estimate_id}/results`)}
                  style={primaryBtnStyle}
                >
                  View Full Breakdown &amp; Charts <ArrowRight size={15} />
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
