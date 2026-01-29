import { api } from './api';
import type { Event, EventInput, PaginatedResponse } from '../types';

export interface EventIngestResponse {
  timestamp: string;
  source: string;
  event_type: string;
  data: Record<string, unknown>;
}

export const eventService = {
  getAll: (params: Record<string, unknown> = {}): Promise<PaginatedResponse<Event>> => {
    const searchParams = new URLSearchParams();
    ['offset', 'limit', 'source_id', 'event_type'].forEach((key) => {
      const value = params[key];
      if (value !== undefined && value !== null && value !== '') {
        searchParams.set(key, String(value));
      }
    });
    const query = searchParams.toString();
    return api.get<PaginatedResponse<Event>>(`/events${query ? `?${query}` : ''}`);
  },
  ingest: (event: EventInput): Promise<EventIngestResponse> =>
    api.post<EventIngestResponse>('/events', event as unknown as Record<string, unknown>),
};
