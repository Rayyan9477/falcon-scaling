import { useState } from 'react';
import type { FamilyOfficeResult } from '../types';

interface Props {
  result: FamilyOfficeResult;
  index: number;
}

export default function ResultCard({ result, index }: Props) {
  const [expanded, setExpanded] = useState(false);

  const pct = Math.round(result.relevance_score * 100);
  const scoreClass = pct >= 40 ? 'score-high' : pct >= 25 ? 'score-mid' : 'score-low';

  return (
    <button
      type="button"
      onClick={() => setExpanded(!expanded)}
      className="w-full text-left rounded-lg px-3 py-2.5 transition-all cursor-pointer result-card"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-mono result-meta">{index + 1}</span>
            <span className="text-[13px] font-semibold truncate result-name">{result.name}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
              result.type === 'SFO' ? 'badge-sfo' : 'badge-mfo'
            }`}>
              {result.type}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-0.5 text-[11px] result-meta">
            <span>{result.country}</span>
            <span>|</span>
            <span>${result.aum_b}B AUM</span>
            <span>|</span>
            <span className={scoreClass}>{pct}% match</span>
          </div>
        </div>
        <span className="text-[10px] mt-1 shrink-0 result-meta">
          {expanded ? '\u25B2' : '\u25BC'}
        </span>
      </div>

      {expanded && (
        <div className="mt-2 pt-2 border-t border-slate-100 text-[11px] space-y-0.5">
          <p><span className="font-medium result-detail-label">Region:</span> <span className="result-detail-val">{result.region}</span></p>
          <p><span className="font-medium result-detail-label">Sectors:</span> <span className="result-detail-val">{result.sector_focus}</span></p>
        </div>
      )}
    </button>
  );
}
