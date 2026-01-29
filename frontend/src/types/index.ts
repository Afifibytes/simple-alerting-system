// API Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

// Entity Types
export interface Source {
  id: string;
  name: string;
  description: string | null;
  owner: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Rule {
  id: string;
  name: string;
  source_id: string;
  source_name?: string;
  condition_type: 'count' | 'threshold';
  condition_field: string;
  condition_operator: 'contains' | 'eq' | 'gt' | 'lt' | 'gte' | 'lte';
  condition_value: string;
  condition_threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  time_window_seconds: number;
  notification_channel_ids: string[];
  notification_channels?: NotificationChannel[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  rule_name?: string;
  status: 'triggered' | 'acknowledged' | 'resolved';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string | null;
  triggered_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  resolved_message: string | null;
  matches_count: number;
}

export interface NotificationChannel {
  id: string;
  name: string;
  channel_type: 'email' | 'webhook' | 'slack';
  config: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  source_id: string;
  source_name: string;
  event_type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface EventInput {
  source: string;
  event_type: string;
  data: Record<string, unknown>;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'error';
  message?: string;
  database?: 'connected' | 'disconnected';
  rabbitmq?: 'connected' | 'disconnected';
}

// Service Types
export interface Service<T, CreateDTO = Partial<T>, UpdateDTO = Partial<T>> {
  getAll: (params?: Record<string, unknown>) => Promise<PaginatedResponse<T>>;
  getById: (id: string) => Promise<T>;
  create: (data: CreateDTO) => Promise<T>;
  update: (id: string, data: UpdateDTO) => Promise<T>;
  delete: (id: string) => Promise<void>;
}

// Form Types
export interface SourceFormData {
  name: string;
  description: string | null;
  owner: string | null;
  is_active?: boolean;
}

export interface RuleFormData {
  name: string;
  source_id: string;
  condition_type: 'count' | 'threshold';
  condition_field: string;
  condition_operator: 'contains' | 'eq' | 'gt' | 'lt' | 'gte' | 'lte';
  condition_value: string;
  condition_threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  time_window_seconds: number;
  notification_channel_ids: string[];
}

export interface NotificationFormData {
  name: string;
  channel_type: 'email' | 'webhook' | 'slack';
  config: Record<string, unknown>;
}

export interface AlertFilters {
  status?: string;
  severity?: string;
  [key: string]: string | undefined;
}

// Evaluation Result
export interface EvaluationResult {
  triggered: boolean;
  message: string;
}
