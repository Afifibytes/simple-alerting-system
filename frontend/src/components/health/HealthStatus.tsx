import React from 'react';
import { useHealth } from '../../hooks/useHealth';
import { StatusBadge } from '../common/StatusBadge';

interface HealthStatusProps {
  compact?: boolean;
}

interface HealthItemProps {
  label: string;
  status?: string;
}

function HealthItem({ label, status }: HealthItemProps): React.ReactElement {
  const isConnected = status === 'connected';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 'var(--spacing-sm)',
        background: 'var(--color-surface-hover)',
        borderRadius: 'var(--radius-sm)',
      }}
    >
      <span style={{ fontWeight: 500, color: 'var(--color-text)' }}>{label}</span>
      <StatusBadge status={isConnected ? 'connected' : 'error'} />
    </div>
  );
}

export function HealthStatus({ compact = false }: HealthStatusProps): React.ReactElement {
  const { health, loading } = useHealth();

  if (compact) {
    if (loading) {
      return <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>Checking...</span>;
    }

    const isHealthy = health?.status === 'healthy';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>System:</span>
        <StatusBadge status={isHealthy ? 'healthy' : 'unhealthy'} />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Checking system health...</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">System Health</h2>
        <StatusBadge status={health?.status || 'unknown'} />
      </div>
      <div style={{ display: 'grid', gap: 'var(--spacing-sm)' }}>
        <HealthItem label="Database" status={health?.database} />
        <HealthItem label="RabbitMQ" status={health?.rabbitmq} />
      </div>
    </div>
  );
}
