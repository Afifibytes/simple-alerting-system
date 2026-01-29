/**
 * Tests for StatusBadge component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '../components/common/StatusBadge';

describe('StatusBadge', () => {
  describe('status type (default)', () => {
    it('renders healthy status with success style', () => {
      render(<StatusBadge status="healthy" />);

      const badge = screen.getByText('healthy');
      expect(badge).toHaveClass('badge-success');
    });

    it('renders connected status with success style', () => {
      render(<StatusBadge status="connected" />);

      const badge = screen.getByText('connected');
      expect(badge).toHaveClass('badge-success');
    });

    it('renders unhealthy status with danger style', () => {
      render(<StatusBadge status="unhealthy" />);

      const badge = screen.getByText('unhealthy');
      expect(badge).toHaveClass('badge-danger');
    });

    it('renders error status with danger style', () => {
      render(<StatusBadge status="error" />);

      const badge = screen.getByText('error');
      expect(badge).toHaveClass('badge-danger');
    });

    it('renders unknown status with warning style', () => {
      render(<StatusBadge status="unknown" />);

      const badge = screen.getByText('unknown');
      expect(badge).toHaveClass('badge-warning');
    });

    it('renders unrecognized status with info style', () => {
      render(<StatusBadge status="custom" />);

      const badge = screen.getByText('custom');
      expect(badge).toHaveClass('badge-info');
    });
  });

  describe('severity type', () => {
    it('renders low severity with success style', () => {
      render(<StatusBadge status="low" type="severity" />);

      const badge = screen.getByText('low');
      expect(badge).toHaveClass('badge-success');
    });

    it('renders medium severity with warning style', () => {
      render(<StatusBadge status="medium" type="severity" />);

      const badge = screen.getByText('medium');
      expect(badge).toHaveClass('badge-warning');
    });

    it('renders high severity with danger style', () => {
      render(<StatusBadge status="high" type="severity" />);

      const badge = screen.getByText('high');
      expect(badge).toHaveClass('badge-danger');
    });
  });

  describe('alert type', () => {
    it('renders triggered alert with danger style', () => {
      render(<StatusBadge status="triggered" type="alert" />);

      const badge = screen.getByText('triggered');
      expect(badge).toHaveClass('badge-danger');
    });

    it('renders acknowledged alert with warning style', () => {
      render(<StatusBadge status="acknowledged" type="alert" />);

      const badge = screen.getByText('acknowledged');
      expect(badge).toHaveClass('badge-warning');
    });

    it('renders resolved alert with success style', () => {
      render(<StatusBadge status="resolved" type="alert" />);

      const badge = screen.getByText('resolved');
      expect(badge).toHaveClass('badge-success');
    });
  });

  describe('dot indicator', () => {
    it('shows dot by default', () => {
      const { container } = render(<StatusBadge status="active" />);

      const dot = container.querySelector('.badge-dot');
      expect(dot).toBeInTheDocument();
    });

    it('hides dot when showDot is false', () => {
      const { container } = render(<StatusBadge status="active" showDot={false} />);

      const dot = container.querySelector('.badge-dot');
      expect(dot).not.toBeInTheDocument();
    });
  });
});
