import { useState } from 'react';
import type { FamilyOfficeResult } from '../types';

interface Props {
  result: FamilyOfficeResult;
  index: number;
}

export default function ResultCard({ result, index }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="border border-gray-200 rounded-lg p-3 bg-white hover:border-blue-300 transition-colors cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-gray-400">#{index + 1}</span>
            <h4 className="text-sm font-semibold text-gray-900">{result.name}</h4>
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
              result.type === 'SFO'
                ? 'bg-purple-50 text-purple-700'
                : 'bg-orange-50 text-orange-700'
            }`}>
              {result.type}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
            <span>{result.country}</span>
            <span>AUM: ${result.aum_b}B</span>
            <span className="text-gray-300">|</span>
            <span>Score: {(result.relevance_score * 100).toFixed(1)}%</span>
          </div>
        </div>
        <button className="text-gray-400 text-xs">
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-600 space-y-1">
          <p><span className="font-medium text-gray-700">Region:</span> {result.region}</p>
          <p><span className="font-medium text-gray-700">Sectors:</span> {result.sector_focus}</p>
          <p><span className="font-medium text-gray-700">Summary:</span> {result.summary}</p>
        </div>
      )}
    </div>
  );
}
