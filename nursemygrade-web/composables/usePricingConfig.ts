export interface PricingLevel {
  code: string
  label: string
  multiplier: number
  price_per_page: number | null
}

export interface PricingDeadline {
  label: string
  max_hours: number
  multiplier: number
}

export interface PricingPaperType {
  code: string
  label: string
  multiplier: number
}

export interface PublicPricingConfig {
  currency: string
  base_price_per_page: number | null
  academic_levels: PricingLevel[]
  paper_types: PricingPaperType[]
  deadlines: PricingDeadline[]
}

// Static fallbacks matching seed_pricing_defaults codes + labels.
export const FALLBACK_LEVELS: PricingLevel[] = [
  { code: 'high_school', label: 'High School',       multiplier: 1,    price_per_page: 15 },
  { code: 'undergrad',   label: 'Undergraduate',     multiplier: 1.2,  price_per_page: 18 },
  { code: 'masters',     label: "Master's",          multiplier: 1.5,  price_per_page: 24 },
  { code: 'phd',         label: 'PhD / Doctoral',    multiplier: 1.8,  price_per_page: 32 },
]

export const FALLBACK_DEADLINES: PricingDeadline[] = [
  { label: '14 days',   max_hours: 336, multiplier: 1.00 },
  { label: '7 days',    max_hours: 168, multiplier: 1.10 },
  { label: '5 days',    max_hours: 120, multiplier: 1.15 },
  { label: '3 days',    max_hours: 72,  multiplier: 1.25 },
  { label: '24 hours',  max_hours: 24,  multiplier: 1.35 },
  { label: '12 hours',  max_hours: 12,  multiplier: 1.50 },
  { label: '6 hours',   max_hours: 6,   multiplier: 1.65 },
]

export const FALLBACK_PAPER_TYPES: PricingPaperType[] = [
  { code: 'essay',           label: 'Essay',              multiplier: 1 },
  { code: 'research_paper',  label: 'Research Paper',     multiplier: 1.1 },
  { code: 'thesis',          label: 'Dissertation',       multiplier: 1.4 },
  { code: 'case_study',      label: 'Case Study',         multiplier: 1.1 },
  { code: 'coursework',      label: 'Coursework',         multiplier: 1 },
  { code: 'lab_report',      label: 'Lab Report',         multiplier: 1.2 },
  { code: 'editing',         label: 'Editing',            multiplier: 0.7 },
]

export async function fetchPricingConfig(): Promise<PublicPricingConfig> {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || ''
  if (!apiBase) return _fallback()

  try {
    const raw = await $fetch<PublicPricingConfig>(`${apiBase}/api/v1/pricing/public/config/`)
    return {
      currency:           raw.currency || 'USD',
      base_price_per_page: raw.base_price_per_page ?? null,
      academic_levels: raw.academic_levels?.length ? raw.academic_levels.map(_coerceLevel) : FALLBACK_LEVELS,
      paper_types:     raw.paper_types?.length     ? raw.paper_types.map(_coercePaperType)  : FALLBACK_PAPER_TYPES,
      deadlines:       raw.deadlines?.length        ? raw.deadlines.map(_coerceDeadline)     : FALLBACK_DEADLINES,
    }
  } catch {
    return _fallback()
  }
}

function _fallback(): PublicPricingConfig {
  return { currency: 'USD', base_price_per_page: null, academic_levels: FALLBACK_LEVELS, paper_types: FALLBACK_PAPER_TYPES, deadlines: FALLBACK_DEADLINES }
}

function _coerceLevel(r: Record<string, unknown>): PricingLevel {
  return { code: String(r.code ?? ''), label: String(r.label ?? ''), multiplier: Number(r.multiplier ?? 1), price_per_page: r.price_per_page != null ? Number(r.price_per_page) : null }
}
function _coercePaperType(r: Record<string, unknown>): PricingPaperType {
  return { code: String(r.code ?? ''), label: String(r.label ?? ''), multiplier: Number(r.multiplier ?? 1) }
}
function _coerceDeadline(r: Record<string, unknown>): PricingDeadline {
  return { label: String(r.label ?? ''), max_hours: Number(r.max_hours ?? 336), multiplier: Number(r.multiplier ?? 1) }
}
