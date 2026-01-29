import { useState, useCallback, useRef, useReducer } from 'react';
import { eventService, EventIngestResponse } from '../services/eventService';
import type { Event, EventInput, PaginatedResponse } from '../types';

interface Pagination {
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

interface EventState {
  events: Event[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
}

type EventAction =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: PaginatedResponse<Event> }
  | { type: 'FETCH_ERROR'; error: string };

function eventReducer(state: EventState, action: EventAction): EventState {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return {
        events: action.payload.items || [],
        loading: false,
        error: null,
        pagination: {
          total: action.payload.total,
          offset: action.payload.offset,
          limit: action.payload.limit,
          has_more: action.payload.has_more,
        },
      };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.error };
    default:
      return state;
  }
}

const DEFAULT_LIMIT = 50;

interface UseEventsReturn {
  events: Event[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  ingestEvent: (event: EventInput) => Promise<EventIngestResponse>;
  ingestLoading: boolean;
  lastEvent: EventIngestResponse | null;
}

export function useEvents(): UseEventsReturn {
  const [state, dispatch] = useReducer(eventReducer, {
    events: [],
    loading: true,
    error: null,
    pagination: { total: 0, offset: 0, limit: DEFAULT_LIMIT, has_more: false },
  });

  const [ingestLoading, setIngestLoading] = useState(false);
  const [lastEvent, setLastEvent] = useState<EventIngestResponse | null>(null);

  const hasFetchedRef = useRef(false);
  const latestRequestRef = useRef(0);

  const refresh = useCallback(async (params: Record<string, unknown> = {}) => {
    const requestId = ++latestRequestRef.current;
    dispatch({ type: 'FETCH_START' });

    try {
      const response = await eventService.getAll({
        limit: DEFAULT_LIMIT,
        offset: 0,
        ...params,
      });

      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_SUCCESS', payload: response });
      }
    } catch (err) {
      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_ERROR', error: err instanceof Error ? err.message : 'An error occurred' });
      }
    }
  }, []);

  // Initial fetch
  if (!hasFetchedRef.current) {
    hasFetchedRef.current = true;
    refresh();
  }

  const ingestEvent = useCallback(async (event: EventInput): Promise<EventIngestResponse> => {
    try {
      setIngestLoading(true);
      const result = await eventService.ingest(event);
      setLastEvent(result);
      // Refresh list after successful ingest
      refresh();
      return result;
    } finally {
      setIngestLoading(false);
    }
  }, [refresh]);

  return {
    events: state.events,
    loading: state.loading,
    error: state.error,
    pagination: state.pagination,
    refresh,
    ingestEvent,
    ingestLoading,
    lastEvent,
  };
}
