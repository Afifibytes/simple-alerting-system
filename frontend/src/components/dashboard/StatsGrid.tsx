import React from 'react';
import { Icon } from '../common/Icon';
import type { Rule, Source, Alert, HealthStatus } from '../../types';

interface StatsGridProps {
  rules: Rule[];
  sources: Source[];
  alerts: Alert[];
  healthStatus: HealthStatus | null;
}

interface Stat {
  title: string;
  value: number | string;
  subtitle: string;
  icon: string;
  color: string;
}

export function StatsGrid({ rules, sources, alerts, healthStatus }: StatsGridProps): React.ReactElement {
  const triggeredAlerts = alerts.filter(
    (a) => a.status === 'triggered' && isWithin24Hours(a.triggered_at)
  ).length;

  const activeSources = sources.filter((s) => s.is_active).length;

  const stats: Stat[] = [
    {
      title: 'Total Rules',
      value: rules.length,
      subtitle: 'Configured alert rules',
      icon: 'rule',
      color: 'var(--color-primary)',
    },
    {
      title: 'Active Sources',
      value: activeSources,
      subtitle: `${sources.length} total sources`,
      icon: 'source',
      color: 'var(--color-info)',
    },
    {
      title: 'Triggered Alerts',
      value: triggeredAlerts,
      subtitle: 'Last 24 hours',
      icon: 'warning',
      color: triggeredAlerts > 0 ? 'var(--color-danger)' : 'var(--color-success)',
    },
    {
      title: 'System Health',
      value: healthStatus?.status === 'healthy' ? 'OK' : 'Issue',
      subtitle: getHealthSubtitle(healthStatus),
      icon: healthStatus?.status === 'healthy' ? 'check_circle' : 'error',
      color:
        healthStatus?.status === 'healthy'
          ? 'var(--color-success)'
          : 'var(--color-warning)',
    },
  ];

  return (
    <div className="stats-grid">
      {stats.map((stat) => (
        <div key={stat.title} className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">{stat.title}</span>
            <Icon
              name={stat.icon}
              style={{ color: stat.color }}
            />
          </div>
          <div className="stat-card-value" style={{ color: stat.color }}>
            {stat.value}
          </div>
          <div className="stat-card-subtitle">{stat.subtitle}</div>
        </div>
      ))}
    </div>
  );
}

function isWithin24Hours(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = diffMs / (1000 * 60 * 60);
  return diffHours <= 24;
}

function getHealthSubtitle(healthStatus: HealthStatus | null): string {
  if (!healthStatus) return 'Checking...';
  const services: string[] = [];
  if (healthStatus.database) services.push('DB');
  if (healthStatus.rabbitmq) services.push('RabbitMQ');
  return services.length > 0 ? `${services.join(', ')} connected` : 'No services';
}
