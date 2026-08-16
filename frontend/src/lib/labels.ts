import type {
  EmploymentType,
  ExperienceLevel,
  Source,
} from '../types/job'

export const EMPLOYMENT_TYPE_LABELS: Record<EmploymentType, string> = {
  full_time: 'Tiempo completo',
  part_time: 'Medio tiempo',
  contract: 'Contrato',
  freelance: 'Freelance',
  internship: 'Práctica',
}

export const EXPERIENCE_LEVEL_LABELS: Record<ExperienceLevel, string> = {
  intern: 'Interno',
  entry: 'Entry',
  junior: 'Junior',
  mid: 'Semi senior',
  senior: 'Senior',
  staff: 'Staff',
  lead: 'Lead',
  principal: 'Principal',
}

export const SOURCE_LABELS: Record<Source, string> = {
  linkedin: 'LinkedIn',
  indeed: 'Indeed',
  computrabajo: 'Computrabajo',
  getonboard: 'GetOnBoard',
  glassdoor: 'Glassdoor',
  remoteok: 'RemoteOK',
  wellfound: 'Wellfound',
  greenhouse: 'Greenhouse',
  lever: 'Lever',
  other: 'Otro',
}

export const SORT_LABELS: Record<string, string> = {
  posted_at: 'Fecha de publicación',
  salary_min: 'Salario mínimo',
  salary_max: 'Salario máximo',
  title: 'Título',
  created_at: 'Fecha de ingreso',
  scraped_at: 'Fecha de scraping',
}
