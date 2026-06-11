<script setup lang="ts">
import { ArrowRight, CheckCircle2 } from '@lucide/vue'
import ServiceBlocks from '~/components/cms/ServiceBlocks.vue'
import PricingCalculator from '~/components/ui/PricingCalculator.vue'
import type { CmsServicePage } from '~/types/cms'

const app    = useAppUrl()
const route  = useRoute()
const slug   = route.params.slug as string

const { data: cmsService } = await useAsyncData(
  `cms-service-${slug}`,
  () => fetchCmsServicePage(slug),
  { default: () => null },
)

type ServiceView = {
  title: string
  tagline: string
  description: string
  price: number
  metaTitle: string
  metaDesc: string
  intro: string
  bullets: string[]
  process: { title: string; desc: string }[]
  faqs: { q: string; a: string }[]
  related: string[]
  ctaText?: string
  ctaUrl?: string
}

// ── Service definitions (CMS-ready: can swap to Wagtail API fetch) ────────────
const SERVICE_MAP: Record<string, ServiceView> = {
  'essay-writing': {
    title: 'Essay Writing Service',
    tagline: 'Any type. Any subject. Any level.',
    description: 'Professional essay writing by verified human experts. Argumentative, analytical, descriptive, compare-and-contrast — all formats, all subjects.',
    price: 13,
    metaTitle: 'Essay Writing Service from $13/Page | GradeCrest',
    metaDesc: 'Get a custom essay written by a human expert from $13/page. Argumentative, analytical, descriptive essays. Grade or money back. Zero AI content.',
    intro: 'Whether you need a 500-word argumentative essay or a 5,000-word analytical piece, GradeCrest connects you with a subject-specialist writer who understands your assignment and your institution\'s expectations.',
    bullets: [
      'All essay types: argumentative, analytical, descriptive, reflective, compare-and-contrast',
      'Matched to your exact subject — over 100 disciplines covered',
      'Correct referencing style (APA, MLA, Chicago, Harvard, Turabian)',
      'Full plagiarism report included at no extra cost',
      'AI-detection certificate included on request',
      'Unlimited revisions within the revision window',
    ],
    process: [
      { title: 'Fill in your brief',     desc: 'Topic, essay type, academic level, word count, deadline, and any specific instructions or reading materials.' },
      { title: 'Get matched',            desc: 'We assign a writer with relevant subject expertise. You can message them directly before writing begins.' },
      { title: 'Track progress',         desc: 'Receive updates and communicate with your writer in real time through our messaging system.' },
      { title: 'Review & request edits', desc: 'Download your essay and request any changes for free within the revision window.' },
    ],
    faqs: [
      { q: 'Can you write essays on any topic?', a: 'Yes. We cover 100+ academic subjects from nursing to philosophy to engineering. If you can name the topic, we have a writer for it.' },
      { q: 'Will my essay be plagiarism-free?',  a: 'Every essay is written from scratch and checked against plagiarism databases. Your report is included free of charge.' },
      { q: 'Will my essay contain AI content?',  a: 'No. Every essay is written by a verified human expert. We offer a free AI-detection certificate on request.' },
      { q: 'What if I need changes?',            a: 'Unlimited free revisions within 14 days of delivery. If we still cannot meet your requirements, you receive a full refund.' },
    ],
    related: ['research-papers', 'term-papers', 'literature-review'],
  },
  'research-papers': {
    title: 'Research Paper Writing Service',
    tagline: 'Original. Citation-rich. Properly structured.',
    description: 'Custom research papers written by subject experts from $15/page. Full methodology, proper citations, and plagiarism-free content.',
    price: 15,
    metaTitle: 'Research Paper Writing Service from $15/Page | GradeCrest',
    metaDesc: 'Custom research papers written by human experts. Full methodology, proper citations, plagiarism-free. From $15/page. Grade or money back.',
    intro: 'A well-structured research paper requires more than writing ability — it demands domain knowledge, sound methodology, and mastery of academic conventions. GradeCrest writers hold postgraduate degrees in your subject and have produced research at the level your assignment demands.',
    bullets: [
      'Original research papers written from scratch by subject specialists',
      'Correct citation format: APA, MLA, Chicago, Harvard, Vancouver',
      'Full methodology section with justified research design',
      'Literature review integrated into the paper',
      'Statistical analysis support (SPSS, R, Python) where required',
      'Full plagiarism and AI-detection reports included',
    ],
    process: [
      { title: 'Submit your requirements', desc: 'Topic, research question, methodology preferences, citation style, and any sources you require.' },
      { title: 'Writer matching',          desc: 'Matched with a writer holding a postgraduate degree in your subject.' },
      { title: 'Collaborative writing',    desc: 'Message your writer at any stage. Share feedback on early drafts if you need them.' },
      { title: 'Delivery & revisions',     desc: 'Receive your paper with all reports. Request free revisions until fully satisfied.' },
    ],
    faqs: [
      { q: 'Can you write a research paper in my subject?', a: 'Yes. We cover STEM, humanities, business, social sciences, health sciences, law, and 100+ other disciplines.' },
      { q: 'Do you provide sources and citations?',         a: 'Yes. Your writer will source appropriate peer-reviewed references and cite them correctly in your chosen style.' },
      { q: 'Can I see a draft before final delivery?',      a: 'Yes. You can request a progress update or partial draft from your writer at any time.' },
      { q: 'What if the paper does not meet my grade?',     a: 'We rewrite it free of charge. If still unsatisfied after revision, you receive a full refund.' },
    ],
    related: ['dissertations', 'literature-review', 'data-analysis'],
  },
  'dissertations': {
    title: 'Dissertation & Thesis Writing Service',
    tagline: 'Full support from proposal to final submission.',
    description: 'Expert dissertation and thesis support across all chapters, methodology, data analysis, and presentation. PhD and Master\'s level.',
    price: 22,
    metaTitle: "Dissertation Writing Service | Full Thesis Support | GradeCrest",
    metaDesc: "Expert dissertation support from proposal to final chapter. Master's and PhD level. Methodology, data analysis, literature review, discussion. Grade guaranteed.",
    intro: 'A dissertation is the most significant piece of academic writing most students ever produce. GradeCrest assigns PhD-qualified experts who have completed dissertations at the same level you\'re working at — so they understand the depth, rigour, and structure your committee expects.',
    bullets: [
      'Full dissertation support or individual chapters',
      'Proposal, literature review, methodology, findings, discussion, conclusion',
      'Quantitative, qualitative, and mixed-methods expertise',
      'Statistical analysis (SPSS, R, NVivo, Python)',
      'APA, Harvard, Chicago, Vancouver formatting',
      'Plagiarism report and AI certificate included',
      'Up to 30-day revision window for dissertations',
    ],
    process: [
      { title: 'Brief your project',   desc: 'Share your research question, methodology, existing work, and any supervisor feedback.' },
      { title: 'PhD-level matching',   desc: 'Assigned a writer with a doctoral degree in your field and dissertation experience.' },
      { title: 'Chapter-by-chapter',   desc: 'Work through chapters progressively. Review each before the next begins.' },
      { title: 'Final review',         desc: 'Full document delivered with plagiarism report. Request revisions at no extra cost.' },
    ],
    faqs: [
      { q: 'Can you help with just one chapter?',    a: 'Yes. You can order a single chapter, section, or the full dissertation — your choice.' },
      { q: 'How do I ensure the writer knows my field?', a: 'We match by discipline, methodology, and academic level. You can also review your writer\'s profile and message them before work begins.' },
      { q: 'Will the methodology be original?',      a: 'Yes. Your writer designs a methodology appropriate to your research question, not a recycled template.' },
      { q: 'What is the revision period for dissertations?', a: 'Up to 30 days from delivery. We revise until the work meets your specifications.' },
    ],
    related: ['research-papers', 'data-analysis', 'literature-review'],
  },
  'nursing-essays': {
    title: 'Nursing Essay Writing Service',
    tagline: 'Written by registered nursing professionals.',
    description: 'SOAP notes, care plans, EBP papers, pharmacology, and clinical case studies written by nurses with active clinical experience.',
    price: 15,
    metaTitle: 'Nursing Essay Writing Service | SOAP Notes, Care Plans | GradeCrest',
    metaDesc: 'Nursing essays, SOAP notes, care plans, and EBP papers written by registered nurses. From $15/page. NMC, ANA, APA compliant. Grade or money back.',
    intro: 'Nursing assignments demand clinical knowledge that generalist writers simply do not have. Our nursing writers are registered nurses and nursing academics — they understand patient care frameworks, clinical terminology, evidence-based practice, and the expectations of nursing faculties.',
    bullets: [
      'SOAP notes, DAR notes, and clinical documentation',
      'Care plans with nursing diagnoses and interventions',
      'Evidence-based practice (EBP) and PICO papers',
      'Pharmacology assignments and drug calculations',
      'Case studies with clinical reasoning frameworks',
      'NMC, ANA, NANDA-aligned content',
      'APA 7th edition formatting as standard',
    ],
    process: [
      { title: 'Describe your patient scenario',  desc: 'Share the clinical scenario, patient data, assessment guidelines, and rubric.' },
      { title: 'Matched to a nursing expert',     desc: 'Assigned to a writer with active nursing credentials in your specific area.' },
      { title: 'Clinical-quality writing',         desc: 'Evidence-based content with appropriate clinical reasoning and current guidelines.' },
      { title: 'Review & revisions',              desc: 'Download your paper and request changes within the revision window.' },
    ],
    faqs: [
      { q: 'Are your nursing writers actually nurses?', a: 'Yes. Our nursing writers hold nursing degrees and most have active clinical experience. Credentials are verified before assignment.' },
      { q: 'Can you write SOAP notes?',                a: 'Yes — SOAP, DAR, SBAR, and other clinical documentation formats.' },
      { q: 'Do you cover BSN, MSN, and DNP levels?',   a: 'Yes. From undergraduate BSN through doctoral DNP and PhD nursing programmes.' },
      { q: 'Will the content be evidence-based?',       a: 'Yes. All claims are supported by current peer-reviewed sources and referenced in APA 7th edition.' },
    ],
    related: ['coursework', 'dissertations', 'research-papers'],
  },
  'editing-proofreading': {
    title: 'Editing & Proofreading Service',
    tagline: 'Professional academic editing by expert editors.',
    description: 'Grammar, clarity, structure, flow, referencing, and formatting corrected by professional academic editors. From $8/page.',
    price: 8,
    metaTitle: 'Academic Editing & Proofreading Service | GradeCrest',
    metaDesc: 'Professional academic editing and proofreading from $8/page. Grammar, structure, flow, citations, and formatting. Returned within your deadline.',
    intro: 'Even excellent research can be let down by unclear writing, grammatical errors, or inconsistent formatting. Our editors are academic writing specialists — they improve your work without changing your ideas or voice.',
    bullets: [
      'Grammar, spelling, punctuation, and syntax correction',
      'Sentence clarity, flow, and paragraph structure',
      'Academic tone and register consistency',
      'Citation checking and reference list formatting',
      'Formatting to APA, MLA, Chicago, Harvard, or your institution\'s style guide',
      'Track-changes version provided so you can see every edit',
    ],
    process: [
      { title: 'Upload your document',    desc: 'Share your draft along with your citation style, word count, and any specific concerns.' },
      { title: 'Expert editor assigned',  desc: 'An editor with expertise in your subject area reviews your work.' },
      { title: 'Comprehensive edit',      desc: 'Line-by-line editing with tracked changes and optional margin comments.' },
      { title: 'Return with clean copy',  desc: 'Receive both the tracked-changes version and the clean final copy.' },
    ],
    faqs: [
      { q: 'Will my ideas and arguments be changed?', a: 'No. Editing improves how your ideas are expressed — it never changes what you are arguing.' },
      { q: 'Do you check citations and references?',  a: 'Yes. We verify citation format consistency and reference list accuracy in your chosen style.' },
      { q: 'How fast can you edit a document?',       a: 'Standard turnaround is 3–5 days. Rush editing from 24 hours is available at a surcharge.' },
      { q: 'What file formats do you accept?',        a: 'DOCX, DOC, PDF, RTF, and Google Docs (shared link). DOCX is preferred for track changes.' },
    ],
    related: ['essay-writing', 'dissertations', 'research-papers'],
  },
  'admission-essays': {
    title: 'Admission Essay Writing Service',
    tagline: 'Stand out from thousands of applicants.',
    description: 'Personal statements, college essays, and graduate school applications written by admissions specialists who know what committees look for.',
    price: 15,
    metaTitle: 'Admission Essay Writing Service | Personal Statement Help | GradeCrest',
    metaDesc: 'Expert admission essay and personal statement writing. College, university, and graduate school applications. Stand out with a compelling, authentic narrative.',
    intro: 'Admission committees read thousands of essays. A great personal statement is specific, authentic, and shows — not tells — who you are and why you belong at that institution. Our admissions writers have worked at top universities and know exactly what makes an application stand out.',
    bullets: [
      'College and university personal statements',
      'Graduate school and MBA admissions essays',
      'Medical, law, and nursing school applications',
      'Scholarship essays and grant applications',
      'Statement of purpose (SOP)',
      'Letter of intent (LOI)',
      'Completely original — built around your story and achievements',
    ],
    process: [
      { title: 'Share your profile',     desc: 'Tell us about yourself, your achievements, and the programme you\'re applying to.' },
      { title: 'Writer matching',         desc: 'Matched with a writer who has experience with your target programme type.' },
      { title: 'Draft + feedback loop',  desc: 'Receive a draft and work through revisions until you\'re completely happy.' },
      { title: 'Final essay delivered',  desc: 'Authentic, specific, and compelling — ready to submit.' },
    ],
    faqs: [
      { q: 'Will the essay sound like me?',           a: 'Yes. We build the essay around your experiences and voice. You provide the story; we craft the narrative.' },
      { q: 'Can you help with multiple applications?',a: 'Yes. We can write multiple versions tailored to different institutions.' },
      { q: 'Do you handle graduate school SOPs?',     a: 'Yes — statement of purpose, personal statement, letter of intent, and research proposals.' },
      { q: 'Is the essay plagiarism-free?',           a: 'Every essay is written from scratch and is unique to you. It is never resold or reused.' },
    ],
    related: ['essay-writing', 'coursework', 'editing-proofreading'],
  },
  'term-papers': {
    title: 'Term Paper Writing Service',
    tagline: 'Well-argued semester papers, delivered on time.',
    description: 'Custom term papers written by subject experts from $14/page. Structured arguments, proper citations, and on-time delivery.',
    price: 14,
    metaTitle: 'Term Paper Writing Service from $14/Page | GradeCrest',
    metaDesc: 'Custom term papers written by human experts. Well-structured arguments, full citations, on-time delivery. From $14/page. Grade or money back.',
    intro: 'A term paper is a substantial piece of writing that contributes to your module grade — it needs a clear thesis, well-organised arguments, and proper academic sourcing. GradeCrest writers hold postgraduate degrees in your subject and know exactly what your faculty expects.',
    bullets: [
      'Original term papers written from scratch by subject specialists',
      'Clear thesis with structured argumentation throughout',
      'Peer-reviewed sources researched and cited correctly',
      'APA, MLA, Chicago, Harvard, or any other citation style',
      'Full plagiarism report included at no extra cost',
      'Unlimited free revisions within the revision window',
    ],
    process: [
      { title: 'Submit your requirements', desc: 'Topic or question, academic level, citation style, deadline, and any module guidelines or rubric.' },
      { title: 'Writer matching',           desc: 'Assigned to a writer with postgraduate expertise in your subject.' },
      { title: 'Research and writing',      desc: 'Your writer builds the argument from scratch with properly sourced evidence.' },
      { title: 'Review and revisions',      desc: 'Download your paper and request any changes free of charge within the revision window.' },
    ],
    faqs: [
      { q: 'Can you write a term paper on any subject?',  a: 'Yes. We cover 100+ academic subjects from STEM to humanities, business, and social sciences.' },
      { q: 'Will you follow my professor\'s instructions?', a: 'Yes. Share your rubric, marking criteria, or any specific requirements and your writer will follow them precisely.' },
      { q: 'Will the paper be plagiarism-free?',          a: 'Every paper is written from scratch and comes with a plagiarism report at no extra charge.' },
      { q: 'What if the grade requirement is not met?',   a: 'We rewrite it free of charge. If still unsatisfied after revision, you receive a full refund.' },
    ],
    related: ['essay-writing', 'research-papers', 'coursework'],
  },
  'case-studies': {
    title: 'Case Study Writing Service',
    tagline: 'In-depth analysis with evidence-backed conclusions.',
    description: 'Custom academic case studies written by subject experts. Deep analysis, structured argumentation, and properly sourced evidence from $15/page.',
    price: 15,
    metaTitle: 'Case Study Writing Service from $15/Page | GradeCrest',
    metaDesc: 'Expert case study writing for business, law, nursing, and any subject. In-depth analysis, structured arguments, plagiarism-free. From $15/page.',
    intro: 'A strong case study requires more than summarising facts — it demands analytical depth, a clear framework, and the ability to draw credible conclusions from evidence. GradeCrest writers hold postgraduate qualifications and have hands-on experience with case analysis in their fields.',
    bullets: [
      'Business, law, nursing, psychology, and social science case studies',
      'Analysis structured around recognised academic frameworks',
      'Evidence-based conclusions with cited supporting sources',
      'SWOT, PESTLE, Porter\'s Five Forces, and other models applied correctly',
      'APA, Harvard, APA, Chicago, MLA formatting',
      'Plagiarism report included at no extra cost',
    ],
    process: [
      { title: 'Share the case details',    desc: 'The scenario, the analytical framework required, your subject, level, and any grading criteria.' },
      { title: 'Expert matched to subject', desc: 'Assigned to a writer with domain expertise relevant to your specific case.' },
      { title: 'Structured analysis',       desc: 'Your writer works through the case methodically, applying the right analytical framework.' },
      { title: 'Delivery and revisions',    desc: 'Receive your case study with plagiarism report. Free revisions within the revision window.' },
    ],
    faqs: [
      { q: 'Can you write business and law case studies?', a: 'Yes. We cover business, law, nursing, psychology, social science, and any other discipline.' },
      { q: 'Will you apply a specific framework?',        a: 'Yes — SWOT, PESTLE, Porter\'s Five Forces, legal case analysis, clinical frameworks, and others. Specify in your instructions.' },
      { q: 'Can I include specific source requirements?', a: 'Yes. Add required readings, textbooks, or databases to your instructions and your writer will incorporate them.' },
      { q: 'What if I need revisions?',                   a: 'Unlimited free revisions within 14 days of delivery. Full refund if requirements are not met.' },
    ],
    related: ['research-papers', 'essay-writing', 'dissertations'],
  },
  'coursework': {
    title: 'Coursework Help',
    tagline: 'Consistent support throughout your module.',
    description: 'Ongoing academic assignment support from a dedicated writer. Consistent quality and voice across every piece of coursework from $14/page.',
    price: 14,
    metaTitle: 'Coursework Help from $14/Page | Ongoing Assignment Support | GradeCrest',
    metaDesc: 'Expert coursework help for any module or subject. Dedicated writer, consistent quality across every assignment. From $14/page. Grade or money back.',
    intro: 'Coursework spans an entire module — and inconsistent support from different writers shows. GradeCrest lets you work with the same writer throughout your course, building familiarity with your subject, your voice, and your institution\'s expectations over time.',
    bullets: [
      'Same writer for every assignment across your module',
      'Consistent academic voice and argument style throughout',
      'Covers essays, reports, reflections, presentations, and more',
      'Any subject, undergraduate through postgraduate',
      'All citation styles formatted correctly',
      'Plagiarism report on every submission',
    ],
    process: [
      { title: 'Brief your module',         desc: 'Share your module handbook, assignment brief, academic level, and any past feedback.' },
      { title: 'Your dedicated writer',     desc: 'Matched with a writer who has subject expertise and stays with you for the module.' },
      { title: 'Assignment by assignment',  desc: 'Submit each piece as it comes up. Your writer builds on prior work and feedback.' },
      { title: 'Review and iterate',        desc: 'Receive each assignment with a plagiarism report. Request revisions at no extra cost.' },
    ],
    faqs: [
      { q: 'Can I keep the same writer for my whole course?', a: 'Yes. We strongly recommend this for coursework — request your writer by name when placing each new order.' },
      { q: 'What types of coursework do you cover?',          a: 'Essays, reports, reflective journals, lab reports, portfolios, presentations, and more.' },
      { q: 'What if I have feedback from my tutor to incorporate?', a: 'Share tutor feedback with your writer before the next assignment and they will adjust their approach accordingly.' },
      { q: 'Is the work plagiarism-free?',                    a: 'Yes. Every assignment is written from scratch with a full plagiarism report included.' },
    ],
    related: ['essay-writing', 'term-papers', 'online-class-help'],
  },
  'literature-review': {
    title: 'Literature Review Writing Service',
    tagline: 'Comprehensive, critically synthesised scholarly reviews.',
    description: 'Academic literature reviews written by subject experts. Critically synthesised, thematically structured, and fully cited from $16/page.',
    price: 16,
    metaTitle: 'Literature Review Writing Service from $16/Page | GradeCrest',
    metaDesc: 'Expert literature reviews written by human academics. Critically synthesised, thematically structured, fully cited. From $16/page. Grade or money back.',
    intro: 'A literature review is not a summary — it is a critical synthesis of the field, identifying themes, debates, gaps, and methodological trends. Our writers hold postgraduate degrees and have conducted original research, giving them the depth to produce literature reviews that meet doctoral-level expectations.',
    bullets: [
      'Systematic, narrative, and integrative review formats',
      'Critical synthesis — not just description — of source material',
      'Thematic structure developed around your research question',
      'Appropriate primary and secondary sources identified and included',
      'PRISMA-compliant systematic reviews upon request',
      'APA, Harvard, Chicago, Vancouver, and all major citation styles',
      'Plagiarism report included at no extra cost',
    ],
    process: [
      { title: 'Define your scope',         desc: 'Share your research question or topic, required databases or sources, review type, and any existing material.' },
      { title: 'PhD-level writer matched',  desc: 'Assigned to a researcher with expertise in your specific field and methodology.' },
      { title: 'Source identification',     desc: 'Your writer conducts a systematic search and selects the most relevant and credible literature.' },
      { title: 'Critical synthesis',        desc: 'Sources are synthesised into a coherent narrative that positions your research within the field.' },
    ],
    faqs: [
      { q: 'Can you conduct the source search for me?',  a: 'Yes. Your writer identifies appropriate sources from databases such as PubMed, JSTOR, Scopus, and Google Scholar.' },
      { q: 'Can I supply my own list of sources?',        a: 'Yes. Add any required sources in your instructions and your writer will incorporate and synthesise them.' },
      { q: 'Do you write PRISMA-compliant reviews?',      a: 'Yes. Specify systematic review and PRISMA framework in your instructions.' },
      { q: 'What if I need a literature review as part of a larger dissertation?', a: 'Absolutely. We can write individual chapters or the full dissertation — your choice.' },
    ],
    related: ['dissertations', 'research-papers', 'data-analysis'],
  },
  'thesis-writing': {
    title: 'Thesis Writing Service',
    tagline: 'Graduate-level thesis support from proposal to submission.',
    description: 'Expert thesis writing support at Master\'s and PhD level. Proposal, all chapters, methodology, data analysis, and discussion from $22/page.',
    price: 22,
    metaTitle: "Thesis Writing Service | Master's & PhD Thesis Help | GradeCrest",
    metaDesc: "Expert thesis writing support at Master's and PhD level. Proposal through submission. Methodology, data, discussion. Grade guaranteed.",
    intro: 'A thesis is the most rigorous piece of academic writing in your programme. It requires original argumentation, sound methodology, and mastery of your discipline\'s scholarly conventions. GradeCrest assigns writers who hold the same qualification you\'re working towards — so they understand the standard from the inside.',
    bullets: [
      "Full thesis support or individual chapters — Master's and PhD",
      'Research proposal and research question development',
      'Literature review, theoretical framework, and methodology',
      'Data collection planning and analysis (SPSS, R, NVivo, Python)',
      'Findings, discussion, and conclusion chapters',
      'Abstract, acknowledgements, and reference list',
      'Up to 30-day revision window',
    ],
    process: [
      { title: 'Share your research',       desc: 'Your research question, field, methodology, existing work, and any supervisor feedback received.' },
      { title: 'Qualified writer matched',  desc: 'Assigned to a writer holding a degree at your level in your specific subject.' },
      { title: 'Progressive chapter work',  desc: 'Work chapter by chapter. Review and approve each section before the next begins.' },
      { title: 'Complete and refine',       desc: 'Full document delivered with plagiarism report. Extended revision window for thesis-level work.' },
    ],
    faqs: [
      { q: 'Can you help with just the methodology chapter?', a: 'Yes. You can order any individual chapter, section, or the full thesis.' },
      { q: 'How do you ensure the writer knows my field?',    a: 'We match by discipline, methodology type, and academic level. You can review your writer\'s credentials before work begins.' },
      { q: 'Will my supervisor see something generic?',       a: 'No. Every thesis is built around your specific research question, theoretical framework, and existing literature.' },
      { q: 'What is the revision period for a thesis?',       a: 'Up to 30 days from delivery. We revise until the work meets your specifications.' },
    ],
    related: ['dissertations', 'literature-review', 'data-analysis'],
  },
  'capstone-projects': {
    title: 'Capstone Project Writing Service',
    tagline: 'End-of-programme projects delivered with depth and precision.',
    description: 'Custom capstone project support from research and analysis through to presentation. Expert writers matched to your programme and institution from $22/page.',
    price: 22,
    metaTitle: 'Capstone Project Writing Service from $22/Page | GradeCrest',
    metaDesc: 'Expert capstone project support: research, analysis, and presentation. Undergraduate through postgraduate. Grade guaranteed. From $22/page.',
    intro: 'A capstone project is the defining piece of your programme — it synthesises everything you have learned and is assessed at the highest standard. GradeCrest assigns writers who understand capstone expectations at your level and in your discipline, delivering work that reflects genuine command of the subject.',
    bullets: [
      'Full capstone support or individual sections',
      'Research design, literature review, methodology, analysis, and discussion',
      'Quantitative, qualitative, and mixed-methods research',
      'Business, nursing, education, STEM, and all other disciplines',
      'Presentation and executive summary support included',
      'APA, Harvard, Chicago, and all major citation styles',
      'Plagiarism report and AI-detection certificate included',
    ],
    process: [
      { title: 'Brief your project',    desc: 'Your programme, discipline, research question or topic, required methodology, and any marking criteria or rubric.' },
      { title: 'Expert matched',        desc: 'Assigned to a writer with capstone experience in your specific field and academic level.' },
      { title: 'Research and writing',  desc: 'Your writer builds the project from your brief — research, analysis, structured writing, and accurate citation.' },
      { title: 'Review and refine',     desc: 'Receive your project with all reports. Free revisions within the extended revision window.' },
    ],
    faqs: [
      { q: 'Can you help with the full capstone or just part of it?', a: 'Either. We can handle the full project from proposal to final submission, or just the sections you need most help with.' },
      { q: 'Do you cover capstone presentations and posters?',        a: 'Yes. We can write your presentation script, speaker notes, executive summary, or project abstract alongside the written work.' },
      { q: 'How do you match the writer to my programme?',           a: 'We match by discipline, academic level, and research methodology type. You can review your writer\'s credentials before work begins.' },
      { q: 'What is the revision window for a capstone project?',    a: 'Up to 30 days from delivery. We revise until the work meets your requirements.' },
    ],
    related: ['dissertations', 'research-papers', 'data-analysis'],
  },
  'data-analysis': {
    title: 'Data Analysis Service',
    tagline: 'SPSS, R, Python, and Excel — results and written interpretation.',
    description: 'Professional academic data analysis by statisticians and researchers. Quantitative, qualitative, and mixed-methods. Results, charts, and written interpretation from $20/page.',
    price: 20,
    metaTitle: 'Data Analysis Service for Academic Research | SPSS, R, Python | GradeCrest',
    metaDesc: 'Academic data analysis by expert statisticians. SPSS, R, Python, Excel, NVivo. Quantitative and qualitative analysis with written interpretation. Grade guaranteed.',
    intro: 'Data analysis is the most technically demanding part of academic research — and errors in your methodology or interpretation can undermine an otherwise strong dissertation. Our analysts hold postgraduate degrees in statistics, research methods, or your specific subject, and work with the exact software your programme requires.',
    bullets: [
      'Quantitative: descriptive stats, regression, ANOVA, t-tests, chi-square, factor analysis',
      'Qualitative: thematic analysis, discourse analysis, content analysis (NVivo)',
      'Mixed-methods research designs',
      'SPSS, R, Python (pandas/scipy), Stata, and Excel',
      'Written interpretation of results in academic language',
      'Charts, tables, and figures formatted to your style guide',
      'Methodology section and results chapter written if required',
    ],
    process: [
      { title: 'Share your data and brief', desc: 'Your dataset, research questions, software preference, and what analysis you need performed.' },
      { title: 'Analyst matched',           desc: 'Assigned to an analyst with expertise in your methodology and the required software.' },
      { title: 'Analysis performed',        desc: 'Statistical tests run, results verified, and outputs formatted correctly.' },
      { title: 'Delivery with interpretation', desc: 'Receive analysis files plus written interpretation ready to paste into your dissertation.' },
    ],
    faqs: [
      { q: 'Can you analyse my existing dataset?',          a: 'Yes. Share your dataset (Excel, CSV, SPSS .sav, etc.) along with your research questions and methodology.' },
      { q: 'Do you provide the SPSS/R output files?',        a: 'Yes. You receive both the raw output files and a clean written interpretation of the results.' },
      { q: 'Can you help if I don\'t know which test to use?', a: 'Yes. Our analysts can recommend the appropriate statistical tests based on your research design and data type.' },
      { q: 'Do you cover qualitative methods?',              a: 'Yes — thematic analysis, content analysis, grounded theory coding, and NVivo-supported analysis.' },
    ],
    related: ['dissertations', 'research-papers', 'literature-review'],
  },
  'online-class-help': {
    title: 'Online Class Help',
    tagline: 'Consistent assignment completion throughout your online course.',
    description: 'Academic assignment support for fully online courses. Essays, quizzes, discussion boards, and module work completed by subject experts from $14/page.',
    price: 14,
    metaTitle: 'Online Class Help | Assignment Support for Online Courses | GradeCrest',
    metaDesc: 'Expert help with online course assignments. Essays, discussion posts, quizzes, and coursework completed by verified subject specialists. From $14/page.',
    intro: 'Fully online courses demand the same academic rigour as campus programmes — but without the in-person support structure. GradeCrest provides consistent, subject-expert help across your entire online module, so every submission reflects the quality your grade requires.',
    bullets: [
      'Essays, reports, and written assignments',
      'Discussion board posts and response threads',
      'Quiz and short-answer question support',
      'Weekly and module-long coursework',
      'Any LMS platform — Canvas, Blackboard, Moodle',
      'Any subject, any level, undergraduate through postgraduate',
      'Plagiarism report included on written work',
    ],
    process: [
      { title: 'Share your course details', desc: 'Your module, platform, assignment types, deadlines, and any syllabus or rubric documents.' },
      { title: 'Expert matched',            desc: 'Assigned to a writer with subject expertise relevant to your online course.' },
      { title: 'Ongoing support',           desc: 'Your writer handles assignments as they come due throughout the module.' },
      { title: 'Review each submission',    desc: 'Receive each assignment before the due date. Request revisions at no extra cost.' },
    ],
    faqs: [
      { q: 'Can you help with my entire online course?',  a: 'Yes. We can provide ongoing support throughout your module for every type of assignment.' },
      { q: 'Do you cover discussion board posts?',         a: 'Yes — initial discussion posts and response posts to peers.' },
      { q: 'What subjects do you cover?',                  a: 'All subjects offered in online programmes — nursing, business, education, IT, social sciences, psychology, and more.' },
      { q: 'Is the work plagiarism-free?',                 a: 'Yes. Every written submission is original and comes with a plagiarism report.' },
    ],
    related: ['coursework', 'homework-help', 'essay-writing'],
  },
  'homework-help': {
    title: 'Homework Help',
    tagline: 'Day-to-day assignment support across any subject.',
    description: 'Fast, expert homework help across any subject and level from $13/page. Same-day support available. Human-written, plagiarism-free.',
    price: 13,
    metaTitle: 'Homework Help from $13/Page | Any Subject, Any Level | GradeCrest',
    metaDesc: 'Expert homework help for any subject, any level. Same-day support available. Human-written, plagiarism-free. From $13/page. Grade or money back.',
    intro: 'Whether it is a single assignment due tomorrow or a weekly flow of tasks across a difficult module, GradeCrest connects you with a subject specialist who can handle the work to the standard your course demands.',
    bullets: [
      'Any assignment type: essays, reports, problems, short answers, reflections',
      'Any subject: STEM, humanities, business, nursing, law, and more',
      'Any level: high school, undergraduate, and postgraduate',
      'Same-day and 6-hour rush turnaround available',
      'Correct citation style and formatting included',
      'Plagiarism report on every written submission',
    ],
    process: [
      { title: 'Submit your assignment',    desc: 'Your subject, assignment type, academic level, deadline, and any instructions or rubric.' },
      { title: 'Expert matched quickly',    desc: 'Matched to a writer with subject expertise. Rush matching available for urgent deadlines.' },
      { title: 'Assignment completed',      desc: 'Your writer completes the work to your brief and academic standard.' },
      { title: 'Review and request edits',  desc: 'Download your completed assignment. Free revisions if anything needs adjusting.' },
    ],
    faqs: [
      { q: 'How fast can you complete homework?',          a: 'We offer turnarounds from 6 hours for short assignments. Complexity and length affect the minimum deadline.' },
      { q: 'Can you help with maths and STEM assignments?', a: 'Yes. We have specialists in mathematics, physics, chemistry, engineering, statistics, and computer science.' },
      { q: 'What if I only need help understanding, not a full answer?', a: 'We can provide worked examples, explanations, or model answers — whatever is most useful for your situation.' },
      { q: 'Is the work original?',                         a: 'Yes. Every answer is written specifically for your assignment and never reused.' },
    ],
    related: ['coursework', 'online-class-help', 'essay-writing'],
  },
}

