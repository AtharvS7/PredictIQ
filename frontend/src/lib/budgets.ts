import api from './api';

export interface BudgetTask {
  name: string;
  low_hours: string;
  likely_hours: string;
  high_hours: string;
  hourly_rate_usd: string;
}
export interface BudgetInputs {
  project_name: string;
  contingency_pct: string;
  tasks: BudgetTask[];
}
export interface SavedBudget {
  id: string;
  created_at: string;
  method: 'manual_task_budget_v1';
  inputs: BudgetInputs;
  totals: Record<'low_hours' | 'likely_hours' | 'high_hours' | 'low_cost_usd' | 'likely_cost_usd' | 'high_cost_usd', string>;
}
export const saveBudget = async (inputs: BudgetInputs) => (await api.post<SavedBudget>('/budgets', inputs)).data;
export const listBudgets = async (offset = 0) => (await api.get<SavedBudget[]>('/budgets', { params: { limit: 20, offset } })).data;
