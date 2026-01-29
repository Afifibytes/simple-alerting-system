import { createService } from './createService';
import { api } from './api';
import type { Rule, RuleFormData, EvaluationResult, Service } from '../types';

const base = createService<Rule, RuleFormData, Partial<RuleFormData>>('/rules', ['source_id', 'severity']);

export interface RuleService extends Service<Rule, RuleFormData, Partial<RuleFormData>> {
  evaluate: (id: string) => Promise<EvaluationResult>;
}

export const ruleService: RuleService = {
  ...base,
  evaluate: (id: string): Promise<EvaluationResult> => api.post<EvaluationResult>(`/rules/${id}/evaluate`),
};
