// Pricing config — synced with the backend order_configs API.
// Base prices are per page (275 words). All values in USD.

export const ACADEMIC_LEVELS = [
  { key: 'high_school',        label: 'High School',          base: 13 },
  { key: 'undergrad_1_2',      label: 'Undergraduate (1–2)',  base: 15 },
  { key: 'undergrad_3_4',      label: 'Undergraduate (3–4)',  base: 18 },
  { key: 'masters',            label: "Master's",             base: 22 },
  { key: 'phd',                label: 'PhD / Doctoral',       base: 28 },
]

export const DEADLINES = [
  { key: '14d',  label: '14 days',    multiplier: 1.00, urgent: false },
  { key: '7d',   label: '7 days',     multiplier: 1.10, urgent: false },
  { key: '5d',   label: '5 days',     multiplier: 1.15, urgent: false },
  { key: '3d',   label: '3 days',     multiplier: 1.25, urgent: false },
  { key: '24h',  label: '24 hours',   multiplier: 1.35, urgent: true  },
  { key: '12h',  label: '12 hours',   multiplier: 1.50, urgent: true  },
  { key: '6h',   label: '6 hours',    multiplier: 1.65, urgent: true  },
]

export const PAPER_TYPES = [
  { key: 'essay',         label: 'Essay'                  },
  { key: 'research',      label: 'Research Paper'         },
  { key: 'dissertation',  label: 'Dissertation / Thesis'  },
  { key: 'coursework',    label: 'Coursework'             },
  { key: 'case_study',    label: 'Case Study'             },
  { key: 'term_paper',    label: 'Term Paper'             },
  { key: 'admission',     label: 'Admission Essay'        },
  { key: 'editing',       label: 'Editing / Proofreading' },
  { key: 'other',         label: 'Other'                  },
]

export const WRITER_TIERS = [
  { key: 'standard', label: 'Standard', multiplier: 1.00, badge: null,         desc: "Master's degree holders" },
  { key: 'advanced', label: 'Advanced', multiplier: 1.10, badge: 'Popular',    desc: 'Top-rated, 4.8+ stars' },
  { key: 'expert',   label: 'Expert',   multiplier: 1.20, badge: 'PhD level',  desc: 'Doctoral specialists' },
]

export function usePricing() {
  function calculate(opts: {
    levelKey: string
    deadlineKey: string
    pages: number
    tierKey?: string
  }): number {
    const level    = ACADEMIC_LEVELS.find(l => l.key === opts.levelKey) ?? ACADEMIC_LEVELS[1]
    const deadline = DEADLINES.find(d => d.key === opts.deadlineKey)    ?? DEADLINES[0]
    const tier     = WRITER_TIERS.find(t => t.key === opts.tierKey)     ?? WRITER_TIERS[0]
    const perPage  = level.base * deadline.multiplier * tier.multiplier
    return Math.ceil(perPage * opts.pages * 100) / 100
  }

  function perPage(levelKey: string, deadlineKey: string, tierKey = 'standard'): number {
    return calculate({ levelKey, deadlineKey, pages: 1, tierKey })
  }

  return { calculate, perPage }
}
