import { useState, useCallback, useRef, useReducer } from 'react';
import type { PaginatedResponse } from '../types';

interface Pagination {
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

interface ResourceState<T> {
  items: T[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
}

type ResourceAction<T> =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: PaginatedResponse<T> }
  | { type: 'FETCH_ERROR'; error: string }
  | { type: 'ADD_ITEM'; item: T }
  | { type: 'UPDATE_ITEM'; id: string; item: T }
  | { type: 'REMOVE_ITEM'; id: string };

interface UseResourceReturn<T, CreateDTO, UpdateDTO> {
  items: T[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  create: (data: CreateDTO) => Promise<T>;
  update: (id: string, data: UpdateDTO) => Promise<T>;
  remove: (id: string) => Promise<void>;
}

interface EntityWithId {
  id: string;
}

interface ServiceLike<T, CreateDTO, UpdateDTO> {
  getAll: (params?: Record<string, unknown>) => Promise<PaginatedResponse<T>>;
  create: (data: CreateDTO) => Promise<T>;
  update: (id: string, data: UpdateDTO) => Promise<T>;
  delete: (id: string) => Promise<void>;
}

function createReducer<T extends EntityWithId>() {
  return (state: ResourceState<T>, action: ResourceAction<T>): ResourceState<T> => {
    switch (action.type) {
      case 'FETCH_START':
        return { ...state, loading: true, error: null };
      case 'FETCH_SUCCESS':
        return {
          items: action.payload.items || [],
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
      case 'ADD_ITEM':
        return { ...state, items: [action.item, ...state.items] };
      case 'UPDATE_ITEM':
        return {
          ...state,
          items: state.items.map((i) => (i.id === action.id ? action.item : i)),
        };
      case 'REMOVE_ITEM':
        return {
          ...state,
          items: state.items.filter((i) => i.id !== action.id),
        };
      default:
        return state;
    }
  };
}

/**
 * Generic hook for CRUD resources with pagination.
 * Uses ref-based initialization to prevent double-fetch in StrictMode.
 * No useEffect - data fetching is triggered synchronously on first render.
 *
 * @param service - Service object with getAll, create, update, delete methods
 * @param defaultParams - Default fetch parameters
 */
export function useResource<T extends EntityWithId, CreateDTO = Partial<T>, UpdateDTO = Partial<T>>(
  service: ServiceLike<T, CreateDTO, UpdateDTO>,
  defaultParams: Record<string, unknown> = {}
): UseResourceReturn<T, CreateDTO, UpdateDTO> {
  const [state, dispatch] = useReducer(createReducer<T>(), {
    items: [],
    loading: true,
    error: null,
    pagination: { total: 0, offset: 0, limit: 50, has_more: false },
  });

  // Refs for stable references
  const defaultParamsRef = useRef(defaultParams);
  defaultParamsRef.current = defaultParams;

  const hasFetchedRef = useRef(false);
  const latestRequestRef = useRef(0);

  const refresh = useCallback(async (params: Record<string, unknown> = {}) => {
    const requestId = ++latestRequestRef.current;
    dispatch({ type: 'FETCH_START' });

    try {
      const response = await service.getAll({ ...defaultParamsRef.current, ...params });

      // Only update if this is still the latest request (prevents race conditions)
      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_SUCCESS', payload: response });
      }
    } catch (err) {
      if (requestId === latestRequestRef.current) {
        dispatch({ type: 'FETCH_ERROR', error: err instanceof Error ? err.message : 'An error occurred' });
      }
    }
  }, [service]);

  // Initial fetch - triggered synchronously, ref prevents double-fetch in StrictMode
  if (!hasFetchedRef.current) {
    hasFetchedRef.current = true;
    refresh();
  }

  const create = useCallback(async (data: CreateDTO): Promise<T> => {
    const item = await service.create(data);
    dispatch({ type: 'ADD_ITEM', item });
    return item;
  }, [service]);

  const update = useCallback(async (id: string, data: UpdateDTO): Promise<T> => {
    const item = await service.update(id, data);
    dispatch({ type: 'UPDATE_ITEM', id, item });
    return item;
  }, [service]);

  const remove = useCallback(async (id: string): Promise<void> => {
    await service.delete(id);
    dispatch({ type: 'REMOVE_ITEM', id });
  }, [service]);

  return {
    items: state.items,
    loading: state.loading,
    error: state.error,
    pagination: state.pagination,
    refresh,
    create,
    update,
    remove,
  };
}
