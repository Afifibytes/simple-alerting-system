import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import type { Alert } from '../../types';

interface AlertCardProps {
  alert: Alert;
  onAcknowledge: (id: string) => Promise<Alert>;
  onResolve: (id: string, message: string | null) => Promise<Alert>;
}

export function AlertCard({ alert, onAcknowledge, onResolve }: AlertCardProps): React.ReactElement {
  const [acknowledging, setAcknowledging] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [showResolveForm, setShowResolveForm] = useState(false);
  const [resolveMessage, setResolveMessage] = useState('');

  const handleAcknowledge = async (): Promise<void> => {
    setAcknowledging(true);
    try {
      await onAcknowledge(alert.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setAcknowledging(false);
    }
  };

  const handleResolve = async (): Promise<void> => {
    setResolving(true);
    try {
      await onResolve(alert.id, resolveMessage || null);
      setShowResolveForm(false);
      setResolveMessage('');
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setResolving(false);
    }
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="card" style={{ marginBottom: 'var(--spacing-md)' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 'var(--spacing-md)',
        }}
      >
        <div>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
            <StatusBadge status={alert.severity} type="severity" />
            <StatusBadge status={alert.status} type="alert" />
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            Rule: {alert.rule_name || alert.rule_id.substring(0, 8)}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          {alert.status === 'triggered' && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleAcknowledge}
              disabled={acknowledging}
            >
              {acknowledging ? 'Acknowledging...' : 'Acknowledge'}
            </button>
          )}
          {alert.status !== 'resolved' && (
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setShowResolveForm(true)}
            >
              Resolve
            </button>
          )}
        </div>
      </div>

      {showResolveForm && (
        <div style={{ marginBottom: 'var(--spacing-md)', padding: 'var(--spacing-sm)', background: 'var(--color-gray-100)', borderRadius: '4px' }}>
          <div className="form-group" style={{ marginBottom: 'var(--spacing-sm)' }}>
            <label className="form-label">Resolution Message (optional)</label>
            <input
              type="text"
              value={resolveMessage}
              onChange={(e) => setResolveMessage(e.target.value)}
              className="form-input"
              placeholder="e.g., Fixed by deploying hotfix"
            />
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleResolve}
              disabled={resolving}
            >
              {resolving ? 'Resolving...' : 'Confirm Resolve'}
            </button>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setShowResolveForm(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: 'var(--spacing-sm)',
          fontSize: '0.875rem',
          color: 'var(--color-text-secondary)',
        }}
      >
        <div>
          <strong>Triggered:</strong> {formatDate(alert.triggered_at)}
        </div>
        <div>
          <strong>Matches:</strong> {alert.matches_count}
        </div>
        {alert.acknowledged_at && (
          <div>
            <strong>Acknowledged:</strong> {formatDate(alert.acknowledged_at)}
          </div>
        )}
        {alert.resolved_at && (
          <div>
            <strong>Resolved:</strong> {formatDate(alert.resolved_at)}
          </div>
        )}
        {alert.message && (
          <div style={{ gridColumn: 'span 2' }}>
            <strong>Message:</strong> {alert.message}
          </div>
        )}
      </div>
    </div>
  );
}
