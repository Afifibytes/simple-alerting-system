import React from 'react';
import type { AlertFilters as AlertFiltersType } from '../../types';

interface AlertFiltersProps {
  filters: AlertFiltersType;
  onChange: (filters: AlertFiltersType) => void;
}

export function AlertFilters({ filters, onChange }: AlertFiltersProps): React.ReactElement {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    const { name, value } = e.target;
    onChange({ ...filters, [name]: value || undefined });
  };

  return (
    <div className="card mb-md">
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Status</label>
          <select
            name="status"
            value={filters.status || ''}
            onChange={handleChange}
            className="form-select"
          >
            <option value="">All</option>
            <option value="triggered">Triggered</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Severity</label>
          <select
            name="severity"
            value={filters.severity || ''}
            onChange={handleChange}
            className="form-select"
          >
            <option value="">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
    </div>
  );
}
