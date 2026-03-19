import { useQuery } from '@tanstack/react-query';
import { getFilters } from '../services/api';
import type { FilterParams } from '../types';

interface Props {
  filters: FilterParams;
  onFilterChange: <K extends keyof FilterParams>(key: K, value: FilterParams[K]) => void;
  onReset: () => void;
  hasActiveFilters: boolean;
}

function Label({ children }: { children: React.ReactNode }) {
  return <label className="block text-[11px] font-medium uppercase tracking-wider mb-1.5 filter-label">{children}</label>;
}

export default function FilterSidebar({ filters, onFilterChange, onReset, hasActiveFilters }: Props) {
  const { data: options, isLoading, isError } = useQuery({
    queryKey: ['filters'],
    queryFn: getFilters,
    staleTime: Infinity,
  });

  if (isLoading) return <div className="p-5 text-xs loading-text">Loading filters...</div>;
  if (isError) return <div className="p-5 text-xs error-text">Could not load filters.</div>;
  if (!options) return null;

  return (
    <div className="p-4 space-y-4 text-sm">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider filter-heading">Filters</span>
        {hasActiveFilters && (
          <button type="button" onClick={onReset} className="text-[11px] filter-reset">Clear all</button>
        )}
      </div>

      <hr className="border-0 h-px bg-slate-100" />

      {/* Region chips */}
      <div>
        <Label>Region</Label>
        <div className="flex flex-wrap gap-1">
          {options.regions.map(r => (
            <button
              type="button"
              key={r}
              onClick={() => {
                const cur = filters.regions || [];
                onFilterChange('regions', cur.includes(r) ? cur.filter(x => x !== r) : [...cur, r]);
              }}
              className={`text-[11px] px-2 py-0.5 rounded border transition-colors ${
                filters.regions?.includes(r) ? 'filter-chip-on' : 'filter-chip'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Type chips */}
      <div>
        <Label>Type</Label>
        <div className="flex gap-1">
          {options.types.map(t => (
            <button
              type="button"
              key={t}
              onClick={() => {
                const cur = filters.types || [];
                onFilterChange('types', cur.includes(t) ? cur.filter(x => x !== t) : [...cur, t]);
              }}
              className={`text-[11px] px-3 py-1 rounded border transition-colors ${
                filters.types?.includes(t) ? 'filter-chip-on' : 'filter-chip'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* AUM slider */}
      <div>
        <Label>AUM Min (${filters.aum_min ?? options.aum_range.min}B)</Label>
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
          title="AUM minimum filter"
          className="w-full h-1"
        />
        <div className="flex justify-between text-[10px] mt-0.5 filter-hint">
          <span>${options.aum_range.min}B</span>
          <span>${options.aum_range.max}B</span>
        </div>
      </div>

      {/* Sectors */}
      <div>
        <Label>Sectors</Label>
        <select
          multiple
          title="Select sectors"
          value={filters.sectors || []}
          onChange={(e) => onFilterChange('sectors', Array.from(e.target.selectedOptions, o => o.value))}
          className="w-full text-[11px] rounded-md p-1.5 h-20 filter-input"
        >
          {options.sectors.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <p className="text-[10px] mt-0.5 filter-hint">Ctrl+click to multi-select</p>
      </div>

      {/* Check Size */}
      <div>
        <Label>Check Size Min ($M)</Label>
        <input
          type="number"
          placeholder="e.g. 10"
          value={filters.check_size_min ?? ''}
          onChange={(e) => onFilterChange('check_size_min', e.target.value ? Number(e.target.value) : undefined)}
          className="w-full text-xs rounded-md px-2.5 py-1.5 filter-input"
        />
      </div>

      {/* Dropdowns */}
      {([
        { key: 'direct_investment' as const, label: 'Direct Investment', opts: ['Yes', 'No'] },
        { key: 'co_invest_frequency' as const, label: 'Co-Invest Freq', opts: options.co_invest_frequencies },
        { key: 'esg_level' as const, label: 'ESG / Impact', opts: options.esg_levels },
      ]).map(({ key, label, opts }) => (
        <div key={key}>
          <Label>{label}</Label>
          <select
            title={label}
            value={(filters as Record<string, unknown>)[key] as string || ''}
            onChange={(e) => onFilterChange(key, e.target.value || undefined)}
            className="w-full text-xs rounded-md px-2 py-1.5 filter-input"
          >
            <option value="">Any</option>
            {opts.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
      ))}
    </div>
  );
}
