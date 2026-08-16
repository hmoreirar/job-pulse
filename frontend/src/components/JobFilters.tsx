import type { ChangeEvent } from 'react'

import type { JobFilters } from '../types/job'
import {
  EMPLOYMENT_TYPE_LABELS,
  EXPERIENCE_LEVEL_LABELS,
  SORT_LABELS,
  SOURCE_LABELS,
} from '../lib/labels'

interface JobFiltersProps {
  filters: JobFilters
  onChange: (filters: JobFilters) => void
}

type FilterField = Exclude<
  keyof JobFilters,
  'page' | 'page_size' | 'salary_min' | 'salary_max'
>

export function JobFilters({ filters, onChange }: JobFiltersProps) {
  const handleChange = (key: FilterField) => (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    onChange({ ...filters, [key]: event.target.value, page: 1 })
  }

  return (
    <form className="job-filters" onSubmit={(event) => event.preventDefault()}>
      <div className="job-filters-row">
        <input
          className="job-filters-input"
          type="search"
          placeholder="Buscar por título, descripción o empresa..."
          value={filters.search ?? ''}
          onChange={handleChange('search')}
        />
        <input
          className="job-filters-input"
          type="text"
          placeholder="Ubicación"
          value={filters.location ?? ''}
          onChange={handleChange('location')}
        />
      </div>

      <div className="job-filters-row">
        <select
          className="job-filters-select"
          value={filters.source ?? ''}
          onChange={handleChange('source')}
        >
          <option value="">Todas las fuentes</option>
          {Object.entries(SOURCE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <select
          className="job-filters-select"
          value={filters.employment_type ?? ''}
          onChange={handleChange('employment_type')}
        >
          <option value="">Todos los tipos</option>
          {Object.entries(EMPLOYMENT_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <select
          className="job-filters-select"
          value={filters.experience_level ?? ''}
          onChange={handleChange('experience_level')}
        >
          <option value="">Toda experiencia</option>
          {Object.entries(EXPERIENCE_LEVEL_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <select
          className="job-filters-select"
          value={filters.sort ?? ''}
          onChange={handleChange('sort')}
        >
          <option value="">Ordenar por...</option>
          {Object.entries(SORT_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <select
          className="job-filters-select"
          value={filters.order ?? 'desc'}
          onChange={handleChange('order')}
        >
          <option value="desc">Descendente</option>
          <option value="asc">Ascendente</option>
        </select>
      </div>
    </form>
  )
}
