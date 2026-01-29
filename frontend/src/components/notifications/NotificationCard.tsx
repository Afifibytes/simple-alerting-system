import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import type { NotificationChannel } from '../../types';

interface NotificationCardProps {
  channel: NotificationChannel;
  onUpdate: (id: string, data: Partial<NotificationChannel>) => Promise<NotificationChannel>;
  onDelete: (id: string) => Promise<void>;
}

interface FormState {
  name: string;
  is_active: boolean;
  config: string;
}

const CHANNEL_TYPE_LABELS: Record<string, string> = {
  email: 'Email',
  webhook: 'Webhook',
  slack: 'Slack',
};

export function NotificationCard({ channel, onUpdate, onDelete }: NotificationCardProps): React.ReactElement {
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [form, setForm] = useState<FormState>({
    name: channel.name,
    is_active: channel.is_active,
    config: JSON.stringify(channel.config, null, 2),
  });
  const [configError, setConfigError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    if (name === 'config') setConfigError(null);
  };

  const handleSave = async (): Promise<void> => {
    try {
      const parsedConfig = JSON.parse(form.config);
      await onUpdate(channel.id, {
        name: form.name,
        is_active: form.is_active,
        config: parsedConfig,
      });
      setEditing(false);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setConfigError('Invalid JSON format');
      } else {
        window.alert(err instanceof Error ? err.message : 'An error occurred');
      }
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!window.confirm(`Delete notification channel "${channel.name}"?`)) return;
    setDeleting(true);
    try {
      await onDelete(channel.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting(false);
    }
  };

  const formatConfig = (config: Record<string, unknown>): string => {
    if (channel.channel_type === 'email' && config.recipients) {
      return `Recipients: ${(config.recipients as string[]).join(', ')}`;
    }
    if (channel.channel_type === 'webhook' && config.url) {
      return `URL: ${config.url}`;
    }
    if (channel.channel_type === 'slack' && config.webhook_url) {
      return `Webhook: ${(config.webhook_url as string).substring(0, 40)}...`;
    }
    return JSON.stringify(config);
  };

  if (editing) {
    return (
      <div className="card card-spacing">
        <div className="form-group">
          <label className="form-label">Name</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Configuration (JSON)</label>
          <textarea
            name="config"
            value={form.config}
            onChange={handleChange}
            className="form-input font-mono text-sm"
            rows={4}
          />
          {configError && <div className="form-error">{configError}</div>}
        </div>
        <div className="form-group">
          <label className="flex items-center gap-sm">
            <input
              type="checkbox"
              name="is_active"
              checked={form.is_active}
              onChange={handleChange}
            />
            Active
          </label>
        </div>
        <div className="flex gap-sm">
          <button className="btn btn-primary btn-sm" onClick={handleSave}>
            Save
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => setEditing(false)}>
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card card-spacing">
      <div className="flex justify-between items-start mb-md">
        <div>
          <h3 className="font-semibold mb-xs">{channel.name}</h3>
          <div className="flex gap-sm">
            <span className="badge badge-info">
              {CHANNEL_TYPE_LABELS[channel.channel_type] || channel.channel_type}
            </span>
            <StatusBadge status={channel.is_active ? 'active' : 'inactive'} type="status" />
          </div>
        </div>
        <div className="flex gap-sm">
          <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}>
            Edit
          </button>
          <button
            className="btn btn-danger btn-sm"
            onClick={handleDelete}
            disabled={deleting}
          >
            Delete
          </button>
        </div>
      </div>

      <div className="text-sm text-muted">
        <strong>Config:</strong> {formatConfig(channel.config)}
      </div>
    </div>
  );
}
