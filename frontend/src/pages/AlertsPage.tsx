import React, { useState } from 'react';
import { AlertList } from '../components/alerts/AlertList';
import { AlertFilters } from '../components/alerts/AlertFilters';
import { useAlerts } from '../hooks/useAlerts';
import type { AlertFilters as AlertFiltersType } from '../types';

export function AlertsPage(): React.ReactElement {
  const [filters, setFilters] = useState<AlertFiltersType>({});
  const {
    alerts,
    loading,
    pagination,
    refresh,
    acknowledgeAlert,
    resolveAlert,
  } = useAlerts();

  const handleFiltersChange = (newFilters: AlertFiltersType): void => {
    setFilters(newFilters);
    refresh({ ...newFilters, offset: 0 });
  };

  const handlePageChange = (page: number): void => {
    const offset = (page - 1) * pagination.limit;
    refresh({ ...filters, offset });
  };

  return (
    <>
      <AlertFilters filters={filters} onChange={handleFiltersChange} />
      <AlertList
        alerts={alerts}
        loading={loading}
        onAcknowledge={acknowledgeAlert}
        onResolve={resolveAlert}
        pagination={pagination}
        onPageChange={handlePageChange}
      />
    </>
  );
}
