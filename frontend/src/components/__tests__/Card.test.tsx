import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../shared/Card';

describe('Card Component Primitives', () => {
  it('renders default card variant with appropriate container classes', () => {
    const { container } = render(
      <Card data-testid="test-card">
        <div>Card body</div>
      </Card>
    );

    const card = screen.getByTestId('test-card');
    expect(card).toBeInTheDocument();
    expect(card).toHaveTextContent('Card body');
    expect(container.querySelector('.card-container')).toBeInTheDocument();
  });

  it('renders interactive variant with hover and cursor styling', () => {
    render(
      <Card variant="interactive" data-testid="interactive-card">
        Clickable Card
      </Card>
    );

    const card = screen.getByTestId('interactive-card');
    expect(card.className).toContain('cursor-pointer');
  });

  it('renders accent variant with top border highlight', () => {
    render(
      <Card variant="accent" data-testid="accent-card">
        Accent Card
      </Card>
    );

    const card = screen.getByTestId('accent-card');
    expect(card.className).toContain('border-t-4');
  });

  it('renders subcomponents (Header, Title, Description, Content, Footer)', () => {
    render(
      <Card>
        <CardHeader bordered data-testid="card-header">
          <CardTitle as="h2">Project Estimation</CardTitle>
          <CardDescription>Calibrated effort breakdown</CardDescription>
        </CardHeader>
        <CardContent data-testid="card-content">
          <p>Main content area</p>
        </CardContent>
        <CardFooter bordered data-testid="card-footer">
          <button>Action</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Project Estimation');
    expect(screen.getByText('Calibrated effort breakdown')).toBeInTheDocument();
    expect(screen.getByTestId('card-content')).toHaveTextContent('Main content area');
    expect(screen.getByTestId('card-footer')).toContainElement(screen.getByRole('button', { name: 'Action' }));
  });
});
