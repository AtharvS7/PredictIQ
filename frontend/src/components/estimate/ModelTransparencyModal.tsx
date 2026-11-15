import React, { useEffect } from 'react';
import { X, Info } from 'lucide-react';
import type { EstimateResult } from '@/types';

interface ModelTransparencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  tier?: 'A' | 'B' | 'C';
  modelVersion?: string;
  sizeFp?: number | null;
  currencyCode?: string;
  currencyRate?: number;
  estimate?: EstimateResult | null;
}

export const ModelTransparencyModal: React.FC<ModelTransparencyModalProps> = ({
  isOpen,
  onClose,
}) => {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const projectCount = 915;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto bg-slate-950/70 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="about-estimate-title"
      data-testid="model-transparency-modal"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-lg flex flex-col rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-2xl overflow-hidden my-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-5 border-b border-[var(--border-color)] bg-[var(--bg-elevated)] shrink-0">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300">
              <Info size={18} aria-hidden="true" />
            </span>
            <h2
              id="about-estimate-title"
              className="text-base sm:text-lg font-bold text-[var(--text-primary)] tracking-tight"
            >
              About this estimate
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface)] border border-transparent hover:border-[var(--border-color)] transition shrink-0 cursor-pointer"
            aria-label="Close modal"
            data-testid="modal-close-button"
          >
            <X size={18} />
          </button>
        </div>

        {/* 3-sentence clean body */}
        <div className="p-5 sm:p-6 space-y-3.5 text-sm text-[var(--text-secondary)] leading-relaxed">
          <p>
            This estimate is based on data from {projectCount} real software projects.
          </p>
          <p>
            The likely range covers most outcomes; the wider range covers almost all.
          </p>
          <p>
            Add your completed projects in Settings to adjust estimates to your team.
          </p>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--border-color)] bg-[var(--bg-elevated)] flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white transition shadow-sm cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModelTransparencyModal;
