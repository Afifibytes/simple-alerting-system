import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import type { Source } from '../../types';

interface SourceCardProps {
  source: Source;
  onUpdate: (id: string, data: Partial<Source>) => Promise<Source>;
  onDelete: (id: string) => Promise<void>;
}

interface FormState {
  name: string;
  description: string;
  owner: string;
  is_active: boolean;
}

export function SourceCard({ source, onUpdate, onDelete }: SourceCardProps): React.ReactElement {
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [form, setForm] = useState<FormState>({
    name: source.name,
    description: source.description || '',
    owner: source.owner || '',
    is_active: source.is_active,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async (): Promise<void> => {
    try {
      await onUpdate(source.id, form);
      setEditing(false);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!window.confirm(`Delete source "${source.name}"?`)) return;
    setDeleting(true);
    try {
      await onDelete(source.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting(false);
    }
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
          <label className="form-label">Description</label>
          <input
            type="text"
            name="description"
            value={form.description}
            onChange={handleChange}
            className="form-input"
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
          />
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
          <h3 className="font-semibold mb-xs">{source.name}</h3>
          <StatusBadge status={source.is_active ? 'active' : 'inactive'} type="status" />
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

      <div className="grid grid-cols-2 gap-sm text-sm text-muted">
        <div>
          <strong>Description:</strong> {source.description || 'N/A'}
        </div>
        <div>
          <strong>Owner:</strong> {source.owner || 'N/A'}
        </div>
      </div>
    </div>
  );
}
