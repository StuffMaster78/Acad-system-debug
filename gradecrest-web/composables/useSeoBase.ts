// Site-wide structured data + canonical helpers
// Organization and WebSite LD+JSON are data-driven from TenantSEOSettings
// (fetched in the layout via fetchSiteSettings). Per-page overrides add to these.

export function useSeoBase(canonical: string, settings?: Awaited<ReturnType<typeof fetchSiteSettings>>) {
  // Fall back to the cached settings the layout already fetched — no extra request
  const cached  = useNuxtData<Awaited<ReturnType<typeof fetchSiteSettings>>>('gc-site-settings')
  const s       = settings ?? cached.data.value ?? null
  const orgName = s?.schema_org_name || 'GradeCrest'
  const siteUrl = canonical.replace(/\/[^/]*$/, '') || 'https://gradecrest.com'
  const logoUrl = s?.schema_org_logo_url || undefined

  const org: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${siteUrl}/#org`,
    name: orgName,
    url: siteUrl,
    ...(logoUrl ? { logo: logoUrl } : {}),
    contactPoint: { '@type': 'ContactPoint', contactType: 'customer support', availableLanguage: 'English' },
  }

  const website: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${siteUrl}/#website`,
    url: siteUrl,
    name: orgName,
    publisher: { '@id': `${siteUrl}/#org` },
    potentialAction: {
      '@type': 'SearchAction',
      target: { '@type': 'EntryPoint', urlTemplate: `${siteUrl}/services?q={search_term_string}` },
      'query-input': 'required name=search_term_string',
    },
  }

  useHead({
    link: [{ rel: 'canonical', href: canonical }],
    script: [
      { type: 'application/ld+json', innerHTML: JSON.stringify(org) },
      { type: 'application/ld+json', innerHTML: JSON.stringify(website) },
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
