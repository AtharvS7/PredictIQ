/**
 * Predictify — LoadingSkeleton Component Tests
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSkeleton from '../../components/shared/LoadingSkeleton';

describe('LoadingSkeleton', () => {
  it('renders default 3 skeleton lines', () => {
    const { container } = render(<LoadingSkeleton />);
    const skeletons = container.querySelectorAll('.skeleton-pulse');
    expect(skeletons.length).toBe(3);
  });

  it('renders custom number of lines', () => {
    const { container } = render(<LoadingSkeleton lines={5} />);
    const skeletons = container.querySelectorAll('.skeleton-pulse');
    expect(skeletons.length).toBe(5);
  });

  it('renders single line', () => {
    const { container } = render(<LoadingSkeleton lines={1} />);
    const skeletons = container.querySelectorAll('.skeleton-pulse');
    expect(skeletons.length).toBe(1);
  });

  it('applies correct height', () => {
    const { container } = render(<LoadingSkeleton height={40} lines={1} />);
    const skeleton = container.querySelector('.skeleton-pulse') as HTMLElement;
    expect(skeleton.style.height).toBe('40px');
  });

  it('last line is shorter when multiple lines', () => {
    const { container } = render(<LoadingSkeleton lines={3} width="full" />);
    const skeletons = container.querySelectorAll('.skeleton-pulse') as NodeListOf<HTMLElement>;
    // Last line should be 60% width, others 100%
    expect(skeletons[0].style.width).toBe('100%');
    expect(skeletons[2].style.width).toBe('60%');
  });

  it('includes shimmer animation keyframes', () => {
    const { container } = render(<LoadingSkeleton />);
    const styleTag = container.querySelector('style');
    expect(styleTag).not.toBeNull();
    expect(styleTag?.textContent).toContain('shimmer');
  });
});
