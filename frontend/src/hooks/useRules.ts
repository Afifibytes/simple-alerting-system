import { useResource } from './useResource';
import { ruleService } from '../services/ruleService';
import type { Rule, RuleFormData, EvaluationResult } from '../types';

interface UseRulesReturn {
  rules: Rule[];
  loading: boolean;
  error: string | null;
  pagination: {
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
  };
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  createRule: (data: RuleFormData) => Promise<Rule>;
  updateRule: (id: string, data: Partial<RuleFormData>) => Promise<Rule>;
  deleteRule: (id: string) => Promise<void>;
  evaluateRule: (id: string) => Promise<EvaluationResult>;
}

export function useRules(): UseRulesReturn {
  const { items: rules, create, update, remove, ...rest } = useResource<Rule, RuleFormData, Partial<RuleFormData>>(ruleService);
  const evaluateRule = (id: string): Promise<EvaluationResult> => ruleService.evaluate(id);
  return { rules, createRule: create, updateRule: update, deleteRule: remove, evaluateRule, ...rest };
}
