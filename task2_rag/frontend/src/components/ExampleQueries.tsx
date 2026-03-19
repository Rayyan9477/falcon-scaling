const EXAMPLES = [
  "Family offices in Asia that invest in healthcare",
  "European SFOs with high co-investment frequency",
  "Who are the largest FOs by AUM in the Middle East?",
  "Compare Walton Enterprises and Cascade Investment",
  "FOs focused on climate tech and ESG impact",
];

interface Props {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

export default function ExampleQueries({ onSelect, disabled }: Props) {
  return (
    <div className="flex flex-wrap gap-1.5 justify-center">
      {EXAMPLES.map((q) => (
        <button
          type="button"
          key={q}
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="text-[11px] px-3 py-1.5 rounded-md transition-colors pill"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
