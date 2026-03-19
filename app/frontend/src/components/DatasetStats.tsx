import { useQuery } from '@tanstack/react-query';
import { getStats } from '../services/api';

export default function DatasetStats() {
  const { data: stats, isError } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    staleTime: Infinity,
  });

  if (isError || !stats) return null;

  return (
    <div className="border-t px-6 py-2 footer-bar">
      <div className="flex items-center gap-5 text-[11px] stat-text">
        <span>{stats.total_records} records</span>
        <span>{stats.total_fields} fields</span>
        <span>${stats.aum_stats.min}B &ndash; ${stats.aum_stats.max}B AUM</span>
        <span>SFO {stats.type_breakdown.SFO || 0} / MFO {stats.type_breakdown.MFO || 0}</span>
        <span>{Object.keys(stats.region_breakdown).length} regions</span>
      </div>
    </div>
  );
}
