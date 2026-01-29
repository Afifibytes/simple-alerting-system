import { useCallback, useRef, useReducer } from 'react';
import { useSyncExternalStore } from 'react';
import { healthService } from '../services/healthService';
import type { HealthStatus } from '../types';

interface HealthState {
  health: HealthStatus | null;
  loading: boolean;
  error: string | null;
}

type HealthAction =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; health: HealthStatus }
  | { type: 'FETCH_ERROR'; error: string };

function healthReducer(state: HealthState, action: HealthAction): HealthState {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true };
    case 'FETCH_SUCCESS':
      return { health: action.health, loading: false, error: null };
    case 'FETCH_ERROR':
      return {
        health: { status: 'error', message: action.error },
        loading: false,
        error: action.error,
      };
    default:
      return state;
  }
}

/**
 * Creates an interval store for useSyncExternalStore.
 * This replaces useEffect + setInterval with a more React-idiomatic pattern.
 */
function createIntervalStore(intervalMs: number) {
  let tick = 0;
  let intervalId: ReturnType<typeof setInterval> | null = null;
  const listeners = new Set<() => void>();

  return {
    subscribe: (callback: () => void) => {
      listeners.add(callback);
      if (listeners.size === 1 && intervalMs > 0) {
        intervalId = setInterval(() => {
          tick++;
          listeners.forEach((l) => l());
        }, intervalMs);
      }
      return () => {
        listeners.delete(callback);
        if (listeners.size === 0 && intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      };
    },
    getSnapshot: () => tick,
  };
}

interface UseHealthReturn {
  health: HealthStatus | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

/**
 * Hook for health status with automatic polling.
 * Uses useSyncExternalStore for interval management instead of useEffect.
 *
 * @param refreshInterval - Polling interval in ms (default: 30000, 0 to disable)
 */
export function useHealth(refreshInterval = 30000): UseHealthReturn {
  const [state, dispatch] = useReducer(healthReducer, {
    health: null,
    loading: true,
    error: null,
  });

  const hasFetchedRef = useRef(false);
  const latestRequestRef = useRef(0);
  const storeRef = useRef<ReturnType<typeof createIntervalStore> | null>(null);

  const fetchHealth = useCallback(async () => {
    const requestId = ++latestRequestRef.current;

    try {
      const data = await healthService.check();
      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_SUCCESS', health: data });
      }
    } catch (err) {
      if (requestId === latestRequestRef.current) {
        dispatch({
          type: 'FETCH_ERROR',
          error: err instanceof Error ? err.message : 'An error occurred',
        });
      }
    }
  }, []);

  // Create interval store lazily
  if (!storeRef.current && refreshInterval > 0) {
    storeRef.current = createIntervalStore(refreshInterval);
  }

  // Subscribe to interval ticks using useSyncExternalStore
  const tick = useSyncExternalStore(
    storeRef.current?.subscribe ?? (() => () => {}),
    storeRef.current?.getSnapshot ?? (() => 0),
    storeRef.current?.getSnapshot ?? (() => 0)
  );

  // Initial fetch - ref prevents double-fetch in StrictMode
  if (!hasFetchedRef.current) {
    hasFetchedRef.current = true;
    fetchHealth();
  }

  // Interval-based refresh (when tick changes)
  const prevTickRef = useRef(tick);
  if (tick !== prevTickRef.current && tick > 0) {
    prevTickRef.current = tick;
    fetchHealth();
  }

  return {
    health: state.health,
    loading: state.loading,
    error: state.error,
    refresh: fetchHealth,
  };
}
