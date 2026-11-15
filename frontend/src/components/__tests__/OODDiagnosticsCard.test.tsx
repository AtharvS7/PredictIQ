import { describe, it, expect } from 'vitest';
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

  it('renders large project notice for large scope factors', () => {
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
    expect(screen.getByText(/Large project notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Wider range/i)).toBeInTheDocument();

    // Specific triggers
    expect(screen.getByText(/Planned team size of 45 exceeds typical team sizes/i)).toBeInTheDocument();
    expect(screen.getByText(/Planned duration of 36 months exceeds typical timelines/i)).toBeInTheDocument();
    expect(screen.getByText(/Project size of 3,500 FP is larger than typical projects/i)).toBeInTheDocument();
    expect(screen.getByText(/High external integration density \(14 interfaces\)/i)).toBeInTheDocument();
  });

  it('renders recommendations panel when expanded', () => {
    render(
      <OODDiagnosticsCard
        inputs={{
          team_size: 50,
        }}
        defaultExpanded={true}
      />
    );

    expect(screen.getByText(/Suggestions/i)).toBeInTheDocument();
    expect(screen.getByText(/Scope phasing/i)).toBeInTheDocument();
    expect(screen.getByText(/Team squads/i)).toBeInTheDocument();
    expect(screen.getByText(/Iterative schedule/i)).toBeInTheDocument();
  });

  it('toggles details visibility when the toggle button is clicked', () => {
    render(
      <OODDiagnosticsCard
        inputs={{
          size_fp: 2500,
        }}
        defaultExpanded={false}
      />
    );

    const toggleBtn = screen.getByTestId('ood-toggle-button');
    expect(toggleBtn).toHaveTextContent(/View details/i);
    expect(screen.queryByTestId('ood-expanded-panel')).not.toBeInTheDocument();

    // Expand
    fireEvent.click(toggleBtn);
    expect(toggleBtn).toHaveTextContent(/Hide details/i);
    expect(screen.getByTestId('ood-expanded-panel')).toBeInTheDocument();
    expect(screen.getByText(/Project size of 2,500 FP is larger than typical projects/i)).toBeInTheDocument();

    // Collapse
    fireEvent.click(toggleBtn);
    expect(toggleBtn).toHaveTextContent(/View details/i);
    expect(screen.queryByTestId('ood-expanded-panel')).not.toBeInTheDocument();
  });
});
