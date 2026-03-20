import Header from './components/Header'
import FilterSidebar from './components/FilterSidebar'
import ChatInterface from './components/ChatInterface'
import DatasetStats from './components/DatasetStats'
import { useFilters } from './hooks/useFilters'

function App() {
  const { filters, updateFilter, resetFilters, hasActiveFilters } = useFilters()

  return (
    <div className="h-screen flex flex-col shell">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-56 border-r shrink-0 overflow-y-auto surface">
          <FilterSidebar
            filters={filters}
            onFilterChange={updateFilter}
            onReset={resetFilters}
            hasActiveFilters={hasActiveFilters}
          />
        </aside>

        <main className="flex-1 flex flex-col overflow-hidden surface-alt">
          <ChatInterface filters={filters} />
        </main>
      </div>

      <DatasetStats />
    </div>
  )
}

export default App
