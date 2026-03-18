import { useQuery } from '@tanstack/react-query';
import { getStats } from '../services/api';

export default function DatasetStats() {
  const { data: stats, isError } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    staleTime: Infinity,
  });

  if (isError) return (
    <div className="bg-red-50 border-t border-red-200 px-6 py-3 text-xs text-red-500">
      Unable to load dataset stats.
    </div>
  );
  if (!stats) return null;

  return (
    <div className="bg-gray-50 border-t border-gray-200 px-6 py-3">
      <div className="flex items-center gap-6 text-xs text-gray-500">
        <span><strong>{stats.total_records}</strong> records</span>
        <span><strong>{stats.total_fields}</strong> fields</span>
        <span>AUM: ${stats.aum_stats.min}B - ${stats.aum_stats.max}B (avg ${stats.aum_stats.avg}B)</span>
        <span>SFO: {stats.type_breakdown.SFO || 0} | MFO: {stats.type_breakdown.MFO || 0}</span>
        <span>{Object.keys(stats.region_breakdown).length} regions</span>
      </div>
    </div>
  );
}
