import React from 'react';
import { EventForm } from '../components/events/EventForm';
import { EventList } from '../components/events/EventList';
import { useEvents } from '../hooks/useEvents';
import { useSources } from '../hooks/useSources';

interface EventsPageProps {
  showForm: boolean;
}

export function EventsPage({ showForm }: EventsPageProps): React.ReactElement {
  const {
    events,
    loading: eventsLoading,
    pagination,
    refresh,
    ingestEvent,
    ingestLoading,
    lastEvent,
  } = useEvents();
  const { sources, loading: sourcesLoading } = useSources();

  const handlePageChange = (page: number): void => {
    const offset = (page - 1) * pagination.limit;
    refresh({ offset });
  };

  return (
    <>
      {showForm && (
        <>
          <EventForm
            onSubmit={ingestEvent}
            loading={ingestLoading}
            sources={sources}
            loadingSources={sourcesLoading}
          />
          {lastEvent && (
            <div className="card mt-md">
              <h3 className="mb-sm font-semibold">Last Ingested Event</h3>
              <pre>{JSON.stringify(lastEvent, null, 2)}</pre>
            </div>
          )}
          <div className="section-divider" />
        </>
      )}
      <EventList
        events={events}
        loading={eventsLoading}
        pagination={pagination}
        onPageChange={handlePageChange}
      />
    </>
  );
}
