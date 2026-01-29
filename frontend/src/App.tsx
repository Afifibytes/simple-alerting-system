import React, { useState, useCallback } from 'react';
import { Header } from './components/layout/Header';
import { PageHeader } from './components/layout/PageHeader';
import {
  DashboardPage,
  SourcesPage,
  EventsPage,
  RulesPage,
  AlertsPage,
  NotificationsPage,
} from './pages';
import { useAlerts } from './hooks/useAlerts';

type Section = 'dashboard' | 'sources' | 'events' | 'rules' | 'alerts' | 'notifications';
type Tab = 'list' | 'create';

interface PageConfig {
  title: string;
  description: string;
  actionLabel?: string;
}

const PAGE_CONFIGS: Record<Section, PageConfig> = {
  dashboard: {
    title: 'Dashboard',
    description: 'Overview of your alerting system',
  },
  sources: {
    title: 'Event Sources',
    description: 'Manage sources that emit events to the alerting system',
    actionLabel: 'Create Source',
  },
  events: {
    title: 'Events',
    description: 'View and ingest events to be processed by the alerting system',
    actionLabel: 'Ingest Event',
  },
  rules: {
    title: 'Alert Rules',
    description: 'Configure rules that trigger alerts based on event conditions',
    actionLabel: 'Create Rule',
  },
  alerts: {
    title: 'Alerts',
    description: 'View and manage triggered alerts',
  },
  notifications: {
    title: 'Notification Channels',
    description: 'Configure channels to receive alert notifications',
    actionLabel: 'Create Channel',
  },
};

const SECTIONS_WITH_FORMS: Section[] = ['sources', 'events', 'rules', 'notifications'];

function App(): React.ReactElement {
  const [activeSection, setActiveSection] = useState<Section>('dashboard');
  const [activeTab, setActiveTab] = useState<Tab>('list');
  const { alerts } = useAlerts();

  const triggeredAlertCount = alerts.filter((a) => a.status === 'triggered').length;
  const currentPage = PAGE_CONFIGS[activeSection];
  const showAction = SECTIONS_WITH_FORMS.includes(activeSection);

  const handleNavigate = useCallback((section: string): void => {
    setActiveSection(section as Section);
    setActiveTab('list');
  }, []);

  const handleAction = useCallback((): void => {
    setActiveTab((prev) => (prev === 'create' ? 'list' : 'create'));
  }, []);

  const handleFormComplete = useCallback((): void => {
    setActiveTab('list');
  }, []);

  const renderContent = (): React.ReactElement => {
    const showForm = activeTab === 'create';

    switch (activeSection) {
      case 'dashboard':
        return <DashboardPage />;
      case 'sources':
        return <SourcesPage showForm={showForm} onFormComplete={handleFormComplete} />;
      case 'events':
        return <EventsPage showForm={showForm} />;
      case 'rules':
        return <RulesPage showForm={showForm} onFormComplete={handleFormComplete} />;
      case 'alerts':
        return <AlertsPage />;
      case 'notifications':
        return <NotificationsPage showForm={showForm} onFormComplete={handleFormComplete} />;
    }
  };

  const actionLabel = activeTab === 'create' ? 'Cancel' : currentPage.actionLabel;
  const actionIcon = activeTab === 'create' ? 'close' : 'add';

  return (
    <div className="app">
      <Header
        activeSection={activeSection}
        onNavigate={handleNavigate}
        alertCount={triggeredAlertCount}
      />
      <main>
        <PageHeader
          title={currentPage.title}
          description={currentPage.description}
          actionLabel={showAction ? actionLabel : null}
          actionIcon={showAction ? actionIcon : null}
          onAction={showAction ? handleAction : null}
        />
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
