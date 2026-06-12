import { ACADEMIC_LEVELS, DEADLINES, PAPER_TYPES } from './usePricing'

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
  base_price_per_slide: number | null
  base_price_per_diagram: number | null
  academic_levels: PricingLevel[]
  paper_types: PricingPaperType[]
  deadlines: PricingDeadline[]
}

// Static fallbacks — used when the backend is unreachable or not yet configured.
// Keys map directly to AcademicLevelRate.code values seeded by seed_pricing_defaults.
const KEY_TO_HOURS: Record<string, number> = {
  '14d': 336, '7d': 168, '5d': 120, '3d': 72, '24h': 24, '12h': 12, '6h': 6,
}

export const FALLBACK_LEVELS: PricingLevel[] = ACADEMIC_LEVELS.map(l => ({
  code: l.key,
  label: l.label,
  multiplier: 1,
  price_per_page: l.base,
}))

export const FALLBACK_DEADLINES: PricingDeadline[] = DEADLINES.map(d => ({
  label: d.label,
  max_hours: KEY_TO_HOURS[d.key] ?? 336,
  multiplier: d.multiplier,
}))

export const FALLBACK_PAPER_TYPES: PricingPaperType[] = PAPER_TYPES.map(p => ({
  code: p.key,
  label: p.label,
  multiplier: 1,
}))

export async function fetchPricingConfig(): Promise<PublicPricingConfig> {
  const config = useRuntimeConfig()
  const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

  if (!apiBase) return _fallback()

  try {
    const raw = await $fetch<PublicPricingConfig>(`${apiBase}/api/v1/pricing/public/config/`)
    return {
      currency: raw.currency || 'USD',
      base_price_per_page: raw.base_price_per_page ?? null,
      base_price_per_slide: raw.base_price_per_slide ?? null,
      base_price_per_diagram: raw.base_price_per_diagram ?? null,
      academic_levels: raw.academic_levels?.length ? raw.academic_levels.map(_coerceLevel) : FALLBACK_LEVELS,
      paper_types:     raw.paper_types?.length     ? raw.paper_types.map(_coercePaperType)  : FALLBACK_PAPER_TYPES,
      deadlines:       raw.deadlines?.length        ? raw.deadlines.map(_coerceDeadline)     : FALLBACK_DEADLINES,
    }
  } catch {
    return _fallback()
  }
}

function _fallback(): PublicPricingConfig {
  return {
    currency: 'USD',
    base_price_per_page: null,
    base_price_per_slide: null,
    base_price_per_diagram: null,
    academic_levels: FALLBACK_LEVELS,
    paper_types:     FALLBACK_PAPER_TYPES,
    deadlines:       FALLBACK_DEADLINES,
  }
}

function _coerceLevel(r: Record<string, unknown>): PricingLevel {
  return {
    code:          String(r.code ?? ''),
    label:         String(r.label ?? ''),
    multiplier:    Number(r.multiplier ?? 1),
    price_per_page: r.price_per_page != null ? Number(r.price_per_page) : null,
  }
}

function _coercePaperType(r: Record<string, unknown>): PricingPaperType {
  return {
    code:       String(r.code ?? ''),
    label:      String(r.label ?? ''),
    multiplier: Number(r.multiplier ?? 1),
  }
}

function _coerceDeadline(r: Record<string, unknown>): PricingDeadline {
  return {
    label:      String(r.label ?? ''),
    max_hours:  Number(r.max_hours ?? 336),
    multiplier: Number(r.multiplier ?? 1),
  }
}
