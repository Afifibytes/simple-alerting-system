import { api } from './api';
import type { PaginatedResponse, Service } from '../types';

/**
 * Factory to create CRUD services for API resources.
 * @param resource - The API resource path (e.g., '/sources', '/alerts')
 * @param filterParams - Query params to include in getAll (e.g., ['active_only', 'search'])
 */
export function createService<T, CreateDTO = Partial<T>, UpdateDTO = Partial<T>>(
  resource: string,
  filterParams: string[] = []
): Service<T, CreateDTO, UpdateDTO> {
  const buildQuery = (params: Record<string, unknown>): string => {
    const searchParams = new URLSearchParams();
    // Always include pagination params
    ['offset', 'limit', ...filterParams].forEach((key) => {
      const value = params[key];
      if (value !== undefined && value !== null && value !== '') {
        searchParams.set(key, String(value));
      }
    });
    const query = searchParams.toString();
    return query ? `?${query}` : '';
  };

  return {
    getAll: (params: Record<string, unknown> = {}): Promise<PaginatedResponse<T>> =>
      api.get<PaginatedResponse<T>>(`${resource}${buildQuery(params)}`),
    getById: (id: string): Promise<T> => api.get<T>(`${resource}/${id}`),
    create: (data: CreateDTO): Promise<T> => api.post<T>(resource, data as Record<string, unknown>),
    update: (id: string, data: UpdateDTO): Promise<T> => api.patch<T>(`${resource}/${id}`, data as Record<string, unknown>),
    delete: (id: string): Promise<void> => api.delete<void>(`${resource}/${id}`),
  };
}
