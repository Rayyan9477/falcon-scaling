import { useState, useCallback } from 'react';
import type { FilterParams } from '../types';

export function useFilters() {
  const [filters, setFilters] = useState<FilterParams>({});

  const updateFilter = useCallback(<K extends keyof FilterParams>(key: K, value: FilterParams[K]) => {
    setFilters(prev => {
      const next = { ...prev, [key]: value };
      // Remove empty arrays and undefined values
      if (Array.isArray(value) && value.length === 0) delete next[key];
      if (value === undefined || value === null || value === '') delete next[key];
      return next;
    });
  }, []);

  const resetFilters = useCallback(() => setFilters({}), []);

  const hasActiveFilters = Object.keys(filters).length > 0;

  return { filters, updateFilter, resetFilters, hasActiveFilters };
}
