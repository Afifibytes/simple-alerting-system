import React, { useState } from 'react';
import type { NotificationFormData } from '../../types';

interface NotificationFormProps {
  onSubmit: (data: NotificationFormData) => Promise<unknown>;
  loading: boolean;
}

interface FormState {
  name: string;
  channel_type: 'email' | 'webhook' | 'slack';
  config: string;
}

const initialFormState: FormState = {
  name: '',
  channel_type: 'email',
  config: '',
};

const configTemplates: Record<string, string> = {
  email: '{\n  "recipients": ["user@example.com"]\n}',
  webhook: '{\n  "url": "https://example.com/webhook"\n}',
  slack: '{\n  "webhook_url": "https://hooks.slack.com/services/..."\n}',
};

export function NotificationForm({ onSubmit, loading }: NotificationFormProps): React.ReactElement {
  const [form, setForm] = useState<FormState>({
    ...initialFormState,
    config: configTemplates.email,
  });
  const [error, setError] = useState<string | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>): void => {
    const { name, value } = e.target;
    setForm((prev) => {
      const newForm = { ...prev, [name]: value };
      if (name === 'channel_type') {
        newForm.config = configTemplates[value] || '{}';
      }
      return newForm as FormState;
    });
    if (name === 'config') setConfigError(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError(null);
    setConfigError(null);

    let parsedConfig: Record<string, unknown>;
    try {
      parsedConfig = JSON.parse(form.config);
    } catch {
      setConfigError('Invalid JSON format');
      return;
    }

    try {
      await onSubmit({
        name: form.name,
        channel_type: form.channel_type,
        config: parsedConfig,
      });
      setForm({
        ...initialFormState,
        config: configTemplates.email,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Create Notification Channel</h2>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Name</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g., Ops Team Email"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Channel Type</label>
            <select
              name="channel_type"
              value={form.channel_type}
              onChange={handleChange}
              className="form-select"
            >
              <option value="email">Email</option>
              <option value="webhook">Webhook</option>
              <option value="slack">Slack</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Configuration (JSON)</label>
          <textarea
            name="config"
            value={form.config}
            onChange={handleChange}
            className="form-input"
            rows={5}
            style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}
            required
          />
          {configError && <div className="form-error">{configError}</div>}
          <p className="form-hint">
            {form.channel_type === 'email' && 'Email config: {"recipients": ["email1", "email2"]}'}
            {form.channel_type === 'webhook' && 'Webhook config: {"url": "https://..."}'}
            {form.channel_type === 'slack' && 'Slack config: {"webhook_url": "https://hooks.slack.com/..."}'}
          </p>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Creating...' : 'Create Channel'}
        </button>
      </form>
    </div>
  );
}
