/**
 * Tests for API service layer
 */

import { api, ApiError } from '../services/api';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Service', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('api.get', () => {
    it('should make GET request with correct URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: 'test' }),
      });

      await api.get('/sources');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/sources',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should return parsed JSON response', async () => {
      const mockData = { items: [], total: 0 };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await api.get('/sources');

      expect(result).toEqual(mockData);
    });

    it('should throw ApiError on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not found' }),
      });

      await expect(api.get('/sources/123')).rejects.toThrow(ApiError);
    });

    it('should include status code in ApiError', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server error' }),
      });

      try {
        await api.get('/sources');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(500);
      }
    });
  });

  describe('api.post', () => {
    it('should make POST request with JSON body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: '123' }),
      });

      const body = { name: 'test', description: 'Test source' };
      await api.post('/sources', body);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/sources',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(body),
        })
      );
    });

    it('should return created resource', async () => {
      const created = { id: '123', name: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(created),
      });

      const result = await api.post('/sources', { name: 'test' });

      expect(result).toEqual(created);
    });
  });

  describe('api.patch', () => {
    it('should make PATCH request with JSON body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: '123', name: 'updated' }),
      });

      const body = { name: 'updated' };
      await api.patch('/sources/123', body);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/sources/123',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(body),
        })
      );
    });
  });

  describe('api.delete', () => {
    it('should make DELETE request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: () => Promise.resolve(null),
      });

      await api.delete('/sources/123');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/v1/sources/123',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should handle 204 No Content response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      const result = await api.delete('/sources/123');

      expect(result).toBeNull();
    });
  });
});

describe('ApiError', () => {
  it('should contain status and data', () => {
    const error = new ApiError('Not found', 404, { detail: 'Source not found' });

    expect(error.message).toBe('Not found');
    expect(error.status).toBe(404);
    expect(error.data).toEqual({ detail: 'Source not found' });
  });

  it('should be an instance of Error', () => {
    const error = new ApiError('Error', 500, {});

    expect(error).toBeInstanceOf(Error);
  });
});
