import React from 'react';
import { Icon } from './Icon';

interface Column {
  key?: string;
  header: string;
  width?: string;
}

interface DataTableProps<T> {
  columns: Column[];
  data: T[];
  loading: boolean;
  emptyIcon?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  renderRow: (item: T, index: number) => React.ReactNode;
}

export function DataTable<T>({
  columns,
  data,
  loading,
  emptyIcon = 'inbox',
  emptyTitle = 'No data found',
  emptyDescription = '',
  renderRow,
}: DataTableProps<T>): React.ReactElement {
  if (loading) {
    return (
      <div className="data-table-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          Loading...
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="data-table-container">
        <div className="empty-state">
          <div className="empty-state-icon">
            <Icon name={emptyIcon} size="lg" />
          </div>
          <div className="empty-state-title">{emptyTitle}</div>
          {emptyDescription && (
            <div className="empty-state-description">{emptyDescription}</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key ?? col.header} style={col.width ? { width: col.width } : undefined}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, rowIndex) => renderRow(item, rowIndex))}
        </tbody>
      </table>
    </div>
  );
}
