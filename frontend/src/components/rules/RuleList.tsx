import React, { useState, useCallback } from 'react';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { ToggleSwitch } from '../common/ToggleSwitch';
import { Icon } from '../common/Icon';
import type { Rule, EvaluationResult } from '../../types';

interface RuleListProps {
  rules: Rule[];
  loading: boolean;
  onDelete: (id: string) => Promise<void>;
  onEvaluate: (id: string) => Promise<EvaluationResult>;
  onUpdate?: (id: string, data: Partial<Rule>) => Promise<Rule>;
}

interface ProcessingState {
  [key: string]: boolean;
}

// Lookup map for rules by ID - avoids needing to pass full rule objects
function createRuleMap(rules: Rule[]): Map<string, Rule> {
  return new Map(rules.map(r => [r.id, r]));
}

export function RuleList({ rules, loading, onDelete, onEvaluate, onUpdate }: RuleListProps): React.ReactElement {
  const [evaluating, setEvaluating] = useState<ProcessingState>({});
  const [deleting, setDeleting] = useState<ProcessingState>({});

  const ruleMap = createRuleMap(rules);

  // Use data-id attribute to avoid creating functions per row
  const handleEvaluateClick = useCallback(async (e: React.MouseEvent<HTMLButtonElement>) => {
    const id = e.currentTarget.dataset.id;
    if (!id) return;
    setEvaluating((prev) => ({ ...prev, [id]: true }));
    try {
      await onEvaluate(id);
    } finally {
      setEvaluating((prev) => ({ ...prev, [id]: false }));
    }
  }, [onEvaluate]);

  const handleDeleteClick = useCallback(async (e: React.MouseEvent<HTMLButtonElement>) => {
    const id = e.currentTarget.dataset.id;
    const name = e.currentTarget.dataset.name;
    if (!id) return;
    if (!window.confirm(`Delete rule "${name}"?`)) return;
    setDeleting((prev) => ({ ...prev, [id]: true }));
    try {
      await onDelete(id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting((prev) => ({ ...prev, [id]: false }));
    }
  }, [onDelete]);

  const handleToggleActive = async (rule: Rule, isActive: boolean): Promise<void> => {
    if (onUpdate) {
      await onUpdate(rule.id, { is_active: isActive });
    }
  };

  const formatCondition = (rule: Rule): string => {
    return `${rule.condition_field} ${rule.condition_operator} "${rule.condition_value}" (${rule.condition_threshold}x)`;
  };

  const formatWindow = (seconds: number): string => {
    if (seconds >= 3600) return `${Math.floor(seconds / 3600)}h`;
    if (seconds >= 60) return `${Math.floor(seconds / 60)}m`;
    return `${seconds}s`;
  };

  const columns = [
    { header: 'Name', width: '20%' },
    { header: 'Source', width: '12%' },
    { header: 'Condition', width: '25%' },
    { header: 'Severity', width: '10%' },
    { header: 'Window', width: '8%' },
    { header: 'Status', width: '10%' },
    { header: 'Actions', width: '15%' },
  ];

  const renderRow = (rule: Rule): React.ReactElement => (
    <tr key={rule.id}>
      <td>
        <div className="table-cell-primary">{rule.name}</div>
        <div className="table-cell-muted">{rule.condition_type} rule</div>
      </td>
      <td className="table-cell-secondary">{rule.source_name || 'Unknown'}</td>
      <td>
        <code className="text-xs text-muted">
          {formatCondition(rule)}
        </code>
      </td>
      <td>
        <StatusBadge status={rule.severity} type="severity" />
      </td>
      <td className="table-cell-secondary">{formatWindow(rule.time_window_seconds)}</td>
      <td>
        {onUpdate ? (
          <ToggleSwitch
            checked={rule.is_active !== false}
            onChange={(checked) => handleToggleActive(rule, checked)}
            label={rule.is_active !== false ? 'Active' : 'Inactive'}
          />
        ) : (
          <StatusBadge
            status={rule.is_active !== false ? 'active' : 'inactive'}
            type="status"
          />
        )}
      </td>
      <td>
        <div className="row-actions">
          <button
            className="btn btn-ghost btn-sm"
            data-id={rule.id}
            onClick={handleEvaluateClick}
            disabled={evaluating[rule.id]}
            title="Test rule"
          >
            <Icon name="play_arrow" size="sm" />
          </button>
          <button
            className="btn btn-ghost btn-sm text-danger"
            data-id={rule.id}
            data-name={rule.name}
            onClick={handleDeleteClick}
            disabled={deleting[rule.id]}
            title="Delete rule"
          >
            <Icon name="delete" size="sm" />
          </button>
        </div>
      </td>
    </tr>
  );

  return (
    <DataTable
      columns={columns}
      data={rules}
      loading={loading}
      emptyIcon="rule"
      emptyTitle="No alert rules configured"
      emptyDescription="Create your first rule to start monitoring events."
      renderRow={renderRow}
    />
  );
}
