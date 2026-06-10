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
    slug: 'essays',
    navLabel: 'Essays',
    icon: 'pen-line',
    title: 'Essay Writing Service',
    hero: {
      headline: 'Essays That Actually Argue Something',
      sub: 'Argumentative, analytical, descriptive, reflective, and narrative essays written to your exact brief by a subject specialist who has written hundreds of them.',
    },
    includes: [
      'All essay types: argumentative, analytical, descriptive, reflective, narrative',
      'High school through doctoral level',
      'Strong thesis and structured argument throughout',
      'All citation styles: APA, MLA, Chicago, Harvard',
      'Free unlimited revisions within review window',
    ],
    delivers: [
      'Introduction with a clear, arguable thesis statement',
      'Well-developed body paragraphs with evidence and analysis',
      'Conclusion that synthesises the argument',
      'Reference list in your required citation style',
      'Free plagiarism report',
    ],
    whoFor: 'Students at any level who need a well-argued, clearly structured essay from 500-word introductory pieces to 5,000-word analytical works.',
    priceFrom: 10,
    relatedSlugs: ['research-papers', 'argumentative-essays', 'coursework'],
    meta: {
      title: 'Essay Writing Service from $10/Page | EssayManiacs',
      description: 'Custom essays by subject specialists. Any type, any level, any citation style. Grade or money back. From $10/page.',
    },
  },
  {
    slug: 'research-papers',
    navLabel: 'Research Papers',
    icon: 'file-text',
    title: 'Research Paper Writing Service',
    hero: {
      headline: 'Research Papers Written by Actual Researchers',
      sub: 'Original, fully referenced papers built on credible academic sources. Any discipline, any citation style, any level.',
    },
    includes: [
      'Original research from peer-reviewed academic sources',
      'Any citation style: APA, MLA, Chicago, Harvard, Vancouver',
      'Abstract, introduction, body, and conclusion structure',
      'Annotated bibliography or reference list included',
      'Free plagiarism report with every order',
    ],
    delivers: [
      'Structured introduction with clear research question',
      'Comprehensive literature engagement and critical analysis',
      'In-text citations and fully formatted reference list',
      'Abstract and title page if required',
    ],
    whoFor: 'Undergraduate, postgraduate, and doctoral students needing a well-researched, properly structured paper with accurate citations and original analysis.',
    priceFrom: 12,
    relatedSlugs: ['literature-reviews', 'dissertations', 'essays'],
    meta: {
      title: 'Research Paper Writing Service from $12/Page | EssayManiacs',
      description: 'Custom research papers by subject specialists. Any level, any citation style. Grade or money back. From $12/page.',
    },
  },
  {
    slug: 'dissertations',
    navLabel: 'Dissertations & Theses',
    icon: 'graduation-cap',
    title: 'Dissertation & Thesis Writing Service',
    hero: {
      headline: 'Dissertation Support from Proposal to Final Chapter',
      sub: 'End-to-end dissertation help: research proposal, literature review, methodology, data analysis, and final editing. Chapter by chapter so you stay in control.',
    },
    includes: [
      'Chapter-by-chapter delivery with supervisor feedback integration',
      'Research proposal and literature review',
      'Methodology design and data analysis chapters',
      'Extended revision window (14 days)',
      'PhD-qualified writers for doctoral work',
    ],
    delivers: [
      'Full dissertation or individual chapters as needed',
      'Properly formatted methodology chapter with rationale',
      'Data analysis with charts, tables, and written interpretation',
      'Comprehensive bibliography in required style',
    ],
    whoFor: "Master's and PhD students needing structured dissertation help for a single chapter, the full document, or last-minute editing before submission.",
    priceFrom: 25,
    relatedSlugs: ['literature-reviews', 'research-papers', 'data-analysis'],
    meta: {
      title: 'Dissertation Writing Service | EssayManiacs',
      description: "Expert dissertation writing from proposal to final chapter. Master's and PhD level. Grade or money back. From $25/page.",
    },
  },
  {
    slug: 'term-papers',
    navLabel: 'Term Papers',
    icon: 'book-open',
    title: 'Term Paper Writing Service',
    hero: {
      headline: 'Term Papers That Deliver at End-of-Semester',
      sub: 'A well-researched, thoroughly argued term paper submitted on time, covering any subject from economics to literature.',
    },
    includes: [
      'Full-semester research and writing support',
      'Any subject: STEM, business, humanities, social sciences',
      'Proper academic formatting and citation',
      'Free unlimited revisions',
    ],
    delivers: [
      'Complete term paper to your exact brief',
      'Properly structured argument with evidence',
      'Reference list in required citation style',
      'Free plagiarism report',
    ],
    whoFor: 'Students facing an end-of-semester term paper who need reliable, well-researched writing on any subject at undergraduate or graduate level.',
    priceFrom: 12,
    relatedSlugs: ['research-papers', 'essays', 'coursework'],
    meta: {
      title: 'Term Paper Writing Service from $12/Page | EssayManiacs',
      description: 'Custom term papers across every subject. Well-researched, properly cited, on time. From $12/page.',
    },
  },
  {
    slug: 'case-studies',
    navLabel: 'Case Studies',
    icon: 'briefcase',
    title: 'Case Study Writing Service',
    hero: {
      headline: 'Case Studies That Analyse, Not Just Describe',
      sub: 'Business, law, nursing, and social science case studies with structured problem-solution-evaluation arguments backed by real evidence.',
    },
    includes: [
      'Business, law, nursing, and social science case studies',
      'Problem-solution-evaluation structure',
      'Real-world source and case law integration',
      'Harvard or APA formatting included',
    ],
    delivers: [
      'Executive summary if required',
      'Clear problem identification and root cause analysis',
      'Evidence-backed solution evaluation',
      'Actionable recommendations and conclusion',
    ],
    whoFor: 'Business school, law, nursing, and social science students needing a structured, evidence-backed analysis of a real-world scenario.',
    priceFrom: 15,
    relatedSlugs: ['essays', 'research-papers', 'coursework'],
    meta: {
      title: 'Case Study Writing Service | EssayManiacs',
      description: 'Expert case study writing for business, law, and social sciences. Structured, evidence-backed. From $10/page.',
    },
  },
  {
    slug: 'coursework',
    navLabel: 'Coursework & Assignments',
    icon: 'clipboard-list',
    title: 'Coursework & Assignment Help',
    hero: {
      headline: 'Coursework Help That Keeps Up With Your Module',
      sub: 'Regular assignments, problem sets, and weekly coursework handled reliably by the same writer who knows your course.',
    },
    includes: [
      'Recurring order discounts for regular customers',
      'Same writer assigned across your modules',
      'Subject specialists for each discipline',
      'Short and long assignments accepted',
    ],
    delivers: [
      'Completed assignment to your exact brief',
      'Properly structured and referenced work',
      'Formatted to your module requirements',
    ],
    whoFor: 'Students with a heavy coursework load needing reliable, on-time help with weekly or monthly assignments across one or more modules.',
    priceFrom: 10,
    relatedSlugs: ['essays', 'research-papers', 'term-papers'],
    meta: {
      title: 'Coursework & Assignment Help from $10/Page | EssayManiacs',
      description: 'Reliable coursework and assignment help from subject specialists. Recurring discounts. From $10/page.',
    },
  },
  {
    slug: 'argumentative-essays',
    navLabel: 'Argumentative Essays',
    icon: 'scale',
    title: 'Argumentative Essay Writing Service',
    hero: {
      headline: 'Argumentative Essays That Win the Argument',
      sub: 'A clear thesis, solid evidence, anticipated counterarguments, and a conclusion that lands. Written by someone who actually enjoys arguing a point.',
    },
    includes: [
      'Clear, arguable thesis statement developed upfront',
      'Evidence from credible peer-reviewed and primary sources',
      'Counterargument acknowledgement and rebuttal',
      'Logical claim-evidence-warrant-rebuttal structure',
    ],
    delivers: [
      'Strong introduction with a debatable thesis',
      'Body paragraphs each developing one main claim',
      'Counterargument section with effective rebuttal',
      'Persuasive conclusion that reinforces the thesis',
    ],
    whoFor: 'Students who need a tightly structured, persuasive argumentative essay at any level, on any topic, in any citation style.',
    priceFrom: 10,
    relatedSlugs: ['essays', 'research-papers', 'term-papers'],
    meta: {
      title: 'Argumentative Essay Writing Service from $10/Page | EssayManiacs',
      description: 'Custom argumentative essays with a strong thesis and solid evidence. Any level, any topic. From $10/page.',
    },
  },
  {
    slug: 'admission-essays',
    navLabel: 'Admission Essays',
    icon: 'door-open',
    title: 'College Admission Essay Writing Service',
    hero: {
      headline: 'Admission Essays That Get You in the Room',
      sub: 'Your personal statement determines whether you get an interview. We write it like it matters, because it does.',
    },
    includes: [
      'College and university personal statements',
      'Why this school / why this programme essays',
      'Scholarship and grant application essays',
      'Activity and supplemental essays',
      'Unlimited revisions until submission',
    ],
    delivers: [
      'A personal statement tailored to the specific school and programme',
      'A genuine, specific narrative beyond generic openers',
      'Aligned to the institution\'s stated values and mission',
      'Within the required word count',
    ],
    whoFor: 'Students applying to college, graduate school, law school, medical school, or MBA programmes who need a compelling, tailored personal statement.',
    priceFrom: 15,
    relatedSlugs: ['scholarship-essays', 'personal-statements', 'essays'],
    meta: {
      title: 'Admission Essay Writing Service | EssayManiacs',
      description: 'Custom college and graduate school admission essays. Tailored to each school. From $10/page.',
    },
  },
  {
    slug: 'scholarship-essays',
    navLabel: 'Scholarship Essays',
    icon: 'award',
    title: 'Scholarship Essay Writing Service',
    hero: {
      headline: 'Scholarship Essays That Stand Out in a 2,000-Application Pool',
      sub: 'A scholarship essay does everything an admission essay does, in fewer words, with a financial argument. We write them well.',
    },
    includes: [
      'Any scholarship essay prompt: leadership, community, diversity, merit',
      'Tight word-count discipline',
      'Specific narrative aligned to the funder\'s values',
      'Unlimited revisions',
    ],
    delivers: [
      'An essay directly addressing the prompt',
      'Concrete, specific evidence of stated qualities',
      'A memorable closing that reinforces the key argument',
      'Properly within the required word count',
    ],
    whoFor: 'Students applying for merit, need-based, athletic, or identity-based scholarships who need a compelling essay that makes the case clearly.',
    priceFrom: 15,
    relatedSlugs: ['admission-essays', 'personal-statements', 'essays'],
    meta: {
      title: 'Scholarship Essay Writing Service | EssayManiacs',
      description: 'Custom scholarship essays for any prompt. Stand out from the crowd. From $10/page.',
    },
  },
  {
    slug: 'personal-statements',
    navLabel: 'Personal Statements',
    icon: 'user-pen',
    title: 'Personal Statement Writing Service',
    hero: {
      headline: 'Personal Statements That Sound Like You at Your Best',
      sub: "A personal statement should be genuinely personal. We write it in your voice, built around your story, tailored to the specific programme.",
    },
    includes: [
      'Personal statements for any application: undergraduate, graduate, professional',
      'Your story, your voice, no templates',
      'Aligned to specific school or programme values',
      'Unlimited revisions',
    ],
    delivers: [
      'A compelling opening that hooks the reader',
      'A coherent narrative connecting past, present, and future',
      'Specific evidence of stated qualities and ambitions',
      'A closing that reinforces your fit for the programme',
    ],
    whoFor: 'Students and professionals applying to undergraduate, graduate, law, medical, MBA, and other competitive programmes.',
    priceFrom: 15,
    relatedSlugs: ['admission-essays', 'scholarship-essays', 'essays'],
    meta: {
      title: 'Personal Statement Writing Service | EssayManiacs',
      description: 'Custom personal statements for any application. Written in your voice, tailored to each school. From $10/page.',
    },
  },
  {
    slug: 'literature-reviews',
    navLabel: 'Literature Reviews',
    icon: 'search',
    title: 'Literature Review Writing Service',
    hero: {
      headline: 'Literature Reviews That Synthesise, Not Just Summarise',
      sub: 'Systematic, narrative, and scoping reviews with gap identification, critical synthesis, and a documented search strategy.',
    },
    includes: [
      'Systematic, narrative, or scoping review formats',
      'PRISMA flow diagram available',
      'Documented database search strategy',
      'Critical gap identification',
    ],
    delivers: [
      'Themed synthesis of the existing literature',
      'Critical evaluation of sources',
      'Research gap identification',
      'Full reference list in required style',
    ],
    whoFor: 'Dissertation and research students needing a rigorous review of existing literature with gap identification for their research rationale.',
    priceFrom: 18,
    relatedSlugs: ['dissertations', 'research-papers', 'annotated-bibliographies'],
    meta: {
      title: 'Literature Review Writing Service from $18/Page | EssayManiacs',
      description: 'Expert literature reviews: systematic, narrative, or scoping. Gap identification included. From $18/page.',
    },
  },
  {
    slug: 'annotated-bibliographies',
    navLabel: 'Annotated Bibliographies',
    icon: 'list',
    title: 'Annotated Bibliography Writing Service',
    hero: {
      headline: 'Annotated Bibliographies Done Properly',
      sub: 'Each source evaluated for relevance, credibility, and contribution to your argument. Not just summarised.',
    },
    includes: [
      'Any citation style: APA, MLA, Chicago, Harvard',
      'Critical evaluation of each source, not just summary',
      'Relevance and credibility assessment',
      'Formatted correctly to your style guide',
    ],
    delivers: [
      'Full citation for each source in required style',
      'Annotation: summary, evaluation, and relevance to your research',
      'Organised alphabetically or thematically as required',
    ],
    whoFor: 'Students who need a properly annotated bibliography for a research project, dissertation, or standalone assignment in any field.',
    priceFrom: 12,
    relatedSlugs: ['literature-reviews', 'research-papers', 'essays'],
    meta: {
      title: 'Annotated Bibliography Writing Service | EssayManiacs',
      description: 'Properly annotated bibliographies in any citation style. Critical evaluation, not just summary. From $12/page.',
    },
  },
  {
    slug: 'book-reports',
    navLabel: 'Book Reports & Reviews',
    icon: 'book-marked',
    title: 'Book Report & Book Review Writing Service',
    hero: {
      headline: 'Book Reports That Go Beyond the Plot Summary',
      sub: 'Critical analysis of theme, argument, structure, and significance, written by someone who has actually read the book and thought about it.',
    },
    includes: [
      'Summary, analysis, and critical evaluation',
      'Theme and argument analysis',
      'Contextual significance and reception',
      'Any citation style',
    ],
    delivers: [
      'Introduction with book context and thesis',
      'Summary sufficient to show comprehension',
      'Critical analysis of themes, structure, and argument',
      'Evaluative conclusion with your stance justified',
    ],
    whoFor: 'Students who need a well-structured book report or critical review for any literary, academic, or professional text at any level.',
    priceFrom: 10,
    relatedSlugs: ['essays', 'literature-reviews', 'coursework'],
    meta: {
      title: 'Book Report & Review Writing Service | EssayManiacs',
      description: 'Critical book reports and reviews. Beyond summary, real analysis. From $10/page.',
    },
  },
  {
    slug: 'lab-reports',
    navLabel: 'Lab Reports',
    icon: 'flask-conical',
    title: 'Lab Report Writing Service',
    hero: {
      headline: 'Lab Reports With Every Section Done Right',
      sub: 'Introduction, method, results, discussion, conclusion, with correct scientific notation, graph formatting, and statistical analysis.',
    },
    includes: [
      'All sections: intro, method, results, discussion, conclusion',
      'Correct scientific notation and units',
      'Graph and table formatting',
      'Statistical analysis where needed',
    ],
    delivers: [
      'Complete lab report to your brief',
      'Formatted figures and data tables',
      'Discussion that interprets results against hypothesis',
      'Bibliography in required style',
    ],
    whoFor: 'Biology, chemistry, physics, and engineering students who need a properly structured report presenting and interpreting experimental data.',
    priceFrom: 15,
    relatedSlugs: ['data-analysis', 'research-papers', 'coursework'],
    meta: {
      title: 'Lab Report Writing Service | EssayManiacs',
      description: 'Properly structured lab reports for biology, chemistry, physics, and engineering. From $10/page.',
    },
  },
  {
    slug: 'data-analysis',
    navLabel: 'Data Analysis',
    icon: 'bar-chart-3',
    title: 'Data Analysis & Statistics Help',
    hero: {
      headline: 'Data Analysis Done Right, With the Write-Up',
      sub: 'SPSS, R, Python, or Excel, with interpretation, charts, and methodology chapter support.',
    },
    includes: [
      'SPSS, R, Python, and Excel analysis',
      'Charts, tables, and data visualisations',
      'Full written interpretation of results',
      'Methodology chapter support',
    ],
    delivers: [
      'Cleaned and analysed dataset',
      'Descriptive and inferential statistics',
      'Charts and tables formatted for your document',
      'Written results section with interpretation',
    ],
    whoFor: 'Students in business, social sciences, healthcare, and STEM needing quantitative or qualitative data analysis with a written results section.',
    priceFrom: 20,
    relatedSlugs: ['dissertations', 'research-papers', 'lab-reports'],
    meta: {
      title: 'Data Analysis & Statistics Help | EssayManiacs',
      description: 'Expert data analysis with full written interpretation. SPSS, R, Python, Excel. From $20/page.',
    },
  },
  {
    slug: 'reflective-essays',
    navLabel: 'Reflective Essays',
    icon: 'sparkles',
    title: 'Reflective Essay Writing Service',
    hero: {
      headline: 'Reflective Essays That Actually Reflect',
      sub: 'Gibbs, Kolb, Schoen, and other reflective frameworks, written in a genuine first-person voice that still meets academic rigour.',
    },
    includes: [
      'Gibbs, Kolb, Schoen, and other reflective frameworks',
      'Healthcare, education, business, and social work reflection',
      'First-person, authentic academic voice',
      'Academic rigour without losing the personal element',
    ],
    delivers: [
      'Description of the experience or situation',
      'Critical reflection against a recognised framework',
      'Analysis of what was learned and how it will change practice',
      'Conclusion with forward-looking commitment',
    ],
    whoFor: 'Students in nursing, social work, education, business, and humanities who need a reflective essay that meets criteria without sounding generic.',
    priceFrom: 12,
    relatedSlugs: ['essays', 'personal-statements', 'coursework'],
    meta: {
      title: 'Reflective Essay Writing Service | EssayManiacs',
      description: 'Reflective essays using Gibbs, Kolb, and other frameworks. Authentic, personal, academically rigorous. From $12/page.',
    },
  },
  {
    slug: 'presentations',
    navLabel: 'Presentations',
    icon: 'layout',
    title: 'Presentation & Speech Writing Service',
    hero: {
      headline: 'Presentations That Land on Slides and in the Room',
      sub: 'Academic and professional PowerPoint presentations with speaker notes, or full speech scripts timed to your delivery slot.',
    },
    includes: [
      'Slide content and logical structure',
      'Speaker notes for every slide',
      'Timed to your presentation slot',
      'Bibliography slide if required',
    ],
    delivers: [
      'Slide-by-slide content plan',
      'Speaker notes or full delivery script',
      'Clear argument flow and transitions',
      'Reference slide in required citation style',
    ],
    whoFor: 'Students preparing for seminar presentations, viva presentations, or professional pitches who need structured content and delivery guidance.',
    priceFrom: 15,
    relatedSlugs: ['essays', 'research-papers', 'case-studies'],
    meta: {
      title: 'Presentation Writing Service | EssayManiacs',
      description: 'Academic and professional presentations with speaker notes. Timed to your slot. From $10/page.',
    },
  },
  {
    slug: 'proofreading',
    navLabel: 'Proofreading & Editing',
    icon: 'check-check',
    title: 'Proofreading & Editing Service',
    hero: {
      headline: 'Proofreading That Fixes the Paper, Not Just the Typos',
      sub: 'Grammar and punctuation corrected, plus argument clarity, flow, structure, and citation accuracy checked.',
    },
    includes: [
      'Grammar, punctuation, and spelling correction',
      'Argument clarity and flow editing',
      'Citation accuracy check: APA, MLA, Chicago, Harvard',
      'Structure and coherence review',
    ],
    delivers: [
      'Corrected document with tracked changes',
      'Inline comments on argument or structural issues',
      'A clean final version ready for submission',
    ],
    whoFor: 'Students who have written their own paper and need a qualified editor to check language, structure, argument, and citations before submission.',
    priceFrom: 5,
    relatedSlugs: ['essays', 'dissertations', 'research-papers'],
    meta: {
      title: 'Proofreading & Editing Service from $5/Page | EssayManiacs',
      description: 'Expert proofreading and editing: grammar, structure, argument, citations. Tracked changes. From $5/page.',
    },
  },
  {
    slug: 'creative-writing',
    navLabel: 'Creative Writing',
    icon: 'pen-square',
    title: 'Creative Writing Service',
    hero: {
      headline: 'Creative Writing With Actual Craft Behind It',
      sub: 'Short stories, narrative essays, personal essays, creative non-fiction, and poetry, written by writers who care about the work.',
    },
    includes: [
      'Short stories, personal narratives, creative non-fiction',
      'Poetry in any form or free verse',
      'Any genre: literary, genre fiction, creative non-fiction',
      'Written to your brief, word count, and tone',
    ],
    delivers: [
      'A complete creative piece to your specification',
      'Consistent voice and style throughout',
      'Proper craft elements: scene, character, voice, tension',
    ],
    whoFor: 'Students in creative writing courses, literature programmes, or humanities classes who need a polished creative piece that demonstrates genuine craft.',
    priceFrom: 12,
    relatedSlugs: ['essays', 'reflective-essays', 'personal-statements'],
    meta: {
      title: 'Creative Writing Service | EssayManiacs',
      description: 'Custom creative writing: short stories, narratives, poetry. Written with craft. From $12/page.',
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
export interface CmsServiceSummary {
  id: number
  title: string
  slug: string
  service_category?: { name: string; slug: string } | null
  pricing_from?: string | null
  turnaround_hours_fastest?: number | null
}

export function useCmsServiceList() {
  const { data } = useFetch<{ items: CmsServiceSummary[] }>('/api/v2/pages/', {
    key: 'cms-service-list',
    query: {
      type: 'cms_service_pages.ServicePage',
      live: true,
      order: 'title',
      fields: 'title,slug,service_category,pricing_from,turnaround_hours_fastest',
      limit: 50,
    },
    default: () => ({ items: [] }),
  })

  const staticServices = services

  const merged = computed(() => {
    const cmsItems = data.value?.items ?? []
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
        icon: local?.icon ?? 'pen-line',
        heroSub: local?.hero.sub ?? '',
        priceFrom: page.pricing_from ? parseFloat(page.pricing_from) : (local?.priceFrom ?? 10),
        category: page.service_category?.name ?? null,
      }
    })
  })

  return merged
}
