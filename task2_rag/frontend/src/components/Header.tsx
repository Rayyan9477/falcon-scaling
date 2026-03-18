export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            PolarityIQ Family Office Intelligence
          </h1>
          <p className="text-sm text-gray-500">
            RAG-powered natural language query interface
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="px-2 py-1 bg-green-50 text-green-700 rounded-full font-medium">
            200 Family Offices
          </span>
          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full font-medium">
            45 Fields
          </span>
        </div>
      </div>
    </header>
  );
}
