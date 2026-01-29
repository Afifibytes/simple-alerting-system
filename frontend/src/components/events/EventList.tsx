import React from 'react';
import { DataTable } from '../common/DataTable';
import { Pagination } from '../common/Pagination';
import type { Event } from '../../types';

interface PaginationData {
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

interface EventListProps {
  events: Event[];
  loading: boolean;
  pagination?: PaginationData;
  onPageChange?: (page: number) => void;
}

export function EventList({ events, loading, pagination, onPageChange }: EventListProps): React.ReactElement {
  const formatDate = (dateStr: string): string => {
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

  const formatData = (data: Record<string, unknown>): string => {
    const str = JSON.stringify(data);
    return str.length > 50 ? str.substring(0, 50) + '...' : str;
  };

  const columns = [
    { key: 'timestamp', header: 'Time', width: '15%' },
    { key: 'source', header: 'Source', width: '15%' },
    { key: 'type', header: 'Type', width: '15%' },
    { key: 'data', header: 'Data', width: '55%' },
  ];

  const renderRow = (event: Event): React.ReactElement => (
    <tr key={event.id}>
      <td className="table-cell-secondary">{formatDate(event.timestamp)}</td>
      <td className="table-cell-primary">{event.source_name}</td>
      <td className="table-cell-secondary">{event.event_type}</td>
      <td>
        <code className="text-xs text-muted">{formatData(event.data)}</code>
      </td>
    </tr>
  );

  const currentPage = pagination ? Math.floor(pagination.offset / pagination.limit) + 1 : 1;
  const totalPages = pagination ? Math.ceil(pagination.total / pagination.limit) : 1;

  return (
    <>
      <DataTable
        columns={columns}
        data={events}
        loading={loading}
        emptyIcon="event"
        emptyTitle="No events found"
        emptyDescription="Events will appear here when ingested."
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
