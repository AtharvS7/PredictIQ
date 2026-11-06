import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Heading, Text, MetricValue, CodeChip } from '../shared/Typography';

describe('Typography Primitives', () => {
  it('renders Heading with specified level and classes', () => {
    render(<Heading level={1}>PredictIQ Architecture</Heading>);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toHaveTextContent('PredictIQ Architecture');
  });

  it('renders Text with body, caption, and overline variants', () => {
    render(
      <div>
        <Text variant="body">Body copy</Text>
        <Text variant="caption">Small note</Text>
        <Text variant="overline">Metadata Tag</Text>
      </div>
    );
    expect(screen.getByText('Body copy')).toBeInTheDocument();
    expect(screen.getByText('Small note')).toBeInTheDocument();
    expect(screen.getByText('Metadata Tag')).toBeInTheDocument();
  });

  it('renders MetricValue with value, unit, label, and trend', () => {
    render(
      <MetricValue
        value="1,820"
        unit="hours"
        label="Effort (p50)"
        subtext="±18% empirical calibration"
        trend={{ direction: 'up', text: '+4.2% vs baseline' }}
      />
    );
    expect(screen.getByText('1,820')).toBeInTheDocument();
    expect(screen.getByText('hours')).toBeInTheDocument();
    expect(screen.getByText('Effort (p50)')).toBeInTheDocument();
    expect(screen.getByText('±18% empirical calibration')).toBeInTheDocument();
    expect(screen.getByText('+4.2% vs baseline')).toBeInTheDocument();
  });

  it('renders CodeChip with monospace formatting', () => {
    render(<CodeChip>p10-p90</CodeChip>);
    const code = screen.getByText('p10-p90');
    expect(code.tagName.toLowerCase()).toBe('code');
  });
});
