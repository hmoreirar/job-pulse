import { JobCard } from './JobCard'
import { Pagination } from './Pagination'
import type { JobListResponse } from '../types/job'

interface JobListProps {
  data: JobListResponse | null
  loading: boolean
  error: string | null
  onPageChange: (page: number) => void
}

export function JobList({ data, loading, error, onPageChange }: JobListProps) {
  if (loading) {
    return <p className="job-list-status">Cargando ofertas...</p>
  }

  if (error) {
    return <p className="job-list-status job-list-error">{error}</p>
  }

  if (!data || data.items.length === 0) {
    return <p className="job-list-status">No se encontraron ofertas.</p>
  }

  return (
    <>
      <div className="job-list">
        {data.items.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
      <Pagination
        page={data.page}
        pages={data.pages}
        total={data.total}
        onPageChange={onPageChange}
      />
    </>
  )
}