// Fallback for slugs not explicitly defined
const DEFAULT_SERVICE = {
  title: 'Academic Writing Service',
  tagline: 'Expert help across every subject.',
  description: 'Custom academic writing by verified human experts.',
  price: 14,
  metaTitle: 'Academic Writing Service | GradeCrest',
  metaDesc: 'Expert academic writing from GradeCrest. Human-written, plagiarism-free, grade guaranteed.',
  intro: 'GradeCrest connects you with verified expert writers who hold postgraduate degrees in your subject. Every paper is written from scratch, checked for plagiarism, and backed by our grade-or-money-back guarantee.',
  bullets: [
    'Written by a verified human expert with subject-specific credentials',
    'Plagiarism-free with full report included',
    'AI-detection certificate on request',
    'Correct referencing style (APA, MLA, Chicago, Harvard)',
    'Grade or money back guarantee',
    'Unlimited revisions within the revision window',
  ],
  process: [
    { title: 'Fill in your brief',        desc: 'Your topic, deadline, level, and instructions.' },
    { title: 'Expert matching',           desc: 'Matched with a writer who holds a degree in your subject.' },
    { title: 'Direct communication',      desc: 'Message your writer, share files, and track progress.' },
    { title: 'Review & revisions',        desc: 'Request free revisions until you are satisfied.' },
  ],
  faqs: [
    { q: 'Is the work plagiarism-free?',     a: 'Yes. Every paper is written from scratch with a plagiarism report included.' },
    { q: 'Do you use AI?',                    a: 'No. Every paper is written by a verified human expert.' },
    { q: 'What is the grade guarantee?',      a: 'If the work does not meet your stated requirements, we rewrite or refund in full.' },
  ],
  related: ['essay-writing', 'research-papers'],
}

