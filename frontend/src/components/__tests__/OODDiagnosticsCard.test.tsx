import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import OODDiagnosticsCard from '../estimate/OODDiagnosticsCard';

describe('OODDiagnosticsCard Component', () => {
  it('returns null and does not render when no OOD conditions exist', () => {
    const { container } = render(
      <OODDiagnosticsCard
        inputs={{
          team_size: 6,
          duration_months: 6,
          size_fp: 250,
          integration_count: 3,
        }}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders OOD warning for Functional Size > 2,000 FP, Team Size > 30, and Duration > 24 mo', () => {
    render(
      <OODDiagnosticsCard
        inputs={{
          team_size: 45,
          duration_months: 36,
          size_fp: 3500,
          integration_count: 14,
        }}
        defaultExpanded={true}
      />
    );

    // Title and badge
    expect(screen.getByText(/Out-of-Distribution \(OOD\) Parameter Notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Statistical Variance Widened/i)).toBeInTheDocument();

    // Specific triggers
    expect(screen.getByText(/Planned team size of 45 exceeds the calibrated benchmark envelope/i)).toBeInTheDocument();
    expect(screen.getByText(/Planned target duration of 36 months exceeds single-phase empirical horizons/i)).toBeInTheDocument();
    expect(screen.getByText(/Functional size of 3,500 FP is beyond standard calibrated cluster envelopes/i)).toBeInTheDocument();
    expect(screen.getByText(/High external integration density \(14 interfaces\)/i)).toBeInTheDocument();
  });

  it('clearly explains why intervals widen for OOD projects without falsely clamping estimates', () => {
    render(
      <OODDiagnosticsCard
        inputs={{
          team_size: 50,
        }}
        defaultExpanded={true}
      />
    );

    // Statistical mechanics explanation
    expect(screen.getByText(/Why Intervals Widen Without Arbitrary Clamping/i)).toBeInTheDocument();
    expect(screen.getByText(/Conformal Residual Dispersion/i)).toBeInTheDocument();
    expect(screen.getByText(/Monotonic Power-Law Scaling/i)).toBeInTheDocument();
    expect(screen.getByText(/Recommended Engineering Mitigations/i)).toBeInTheDocument();
  });

  it('toggles diagnostics visibility when the toggle button is clicked', () => {
    render(
      <OODDiagnosticsCard
        inputs={{
          size_fp: 2500,
        }}
        defaultExpanded={false}
      />
    );

    const toggleBtn = screen.getByTestId('ood-toggle-button');
    expect(toggleBtn).toHaveTextContent(/View Diagnostics & Why Intervals Widen/i);
    expect(screen.queryByTestId('ood-expanded-panel')).not.toBeInTheDocument();

    // Expand
    fireEvent.click(toggleBtn);
    expect(toggleBtn).toHaveTextContent(/Hide Diagnostics/i);
    expect(screen.getByTestId('ood-expanded-panel')).toBeInTheDocument();
    expect(screen.getByText(/Functional size of 2,500 FP is beyond standard calibrated cluster envelopes/i)).toBeInTheDocument();

    // Collapse
    fireEvent.click(toggleBtn);
    expect(toggleBtn).toHaveTextContent(/View Diagnostics & Why Intervals Widen/i);
    expect(screen.queryByTestId('ood-expanded-panel')).not.toBeInTheDocument();
  });
});
