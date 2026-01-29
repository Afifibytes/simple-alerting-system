/**
 * Tests for createService factory
 */

import { createService } from '../services/createService';
import { api } from '../services/api';

// Mock the api module
jest.mock('../services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
  },
}));

interface TestEntity {
  id: string;
  name: string;
  description?: string;
}

describe('createService', () => {
  const mockApi = api as jest.Mocked<typeof api>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should call api.get with correct endpoint', async () => {
      const service = createService<TestEntity>('/sources');
      mockApi.get.mockResolvedValueOnce({ items: [], total: 0 });

      await service.getAll();

      expect(mockApi.get).toHaveBeenCalledWith('/sources');
    });

    it('should include pagination params in query', async () => {
      const service = createService<TestEntity>('/sources');
      mockApi.get.mockResolvedValueOnce({ items: [], total: 0 });

      await service.getAll({ offset: 10, limit: 20 });

      expect(mockApi.get).toHaveBeenCalledWith('/sources?offset=10&limit=20');
    });

    it('should include filter params when configured', async () => {
      const service = createService<TestEntity>('/sources', ['active_only', 'search']);
      mockApi.get.mockResolvedValueOnce({ items: [], total: 0 });

      await service.getAll({ active_only: true, search: 'test' });

      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('active_only=true')
      );
      expect(mockApi.get).toHaveBeenCalledWith(
        expect.stringContaining('search=test')
      );
    });

    it('should exclude undefined/null filter values', async () => {
      const service = createService<TestEntity>('/sources', ['search']);
      mockApi.get.mockResolvedValueOnce({ items: [], total: 0 });

      await service.getAll({ search: undefined });

      expect(mockApi.get).toHaveBeenCalledWith('/sources');
    });

    it('should exclude empty string filter values', async () => {
      const service = createService<TestEntity>('/sources', ['search']);
      mockApi.get.mockResolvedValueOnce({ items: [], total: 0 });

      await service.getAll({ search: '' });

      expect(mockApi.get).toHaveBeenCalledWith('/sources');
    });
  });

  describe('getById', () => {
    it('should call api.get with id in path', async () => {
      const service = createService<TestEntity>('/sources');
      mockApi.get.mockResolvedValueOnce({ id: '123', name: 'Test' });

      await service.getById('123');

      expect(mockApi.get).toHaveBeenCalledWith('/sources/123');
    });

    it('should return the entity', async () => {
      const service = createService<TestEntity>('/sources');
      const entity = { id: '123', name: 'Test' };
      mockApi.get.mockResolvedValueOnce(entity);

      const result = await service.getById('123');

      expect(result).toEqual(entity);
    });
  });

  describe('create', () => {
    it('should call api.post with data', async () => {
      const service = createService<TestEntity>('/sources');
      const newEntity = { name: 'New Source', description: 'Description' };
      mockApi.post.mockResolvedValueOnce({ id: '123', ...newEntity });

      await service.create(newEntity);

      expect(mockApi.post).toHaveBeenCalledWith('/sources', newEntity);
    });

    it('should return created entity', async () => {
      const service = createService<TestEntity>('/sources');
      const created = { id: '123', name: 'New Source' };
      mockApi.post.mockResolvedValueOnce(created);

      const result = await service.create({ name: 'New Source' });

      expect(result).toEqual(created);
    });
  });

  describe('update', () => {
    it('should call api.patch with id and data', async () => {
      const service = createService<TestEntity>('/sources');
      const updates = { name: 'Updated Name' };
      mockApi.patch.mockResolvedValueOnce({ id: '123', ...updates });

      await service.update('123', updates);

      expect(mockApi.patch).toHaveBeenCalledWith('/sources/123', updates);
    });

    it('should return updated entity', async () => {
      const service = createService<TestEntity>('/sources');
      const updated = { id: '123', name: 'Updated' };
      mockApi.patch.mockResolvedValueOnce(updated);

      const result = await service.update('123', { name: 'Updated' });

      expect(result).toEqual(updated);
    });
  });

  describe('delete', () => {
    it('should call api.delete with id', async () => {
      const service = createService<TestEntity>('/sources');
      mockApi.delete.mockResolvedValueOnce(undefined);

      await service.delete('123');

      expect(mockApi.delete).toHaveBeenCalledWith('/sources/123');
    });
  });
});
