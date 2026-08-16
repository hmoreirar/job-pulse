export type EmploymentType =
  | 'full_time'
  | 'part_time'
  | 'contract'
  | 'freelance'
  | 'internship'

export type ExperienceLevel =
  | 'intern'
  | 'entry'
  | 'junior'
  | 'mid'
  | 'senior'
  | 'staff'
  | 'lead'
  | 'principal'

export type Source =
  | 'linkedin'
  | 'indeed'
  | 'computrabajo'
  | 'getonboard'
  | 'glassdoor'
  | 'remoteok'
  | 'wellfound'
  | 'greenhouse'
  | 'lever'
  | 'other'

export interface Job {
  id: string
  company_id: string
  company_name: string | null
  title: string
  description: string | null
  location: string | null
  salary_min: string | null
  salary_max: string | null
  currency: string | null
  employment_type: EmploymentType | null
  experience_level: ExperienceLevel | null
  source: Source
  external_id: string | null
  source_url: string | null
  posted_at: string | null
  scraped_at: string | null
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface JobListResponse {
  items: Job[]
  total: number
  page: number
  page_size: number
  pages: number
}

export type SortField =
  | 'posted_at'
  | 'scraped_at'
  | 'created_at'
  | 'salary_min'
  | 'salary_max'
  | 'title'

export interface JobFilters {
  search?: string
  source?: Source | ''
  employment_type?: EmploymentType | ''
  experience_level?: ExperienceLevel | ''
  location?: string
  salary_min?: string
  salary_max?: string
  sort?: SortField | ''
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}
