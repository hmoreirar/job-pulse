import { useState } from 'react'

import { JobFilters } from './components/JobFilters'
import { JobList } from './components/JobList'
import { useJobs } from './hooks/useJobs'
import type { JobFilters as JobFiltersType } from './types/job'

const PAGE_SIZE = 20

export default function App() {
  const [filters, setFilters] = useState<JobFiltersType>({
    page: 1,
    page_size: PAGE_SIZE,
    order: 'desc',
    sort: 'posted_at',
  })

  const { data, loading, error } = useJobs(filters)

  const handlePageChange = (page: number) => {
    setFilters((current) => ({ ...current, page }))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">JobPulse</h1>
        <p className="app-subtitle">Inteligencia del mercado laboral</p>
      </header>

      <main className="app-main">
        <JobFilters filters={filters} onChange={setFilters} />
        <JobList data={data} loading={loading} error={error} onPageChange={handlePageChange} />
      </main>
    </div>
  )
}
