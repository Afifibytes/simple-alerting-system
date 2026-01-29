import { useState, useCallback, useRef } from 'react';

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseAsyncReturn<T, Args extends unknown[]> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: Args) => Promise<T | null>;
  reset: () => void;
}

/**
 * Hook for handling async operations with proper state management.
 * Unlike useEffect-based fetching, this gives you control over when to execute.
 *
 * Best practice: Call execute() in event handlers or use useAsyncOnMount for initial fetch.
 */
export function useAsync<T, Args extends unknown[] = []>(
  asyncFn: (...args: Args) => Promise<T>
): UseAsyncReturn<T, Args> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  // Track the latest request to handle race conditions
  const latestRequestRef = useRef(0);

  const execute = useCallback(async (...args: Args): Promise<T | null> => {
    const requestId = ++latestRequestRef.current;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await asyncFn(...args);

      // Only update state if this is still the latest request (prevents race conditions)
      if (requestId === latestRequestRef.current) {
        setState({ data: result, loading: false, error: null });
        return result;
      }
      return null;
    } catch (err) {
      if (requestId === latestRequestRef.current) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setState({ data: null, loading: false, error: errorMessage });
      }
      return null;
    }
  }, [asyncFn]);

  const reset = useCallback(() => {
    latestRequestRef.current++;
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

/**
 * Hook for data that should be fetched once on mount.
 * Uses a ref to prevent double-fetching in StrictMode.
 */
export function useAsyncOnMount<T>(
  asyncFn: () => Promise<T>,
  deps: React.DependencyList = []
): Omit<UseAsyncReturn<T, []>, 'execute'> & { refresh: () => Promise<T | null> } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true, // Start loading immediately
    error: null,
  });

  const hasFetchedRef = useRef(false);
  const latestRequestRef = useRef(0);

  const execute = useCallback(async (): Promise<T | null> => {
    const requestId = ++latestRequestRef.current;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await asyncFn();

      if (requestId === latestRequestRef.current) {
        setState({ data: result, loading: false, error: null });
        return result;
      }
      return null;
    } catch (err) {
      if (requestId === latestRequestRef.current) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setState({ data: null, loading: false, error: errorMessage });
      }
      return null;
    }
  }, [asyncFn]);

  const reset = useCallback(() => {
    latestRequestRef.current++;
    setState({ data: null, loading: false, error: null });
  }, []);

  // Initial fetch - only runs once even in StrictMode
  if (!hasFetchedRef.current) {
    hasFetchedRef.current = true;
    execute();
  }

  return { ...state, refresh: execute, reset };
}
