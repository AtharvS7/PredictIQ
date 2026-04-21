import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useToast } from '@/App';
import { useAuthStore } from '@/store/authStore';
import { uploadDocumentFile, analyzeEstimate } from '@/lib/api';
import {
  Upload,
  FileText,
  Loader2,
  X,
} from 'lucide-react';

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

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const [params, setParams] = useState({
    project_name: '',
  });

  const isDark =
    document.documentElement.getAttribute('data-theme') === 'dark';

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

    try {
      const interval = setInterval(() => {
        setUploadProgress((p) => Math.min(p + 15, 90));
      }, 200);

      // Upload file directly to backend API (Firebase/Neon)
      const { data } = await uploadDocumentFile(file);

      clearInterval(interval);
      setUploadProgress(100);

      setDocumentId(data.id);

      setParams((prev) => ({
        ...prev,
        project_name: file.name.replace(/\.[^/.]+$/, ''),
      }));

      addToast('success', 'Document uploaded successfully!');
      setStep(2);
    } catch {
      addToast('error', 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: '2rem',
            maxWidth: 800,
            margin: '0 auto',
          }}
        >
          {step === 1 && (
            <div className="card" style={{ padding: 32 }}>
              <h2
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  marginBottom: 8,
                  color: 'var(--text-primary)',
                  textAlign: 'center',
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

              {/* Drag & Drop Box */}

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

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                      style={{
                        marginTop: 12,
                        background: 'none',
                        border: '1px solid var(--color-danger)',
                        color: 'var(--color-danger)',
                        padding: '6px 16px',
                        borderRadius: 8,
                        cursor: 'pointer',
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

              {/* Buttons */}

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
                    opacity: !file || uploading ? 0.5 : 1,

                    padding: '10px 18px',
                    borderRadius: 8,

                    background: isDark ? 'black' : 'white',
                    color: isDark ? 'white' : 'black',
                    border: isDark
                      ? '1px solid white'
                      : '1px solid black',

                    cursor: 'pointer',

                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,

                    transition: 'all 0.2s ease',
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
        </main>
      </div>
    </div>
  );
}