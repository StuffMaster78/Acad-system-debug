export interface ServiceData {
  slug: string
  navLabel: string
  icon: string
  title: string
  hero: { headline: string; sub: string }
  includes: string[]
  delivers: string[]
  whoFor: string
  priceFrom: number
  relatedSlugs: string[]
  meta: { title: string; description: string }
}

const services: ServiceData[] = [
  {
    slug: 'research-papers',
    navLabel: 'Research Papers',
    icon: 'file-text',
    title: 'Research Paper Writing Service',
    hero: {
      headline: 'Research Papers Written by Specialists',
      sub: 'Original, fully referenced papers built on credible academic sources. Any citation style — APA, MLA, Chicago, Harvard, Vancouver.',
    },
    includes: [
      'Written from scratch to your exact brief',
      'Primary and secondary source integration',
      'Any citation style: APA, MLA, Chicago, Harvard, Vancouver',
      'Free plagiarism report included',
      'Unlimited revisions within review window',
    ],
    delivers: [
      'Structured introduction, body, and conclusion',
      'In-text citations and full bibliography',
      'Abstract and title page (if required)',
      'Formatted to your university style guide',
    ],
    whoFor: 'Undergraduate, postgraduate, and doctoral students who need a well-researched, properly structured paper with accurate citations.',
    priceFrom: 15,
    relatedSlugs: ['literature-reviews', 'data-analysis', 'dissertations'],
    meta: {
      title: 'Research Paper Writing Service from $15/Page',
      description: 'Custom research papers written by subject specialists. Any citation style, any level. Grade or money back. From $15/page.',
    },
  },
  {
    slug: 'essays',
    navLabel: 'Essays',
    icon: '✍️',
    title: 'Essay Writing Service',
    hero: {
      headline: 'Essays That Argue, Analyse & Impress',
      sub: 'Argumentative, analytical, descriptive, narrative, and reflective essays written to your exact brief — any format, any level.',
    },
    includes: [
      'High school through PhD level',
      'All essay types: argumentative, analytical, descriptive, reflective',
      'Clear thesis and structured argument',
      'Proper formatting and citations',
      'Free unlimited revisions',
    ],
    delivers: [
      'Introduction with strong thesis statement',
      'Well-developed body paragraphs with evidence',
      'Conclusion that ties the argument together',
      'References page in required citation style',
    ],
    whoFor: 'Students at any level who need a well-argued, clearly written essay on any topic — from 500-word introductory essays to 5,000-word analytical pieces.',
    priceFrom: 15,
    relatedSlugs: ['research-papers', 'literature-reviews', 'coursework'],
    meta: {
      title: 'Essay Writing Service from $15/Page',
      description: 'Custom essays written by academic experts. Argumentative, analytical, descriptive — any type, any level. From $15/page.',
    },
  },
  {
    slug: 'dissertations',
    navLabel: 'Dissertations',
    icon: '🎓',
    title: 'Dissertation & Thesis Writing Service',
    hero: {
      headline: 'Dissertation Support from Proposal to Defence',
      sub: 'End-to-end dissertation help — proposal writing, individual chapters, methodology, data analysis, and final editing.',
    },
    includes: [
      'Chapter-by-chapter delivery and review',
      'Research proposal and literature review',
      'Methodology and data analysis chapters',
      'Supervisor feedback integration',
      'Extended revision window (14 days)',
    ],
    delivers: [
      'Full dissertation or individual chapters',
      'Properly formatted methodology chapter',
      'Data analysis with charts and tables',
      'Comprehensive bibliography',
    ],
    whoFor: 'Master\'s and PhD students who need structured dissertation help — whether for a single chapter, the full document, or last-minute polishing before submission.',
    priceFrom: 28,
    relatedSlugs: ['literature-reviews', 'data-analysis', 'research-papers'],
    meta: {
      title: 'Dissertation Writing Service — Chapter by Chapter Help',
      description: 'Expert dissertation writing from proposal to final chapter. Master\'s and PhD level. Grade or money back. From $28/page.',
    },
  },
  {
    slug: 'case-studies',
    navLabel: 'Case Studies',
    icon: '📋',
    title: 'Case Study Writing Service',
    hero: {
      headline: 'Case Studies That Analyse, Argue & Conclude',
      sub: 'In-depth business, medical, and social science case study analysis — structured arguments, real evidence, professional presentation.',
    },
    includes: [
      'Business, law, nursing, and social work case studies',
      'Problem–solution–evaluation structure',
      'Real-world source and case law integration',
      'Proper Harvard or APA formatting',
      'Free revisions',
    ],
    delivers: [
      'Executive summary (if required)',
      'Problem identification and analysis',
      'Solution evaluation with evidence',
      'Recommendations and conclusion',
    ],
    whoFor: 'Business school, law, nursing, and social science students who need a structured, evidence-backed analysis of a real-world scenario.',
    priceFrom: 18,
    relatedSlugs: ['essays', 'research-papers', 'coursework'],
    meta: {
      title: 'Case Study Writing Service — Business, Law & Nursing',
      description: 'Expert case study writing for business, law, and nursing. Structured, evidence-backed analysis. From $18/page.',
    },
  },
  {
    slug: 'coursework',
    navLabel: 'Coursework & Assignments',
    icon: '📚',
    title: 'Coursework & Assignment Help',
    hero: {
      headline: 'Consistent Coursework Help, Every Week',
      sub: 'Regular assignments, problem sets, and module work handled reliably — by the same writer who knows your course.',
    },
    includes: [
      'Recurring order discounts for regular customers',
      'Consistent writer assigned across modules',
      'Subject-matter specialists for each discipline',
      'Short and long assignments accepted',
      'Free revisions',
    ],
    delivers: [
      'Completed assignment to your brief',
      'Properly structured and referenced work',
      'Formatted to your module\'s requirements',
    ],
    whoFor: 'Students with heavy coursework loads who need reliable, on-time help with weekly or monthly assignments across one or more modules.',
    priceFrom: 15,
    relatedSlugs: ['essays', 'research-papers', 'case-studies'],
    meta: {
      title: 'Coursework & Assignment Writing Help from $15/Page',
      description: 'Reliable coursework and assignment help from subject specialists. Recurring discounts available. From $15/page.',
    },
  },
  {
    slug: 'data-analysis',
    navLabel: 'Data Analysis',
    icon: '📊',
    title: 'Data Analysis & Statistics Help',
    hero: {
      headline: 'Data Analysis Done Right — With Full Write-Up',
      sub: 'Quantitative and qualitative analysis using SPSS, R, Python, or Excel — with interpretation, charts, and methodology chapter support.',
    },
    includes: [
      'SPSS, R, Python, and Excel analysis',
      'Charts, tables, and data visualisations',
      'Full statistical write-up with interpretation',
      'Methodology chapter support',
      'Free revisions',
    ],
    delivers: [
      'Cleaned and analysed dataset',
      'Descriptive and inferential statistics',
      'Charts and tables formatted for your document',
      'Written interpretation of results',
    ],
    whoFor: 'Students in business, social sciences, healthcare, and STEM who need quantitative or qualitative data analysis with a written results section.',
    priceFrom: 22,
    relatedSlugs: ['dissertations', 'research-papers', 'lab-reports'],
    meta: {
      title: 'Data Analysis & Statistics Help — SPSS, R, Python',
      description: 'Expert data analysis with full written interpretation. SPSS, R, Python, Excel. From $22/page.',
    },
  },
  {
    slug: 'literature-reviews',
    navLabel: 'Literature Reviews',
    icon: '🔍',
    title: 'Literature Review Writing Service',
    hero: {
      headline: 'Literature Reviews That Synthesise & Critique',
      sub: 'Systematic, narrative, and scoping reviews — with proper gap identification, critical synthesis, and full database search strategy.',
    },
    includes: [
      'Systematic, narrative, or scoping review formats',
      'PRISMA flow diagrams available',
      'Database search strategy documented',
      'Gap identification and critique',
      'Free revisions',
    ],
    delivers: [
      'Themed synthesis of existing literature',
      'Critical evaluation of sources',
      'Clear identification of research gaps',
      'Full reference list in required style',
    ],
    whoFor: 'Dissertation and research students who need a rigorous review of the existing literature in their field — including gap identification for their own research rationale.',
    priceFrom: 22,
    relatedSlugs: ['dissertations', 'research-papers', 'data-analysis'],
    meta: {
      title: 'Literature Review Writing Service from $22/Page',
      description: 'Expert literature review writing — systematic, narrative, or scoping. Gap identification, critical synthesis. From $22/page.',
    },
  },
  {
    slug: 'lab-reports',
    navLabel: 'Lab Reports',
    icon: '🔬',
    title: 'Lab Report Writing Service',
    hero: {
      headline: 'Lab Reports with Every Section Done Properly',
      sub: 'Correctly structured scientific lab reports — introduction, method, results, discussion — with proper notation, graph formatting, and citations.',
    },
    includes: [
      'All standard sections: intro, method, results, discussion, conclusion',
      'Correct scientific notation and units',
      'Graph and table formatting',
      'Statistical analysis where needed',
      'Free revisions',
    ],
    delivers: [
      'Complete lab report to your brief',
      'Formatted figures and data tables',
      'Discussion with reference to your results',
      'Bibliography in required style',
    ],
    whoFor: 'Biology, chemistry, physics, and engineering students who need a well-structured report that correctly presents and interprets their experimental data.',
    priceFrom: 18,
    relatedSlugs: ['data-analysis', 'research-papers', 'coursework'],
    meta: {
      title: 'Lab Report Writing Service — Science & Engineering',
      description: 'Properly structured lab reports for biology, chemistry, physics, and engineering. All sections included. From $18/page.',
    },
  },
  {
    slug: 'presentations',
    navLabel: 'Presentations',
    icon: '📽️',
    title: 'Presentation & Speech Writing Service',
    hero: {
      headline: 'Presentations That Persuade and Speeches That Land',
      sub: 'Academic and professional PowerPoint presentations with speaker notes — or full speech scripts timed to your delivery slot.',
    },
    includes: [
      'Slide content and structure',
      'Speaker notes for every slide',
      'Timed to your presentation slot',
      'Visual design guidance',
      'Free revisions',
    ],
    delivers: [
      'Slide-by-slide content plan',
      'Presentation script or speaker notes',
      'Key argument flow and transitions',
      'Bibliography slide (if required)',
    ],
    whoFor: 'Students preparing for seminar presentations, viva presentations, conference talks, or professional pitches who need structured content and speaker notes.',
    priceFrom: 18,
    relatedSlugs: ['essays', 'research-papers', 'case-studies'],
    meta: {
      title: 'Presentation & Speech Writing Service from $18/Page',
      description: 'Academic and professional presentation writing with speaker notes. Timed to your slot. From $18/page.',
    },
  },
]

