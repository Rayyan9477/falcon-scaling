import Header from './components/Header'
import FilterSidebar from './components/FilterSidebar'
import ChatInterface from './components/ChatInterface'
import DatasetStats from './components/DatasetStats'
import { useFilters } from './hooks/useFilters'

function App() {
  const { filters, updateFilter, resetFilters, hasActiveFilters } = useFilters()

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 overflow-y-auto shrink-0">
          <FilterSidebar
            filters={filters}
            onFilterChange={updateFilter}
            onReset={resetFilters}
            hasActiveFilters={hasActiveFilters}
          />
        </aside>

        {/* Main chat area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatInterface filters={filters} />
        </main>
      </div>

      <DatasetStats />
    </div>
  )
}

export default App
