import React from 'react';
import { StatsGrid } from '../components/dashboard/StatsGrid';
import { AlertList } from '../components/alerts/AlertList';
import { useRules } from '../hooks/useRules';
import { useSources } from '../hooks/useSources';
import { useAlerts } from '../hooks/useAlerts';
import { useHealth } from '../hooks/useHealth';

export function DashboardPage(): React.ReactElement {
  const { rules } = useRules();
  const { sources } = useSources();
  const { alerts, loading: alertsLoading, acknowledgeAlert, resolveAlert } = useAlerts();
  const { health } = useHealth();

  return (
    <>
      <StatsGrid
        rules={rules}
        sources={sources}
        alerts={alerts}
        healthStatus={health}
      />
      <div className="section-divider" />
      <h2 className="mb-md font-semibold">Recent Alerts</h2>
      <AlertList
        alerts={alerts.slice(0, 5)}
        loading={alertsLoading}
        onAcknowledge={acknowledgeAlert}
        onResolve={resolveAlert}
      />
    </>
  );
}
