/**
 * Predictify — EmptyState Component Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import EmptyState from '../../components/shared/EmptyState';

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState title="No estimates yet" description="Create your first estimate" />);
    expect(screen.getByText('No estimates yet')).toBeInTheDocument();
    expect(screen.getByText('Create your first estimate')).toBeInTheDocument();
  });

  it('renders default icon', () => {
    render(<EmptyState title="Test" description="Desc" />);
    expect(screen.getByText('📊')).toBeInTheDocument();
  });

  it('renders custom icon', () => {
    render(<EmptyState icon="🚀" title="Test" description="Desc" />);
    expect(screen.getByText('🚀')).toBeInTheDocument();
  });

  it('renders action button when actionLabel and onAction provided', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No data"
        description="Start now"
        actionLabel="Create Estimate"
        onAction={handleAction}
      />
    );
    const btn = screen.getByText('Create Estimate');
    expect(btn).toBeInTheDocument();
    expect(btn.tagName).toBe('BUTTON');
  });

  it('calls onAction when button clicked', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No data"
        description="Start now"
        actionLabel="Go"
        onAction={handleAction}
      />
    );
    fireEvent.click(screen.getByText('Go'));
    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it('does not render button when no actionLabel', () => {
    render(<EmptyState title="Empty" description="Nothing here" />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('does not render button when no onAction', () => {
    render(<EmptyState title="Empty" description="Nothing" actionLabel="Click" />);
    expect(screen.queryByText('Click')).not.toBeInTheDocument();
  });
});
