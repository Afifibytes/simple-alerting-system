import { baseApi } from './api';
import type { HealthStatus } from '../types';

export const healthService = {
  check: (): Promise<HealthStatus> => baseApi.get<HealthStatus>('/health'),
};
