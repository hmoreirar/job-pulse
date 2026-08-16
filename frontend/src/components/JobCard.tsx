import type { Job } from '../types/job'
import {
  EMPLOYMENT_TYPE_LABELS,
  EXPERIENCE_LEVEL_LABELS,
  SOURCE_LABELS,
} from '../lib/labels'

function formatSalary(
  min: string | null,
  max: string | null,
  currency: string | null,
): string {
  if (!min && !max) {
    return 'Salario no especificado'
  }
  const formatter = new Intl.NumberFormat('es-CL', {
    maximumFractionDigits: 0,
  })
  const parts = [
    min ? formatter.format(Number(min)) : null,
    max ? formatter.format(Number(max)) : null,
  ].filter((part): part is string => part !== null)
  const currencyLabel = currency ? ` ${currency}` : ''
  return `${parts.join(' - ')}${currencyLabel}`
}

function formatDate(value: string | null): string {
  if (!value) {
    return 'Fecha desconocida'
  }
  const date = new Date(value)
  return new Intl.DateTimeFormat('es-CL', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

interface JobCardProps {
  job: Job
}

export function JobCard({ job }: JobCardProps) {
  return (
    <article className="job-card">
      <header className="job-card-header">
        <h3 className="job-card-title">{job.title}</h3>
        <span className="job-card-source">{SOURCE_LABELS[job.source]}</span>
      </header>

      <p className="job-card-company">{job.company_name ?? 'Empresa desconocida'}</p>

      <dl className="job-card-meta">
        {job.location && (
          <div className="job-card-meta-item">
            <dt>Ubicación</dt>
            <dd>{job.location}</dd>
          </div>
        )}
        {(job.salary_min || job.salary_max) && (
          <div className="job-card-meta-item">
            <dt>Salario</dt>
            <dd>{formatSalary(job.salary_min, job.salary_max, job.currency)}</dd>
          </div>
        )}
        {job.employment_type && (
          <div className="job-card-meta-item">
            <dt>Tipo</dt>
            <dd>{EMPLOYMENT_TYPE_LABELS[job.employment_type]}</dd>
          </div>
        )}
        {job.experience_level && (
          <div className="job-card-meta-item">
            <dt>Experiencia</dt>
            <dd>{EXPERIENCE_LEVEL_LABELS[job.experience_level]}</dd>
          </div>
        )}
        <div className="job-card-meta-item">
          <dt>Publicado</dt>
          <dd>{formatDate(job.posted_at)}</dd>
        </div>
      </dl>

      {job.description && (
        <p className="job-card-description">{job.description}</p>
      )}

      {job.source_url && (
        <a
          className="job-card-link"
          href={job.source_url}
          target="_blank"
          rel="noreferrer"
        >
          Ver oferta original
        </a>
      )}
    </article>
  )
}
