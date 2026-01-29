import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import type { Rule, EvaluationResult } from '../../types';

interface RuleCardProps {
  rule: Rule;
  onDelete: (id: string) => Promise<void>;
  onEvaluate: (id: string) => Promise<EvaluationResult>;
}

export function RuleCard({ rule, onDelete, onEvaluate }: RuleCardProps): React.ReactElement {
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleEvaluate = async (): Promise<void> => {
    setEvaluating(true);
    try {
      const res = await onEvaluate(rule.id);
      setResult(res);
    } catch (err) {
      setResult({ triggered: false, message: err instanceof Error ? err.message : 'An error occurred' });
    } finally {
      setEvaluating(false);
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!window.confirm(`Delete rule "${rule.name}"?`)) return;
    setDeleting(true);
    try {
      await onDelete(rule.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting(false);
    }
  };

  return (
    <div className="card card-spacing">
      <div className="flex justify-between items-start mb-md">
        <div>
          <h3 className="font-semibold mb-xs">{rule.name}</h3>
          <div className="flex gap-sm">
            <StatusBadge status={rule.severity} type="severity" />
            <span className="badge badge-info">{rule.condition_type}</span>
          </div>
        </div>
        <div className="flex gap-sm">
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleEvaluate}
            disabled={evaluating}
          >
            {evaluating ? 'Evaluating...' : 'Evaluate'}
          </button>
          <button
            className="btn btn-danger btn-sm"
            onClick={handleDelete}
            disabled={deleting}
          >
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-sm text-sm text-muted">
        <div>
          <strong>Source:</strong> {rule.source_name || 'Unknown'}
        </div>
        <div>
          <strong>Field:</strong> {rule.condition_field}
        </div>
        <div>
          <strong>Window:</strong> {rule.time_window_seconds}s
        </div>
        <div className="grid-span-3">
          <strong>Condition:</strong> {rule.condition_field}{' '}
          {rule.condition_operator} "{rule.condition_value}" (threshold:{' '}
          {rule.condition_threshold})
        </div>
        <div className="grid-span-3 mt-xs">
          <strong>Notification Channels:</strong>{' '}
          {rule.notification_channels && rule.notification_channels.length > 0 ? (
            <span className="inline-flex gap-xs flex-wrap ml-sm">
              {rule.notification_channels.map((channel) => (
                <span key={channel.id} className="chip">
                  {channel.name} ({channel.channel_type})
                </span>
              ))}
            </span>
          ) : (
            <span className="italic opacity-70">None configured</span>
          )}
        </div>
      </div>

      {result && (
        <div className={`alert ${result.triggered ? 'alert-danger' : 'alert-success'} mt-md mb-0`}>
          <strong>{result.triggered ? 'TRIGGERED' : 'Not Triggered'}</strong>
          <span className="ml-sm">{result.message}</span>
        </div>
      )}
    </div>
  );
}
