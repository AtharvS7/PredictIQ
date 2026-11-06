import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import {
  ConfidenceRangeBar,
  ConfidenceIntervalCard,
} from '../shared/ConfidenceInterval';

describe('Confidence Interval Primitives', () => {
  it('renders ConfidenceRangeBar with p10, p50, and p90 labels and values', () => {
    render(
      <ConfidenceRangeBar
        p10={1150}
        p50={1820}
        p90={2940}
        unit="hours"
        showLabels
      />
    );

    expect(screen.getByText(/p10 \(Best Case\)/i)).toBeInTheDocument();
    expect(screen.getByText('1,150 hrs')).toBeInTheDocument();
    expect(screen.getByText(/p50 \(Median\)/i)).toBeInTheDocument();
    expect(screen.getByText('1,820 hrs')).toBeInTheDocument();
    expect(screen.getByText(/p90 \(Budget Cap\)/i)).toBeInTheDocument();
    expect(screen.getByText('2,940 hrs')).toBeInTheDocument();
  });

  it('calculates and displays spread ratio', () => {
    render(
      <ConfidenceRangeBar
        p10={1000}
        p50={1500}
        p90={2500}
        unit="hours"
        showDetails
      />
    );

    // 2500 / 1000 = 2.5x
    expect(screen.getByText(/2.5x \(p90\/p10\)/i)).toBeInTheDocument();
  });

  it('renders currency format correctly', () => {
    render(
      <ConfidenceRangeBar
        p10={86250}
        p50={136500}
        p90={220500}
        unit="currency"
        currencySymbol="$"
      />
    );

    expect(screen.getByText('$86,250')).toBeInTheDocument();
    expect(screen.getByText('$136,500')).toBeInTheDocument();
    expect(screen.getByText('$220,500')).toBeInTheDocument();
  });

  it('renders ConfidenceIntervalCard container with title, tier, and quantiles', () => {
    render(
      <ConfidenceIntervalCard
        title="Calibrated Effort Quantiles"
        subtitle="Person-hours predicted with Huber power law"
        quantiles={{ p10: 1150, p50: 1820, p90: 2940 }}
        unit="hours"
        tier="A"
        calibrated
      />
    );

    expect(screen.getByText('Calibrated Effort Quantiles')).toBeInTheDocument();
    expect(screen.getByText(/Person-hours predicted/i)).toBeInTheDocument();
    expect(screen.getByText('Tier A')).toBeInTheDocument();
    expect(screen.getByText('1,820 hrs')).toBeInTheDocument();
  });
});