const fallbackService = SERVICE_MAP[slug] ?? DEFAULT_SERVICE

const processFromBlocks = (page: CmsServicePage) => {
  const howItWorks = page.body.find(block => block.type === 'how_it_works')
  const value = howItWorks?.value as { steps?: Array<{ title?: string; description?: string }> } | undefined

  return value?.steps?.length
    ? value.steps.map(step => ({
        title: step.title || 'Step',
        desc: step.description || '',
      }))
    : fallbackService.process
}

const serviceFromCms = (page: CmsServicePage): ServiceView => {
  const price = Number(page.pricing_from ?? fallbackService.price) || fallbackService.price
  const faqs = page.faqs.map(faq => ({ q: faq.question, a: faq.answer }))
  const description = page.search_description
    || page.meta?.search_description
    || page.hero?.subheadline
    || fallbackService.description

  return {
    title: page.hero?.headline || page.title,
    tagline: page.hero?.subheadline || description,
    description,
    price,
    metaTitle: page.meta?.seo_title || page.title,
    metaDesc: page.meta?.search_description || description,
    intro: page.who_for || page.hero?.subheadline || fallbackService.intro,
    bullets: page.includes_items.length
      ? page.includes_items
      : page.delivers_items.length
        ? page.delivers_items
        : fallbackService.bullets,
    process: processFromBlocks(page),
    faqs: faqs.length ? faqs : fallbackService.faqs,
    related: page.related_services.map(service => service.slug),
    ctaText: page.primary_cta_text || 'Order now',
    ctaUrl: page.primary_cta_url || app.order,
  }
}

