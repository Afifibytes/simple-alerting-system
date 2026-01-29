import React, { useCallback } from 'react';
import { Icon } from './Icon';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
}: PaginationProps): React.ReactElement | null {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const handlePrevious = useCallback(() => {
    onPageChange(currentPage - 1);
  }, [onPageChange, currentPage]);

  const handleNext = useCallback(() => {
    onPageChange(currentPage + 1);
  }, [onPageChange, currentPage]);

  // Don't render if only one page
  if (totalPages <= 1) return null;

  return (
    <div className="pagination">
      <div className="pagination-info">
        Showing {startItem} to {endItem} of {totalItems} results
      </div>
      <div className="pagination-buttons">
        <button
          className="btn btn-secondary btn-sm"
          onClick={handlePrevious}
          disabled={currentPage <= 1}
        >
          <Icon name="chevron_left" size="sm" />
          Previous
        </button>
        <button
          className="btn btn-secondary btn-sm"
          onClick={handleNext}
          disabled={currentPage >= totalPages}
        >
          Next
          <Icon name="chevron_right" size="sm" />
        </button>
      </div>
    </div>
  );
}
