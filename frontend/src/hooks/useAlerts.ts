import { useCallback, useRef, useReducer, useEffect } from 'react';
import { alertService } from '../services/alertService';
import type { Alert, PaginatedResponse } from '../types';

interface Pagination {
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

interface AlertState {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
}

type AlertAction =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: PaginatedResponse<Alert> }
  | { type: 'FETCH_ERROR'; error: string }
  | { type: 'UPDATE_ALERT'; id: string; alert: Alert };

function alertReducer(state: AlertState, action: AlertAction): AlertState {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return {
        alerts: action.payload.items || [],
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
    case 'UPDATE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map((a) => (a.id === action.id ? action.alert : a)),
      };
    default:
      return state;
  }
}

interface UseAlertsReturn {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  acknowledgeAlert: (id: string) => Promise<Alert>;
  resolveAlert: (id: string, message?: string | null) => Promise<Alert>;
}

const DEFAULT_LIMIT = 50;
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Hook for managing alerts with real-time SSE updates.
 */
export function useAlerts(): UseAlertsReturn {
  const [state, dispatch] = useReducer(alertReducer, {
    alerts: [],
    loading: true,
    error: null,
    pagination: { total: 0, offset: 0, limit: DEFAULT_LIMIT, has_more: false },
  });

  const hasFetchedRef = useRef(false);
  const latestRequestRef = useRef(0);
  const currentParamsRef = useRef<Record<string, unknown>>({});

  const fetchAlerts = useCallback(async (params: Record<string, unknown>, showLoading: boolean) => {
    const requestId = ++latestRequestRef.current;
    if (showLoading) {
      dispatch({ type: 'FETCH_START' });
    }

    try {
      const response = await alertService.getAll({
        limit: DEFAULT_LIMIT,
        offset: 0,
        ...params,
      });

      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_SUCCESS', payload: response });
      }
    } catch (err) {
      if (requestId === latestRequestRef.current && showLoading) {
        dispatch({ type: 'FETCH_ERROR', error: err instanceof Error ? err.message : 'An error occurred' });
      }
    }
  }, []);

  const refresh = useCallback(async (params: Record<string, unknown> = {}) => {
    currentParamsRef.current = params;
    return fetchAlerts(params, true);
  }, [fetchAlerts]);

  // Initial fetch
  if (!hasFetchedRef.current) {
    hasFetchedRef.current = true;
    refresh();
  }

  // SSE listener for real-time alert updates
  useEffect(() => {
    let eventSource: EventSource | null = null;
    let retryTimeout: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      eventSource = new EventSource(`${API_URL}/v1/alerts/stream`);

      eventSource.onmessage = (event) => {
        if (event.data !== 'connected') {
          // New alert received, refresh the list silently
          fetchAlerts(currentParamsRef.current, false);
        }
      };

      eventSource.onerror = () => {
        eventSource?.close();
        // Retry connection after 5 seconds
        retryTimeout = setTimeout(connect, 5000);
      };
    };

    connect();

    return () => {
      eventSource?.close();
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [fetchAlerts]);

  const acknowledgeAlert = useCallback(async (id: string): Promise<Alert> => {
    const updated = await alertService.acknowledge(id);
    dispatch({ type: 'UPDATE_ALERT', id, alert: updated });
    return updated;
  }, []);

  const resolveAlert = useCallback(async (id: string, message: string | null = null): Promise<Alert> => {
    const updated = await alertService.resolve(id, message);
    dispatch({ type: 'UPDATE_ALERT', id, alert: updated });
    return updated;
  }, []);

  return {
    alerts: state.alerts,
    loading: state.loading,
    error: state.error,
    pagination: state.pagination,
    refresh,
    acknowledgeAlert,
    resolveAlert,
  };
}
