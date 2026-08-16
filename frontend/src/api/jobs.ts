import { request } from './client'
import type { JobFilters, JobListResponse } from '../types/job'

function buildQuery(filters: JobFilters): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function listJobs(filters: JobFilters): Promise<JobListResponse> {
  return request<JobListResponse>(`/jobs${buildQuery(filters)}`)
}
