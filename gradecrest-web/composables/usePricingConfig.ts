import { ACADEMIC_LEVELS, DEADLINES, PAPER_TYPES } from './usePricing'

export interface PricingLevel {
  code: string; label: string; multiplier: number; price_per_page: number | null
}
export interface PricingDeadline {
  label: string; max_hours: number; multiplier: number
}
export interface PricingPaperType {
  code: string; label: string; multiplier: number
}
export interface PricingSpacingMultipliers {
  double: number; single: number
}
export interface CfgDisplayOption { name: string; description?: string }
export interface CfgSubject       { name: string; category: string }
export interface CfgEnglishType   { name: string; code: string }
export interface CfgAddon         { id: number; addon_code: string; name: string; description: string; flat_amount: number }

export interface PublicPricingConfig {
  currency: string
  base_price_per_page: number | null
  base_price_per_slide: number | null
  base_price_per_diagram: number | null
  spacing_multipliers: PricingSpacingMultipliers
  academic_levels: PricingLevel[]
  paper_types: PricingPaperType[]
  deadlines: PricingDeadline[]
  academic_levels_display: CfgDisplayOption[]
  paper_types_display: CfgDisplayOption[]
  subjects: CfgSubject[]
  work_types: CfgDisplayOption[]
  formatting_styles: CfgDisplayOption[]
  english_types: CfgEnglishType[]
  addons: CfgAddon[]
}

export const FALLBACK_SUBJECTS: CfgSubject[] = [
  { name: 'Biology',              category: 'Natural Sciences' },
  { name: 'Chemistry',            category: 'Natural Sciences' },
  { name: 'Physics',              category: 'Natural Sciences' },
  { name: 'Environmental Sci.',   category: 'Natural Sciences' },
  { name: 'Mathematics',          category: 'Mathematics & Statistics' },
  { name: 'Statistics',           category: 'Mathematics & Statistics' },
  { name: 'Computer Science',     category: 'Computing & Technology' },
  { name: 'Engineering',          category: 'Computing & Technology' },
  { name: 'Psychology',           category: 'Social Sciences' },
  { name: 'Sociology',            category: 'Social Sciences' },
  { name: 'Political Science',    category: 'Social Sciences' },
  { name: 'History',              category: 'Humanities' },
  { name: 'Literature / English', category: 'Humanities' },
  { name: 'Philosophy',           category: 'Humanities' },
  { name: 'Business Admin.',      category: 'Business & Economics' },
  { name: 'Economics',            category: 'Business & Economics' },
  { name: 'Marketing',            category: 'Business & Economics' },
  { name: 'Accounting / Finance', category: 'Business & Economics' },
  { name: 'Nursing',              category: 'Healthcare' },
  { name: 'Medicine / Health',    category: 'Healthcare' },
  { name: 'Law',                  category: 'Law & Education' },
  { name: 'Education',            category: 'Law & Education' },
]

const KEY_TO_HOURS: Record<string, number> = {
  '14d': 336, '7d': 168, '5d': 120, '3d': 72, '24h': 24, '12h': 12, '6h': 6,
}

export const FALLBACK_LEVELS: PricingLevel[] = ACADEMIC_LEVELS.map(l => ({
  code: l.key, label: l.label, multiplier: 1, price_per_page: l.base,
}))

export const FALLBACK_DEADLINES: PricingDeadline[] = DEADLINES.map(d => ({
  label: d.label, max_hours: KEY_TO_HOURS[d.key] ?? 336, multiplier: d.multiplier,
}))

export const FALLBACK_PAPER_TYPES: PricingPaperType[] = PAPER_TYPES.map(p => ({
  code: p.key, label: p.label, multiplier: 1,
}))

export async function fetchPricingConfig(): Promise<PublicPricingConfig> {
  const config = useRuntimeConfig()
  const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''
  if (!apiBase) return _fallback()
  try {
    const raw = await $fetch<Record<string, unknown>>(`${apiBase}/api/v1/pricing/public/config/`)
    return _parse(raw)
  } catch {
    return _fallback()
  }
}

