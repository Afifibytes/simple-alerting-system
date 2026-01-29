import React, { useState } from 'react';
import { NotificationForm } from '../components/notifications/NotificationForm';
import { NotificationList } from '../components/notifications/NotificationList';
import { useNotifications } from '../hooks/useNotifications';
import type { NotificationFormData } from '../types';

interface NotificationsPageProps {
  showForm: boolean;
  onFormComplete: () => void;
}

export function NotificationsPage({ showForm, onFormComplete }: NotificationsPageProps): React.ReactElement {
  const { channels, loading, createChannel, updateChannel, deleteChannel } = useNotifications();
  const [creating, setCreating] = useState(false);

  const handleCreateChannel = async (channel: NotificationFormData): Promise<void> => {
    setCreating(true);
    try {
      await createChannel(channel);
      onFormComplete();
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      {showForm && (
        <>
          <NotificationForm onSubmit={handleCreateChannel} loading={creating} />
          <div className="section-divider" />
        </>
      )}
      <NotificationList
        channels={channels}
        loading={loading}
        onUpdate={updateChannel}
        onDelete={deleteChannel}
      />
    </>
  );
}
