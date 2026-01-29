import React from 'react';
import { Icon } from '../common/Icon';

interface PageHeaderProps {
  title: string;
  description?: string;
  actionLabel?: string | null;
  actionIcon?: string | null;
  onAction?: (() => void) | null;
}

export function PageHeader({ title, description, actionLabel, actionIcon, onAction }: PageHeaderProps): React.ReactElement {
  return (
    <div className="page-header">
      <div className="page-header-content">
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>

      {actionLabel && onAction && (
        <button className="btn btn-primary" onClick={onAction}>
          {actionIcon && <Icon name={actionIcon} size="sm" />}
          {actionLabel}
        </button>
      )}
    </div>
  );
}
