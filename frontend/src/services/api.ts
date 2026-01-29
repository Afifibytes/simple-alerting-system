const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  data: Record<string, unknown>;

  constructor(message: string, status: number, data: Record<string, unknown>) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: Record<string, unknown> | string;
}

async function request<T>(endpoint: string, options: RequestOptions = {}, useVersionedApi = true): Promise<T> {
  const baseUrl = useVersionedApi ? `${API_BASE}/v1` : API_BASE;
  const url = `${baseUrl}${endpoint}`;

  const { body, ...restOptions } = options;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...restOptions,
  };

  if (body && typeof body === 'object') {
    config.body = JSON.stringify(body);
  } else if (body) {
    config.body = body;
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(
      data.detail || 'An error occurred',
      response.status,
      data
    );
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string): Promise<T> => request<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, body?: Record<string, unknown>): Promise<T> => request<T>(endpoint, { method: 'POST', body }),
  patch: <T>(endpoint: string, body?: Record<string, unknown>): Promise<T> => request<T>(endpoint, { method: 'PATCH', body }),
  delete: <T>(endpoint: string): Promise<T> => request<T>(endpoint, { method: 'DELETE' }),
};

// Unversioned API for health checks
export const baseApi = {
  get: <T>(endpoint: string): Promise<T> => request<T>(endpoint, { method: 'GET' }, false),
};
