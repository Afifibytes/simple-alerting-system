import { createService } from './createService';
import { api } from './api';
import type { Alert, Service } from '../types';

const base = createService<Alert>('/alerts', ['rule_id', 'status', 'severity']);

export interface AlertService extends Service<Alert> {
  acknowledge: (id: string) => Promise<Alert>;
  resolve: (id: string, message?: string | null) => Promise<Alert>;
}

export const alertService: AlertService = {
  ...base,
  acknowledge: (id: string): Promise<Alert> => api.post<Alert>(`/alerts/${id}/acknowledge`),
  resolve: (id: string, message: string | null = null): Promise<Alert> => api.post<Alert>(`/alerts/${id}/resolve`, { message }),
};
