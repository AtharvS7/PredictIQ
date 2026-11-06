import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import {
  Badge,
  DataQualityBadge,
  ModelVersionBadge,
  UncertaintyBadge,
} from '../shared/Badge';

describe('Badge Primitives', () => {
  it('renders standard badge with correct variant styles', () => {
    render(<Badge variant="primary">Active State</Badge>);
    expect(screen.getByText('Active State')).toBeInTheDocument();
  });

  it('renders DataQualityBadge for Tier A with certified subtext', () => {
    render(<DataQualityBadge tier="A" />);
    expect(screen.getByText('Tier A')).toBeInTheDocument();
    expect(screen.getByText(/Certified Benchmark/i)).toBeInTheDocument();
  });

  it('renders DataQualityBadge in compact mode', () => {
    render(<DataQualityBadge tier="B" compact />);
    expect(screen.getByText('Tier B')).toBeInTheDocument();
    expect(screen.queryByText(/Validated Standard/i)).not.toBeInTheDocument();
  });

  it('renders DataQualityBadge for Tier C with heuristic alert', () => {
    render(<DataQualityBadge tier="C" />);
    expect(screen.getByText('Tier C')).toBeInTheDocument();
    expect(screen.getByText(/Heuristic/i)).toBeInTheDocument();
  });

  it('renders ModelVersionBadge with version and git/model SHA', () => {
    render(
      <ModelVersionBadge
        version="v2.0.0-rc.1"
        sha256="0bea59fbe69a5b17acdf9953d61e659b26d3450052fd8934b2b1e0b716e0b257"
        sourcesCount={4}
      />
    );
    expect(screen.getByText('v2.0.0-rc.1')).toBeInTheDocument();
    expect(screen.getByText('#0bea59f')).toBeInTheDocument();
    expect(screen.getByText('4 sources')).toBeInTheDocument();
  });

  it('renders UncertaintyBadge with interval and calibrated state', () => {
    render(
      <UncertaintyBadge
        interval="80% CI (p10–p90)"
        coverage="90% Conformal"
        calibrated
      />
    );
    expect(screen.getByText('80% CI (p10–p90)')).toBeInTheDocument();
    expect(screen.getByText(/90% Conformal/i)).toBeInTheDocument();
  });
});
