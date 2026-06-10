// Site-wide structured data + canonical helpers

const ORG_LD = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  '@id': 'https://gradecrest.com/#org',
  name: 'GradeCrest',
  url: 'https://gradecrest.com',
  logo: 'https://gradecrest.com/logo.png',
  contactPoint: { '@type': 'ContactPoint', contactType: 'customer support', availableLanguage: 'English' },
  sameAs: ['https://www.trustpilot.com/review/gradecrest.com'],
}

const WEBSITE_LD = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  '@id': 'https://gradecrest.com/#website',
  url: 'https://gradecrest.com',
  name: 'GradeCrest',
  description: 'Academic writing service — essays, research papers, dissertations written by human experts.',
  publisher: { '@id': 'https://gradecrest.com/#org' },
  potentialAction: {
    '@type': 'SearchAction',
    target: { '@type': 'EntryPoint', urlTemplate: 'https://gradecrest.com/services?q={search_term_string}' },
    'query-input': 'required name=search_term_string',
  },
}

export function useSeoBase(canonical: string) {
  useHead({
    link: [{ rel: 'canonical', href: canonical }],
    script: [
      { type: 'application/ld+json', innerHTML: JSON.stringify(ORG_LD) },
      { type: 'application/ld+json', innerHTML: JSON.stringify(WEBSITE_LD) },
    ],
  })
}

export function useBreadcrumbs(items: { name: string; url: string }[]) {
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: item.url,
    })),
  }
  useHead({ script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(ld) }] })
  return items
}

export function useFaqLd(faqs: { q: string; a: string }[]) {
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(f => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  }
  useHead({ script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(ld) }] })
}

export function useServiceLd(opts: {
  name: string
  description: string
  url: string
  price?: string
  ratingValue?: number
  reviewCount?: number
}) {
  const ld: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: opts.name,
    description: opts.description,
    url: opts.url,
    provider: { '@id': 'https://gradecrest.com/#org' },
  }
  if (opts.price) {
    ld.offers = { '@type': 'Offer', price: opts.price, priceCurrency: 'USD', availability: 'https://schema.org/InStock' }
  }
  if (opts.ratingValue && opts.reviewCount) {
    ld.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: opts.ratingValue,
      reviewCount: opts.reviewCount,
      bestRating: 5,
    }
  }
  useHead({ script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(ld) }] })
}
