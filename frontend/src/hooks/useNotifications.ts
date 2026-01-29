import { useResource } from './useResource';
import { notificationService } from '../services/notificationService';
import type { NotificationChannel, NotificationFormData } from '../types';

interface UseNotificationsReturn {
  channels: NotificationChannel[];
  loading: boolean;
  error: string | null;
  pagination: {
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
  };
  refresh: (params?: Record<string, unknown>) => Promise<void>;
  createChannel: (data: NotificationFormData) => Promise<NotificationChannel>;
  updateChannel: (id: string, data: Partial<NotificationFormData>) => Promise<NotificationChannel>;
  deleteChannel: (id: string) => Promise<void>;
}

export function useNotifications(): UseNotificationsReturn {
  const { items: channels, create, update, remove, ...rest } = useResource<NotificationChannel, NotificationFormData, Partial<NotificationFormData>>(notificationService);
  return { channels, createChannel: create, updateChannel: update, deleteChannel: remove, ...rest };
}
