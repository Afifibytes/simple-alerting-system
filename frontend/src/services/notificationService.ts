import { createService } from './createService';
import type { NotificationChannel, NotificationFormData } from '../types';

export const notificationService = createService<NotificationChannel, NotificationFormData, Partial<NotificationFormData>>('/notification-channels', ['active_only', 'channel_type']);
