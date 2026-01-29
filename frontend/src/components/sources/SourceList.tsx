import React, { useState } from 'react';
import { DataTable } from '../common/DataTable';
import { ToggleSwitch } from '../common/ToggleSwitch';
import { Icon } from '../common/Icon';
import type { Source } from '../../types';

interface SourceListProps {
  sources: Source[];
  loading: boolean;
  onUpdate: (id: string, data: Partial<Source>) => Promise<Source>;
  onDelete: (id: string) => Promise<void>;
}

interface EditFormState {
  name: string;
  description: string;
  owner: string;
}

interface DeletingState {
  [key: string]: boolean;
}

export function SourceList({ sources, loading, onUpdate, onDelete }: SourceListProps): React.ReactElement {
  const [editing, setEditing] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>({ name: '', description: '', owner: '' });
  const [deleting, setDeleting] = useState<DeletingState>({});

  const handleEdit = (source: Source): void => {
    setEditing(source.id);
    setEditForm({
      name: source.name,
      description: source.description || '',
      owner: source.owner || '',
    });
  };

  const handleSave = async (source: Source): Promise<void> => {
    try {
      await onUpdate(source.id, editForm);
      setEditing(null);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleCancel = (): void => {
    setEditing(null);
    setEditForm({ name: '', description: '', owner: '' });
  };

  const handleToggleActive = async (source: Source, isActive: boolean): Promise<void> => {
    await onUpdate(source.id, { is_active: isActive });
  };

  const handleDelete = async (source: Source): Promise<void> => {
    if (!window.confirm(`Delete source "${source.name}"?`)) return;
    setDeleting((prev) => ({ ...prev, [source.id]: true }));
    try {
      await onDelete(source.id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'An error occurred');
      setDeleting((prev) => ({ ...prev, [source.id]: false }));
    }
  };

  const columns = [
    { header: 'Name', width: '25%' },
    { header: 'Description', width: '30%' },
    { header: 'Owner', width: '15%' },
    { header: 'Active', width: '10%' },
    { header: 'Actions', width: '20%' },
  ];

  const renderRow = (source: Source): React.ReactElement => {
    if (editing === source.id) {
      return (
        <tr key={source.id}>
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
            <input
              type="text"
              className="form-input"
              value={editForm.description}
              onChange={(e) => setEditForm((prev) => ({ ...prev, description: e.target.value }))}
              style={{ padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.875rem' }}
              placeholder="Description..."
            />
          </td>
          <td>
            <input
              type="text"
              className="form-input"
              value={editForm.owner}
              onChange={(e) => setEditForm((prev) => ({ ...prev, owner: e.target.value }))}
              style={{ padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.875rem' }}
              placeholder="Owner..."
            />
          </td>
          <td>
            <ToggleSwitch
              checked={source.is_active}
              onChange={(checked) => handleToggleActive(source, checked)}
            />
          </td>
          <td>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
              <button className="btn btn-primary btn-sm" onClick={() => handleSave(source)}>
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
      <tr key={source.id}>
        <td>
          <div className="table-cell-primary">{source.name}</div>
        </td>
        <td className="table-cell-secondary">
          {source.description || <span className="table-cell-muted">No description</span>}
        </td>
        <td className="table-cell-secondary">
          {source.owner || <span className="table-cell-muted">Unassigned</span>}
        </td>
        <td>
          <ToggleSwitch
            checked={source.is_active}
            onChange={(checked) => handleToggleActive(source, checked)}
            label={source.is_active ? 'Active' : 'Inactive'}
          />
        </td>
        <td>
          <div className="row-actions">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => handleEdit(source)}
              title="Edit source"
            >
              <Icon name="edit" size="sm" />
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => handleDelete(source)}
              disabled={deleting[source.id]}
              title="Delete source"
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
      data={sources}
      loading={loading}
      emptyIcon="source"
      emptyTitle="No sources configured"
      emptyDescription="Create your first source to start receiving events."
      renderRow={renderRow}
    />
  );
}
