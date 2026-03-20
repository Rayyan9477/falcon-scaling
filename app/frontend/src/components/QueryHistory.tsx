import type { HistoryEntry, FamilyOfficeResult } from '../types';

interface Props {
  history: HistoryEntry[];
  onSelect: (query: string, answer: string, sources?: FamilyOfficeResult[]) => void;
  onClose: () => void;
}

export default function QueryHistory({ history, onSelect, onClose }: Props) {
  if (history.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm empty-sub">No query history yet.</p>
        <button type="button" onClick={onClose} className="text-[11px] mt-2 pill px-3 py-1 rounded">
          Close
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider filter-heading">
          Recent Queries ({history.length})
        </h3>
        <button type="button" onClick={onClose} className="text-[11px] filter-reset">
          Close
        </button>
      </div>

      <div className="space-y-2 max-h-[60vh] overflow-y-auto">
        {history.map((entry) => (
          <button
            key={entry.id}
            type="button"
            onClick={() => onSelect(entry.query, entry.answer, entry.sources)}
            className="w-full text-left rounded-lg px-3 py-2.5 transition-all cursor-pointer result-card"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <p className="text-[12px] font-medium truncate result-name">{entry.query}</p>
                <p className="text-[11px] mt-0.5 result-meta line-clamp-2">
                  {entry.answer.slice(0, 120)}{entry.answer.length > 120 ? '...' : ''}
                </p>
                <div className="flex items-center gap-2 mt-1 text-[10px] result-meta">
                  <span>{entry.total_matches} matches</span>
                  <span>|</span>
                  <span>{new Date(entry.timestamp).toLocaleDateString()}</span>
                </div>
              </div>
              <span className="text-[10px] mt-1 shrink-0 result-meta">&#8594;</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
