import type { RiskItem } from '@/types';

export const RISK_COLORS: Record<RiskItem['severity'], string> = {
  Low: '#10B981',
  Medium: '#F59E0B',
  High: '#EF4444',
  Critical: '#B91C1C',
};
