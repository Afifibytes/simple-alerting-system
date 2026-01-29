import React, { useState } from 'react';
import type { Source, EventInput } from '../../types';

interface EventFormProps {
  onSubmit: (event: EventInput) => Promise<unknown>;
  loading: boolean;
  sources: Source[];
  loadingSources: boolean;
}

/**
 * Event form component.
 * Best practice: Receives sources as props instead of fetching internally.
 * This eliminates useEffect and prevents duplicate data fetching.
 */
export function EventForm({ onSubmit, loading, sources, loadingSources }: EventFormProps): React.ReactElement {
  const [source, setSource] = useState('');
  const [eventType, setEventType] = useState('log');
  const [dataKey, setDataKey] = useState('message');
  const [dataValue, setDataValue] = useState('');
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const event: EventInput = {
        source,
        event_type: eventType,
        data: { [dataKey]: dataValue },
      };
      await onSubmit(event);
      setSuccess('Event ingested successfully!');
      setDataValue('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // Filter for active sources only
  const activeSources = sources.filter(s => s.is_active);

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Ingest Event</h2>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Source</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="form-select"
              required
              disabled={loadingSources}
            >
              <option value="">
                {loadingSources ? 'Loading sources...' : 'Select a source'}
              </option>
              {activeSources.map((s) => (
                <option key={s.id} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
            {!loadingSources && activeSources.length === 0 && (
              <p className="form-hint text-warning">
                No sources available. Create a source first.
              </p>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Event Type</label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="form-select"
            >
              <option value="log">Log</option>
              <option value="metric">Metric</option>
              <option value="trace">Trace</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Data Key</label>
            <input
              type="text"
              value={dataKey}
              onChange={(e) => setDataKey(e.target.value)}
              className="form-input"
              placeholder="e.g., message, value"
              required
            />
            <p className="form-hint">The field name for your event data</p>
          </div>

          <div className="form-group">
            <label className="form-label">Data Value</label>
            <input
              type="text"
              value={dataValue}
              onChange={(e) => setDataValue(e.target.value)}
              className="form-input"
              placeholder="e.g., Error occurred, 95"
              required
            />
            <p className="form-hint">The value that rules will evaluate against</p>
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-success"
          disabled={loading || loadingSources || activeSources.length === 0}
        >
          {loading ? 'Ingesting...' : 'Ingest Event'}
        </button>
      </form>
    </div>
  );
}