function _parse(raw: Record<string, unknown>): PublicPricingConfig {
  const sm = (raw.spacing_multipliers ?? {}) as Record<string, unknown>
  return {
    currency:            String(raw.currency || 'USD'),
    base_price_per_page: raw.base_price_per_page != null ? Number(raw.base_price_per_page) : null,
    base_price_per_slide: raw.base_price_per_slide != null ? Number(raw.base_price_per_slide) : null,
    base_price_per_diagram: raw.base_price_per_diagram != null ? Number(raw.base_price_per_diagram) : null,
    spacing_multipliers: { double: sm.double != null ? Number(sm.double) : 1, single: sm.single != null ? Number(sm.single) : 2 },
    academic_levels:  Array.isArray(raw.academic_levels) && raw.academic_levels.length ? (raw.academic_levels as Record<string, unknown>[]).map(_level) : FALLBACK_LEVELS,
    paper_types:      Array.isArray(raw.paper_types) && raw.paper_types.length ? (raw.paper_types as Record<string, unknown>[]).map(_paperType) : FALLBACK_PAPER_TYPES,
    deadlines:        Array.isArray(raw.deadlines) && raw.deadlines.length ? (raw.deadlines as Record<string, unknown>[]).map(_deadline) : FALLBACK_DEADLINES,
    academic_levels_display: Array.isArray(raw.academic_levels_display) ? (raw.academic_levels_display as Record<string, unknown>[]).map(_display) : [],
    paper_types_display:     Array.isArray(raw.paper_types_display) ? (raw.paper_types_display as Record<string, unknown>[]).map(_display) : [],
    subjects:           Array.isArray(raw.subjects) && raw.subjects.length ? (raw.subjects as Record<string, unknown>[]).map(r => ({ name: String(r.name ?? ''), category: String(r.category ?? 'General') })) : FALLBACK_SUBJECTS,
    work_types:         Array.isArray(raw.work_types) ? (raw.work_types as Record<string, unknown>[]).map(_display) : [],
    formatting_styles:  Array.isArray(raw.formatting_styles) ? (raw.formatting_styles as Record<string, unknown>[]).map(_display) : [],
    english_types:      Array.isArray(raw.english_types) ? (raw.english_types as Record<string, unknown>[]).map(r => ({ name: String(r.name ?? ''), code: String(r.code ?? '') })) : [],
    addons:             Array.isArray(raw.addons) ? (raw.addons as Record<string, unknown>[]).map(r => ({ id: Number(r.id ?? 0), addon_code: String(r.addon_code ?? ''), name: String(r.name ?? ''), description: String(r.description ?? ''), flat_amount: Number(r.flat_amount ?? 0) })) : [],
  }
}

function _fallback(): PublicPricingConfig {
  return {
    currency: 'USD', base_price_per_page: null, base_price_per_slide: null, base_price_per_diagram: null,
    spacing_multipliers: { double: 1, single: 2 },
    academic_levels: FALLBACK_LEVELS, paper_types: FALLBACK_PAPER_TYPES, deadlines: FALLBACK_DEADLINES,
    academic_levels_display: [], paper_types_display: [], subjects: FALLBACK_SUBJECTS, work_types: [], formatting_styles: [], english_types: [], addons: [],
  }
}

function _level(r: Record<string, unknown>): PricingLevel {
  return { code: String(r.code ?? ''), label: String(r.label ?? ''), multiplier: Number(r.multiplier ?? 1), price_per_page: r.price_per_page != null ? Number(r.price_per_page) : null }
}
function _paperType(r: Record<string, unknown>): PricingPaperType {
  return { code: String(r.code ?? ''), label: String(r.label ?? ''), multiplier: Number(r.multiplier ?? 1) }
}
function _deadline(r: Record<string, unknown>): PricingDeadline {
  return { label: String(r.label ?? ''), max_hours: Number(r.max_hours ?? 336), multiplier: Number(r.multiplier ?? 1) }
}
function _display(r: Record<string, unknown>): CfgDisplayOption {
  return { name: String(r.name ?? ''), description: r.description ? String(r.description) : undefined }
}
