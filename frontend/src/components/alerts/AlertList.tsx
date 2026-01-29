import React, { useState } from 'react';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { Pagination } from '../common/Pagination';
import { Icon } from '../common/Icon';
import type { Alert } from '../../types';

interface PaginationData {
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

interface AlertListProps {
  alerts: Alert[];
  loading: boolean;
  onAcknowledge: (id: string) => Promise<Alert>;
  onResolve: (id: string, message: string | null) => Promise<Alert>;
  pagination?: PaginationData;
  onPageChange?: (page: number) => void;
}

interface ProcessingState {
  [key: string]: string | null;
}

interface ResolveFormState {
  id: string | null;
  message: string;
}

export function AlertList({ alerts, loading, onAcknowledge, onResolve, pagination, onPageChange }: AlertListProps): React.ReactElement {
  const [processing, setProcessing] = useState<ProcessingState>({});
  const [resolveForm, setResolveForm] = useState<ResolveFormState>({ id: null, message: '' });

  const handleAcknowledge = async (alertItem: Alert): Promise<void> => {
    setProcessing((prev) => ({ ...prev, [alertItem.id]: 'acknowledge' }));
    try {
      await onAcknowledge(alertItem.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setProcessing((prev) => ({ ...prev, [alertItem.id]: null }));
    }
  };

  const handleResolve = async (alertItem: Alert): Promise<void> => {
    setProcessing((prev) => ({ ...prev, [alertItem.id]: 'resolve' }));
    try {
      await onResolve(alertItem.id, resolveForm.message || null);
      setResolveForm({ id: null, message: '' });
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setProcessing((prev) => ({ ...prev, [alertItem.id]: null }));
    }
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const columns = [
    { header: 'Severity', width: '10%' },
    { header: 'Status', width: '12%' },
    { header: 'Rule', width: '25%' },
    { header: 'Triggered', width: '15%' },
    { header: 'Matches', width: '10%' },
    { header: 'Actions', width: '28%' },
  ];

  const renderRow = (alertItem: Alert): React.ReactElement => (
    <tr key={alertItem.id}>
      <td>
        <StatusBadge status={alertItem.severity} type="severity" />
      </td>
      <td>
        <StatusBadge status={alertItem.status} type="alert" />
      </td>
      <td>
        <div className="table-cell-primary">
          {alertItem.rule_name || `Rule ${alertItem.rule_id.substring(0, 8)}...`}
        </div>
        {alertItem.message && (
          <div className="table-cell-muted">{alertItem.message}</div>
        )}
      </td>
      <td className="table-cell-secondary">{formatDate(alertItem.triggered_at)}</td>
      <td className="table-cell-secondary">{alertItem.matches_count}</td>
      <td>
        {resolveForm.id === alertItem.id ? (
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Resolution message..."
              value={resolveForm.message}
              onChange={(e) => setResolveForm((prev) => ({ ...prev, message: e.target.value }))}
              style={{ flex: 1, padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.75rem' }}
            />
            <button
              className="btn btn-primary btn-sm"
              onClick={() => handleResolve(alertItem)}
              disabled={processing[alertItem.id] === 'resolve'}
            >
              {processing[alertItem.id] === 'resolve' ? '...' : 'Confirm'}
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setResolveForm({ id: null, message: '' })}
            >
              Cancel
            </button>
          </div>
        ) : (
          <div className="row-actions" style={{ opacity: 1 }}>
            {alertItem.status === 'triggered' && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => handleAcknowledge(alertItem)}
                disabled={processing[alertItem.id] === 'acknowledge'}
              >
                <Icon name="check" size="sm" />
                {processing[alertItem.id] === 'acknowledge' ? 'Acknowledging...' : 'Acknowledge'}
              </button>
            )}
            {alertItem.status !== 'resolved' && (
              <button
                className="btn btn-primary btn-sm"
                onClick={() => setResolveForm({ id: alertItem.id, message: '' })}
              >
                <Icon name="done_all" size="sm" />
                Resolve
              </button>
            )}
            {alertItem.status === 'resolved' && (
              <span className="table-cell-muted">
                Resolved {formatDate(alertItem.resolved_at)}
              </span>
            )}
          </div>
        )}
      </td>
    </tr>
  );

  const currentPage = pagination ? Math.floor(pagination.offset / pagination.limit) + 1 : 1;
  const totalPages = pagination ? Math.ceil(pagination.total / pagination.limit) : 1;

  return (
    <>
      <DataTable
        columns={columns}
        data={alerts}
        loading={loading}
        emptyIcon="notifications_off"
        emptyTitle="No alerts found"
        emptyDescription="Alerts will appear here when rules are triggered."
        renderRow={renderRow}
      />
      {pagination && onPageChange && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={pagination.total}
          itemsPerPage={pagination.limit}
          onPageChange={onPageChange}
        />
      )}
    </>
  );
}
