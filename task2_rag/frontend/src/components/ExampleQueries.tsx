const EXAMPLES = [
  "Which family offices focus on AI with check sizes above $10M?",
  "Show me all single-family offices in the Middle East that do direct investments",
  "Which family offices have the highest co-investment frequency in healthcare?",
  "Find European MFOs with ESG focus and AUM above $5B",
  "Compare Walton Enterprises and Cascade Investment strategies",
];

interface Props {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

export default function ExampleQueries({ onSelect, disabled }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {EXAMPLES.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="text-xs px-3 py-1.5 bg-white border border-gray-200 rounded-full
                     text-gray-600 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700
                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed
                     text-left leading-tight"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
