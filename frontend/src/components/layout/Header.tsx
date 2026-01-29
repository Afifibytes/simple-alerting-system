import React, { useCallback } from 'react';
import { Icon } from '../common/Icon';

interface NavItem {
  id: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
  { id: 'alerts', label: 'Alerts', icon: 'warning' },
  { id: 'events', label: 'Events', icon: 'bolt' },
  { id: 'rules', label: 'Rules', icon: 'rule' },
  { id: 'sources', label: 'Sources', icon: 'source' },
  { id: 'notifications', label: 'Channels', icon: 'notifications' },
];

interface HeaderProps {
  activeSection: string;
  onNavigate: (section: string) => void;
  alertCount?: number;
}

export function Header({ activeSection, onNavigate, alertCount = 0 }: HeaderProps): React.ReactElement {
  // Single handler using data-section attribute - avoids creating functions in loop
  const handleNavClick = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    const section = e.currentTarget.dataset.section;
    if (section) onNavigate(section);
  }, [onNavigate]);

  const handleAlertsClick = useCallback(() => {
    onNavigate('alerts');
  }, [onNavigate]);

  return (
    <header className="header">
      <div className="header-inner">
        <div className="flex items-center gap-md">
          <div className="flex items-center gap-sm">
            <Icon name="monitoring" size="lg" />
            <h1>Simple Alerting System</h1>
          </div>

          <nav className="nav">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                data-section={item.id}
                className={`nav-link ${activeSection === item.id ? 'active' : ''}`}
                onClick={handleNavClick}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-sm">
          <button
            className="notification-bell"
            onClick={handleAlertsClick}
            title="View alerts"
          >
            <Icon name="notifications" />
            {alertCount > 0 && (
              <span className="notification-badge">
                {alertCount > 99 ? '99+' : alertCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
