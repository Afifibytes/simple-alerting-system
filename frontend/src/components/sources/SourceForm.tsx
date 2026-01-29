import React, { useState } from 'react';
import type { SourceFormData } from '../../types';

interface SourceFormProps {
  onSubmit: (data: Omit<SourceFormData, 'is_active'>) => Promise<unknown>;
  loading: boolean;
}

interface FormState {
  name: string;
  description: string;
  owner: string;
}

const initialFormState: FormState = {
  name: '',
  description: '',
  owner: '',
};

export function SourceForm({ onSubmit, loading }: SourceFormProps): React.ReactElement {
  const [form, setForm] = useState<FormState>(initialFormState);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError(null);

    try {
      await onSubmit({
        name: form.name,
        description: form.description || null,
        owner: form.owner || null,
      });
      setForm(initialFormState);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Create Source</h2>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Name</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            className="form-input"
            placeholder="e.g., app-logs, payment-service"
            required
          />
          <p className="form-hint">A unique identifier for this event source</p>
        </div>

        <div className="form-group">
          <label className="form-label">Description</label>
          <input
            type="text"
            name="description"
            value={form.description}
            onChange={handleChange}
            className="form-input"
            placeholder="Optional description"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Owner</label>
          <input
            type="text"
            name="owner"
            value={form.owner}
            onChange={handleChange}
            className="form-input"
            placeholder="e.g., team-backend"
          />
          <p className="form-hint">Team or person responsible for this source</p>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Creating...' : 'Create Source'}
        </button>
      </form>
    </div>
  );
}