export function useServices() {
  function getAll() {
    return services
  }

  function getBySlug(slug: string) {
    return services.find(s => s.slug === slug) ?? null
  }

  function getRelated(slugs: string[]) {
    return services.filter(s => slugs.includes(s.slug))
  }

  return { getAll, getBySlug, getRelated }
}

// ── CMS-driven service list ──────────────────────────────────────────────────
// Allows non-technical admins to create/rename service pages in Wagtail and
// have them appear in the footer, header mega-menu, and services index without
// any developer involvement. Static useServices() data enriches the display
// (icons, hero copy, includes) but is NOT required for a page to appear.

export interface CmsServiceSummary {
  id: number
  title: string
  slug: string
  service_category?: { name: string; slug: string } | null
  pricing_from?: string | null
  turnaround_hours_fastest?: number | null
}

export function useCmsServiceList() {
  const { data } = useAsyncData<{ items: CmsServiceSummary[] }>(
    'cms-service-list',
    () => $fetch<{ items: CmsServiceSummary[] }>('/api/v2/pages/', {
      query: {
        type: 'cms_service_pages.ServicePage',
        order: 'title',
        fields: 'title,slug,service_category,pricing_from,turnaround_hours_fastest',
        limit: 20,
      },
    }).catch(() => ({ items: [] })),
    { default: () => ({ items: [] }) },
  )

  // Merge CMS list with static data for richer display (icon, navLabel, hero sub)
  const staticServices = services

  const merged = computed(() => {
    const cmsItems = data.value?.items ?? []
    // If Wagtail returned nothing (dev/offline), fall back to static list
    if (!cmsItems.length) {
      return staticServices.map(s => ({
        slug: s.slug,
        title: s.title,
        navLabel: s.navLabel,
        icon: s.icon,
        heroSub: s.hero.sub,
        priceFrom: s.priceFrom,
        category: null as string | null,
      }))
    }
    return cmsItems.map(page => {
      const local = staticServices.find(s => s.slug === page.slug)
      return {
        slug: page.slug,
        title: page.title,
        navLabel: local?.navLabel ?? page.title,
        icon: local?.icon ?? 'file-text',
        heroSub: local?.hero.sub ?? '',
        priceFrom: page.pricing_from ? parseFloat(page.pricing_from) : (local?.priceFrom ?? 15),
        category: page.service_category?.name ?? null,
      }
    })
  })

  return merged
}
