/**
 * Tests for type definitions - ensures types match expected API contracts
 */

import type {
  Source,
  Rule,
  Alert,
  NotificationChannel,
  HealthStatus,
  PaginatedResponse,
} from '../types';

describe('Type Contracts', () => {
  describe('Source', () => {
    it('should have required fields', () => {
      const source: Source = {
        id: '123',
        name: 'test-source',
        description: 'Test description',
        owner: 'owner@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(source.id).toBeDefined();
      expect(source.name).toBeDefined();
      expect(source.is_active).toBeDefined();
    });

    it('should allow null description and owner', () => {
      const source: Source = {
        id: '123',
        name: 'test-source',
        description: null,
        owner: null,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(source.description).toBeNull();
      expect(source.owner).toBeNull();
    });
  });

  describe('Rule', () => {
    it('should have required fields', () => {
      const rule: Rule = {
        id: '123',
        name: 'High Error Count',
        source_id: '456',
        condition_type: 'count',
        condition_field: 'level',
        condition_operator: 'eq',
        condition_value: 'error',
        condition_threshold: 5,
        severity: 'high',
        time_window_seconds: 300,
        notification_channel_ids: [],
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(rule.condition_type).toMatch(/^(count|threshold)$/);
      expect(rule.severity).toMatch(/^(low|medium|high|critical)$/);
    });

    it('should allow optional source_name', () => {
      const rule: Rule = {
        id: '123',
        name: 'Test Rule',
        source_id: '456',
        source_name: 'test-source',
        condition_type: 'count',
        condition_field: 'level',
        condition_operator: 'eq',
        condition_value: 'error',
        condition_threshold: 5,
        severity: 'medium',
        time_window_seconds: 300,
        notification_channel_ids: [],
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(rule.source_name).toBe('test-source');
    });
  });

  describe('Alert', () => {
    it('should have required fields', () => {
      const alert: Alert = {
        id: '123',
        rule_id: '456',
        rule_name: 'Test Rule',
        status: 'triggered',
        severity: 'high',
        message: 'Found 5 matching events',
        triggered_at: '2024-01-01T00:00:00Z',
        acknowledged_at: null,
        resolved_at: null,
        resolved_message: null,
        match_count: 5,
      };

      expect(alert.status).toMatch(/^(triggered|acknowledged|resolved)$/);
    });

    it('should allow acknowledged state', () => {
      const alert: Alert = {
        id: '123',
        rule_id: '456',
        rule_name: 'Test Rule',
        status: 'acknowledged',
        severity: 'medium',
        message: null,
        triggered_at: '2024-01-01T00:00:00Z',
        acknowledged_at: '2024-01-01T01:00:00Z',
        resolved_at: null,
        resolved_message: null,
        match_count: 3,
      };

      expect(alert.acknowledged_at).not.toBeNull();
    });

    it('should allow resolved state', () => {
      const alert: Alert = {
        id: '123',
        rule_id: '456',
        rule_name: 'Test Rule',
        status: 'resolved',
        severity: 'low',
        message: null,
        triggered_at: '2024-01-01T00:00:00Z',
        acknowledged_at: '2024-01-01T01:00:00Z',
        resolved_at: '2024-01-01T02:00:00Z',
        resolved_message: 'Fixed the issue',
        match_count: 2,
      };

      expect(alert.resolved_at).not.toBeNull();
      expect(alert.resolved_message).not.toBeNull();
    });
  });

  describe('NotificationChannel', () => {
    it('should support webhook type', () => {
      const channel: NotificationChannel = {
        id: '123',
        name: 'My Webhook',
        channel_type: 'webhook',
        config: { url: 'https://example.com/webhook' },
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(channel.channel_type).toBe('webhook');
    });

    it('should support slack type', () => {
      const channel: NotificationChannel = {
        id: '123',
        name: 'Slack Alerts',
        channel_type: 'slack',
        config: { webhook_url: 'https://hooks.slack.com/services/xxx' },
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(channel.channel_type).toBe('slack');
    });

    it('should support email type', () => {
      const channel: NotificationChannel = {
        id: '123',
        name: 'Email Alerts',
        channel_type: 'email',
        config: { recipients: ['alert@example.com'] },
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      expect(channel.channel_type).toBe('email');
    });
  });

  describe('HealthStatus', () => {
    it('should support healthy status', () => {
      const health: HealthStatus = {
        status: 'healthy',
        database: 'connected',
        rabbitmq: 'connected',
      };

      expect(health.status).toBe('healthy');
    });

    it('should support unhealthy status', () => {
      const health: HealthStatus = {
        status: 'unhealthy',
        database: 'disconnected',
        rabbitmq: 'connected',
      };

      expect(health.status).toBe('unhealthy');
    });
  });

  describe('PaginatedResponse', () => {
    it('should have pagination fields', () => {
      const response: PaginatedResponse<Source> = {
        items: [],
        total: 0,
        offset: 0,
        limit: 50,
        has_more: false,
      };

      expect(response.items).toBeDefined();
      expect(response.total).toBeDefined();
      expect(response.offset).toBeDefined();
      expect(response.limit).toBeDefined();
      expect(response.has_more).toBeDefined();
    });

    it('should indicate when more items available', () => {
      const response: PaginatedResponse<Source> = {
        items: [
          {
            id: '1',
            name: 'source-1',
            description: null,
            owner: null,
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 100,
        offset: 0,
        limit: 1,
        has_more: true,
      };

      expect(response.has_more).toBe(true);
    });
  });
});
