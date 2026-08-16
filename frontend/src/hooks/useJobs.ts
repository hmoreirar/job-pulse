import { useCallback, useEffect, useMemo, useState } from 'react'

import { listJobs } from '../api/jobs'
import type { JobFilters, JobListResponse } from '../types/job'

interface UseJobsResult {
  data: JobListResponse | null
  loading: boolean
  error: string | null
  reload: () => void
}

export function useJobs(filters: JobFilters): UseJobsResult {
  const [data, setData] = useState<JobListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  const reload = useCallback(() => setTick((t) => t + 1), [])

  const filtersKey = useMemo(() => JSON.stringify(filters), [filters])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    listJobs(filters)
      .then((result) => {
        if (!cancelled) {
          setData(result)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Error desconocido')
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [filtersKey, tick])

  return { data, loading, error, reload }
}
