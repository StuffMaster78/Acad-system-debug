export interface ServiceData {
  slug: string
  navLabel: string
}

const services: ServiceData[] = [
  { slug: 'essay-writing',   navLabel: 'Essay Writing'   },
  { slug: 'research-papers', navLabel: 'Research Papers' },
  { slug: 'dissertations',   navLabel: 'Dissertations'   },
  { slug: 'nursing-essays',  navLabel: 'Nursing Essays'  },
  { slug: 'data-analysis',   navLabel: 'Data Analysis'   },
  { slug: 'case-studies',    navLabel: 'Case Studies'    },
]

export function useServices() {
  function getAll() {
    return services
  }

  function getBySlug(slug: string) {
    return services.find(s => s.slug === slug) ?? null
  }

  return { getAll, getBySlug }
}
