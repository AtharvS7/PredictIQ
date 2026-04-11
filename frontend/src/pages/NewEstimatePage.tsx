import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import { useToast } from '@/App';
import { supabase } from '@/lib/supabase';
import { useAuthStore } from '@/store/authStore';
import { confirmDocumentUpload, analyzeEstimate, createManualEstimate } from '@/lib/api';
import {
  Upload, FileText, Check, ArrowRight, ArrowLeft, Loader2, AlertTriangle,
  X, Brain, BarChart3, Zap,
} from 'lucide-react';

const PROJECT_TYPES = ['Web App', 'Mobile App', 'API/Backend', 'ML/AI System', 'Data Platform', 'Enterprise Software', 'Other'];
const COMPLEXITIES = ['Low', 'Medium', 'High', 'Very High'];
const METHODOLOGIES = ['Agile', 'Waterfall', 'Hybrid'];

const ACCEPTED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

export default function NewEstimatePage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { user } = useAuthStore();

  const [step, setStep] = useState(1);
  const [useManual, setUseManual] = useState(false);

  // Step 1: Upload
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  // Step 2: Parameters
  const [params, setParams] = useState({
    project_name: '',
    project_type: 'Web App',
    team_size: 5,
    duration_months: 6,
    complexity: 'Medium',
    methodology: 'Agile',
    hourly_rate_usd: 75,
    tech_stack: '' as string,
  });

  // Step 3: Processing
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);

  const processingSteps = [
    'Analyzing document...',
    'Extracting features...',
    'Running AI model...',
    'Calculating risk...',
    'Building report...',
  ];

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && ACCEPTED_TYPES.includes(droppedFile.type)) {
      setFile(droppedFile);
    } else {
      addToast('error', 'Only PDF, DOCX, and TXT files are supported');
    }
  }, [addToast]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!ACCEPTED_TYPES.includes(selected.type)) {
        addToast('error', 'Only PDF, DOCX, and TXT files are supported');
        return;
      }
      if (selected.size > 10 * 1024 * 1024) {
        addToast('error', 'File must be under 10MB');
        return;
      }
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file || !user) return;
    setUploading(true);
    setUploadProgress(0);

    try {
      const path = `project-docs/${user.id}/${crypto.randomUUID()}-${file.name}`;

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 15, 90));
      }, 200);

      const { error: uploadError } = await supabase.storage
        .from('project-docs')
        .upload(path, file);

      clearInterval(progressInterval);

      if (uploadError) throw uploadError;
      setUploadProgress(95);

      const { data } = await confirmDocumentUpload({
        storage_path: path,
        original_filename: file.name,
        file_size_bytes: file.size,
        mime_type: file.type,
      });

      setUploadProgress(100);
      setDocumentId(data.id);
      setParams((prev) => ({ ...prev, project_name: file.name.replace(/\.[^/.]+$/, '') }));
      addToast('success', 'Document uploaded successfully!');
      setStep(2);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      addToast('error', message);
    } finally {
      setUploading(false);
    }
  };

  const handleEstimate = async () => {
    setStep(3);
    setProcessing(true);

    // Animate processing steps
    for (let i = 0; i < processingSteps.length; i++) {
      setProcessingStep(i);
      await new Promise((r) => setTimeout(r, 800));
    }

    try {
      const techArray = params.tech_stack
        ? params.tech_stack.split(',').map((t: string) => t.trim()).filter(Boolean)
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
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Estimation failed';
      addToast('error', message);
      setStep(2);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: 800, margin: '0 auto' }}>
          {/* Progress Steps */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginBottom: 32,
            justifyContent: 'center',
          }}>
            {['Upload', 'Parameters', 'Generate'].map((label, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: step > i + 1 ? 'var(--color-success)' : step === i + 1 ? 'var(--color-primary)' : 'var(--bg-elevated)',
                  color: step >= i + 1 ? 'white' : 'var(--text-tertiary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 600, fontSize: '0.8125rem',
                  transition: 'all 0.3s',
                }}>
                  {step > i + 1 ? <Check size={14} /> : i + 1}
                </div>
                <span style={{
                  fontSize: '0.8125rem', fontWeight: step === i + 1 ? 600 : 400,
                  color: step === i + 1 ? 'var(--text-primary)' : 'var(--text-tertiary)',
                }}>{label}</span>
                {i < 2 && <div style={{ width: 40, height: 1, background: 'var(--border-color)' }} />}
              </div>
            ))}
          </div>

          {/* Step 1: Upload */}
          {step === 1 && (
            <div className="card animate-fade-in" style={{ padding: 32 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>
                Upload Your Project Document
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: 24 }}>
                Drop a project spec, SRS, or proposal. We'll extract the key parameters automatically.
              </p>

              <div
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                style={{
                  border: `2px dashed ${dragOver ? 'var(--color-primary)' : 'var(--border-color)'}`,
                  borderRadius: 16, padding: 48, textAlign: 'center',
                  transition: 'all 0.2s', cursor: 'pointer',
                  background: dragOver ? 'rgba(26,86,219,0.04)' : 'transparent',
                }}
                onClick={() => document.getElementById('file-input')?.click()}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
                {file ? (
                  <div>
                    <FileText size={40} color="var(--color-primary)" />
                    <p style={{ fontWeight: 600, marginTop: 12, color: 'var(--text-primary)' }}>{file.name}</p>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <button onClick={(e) => { e.stopPropagation(); setFile(null); }} style={{
                      marginTop: 8, background: 'none', border: 'none', cursor: 'pointer',
                      color: 'var(--color-danger)', fontSize: '0.8125rem',
                    }}>
                      <X size={14} /> Remove
                    </button>
                  </div>
                ) : (
                  <div>
                    <Upload size={40} color="var(--text-tertiary)" />
                    <p style={{ fontWeight: 500, marginTop: 12, color: 'var(--text-primary)' }}>
                      Drag & drop your file here
                    </p>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                      PDF, DOCX, or TXT • Max 10MB
                    </p>
                  </div>
                )}
              </div>

              {/* Upload Progress */}
              {uploading && (
                <div style={{ marginTop: 16 }}>
                  <div style={{
                    height: 6, background: 'var(--bg-elevated)', borderRadius: 3, overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%', background: 'var(--color-primary)',
                      width: `${uploadProgress}%`, borderRadius: 3,
                      transition: 'width 0.3s ease',
                    }} />
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}

              <div style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'space-between', alignItems: 'center' }}>
                <button onClick={() => { setUseManual(true); setStep(2); }} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--color-primary)', fontSize: '0.8125rem', fontWeight: 500,
                }}>
                  Skip — enter parameters manually →
                </button>
                <button
                  className="btn-primary"
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  style={{ opacity: !file || uploading ? 0.5 : 1 }}
                >
                  {uploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                  Upload & Continue
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Parameters */}
          {step === 2 && (
            <div className="card animate-fade-in" style={{ padding: 32 }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>
                {useManual ? 'Enter Project Parameters' : 'Confirm Extracted Parameters'}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: 24 }}>
                {useManual ? 'Fill in the project details to generate your estimate.' : 'Review and correct if needed. All fields are pre-filled from document analysis.'}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div style={{ gridColumn: '1 / -1' }}>
                  <label className="label">Project Name</label>
                  <input
                    className="input-field"
                    value={params.project_name}
                    onChange={(e) => setParams({ ...params, project_name: e.target.value })}
                    placeholder="My Project"
                  />
                </div>

                <div>
                  <label className="label">Project Type</label>
                  <select
                    className="input-field"
                    value={params.project_type}
                    onChange={(e) => setParams({ ...params, project_type: e.target.value })}
                  >
                    {PROJECT_TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>

                <div>
                  <label className="label">Complexity</label>
                  <select
                    className="input-field"
                    value={params.complexity}
                    onChange={(e) => setParams({ ...params, complexity: e.target.value })}
                  >
                    {COMPLEXITIES.map((c) => <option key={c}>{c}</option>)}
                  </select>
                </div>

                <div>
                  <label className="label">Team Size</label>
                  <input
                    type="number"
                    className="input-field"
                    min={1} max={100}
                    value={params.team_size}
                    onChange={(e) => setParams({ ...params, team_size: Number(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="label">Duration (months)</label>
                  <input
                    type="number"
                    className="input-field"
                    min={1} max={60}
                    value={params.duration_months}
                    onChange={(e) => setParams({ ...params, duration_months: Number(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="label">Methodology</label>
                  <select
                    className="input-field"
                    value={params.methodology}
                    onChange={(e) => setParams({ ...params, methodology: e.target.value })}
                  >
                    {METHODOLOGIES.map((m) => <option key={m}>{m}</option>)}
                  </select>
                </div>

                <div>
                  <label className="label">Hourly Rate (USD)</label>
                  <input
                    type="number"
                    className="input-field"
                    min={10} max={500}
                    value={params.hourly_rate_usd}
                    onChange={(e) => setParams({ ...params, hourly_rate_usd: Number(e.target.value) })}
                  />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                  <label className="label">Technology Stack (comma-separated)</label>
                  <input
                    className="input-field"
                    value={params.tech_stack}
                    onChange={(e) => setParams({ ...params, tech_stack: e.target.value })}
                    placeholder="React, FastAPI, PostgreSQL, Python"
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
                <button className="btn-secondary" onClick={() => setStep(1)}>
                  <ArrowLeft size={16} /> Back
                </button>
                <button
                  className="btn-primary"
                  onClick={handleEstimate}
                  disabled={!params.project_name}
                  style={{ opacity: !params.project_name ? 0.5 : 1 }}
                >
                  Generate Estimate <Zap size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Processing */}
          {step === 3 && (
            <div className="card animate-fade-in" style={{ padding: 48, textAlign: 'center' }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                background: 'linear-gradient(135deg, #1A56DB, #3B82F6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 24px', animation: 'pulse-glow 2s infinite',
              }}>
                <Brain size={28} color="white" />
              </div>

              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>
                Generating Your Estimate
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: 32 }}>
                Our AI is analyzing your project parameters...
              </p>

              <div style={{ maxWidth: 400, margin: '0 auto' }}>
                {processingSteps.map((label, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    padding: '10px 0',
                    opacity: processingStep >= i ? 1 : 0.3,
                    transition: 'opacity 0.3s',
                  }}>
                    <div style={{
                      width: 24, height: 24, borderRadius: '50%',
                      background: processingStep > i ? 'var(--color-success)' :
                        processingStep === i ? 'var(--color-primary)' : 'var(--bg-elevated)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      {processingStep > i ? (
                        <Check size={12} color="white" />
                      ) : processingStep === i ? (
                        <div style={{
                          width: 10, height: 10, border: '2px solid white',
                          borderTopColor: 'transparent', borderRadius: '50%',
                          animation: 'spin 0.8s linear infinite',
                        }} />
                      ) : null}
                    </div>
                    <span style={{
                      fontSize: '0.875rem', fontWeight: processingStep === i ? 600 : 400,
                      color: processingStep >= i ? 'var(--text-primary)' : 'var(--text-tertiary)',
                    }}>{label}</span>
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
