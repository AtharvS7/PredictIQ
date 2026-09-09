import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Sidebar from '../shared/Sidebar';

describe('Workspace navigation', () => {
  it('keeps collapsed links accessible and expands with the keyboard button', () => {
    render(<MemoryRouter><Sidebar /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: 'Collapse sidebar' }));
    for (const name of ['Dashboard', 'New Estimate', 'My Estimates', 'Settings']) {
      expect(screen.getByRole('link', { name })).toBeInTheDocument();
    }
    expect(screen.getByRole('button', { name: 'Expand sidebar' })).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(screen.getByRole('button', { name: 'Expand sidebar' }));
    expect(screen.getByRole('button', { name: 'Collapse sidebar' })).toHaveAttribute('aria-expanded', 'true');
  });

  it('does not identify an existing estimate as the new-estimate form', () => {
    render(<MemoryRouter initialEntries={['/estimate/example']}><Sidebar /></MemoryRouter>);
    expect(screen.getByRole('link', { name: 'New Estimate' })).not.toHaveAttribute('aria-current');
  });

  it('announces the current destination', () => {
    render(<MemoryRouter initialEntries={['/estimates']}><Sidebar /></MemoryRouter>);
    expect(screen.getByRole('link', { name: 'My Estimates' })).toHaveAttribute('aria-current', 'page');
  });
});