const svc = computed(() => cmsService.value ? serviceFromCms(cmsService.value) : fallbackService)

useSeoMeta({
  title:       () => svc.value.metaTitle,
  description: () => svc.value.metaDesc,
  ogTitle:     () => svc.value.metaTitle,
  ogDescription: () => svc.value.metaDesc,
})

useSeoBase(`https://gradecrest.com/services/${slug}`)
useBreadcrumbs([
  { name: 'Home',     url: 'https://gradecrest.com/' },
  { name: 'Services', url: 'https://gradecrest.com/services' },
  { name: svc.value.title,  url: `https://gradecrest.com/services/${slug}` },
])

if (cmsService.value?.schema) {
  useHead({
    script: [{
      type: 'application/ld+json',
      innerHTML: JSON.stringify(cmsService.value.schema),
    }],
  })
} else {
  useServiceLd({
    name:        svc.value.title,
    description: svc.value.description,
    url:         `https://gradecrest.com/services/${slug}`,
    price:       String(svc.value.price),
    ratingValue: 4.9,
    reviewCount: 1200,
  })
}

useFaqLd(svc.value.faqs)
useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'HowTo',
      name: `How to order ${svc.value.title}`,
      step: svc.value.process.map((s, i) => ({
        '@type': 'HowToStep',
        position: i + 1,
        name: s.title,
        text: s.desc,
      })),
    }),
  }],
})
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-navy-900 py-16 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-10 items-center">
          <div class="space-y-5">
            <!-- Breadcrumb -->
            <nav class="flex items-center gap-1.5 text-xs text-slate-500">
              <NuxtLink to="/" class="hover:text-slate-300">Home</NuxtLink>
              <span>/</span>
              <NuxtLink to="/services" class="hover:text-slate-300">Services</NuxtLink>
              <span>/</span>
              <span class="text-slate-300">{{ svc.title }}</span>
            </nav>
            <h1 class="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">{{ svc.title }}</h1>
            <p class="text-xl text-gc-300 font-medium">{{ svc.tagline }}</p>
            <p class="text-slate-300 leading-relaxed max-w-lg">{{ svc.intro }}</p>
            <div class="flex items-center gap-4 text-sm text-slate-400">
              <span class="font-semibold text-white">From ${{ svc.price }}/page</span>
              <span>·</span>
              <span>Grade or money back</span>
              <span>·</span>
              <span>Zero AI content</span>
            </div>
            <a :href="svc.ctaUrl || app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
              {{ svc.ctaText || 'Order now' }} <ArrowRight class="size-4" />
            </a>
          </div>
          <div>
            <p class="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400 text-center">Get an instant quote</p>
            <PricingCalculator />
          </div>
        </div>
      </div>
    </section>

    <!-- What's included -->
    <section class="bg-mist py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-10 items-start">
          <div>
            <h2 class="text-2xl font-bold text-ink mb-6">What's included</h2>
            <ul class="space-y-3">
              <li v-for="b in svc.bullets" :key="b" class="flex items-start gap-3 text-sm text-ink">
                <CheckCircle2 class="size-4 text-gc-600 shrink-0 mt-0.5" />
                {{ b }}
              </li>
            </ul>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-ink mb-6">How it works</h2>
            <div class="space-y-4">
              <div v-for="(step, i) in svc.process" :key="step.title" class="flex gap-4">
                <span class="flex size-8 shrink-0 items-center justify-center rounded-full border-2 border-gc-600 text-xs font-bold text-gc-600">{{ i + 1 }}</span>
                <div>
                  <p class="text-sm font-semibold text-ink">{{ step.title }}</p>
                  <p class="mt-0.5 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <ServiceBlocks v-if="cmsService?.body?.length" :blocks="cmsService.body" />

    <!-- FAQ -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-3xl px-4 sm:px-6">
        <h2 class="text-2xl font-bold text-ink mb-8">Questions about {{ svc.title.toLowerCase() }}</h2>
        <div class="space-y-3">
          <details v-for="faq in svc.faqs" :key="faq.q" class="group rounded-2xl border border-slate-200 bg-white shadow-card">
            <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
              {{ faq.q }}
              <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45">+</span>
            </summary>
            <p class="px-6 pb-5 text-sm text-graphite leading-relaxed">{{ faq.a }}</p>
          </details>
        </div>
      </div>
    </section>

    <!-- Related services -->
    <section v-if="svc.related.length" class="bg-mist py-12">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-lg font-bold text-ink mb-5">Related services</h2>
        <div class="flex flex-wrap gap-3">
          <NuxtLink
            v-for="rel in svc.related" :key="rel"
            :to="`/services/${rel}`"
            class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-graphite hover:border-gc-300 hover:text-gc-700 transition-colors"
          >
            {{ rel.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="bg-navy-900 py-14 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-xl px-4 space-y-5">
        <h2 class="text-2xl font-bold text-white">Ready to get started?</h2>
        <p class="text-slate-300 text-sm">Place your order in under 2 minutes. Grade or money back guaranteed.</p>
        <a :href="svc.ctaUrl || app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          {{ svc.ctaText || `Order ${svc.title.toLowerCase()}` }} <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
