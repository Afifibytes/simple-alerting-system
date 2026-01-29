import React from 'react';
import { Icon } from './Icon';

interface FilterOption {
  value: string;
  label: string;
}

interface Filter {
  value: string;
  placeholder: string;
  options: FilterOption[];
  onChange: (value: string) => void;
}

interface SearchToolbarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder?: string;
  filters?: Filter[];
}

export function SearchToolbar({
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Search...',
  filters = [],
}: SearchToolbarProps): React.ReactElement {
  return (
    <div className="search-toolbar">
      <div className="search-input-wrapper">
        <Icon name="search" size="sm" className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {filters.map((filter) => (
        <select
          key={filter.placeholder}
          className="form-select filter-select"
          value={filter.value}
          onChange={(e) => filter.onChange(e.target.value)}
        >
          <option value="">{filter.placeholder}</option>
          {filter.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ))}
    </div>
  );
}
