import { useQuery } from '@tanstack/react-query';
import { getFilters } from '../services/api';
import type { FilterParams } from '../types';

interface Props {
  filters: FilterParams;
  onFilterChange: <K extends keyof FilterParams>(key: K, value: FilterParams[K]) => void;
  onReset: () => void;
  hasActiveFilters: boolean;
}

export default function FilterSidebar({ filters, onFilterChange, onReset, hasActiveFilters }: Props) {
  const { data: options, isLoading, isError } = useQuery({
    queryKey: ['filters'],
    queryFn: getFilters,
    staleTime: Infinity,
  });

  if (isLoading) return <div className="p-4 text-sm text-gray-400">Loading filters...</div>;
  if (isError) return (
    <div className="p-4 text-sm text-red-500">
      Failed to load filters. Is the backend running at localhost:8000?
    </div>
  );
  if (!options) return null;

  return (
    <div className="p-4 space-y-5 overflow-y-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Reset
          </button>
        )}
      </div>

      {/* Region */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Region</label>
        <select
          multiple
          value={filters.regions || []}
          onChange={(e) => onFilterChange('regions', Array.from(e.target.selectedOptions, o => o.value))}
          className="w-full text-xs border border-gray-300 rounded p-1.5 h-24"
        >
          {options.regions.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {/* Type */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
        <div className="flex flex-wrap gap-2">
          {options.types.map(t => (
            <label key={t} className="flex items-center gap-1 text-xs">
              <input
                type="checkbox"
                checked={filters.types?.includes(t) || false}
                onChange={(e) => {
                  const current = filters.types || [];
                  onFilterChange('types', e.target.checked
                    ? [...current, t]
                    : current.filter(x => x !== t)
                  );
                }}
              />
              {t}
            </label>
          ))}
        </div>
      </div>

      {/* AUM Range */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          AUM Min ($B): {filters.aum_min ?? options.aum_range.min}
        </label>
        <input
          type="range"
          min={options.aum_range.min}
          max={options.aum_range.max}
          step={1}
          value={filters.aum_min ?? options.aum_range.min}
          onChange={(e) => {
            const val = Number(e.target.value);
            onFilterChange('aum_min', val > options.aum_range.min ? val : undefined);
          }}
          className="w-full"
        />
      </div>

      {/* Sectors */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Sectors</label>
        <select
          multiple
          value={filters.sectors || []}
          onChange={(e) => onFilterChange('sectors', Array.from(e.target.selectedOptions, o => o.value))}
          className="w-full text-xs border border-gray-300 rounded p-1.5 h-24"
        >
          {options.sectors.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Check Size Min */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Check Size Min ($M)</label>
        <input
          type="number"
          placeholder="e.g. 10"
          value={filters.check_size_min ?? ''}
          onChange={(e) => onFilterChange('check_size_min', e.target.value ? Number(e.target.value) : undefined)}
          className="w-full text-xs border border-gray-300 rounded p-1.5"
        />
      </div>

      {/* Direct Investment */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Direct Investment</label>
        <select
          value={filters.direct_investment || ''}
          onChange={(e) => onFilterChange('direct_investment', e.target.value || undefined)}
          className="w-full text-xs border border-gray-300 rounded p-1.5"
        >
          <option value="">All</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      {/* Co-Invest Frequency */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Co-Invest Frequency</label>
        <select
          value={filters.co_invest_frequency || ''}
          onChange={(e) => onFilterChange('co_invest_frequency', e.target.value || undefined)}
          className="w-full text-xs border border-gray-300 rounded p-1.5"
        >
          <option value="">All</option>
          {options.co_invest_frequencies.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>

      {/* ESG Level */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">ESG/Impact Level</label>
        <select
          value={filters.esg_level || ''}
          onChange={(e) => onFilterChange('esg_level', e.target.value || undefined)}
          className="w-full text-xs border border-gray-300 rounded p-1.5"
        >
          <option value="">All</option>
          {options.esg_levels.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>
    </div>
  );
}
