import React, { useState } from 'react';
import type { Source, NotificationChannel, RuleFormData } from '../../types';

interface RuleFormProps {
  onSubmit: (data: RuleFormData) => Promise<unknown>;
  loading: boolean;
  sources: Source[];
  loadingSources: boolean;
  channels: NotificationChannel[];
  loadingChannels: boolean;
}

const initialFormState: RuleFormData = {
  name: '',
  source_id: '',
  condition_type: 'count',
  condition_field: '',
  condition_operator: 'contains',
  condition_value: '',
  condition_threshold: 5,
  severity: 'medium',
  time_window_seconds: 60,
  notification_channel_ids: [],
};

/**
 * Rule form component.
 * Best practice: Receives sources and channels as props instead of fetching internally.
 * This eliminates useEffect and prevents duplicate data fetching.
 */
export function RuleForm({
  onSubmit,
  loading,
  sources,
  loadingSources,
  channels,
  loadingChannels
}: RuleFormProps): React.ReactElement {
  const [form, setForm] = useState<RuleFormData>(initialFormState);
  const [error, setError] = useState<string | null>(null);

  // Filter for active sources and channels
  const activeSources = sources.filter(s => s.is_active);
  const activeChannels = channels.filter(c => c.is_active);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]:
        name === 'condition_threshold' || name === 'time_window_seconds'
          ? parseInt(value, 10) || 0
          : value,
    }));
  };

  const handleChannelToggle = (channelId: string): void => {
    setForm((prev) => {
      const ids = prev.notification_channel_ids;
      if (ids.includes(channelId)) {
        return { ...prev, notification_channel_ids: ids.filter((id) => id !== channelId) };
      } else {
        return { ...prev, notification_channel_ids: [...ids, channelId] };
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError(null);

    try {
      await onSubmit(form);
      setForm(initialFormState);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Create Alert Rule</h2>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Rule Name</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            className="form-input"
            placeholder="e.g., High Error Rate Alert"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Source</label>
            <select
              name="source_id"
              value={form.source_id}
              onChange={handleChange}
              className="form-select"
              required
              disabled={loadingSources}
            >
              <option value="">
                {loadingSources ? 'Loading sources...' : 'Select a source'}
              </option>
              {activeSources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Condition Type</label>
            <select
              name="condition_type"
              value={form.condition_type}
              onChange={handleChange}
              className="form-select"
            >
              <option value="count">Count</option>
              <option value="threshold">Threshold</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Field to Check</label>
            <input
              type="text"
              name="condition_field"
              value={form.condition_field}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g., message, value"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Operator</label>
            <select
              name="condition_operator"
              value={form.condition_operator}
              onChange={handleChange}
              className="form-select"
            >
              <option value="contains">Contains</option>
              <option value="eq">Equals</option>
              <option value="gt">Greater Than</option>
              <option value="lt">Less Than</option>
              <option value="gte">Greater or Equal</option>
              <option value="lte">Less or Equal</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Condition Value</label>
            <input
              type="text"
              name="condition_value"
              value={form.condition_value}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g., exception, 90"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Threshold</label>
            <input
              type="number"
              name="condition_threshold"
              value={form.condition_threshold}
              onChange={handleChange}
              className="form-input"
              min="1"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Severity</label>
            <select
              name="severity"
              value={form.severity}
              onChange={handleChange}
              className="form-select"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Time Window (seconds)</label>
            <input
              type="number"
              name="time_window_seconds"
              value={form.time_window_seconds}
              onChange={handleChange}
              className="form-input"
              min="1"
              max="86400"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Notification Channels (optional)</label>
          {loadingChannels ? (
            <p className="form-hint">Loading channels...</p>
          ) : activeChannels.length === 0 ? (
            <p className="form-hint">
              No notification channels configured. Create one in the Channels tab.
            </p>
          ) : (
            <div className="channel-chips">
              {activeChannels.map((channel) => (
                <label
                  key={channel.id}
                  className={`channel-chip ${
                    form.notification_channel_ids.includes(channel.id) ? 'selected' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={form.notification_channel_ids.includes(channel.id)}
                    onChange={() => handleChannelToggle(channel.id)}
                    className="hidden"
                  />
                  <span className="font-medium">{channel.name}</span>
                  <span className="channel-chip-type">({channel.channel_type})</span>
                </label>
              ))}
            </div>
          )}
          <p className="form-hint">
            Select channels to receive notifications when this rule triggers an alert.
          </p>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Creating...' : 'Create Rule'}
        </button>
      </form>
    </div>
  );
}
