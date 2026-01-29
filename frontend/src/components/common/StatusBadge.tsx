import React from 'react';

const statusStyles: Record<string, string> = {
  healthy: 'badge-success',
  connected: 'badge-success',
  active: 'badge-success',
  unhealthy: 'badge-danger',
  error: 'badge-danger',
  inactive: 'badge-secondary',
  unknown: 'badge-warning',
};

const severityStyles: Record<string, string> = {
  low: 'badge-success',
  medium: 'badge-warning',
  high: 'badge-danger',
};

const alertStyles: Record<string, string> = {
  triggered: 'badge-danger',
  acknowledged: 'badge-warning',
  resolved: 'badge-success',
};

interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'severity' | 'alert' | 'info';
  showDot?: boolean;
}

export function StatusBadge({ status, type = 'status', showDot = true }: StatusBadgeProps): React.ReactElement {
  let styles: Record<string, string>;
  if (type === 'severity') {
    styles = severityStyles;
  } else if (type === 'alert') {
    styles = alertStyles;
  } else {
    styles = statusStyles;
  }
  const className = styles[status] || 'badge-info';

  return (
    <span className={`badge ${className}`}>
      {showDot && <span className="badge-dot"></span>}
      {status}
    </span>
  );
}
