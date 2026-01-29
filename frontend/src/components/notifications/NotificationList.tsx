import React, { useState } from 'react';
import { DataTable } from '../common/DataTable';
import { StatusBadge } from '../common/StatusBadge';
import { ToggleSwitch } from '../common/ToggleSwitch';
import { Icon } from '../common/Icon';
import type { NotificationChannel } from '../../types';

interface NotificationListProps {
  channels: NotificationChannel[];
  loading: boolean;
  onUpdate: (id: string, data: Partial<NotificationChannel>) => Promise<NotificationChannel>;
  onDelete: (id: string) => Promise<void>;
}

interface EditFormState {
  name: string;
  config: string;
}

interface DeletingState {
  [key: string]: boolean;
}

export function NotificationList({ channels, loading, onUpdate, onDelete }: NotificationListProps): React.ReactElement {
  const [editing, setEditing] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>({ name: '', config: '' });
  const [configError, setConfigError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<DeletingState>({});

  const handleEdit = (channel: NotificationChannel): void => {
    setEditing(channel.id);
    setEditForm({
      name: channel.name,
      config: JSON.stringify(channel.config, null, 2),
    });
    setConfigError(null);
  };

  const handleSave = async (channel: NotificationChannel): Promise<void> => {
    try {
      const parsedConfig = JSON.parse(editForm.config);
      await onUpdate(channel.id, {
        name: editForm.name,
        config: parsedConfig,
      });
      setEditing(null);
      setConfigError(null);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setConfigError('Invalid JSON format');
      } else {
        window.alert(err instanceof Error ? err.message : 'An error occurred');
      }
    }
  };

  const handleCancel = (): void => {
    setEditing(null);
    setEditForm({ name: '', config: '' });
    setConfigError(null);
  };

  const handleToggleActive = async (channel: NotificationChannel, isActive: boolean): Promise<void> => {
    await onUpdate(channel.id, { is_active: isActive });
  };

  const handleDelete = async (channel: NotificationChannel): Promise<void> => {
    if (!window.confirm(`Delete channel "${channel.name}"?`)) return;
    setDeleting((prev) => ({ ...prev, [channel.id]: true }));
    try {
      await onDelete(channel.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting((prev) => ({ ...prev, [channel.id]: false }));
    }
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'email':
        return 'mail';
      case 'slack':
        return 'tag';
      case 'webhook':
        return 'webhook';
      default:
        return 'notifications';
    }
  };

  const formatConfig = (channel: NotificationChannel): string => {
    const config = channel.config;
    if (channel.channel_type === 'email' && config.recipients) {
      return (config.recipients as string[]).join(', ');
    }
    if (channel.channel_type === 'webhook' && config.url) {
      const url = config.url as string;
      return url.length > 40 ? url.substring(0, 40) + '...' : url;
    }
    if (channel.channel_type === 'slack' && config.webhook_url) {
      return (config.webhook_url as string).substring(0, 40) + '...';
    }
    return JSON.stringify(config);
  };

  const columns = [
    { header: 'Name', width: '20%' },
    { header: 'Type', width: '12%' },
    { header: 'Configuration', width: '33%' },
    { header: 'Active', width: '10%' },
    { header: 'Actions', width: '25%' },
  ];

  const renderRow = (channel: NotificationChannel): React.ReactElement => {
    if (editing === channel.id) {
      return (
        <tr key={channel.id}>
          <td>
            <input
              type="text"
              className="form-input"
              value={editForm.name}
              onChange={(e) => setEditForm((prev) => ({ ...prev, name: e.target.value }))}
              style={{ padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.875rem' }}
            />
          </td>
          <td>
            <StatusBadge status={channel.channel_type} type="info" showDot={false} />
          </td>
          <td>
            <div>
              <textarea
                className="form-input"
                value={editForm.config}
                onChange={(e) => {
                  setEditForm((prev) => ({ ...prev, config: e.target.value }));
                  setConfigError(null);
                }}
                rows={3}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.75rem',
                  padding: 'var(--spacing-xs) var(--spacing-sm)',
                }}
              />
              {configError && <div className="form-error">{configError}</div>}
            </div>
          </td>
          <td>
            <ToggleSwitch
              checked={channel.is_active}
              onChange={(checked) => handleToggleActive(channel, checked)}
            />
          </td>
          <td>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
              <button className="btn btn-primary btn-sm" onClick={() => handleSave(channel)}>
                Save
              </button>
              <button className="btn btn-ghost btn-sm" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </td>
        </tr>
      );
    }

    return (
      <tr key={channel.id}>
        <td>
          <div className="table-cell-primary">{channel.name}</div>
        </td>
        <td>
          <span className="badge badge-info">
            <Icon name={getTypeIcon(channel.channel_type)} size="sm" />
            {channel.channel_type}
          </span>
        </td>
        <td>
          <code className="table-cell-muted" style={{ fontSize: '0.75rem' }}>
            {formatConfig(channel)}
          </code>
        </td>
        <td>
          <ToggleSwitch
            checked={channel.is_active}
            onChange={(checked) => handleToggleActive(channel, checked)}
            label={channel.is_active ? 'Active' : 'Inactive'}
          />
        </td>
        <td>
          <div className="row-actions">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => handleEdit(channel)}
              title="Edit channel"
            >
              <Icon name="edit" size="sm" />
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => handleDelete(channel)}
              disabled={deleting[channel.id]}
              title="Delete channel"
              style={{ color: 'var(--color-danger)' }}
            >
              <Icon name="delete" size="sm" />
            </button>
          </div>
        </td>
      </tr>
    );
  };

  return (
    <DataTable
      columns={columns}
      data={channels}
      loading={loading}
      emptyIcon="notifications"
      emptyTitle="No notification channels"
      emptyDescription="Create a channel to receive alert notifications."
      renderRow={renderRow}
    />
  );
}
