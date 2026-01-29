import { useResource } from './useResource';
import { sourceService } from '../services/sourceService';
import type { Source, SourceFormData } from '../types';

interface UseSourcesReturn {
  sources: Source[];
  loading: boolean;
  error: string | null;
  pagination: {
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
  };
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  createSource: (data: SourceFormData) => Promise<Source>;
  updateSource: (id: string, data: Partial<SourceFormData>) => Promise<Source>;
  deleteSource: (id: string) => Promise<void>;
}

export function useSources(): UseSourcesReturn {
  const { items: sources, create, update, remove, ...rest } = useResource<Source, SourceFormData, Partial<SourceFormData>>(sourceService);
  return { sources, createSource: create, updateSource: update, deleteSource: remove, ...rest };
}
