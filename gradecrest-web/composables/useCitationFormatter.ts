export type SourceType = 'book' | 'journal' | 'website' | 'chapter' | 'newspaper' | 'youtube'
export type CitationStyle = 'apa7' | 'apa6' | 'mla9' | 'chicago' | 'harvard' | 'ieee' | 'vancouver' | 'ama' | 'asa' | 'turabian'

export interface Author {
  first: string
  last: string
}

export interface CitationData {
  sourceType: SourceType
  authors: Author[]
  editors: Author[]
  year: string
  month: string
  day: string
  title: string
  containerTitle: string
  publisher: string
  edition: string
  volume: string
  issue: string
  pages: string
  doi: string
  url: string
  accessYear: string
  accessMonth: string
  accessDay: string
  location: string
}

// ─── Month helpers ────────────────────────────────────────────────────────────

const MONTH_NAMES_FULL = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const MONTH_NAMES_ABB = [
  '', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
]

function monthFull(m: string): string {
  const n = parseInt(m)
  return (n >= 1 && n <= 12) ? MONTH_NAMES_FULL[n] : ''
}

function monthAbb(m: string): string {
  const n = parseInt(m)
  return (n >= 1 && n <= 12) ? MONTH_NAMES_ABB[n] : ''
}

// ─── Author format helpers ────────────────────────────────────────────────────

function initials(name: string): string {
  return name.trim().split(/\s+/).filter(Boolean).map(p => p[0].toUpperCase() + '.').join(' ')
}

function initialsNoSpace(name: string): string {
  return name.trim().split(/\s+/).filter(Boolean).map(p => p[0].toUpperCase() + '.').join('')
}

function validAuthors(authors: Author[]): Author[] {
  return authors.filter(a => a.last.trim())
}

// APA: Last, F. M.
function apaAuthor(a: Author): string {
  const last = a.last.trim()
  if (!last) return ''
  const fi = a.first.trim() ? initials(a.first) : ''
  return fi ? `${last}, ${fi}` : last
}

function apaAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return apaAuthor(va[0])
  if (va.length === 2) return `${apaAuthor(va[0])}, & ${apaAuthor(va[1])}`
  if (va.length > 20) {
    const first19 = va.slice(0, 19).map(apaAuthor).join(', ')
    return `${first19}, . . . ${apaAuthor(va[va.length - 1])}`
  }
  const allButLast = va.slice(0, -1).map(apaAuthor).join(', ')
  return `${allButLast}, & ${apaAuthor(va[va.length - 1])}`
}

// MLA: First author Last, First; subsequent First Last
function mlaAuthorFirst(a: Author): string {
  const last = a.last.trim()
  const first = a.first.trim()
  if (!last) return first
  return first ? `${last}, ${first}` : last
}

function mlaAuthorSubsequent(a: Author): string {
  return [a.first.trim(), a.last.trim()].filter(Boolean).join(' ')
}

function mlaAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return mlaAuthorFirst(va[0])
  if (va.length === 2) return `${mlaAuthorFirst(va[0])} and ${mlaAuthorSubsequent(va[1])}`
  return `${mlaAuthorFirst(va[0])}, et al.`
}

// Chicago: Last, First for first; First Last for subsequent
function chicagoAuthorFirst(a: Author): string {
  const last = a.last.trim()
  const first = a.first.trim()
  if (!last) return first
  return first ? `${last}, ${first}` : last
}

function chicagoAuthorSubsequent(a: Author): string {
  return [a.first.trim(), a.last.trim()].filter(Boolean).join(' ')
}

function chicagoAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return chicagoAuthorFirst(va[0])
  const rest = va.slice(1).map(chicagoAuthorSubsequent)
  return [chicagoAuthorFirst(va[0]), ...rest].join(', ')
}

// Harvard: Last, F.M. — no spaces in initials
function harvardAuthor(a: Author): string {
  const last = a.last.trim()
  if (!last) return ''
  const fi = a.first.trim() ? initialsNoSpace(a.first) : ''
  return fi ? `${last}, ${fi}` : last
}

function harvardAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return harvardAuthor(va[0])
  if (va.length === 2) return `${harvardAuthor(va[0])} and ${harvardAuthor(va[1])}`
  return va.map(harvardAuthor).join(', ')
}

// IEEE: F. M. Last
function ieeeAuthor(a: Author): string {
  const last = a.last.trim()
  if (!last) return ''
  const fi = a.first.trim() ? initials(a.first) + ' ' : ''
  return `${fi}${last}`
}

function ieeeAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return ieeeAuthor(va[0])
  if (va.length === 2) return `${ieeeAuthor(va[0])} and ${ieeeAuthor(va[1])}`
  const allButLast = va.slice(0, -1).map(ieeeAuthor).join(', ')
  return `${allButLast}, and ${ieeeAuthor(va[va.length - 1])}`
}

// ─── Edition helper ───────────────────────────────────────────────────────────

function ordinalEd(ed: string): string {
  const n = parseInt(ed)
  if (isNaN(n)) return ed
  const suffix = n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th'
  return `${n}${suffix}`
}

// ─── DOI / URL helper ─────────────────────────────────────────────────────────

function normaliseDoi(doi: string): string {
  return doi.trim().replace(/^https?:\/\/doi\.org\//i, '')
}

function doiOrUrl(doi: string, url: string): string {
  if (doi.trim()) return `https://doi.org/${normaliseDoi(doi)}`
  return url.trim()
}

// ─── APA 7 ───────────────────────────────────────────────────────────────────

function formatAPA7(d: CitationData): string {
  const auth = apaAuthorList(d.authors)
  const year = d.year.trim()
  const yearPart = year ? `(${year})` : '(n.d.)'

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? ` (${ordinalEd(d.edition)} ed.)` : ''
      const link = doiOrUrl(d.doi, d.url)
      const linkPart = link ? ` ${link}` : ''
      return `${auth || 'Author'} ${yearPart}. *${d.title.trim() || 'Title'}*${ed}. ${d.publisher.trim() || 'Publisher'}.${linkPart}`
    }
    case 'journal': {
      const vol = d.volume.trim() ? `, *${d.volume}*` : ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `, ${d.pages}` : ''
      const link = doiOrUrl(d.doi, d.url)
      const linkPart = link ? ` ${link}` : ''
      return `${auth || 'Author'} ${yearPart}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Journal'}*${vol}${iss}${pp}.${linkPart}`
    }
    case 'website': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const site = d.containerTitle.trim()
      const sitePart = site ? ` ${site}.` : ''
      const urlPart = d.url.trim() ? ` ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearSection}. *${d.title.trim() || 'Page title'}*.${sitePart}${urlPart}`
    }
    case 'chapter': {
      const eds = validAuthors(d.editors)
      const edList = eds.length ? apaAuthorList(d.editors) : ''
      const edStr = edList ? `In ${edList} (${eds.length === 1 ? 'Ed.' : 'Eds.'}), ` : 'In '
      const pp = d.pages.trim() ? ` (pp. ${d.pages})` : ''
      return `${auth || 'Author'} ${yearPart}. ${d.title.trim() || 'Chapter title'}. ${edStr}*${d.containerTitle.trim() || 'Book title'}*${pp}. ${d.publisher.trim() || 'Publisher'}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const urlPart = d.url.trim() ? ` ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearSection}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Newspaper'}*.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel} ${yearSection}. *${d.title.trim() || 'Video title'}* [Video]. YouTube. ${d.url.trim()}`
    }
  }
}

// ─── MLA 9 ───────────────────────────────────────────────────────────────────

function mlaDate(year: string, month: string, day: string): string {
  const mf = monthFull(month)
  return [day.trim(), mf, year.trim()].filter(Boolean).join(' ')
}

function formatMLA9(d: CitationData): string {
  const auth = mlaAuthorList(d.authors)
  const authPart = auth ? `${auth}. ` : ''

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? `, ${ordinalEd(d.edition)} ed.` : ''
      return `${authPart}*${d.title.trim() || 'Title'}*${ed}. ${d.publisher.trim() || 'Publisher'}, ${d.year.trim() || 'n.d.'}.`
    }
    case 'journal': {
      const vol = d.volume.trim() ? `vol. ${d.volume}` : ''
      const no = d.issue.trim() ? `no. ${d.issue}` : ''
      const vn = [vol, no].filter(Boolean).join(', ')
      const pp = d.pages.trim() ? `pp. ${d.pages}` : ''
      const doi = d.doi.trim()
        ? `https://doi.org/${normaliseDoi(d.doi)}`
        : d.url.trim()
      const doiPart = doi ? ` ${doi}.` : '.'
      const parts = [vn, d.year.trim() || 'n.d.', pp].filter(Boolean).join(', ')
      return `${authPart}"${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Journal'}*, ${parts}.${doiPart}`
    }
    case 'website': {
      const dt = mlaDate(d.year, d.month, d.day)
      const acc = mlaDate(d.accessYear, d.accessMonth, d.accessDay)
      const dtPart = dt ? `${dt}, ` : ''
      const accPart = acc ? ` Accessed ${acc}.` : ''
      const urlPart = d.url.trim() ? `${d.url.trim()}.` : ''
      return `${authPart}"${d.title.trim() || 'Page title'}." *${d.containerTitle.trim() || 'Site Name'}*, ${dtPart}${urlPart}${accPart}`
    }
    case 'chapter': {
      const eds = mlaAuthorList(d.editors)
      const edStr = eds ? `edited by ${eds}, ` : ''
      const pp = d.pages.trim() ? `pp. ${d.pages}` : ''
      return `${authPart}"${d.title.trim() || 'Chapter title'}." *${d.containerTitle.trim() || 'Book title'}*, ${edStr}${d.publisher.trim() || 'Publisher'}, ${d.year.trim() || 'n.d.'}, ${pp}.`
    }
    case 'newspaper': {
      const dt = mlaDate(d.year, d.month, d.day)
      const urlPart = d.url.trim() ? ` ${d.url.trim()}.` : ''
      return `${authPart}"${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Newspaper'}*, ${dt}.${urlPart}`
    }
    case 'youtube': {
      const dt = mlaDate(d.year, d.month, d.day)
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel}. "${d.title.trim() || 'Video title'}." *YouTube*, ${dt}, ${d.url.trim()}.`
    }
  }
}

// ─── Chicago Author-Date ──────────────────────────────────────────────────────

function formatChicago(d: CitationData): string {
  const auth = chicagoAuthorList(d.authors)
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${auth || 'Author'}. ${year}. *${d.title.trim() || 'Title'}*. ${pubStr}.`
    }
    case 'journal': {
      const vol = d.volume.trim() || ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `: ${d.pages}` : ''
      const doi = d.doi.trim()
        ? ` https://doi.org/${normaliseDoi(d.doi)}.`
        : d.url.trim() ? ` ${d.url.trim()}.` : '.'
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Journal'}* ${vol}${iss}${pp}.${doi}`
    }
    case 'website': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim()].filter(Boolean).join(' ')
      const datePart = dateStr ? `${dateStr}. ` : ''
      const urlPart = d.url.trim() || ''
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Page title'}." ${d.containerTitle.trim() || 'Site Name'}. ${datePart}${urlPart}.`
    }
    case 'chapter': {
      const eds = d.editors.filter(e => e.last.trim()).map(chicagoAuthorSubsequent).join(', ')
      const edStr = eds ? `edited by ${eds}, ` : ''
      const pp = d.pages.trim() ? `${d.pages}. ` : ''
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Chapter title'}." In *${d.containerTitle.trim() || 'Book title'}*, ${edStr}${pp}${d.publisher.trim() || 'Publisher'}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), d.year.trim()].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` ${d.url.trim()}.` : '.'
      return `${auth || 'Author'}. "${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Newspaper'}*, ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), d.year.trim()].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel}. "${d.title.trim() || 'Video title'}." YouTube video. ${dateStr}. ${d.url.trim()}.`
    }
  }
}

// ─── Harvard ──────────────────────────────────────────────────────────────────

function formatHarvard(d: CitationData): string {
  const auth = harvardAuthorList(d.authors)
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? `, ${ordinalEd(d.edition)} edn` : ''
      return `${auth || 'Author'} (${year}) *${d.title.trim() || 'Title'}*${ed}. ${d.publisher.trim() || 'Publisher'}.`
    }
    case 'journal': {
      const vol = d.volume.trim() || ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `, pp. ${d.pages}` : ''
      const doi = d.doi.trim() ? ` doi: ${normaliseDoi(d.doi)}.` : '.'
      return `${auth || 'Author'} (${year}) '${d.title.trim() || 'Article title'}', *${d.containerTitle.trim() || 'Journal'}*, ${vol}${iss}${pp}.${doi}`
    }
    case 'website': {
      const accDay = d.accessDay.trim()
      const accMonth = monthFull(d.accessMonth)
      const accYear = d.accessYear.trim()
      const accDate = [accDay, accMonth, accYear].filter(Boolean).join(' ')
      const accPart = accDate ? ` (Accessed: ${accDate}).` : '.'
      return `${auth || 'Author'} (${year}) *${d.title.trim() || 'Page title'}*. Available at: ${d.url.trim() || 'URL'}${accPart}`
    }
    case 'chapter': {
      const eds = harvardAuthorList(d.editors)
      const edCount = validAuthors(d.editors).length
      const edStr = eds ? `In: ${eds} (${edCount === 1 ? 'ed.' : 'eds.'}) ` : ''
      const pp = d.pages.trim() ? `, pp. ${d.pages}` : ''
      return `${auth || 'Author'} (${year}) '${d.title.trim() || 'Chapter title'}'. ${edStr}*${d.containerTitle.trim() || 'Book title'}*${pp}. ${d.publisher.trim() || 'Publisher'}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const dateStr = [d.day.trim(), mf, year].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` Available at: ${d.url.trim()}.` : '.'
      return `${auth || 'Author'} (${year}) '${d.title.trim() || 'Article title'}', *${d.containerTitle.trim() || 'Newspaper'}*, ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [d.day.trim(), mf, year].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel} (${year}) *${d.title.trim() || 'Video title'}* [Video]. YouTube, ${dateStr}. Available at: ${d.url.trim()}.`
    }
  }
}

// ─── IEEE ─────────────────────────────────────────────────────────────────────

function formatIEEE(d: CitationData, refNum = 1): string {
  const auth = ieeeAuthorList(d.authors)
  const ref = `[${refNum}]`
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${ref} ${auth || 'Author'}, *${d.title.trim() || 'Title'}*. ${pubStr}, ${year}.`
    }
    case 'journal': {
      const vol = d.volume.trim() ? `vol. ${d.volume}` : ''
      const no = d.issue.trim() ? `no. ${d.issue}` : ''
      const pp = d.pages.trim() ? `pp. ${d.pages}` : ''
      const mf = monthAbb(d.month)
      const dateStr = [mf, year].filter(Boolean).join(' ')
      const parts = [vol, no, pp, dateStr].filter(Boolean).join(', ')
      const doi = d.doi.trim() ? ` doi: ${normaliseDoi(d.doi)}.` : '.'
      return `${ref} ${auth || 'Author'}, "${d.title.trim() || 'Article title'}," *${d.containerTitle.trim() || 'Journal'}*, ${parts}.${doi}`
    }
    case 'website': {
      const mf = monthFull(d.month)
      const dateStr = [mf, year].filter(Boolean).join(' ')
      const accStr = dateStr ? `accessed ${dateStr}` : ''
      const urlPart = d.url.trim()
        ? ` Available: ${d.url.trim()}${accStr ? ` (${accStr})` : ''}.`
        : '.'
      return `${ref} ${auth || 'Author'}, "${d.title.trim() || 'Page title'}," *${d.containerTitle.trim() || 'Site Name'}*. [Online].${urlPart}`
    }
    case 'chapter': {
      const edVa = validAuthors(d.editors)
      const eds = ieeeAuthorList(d.editors)
      const edStr = eds
        ? `in *${d.containerTitle.trim() || 'Book title'}*, ${eds}, Ed${edVa.length > 1 ? 's' : ''}. `
        : `in *${d.containerTitle.trim() || 'Book title'}*. `
      const pp = d.pages.trim() ? `pp. ${d.pages}. ` : ''
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${ref} ${auth || 'Author'}, "${d.title.trim() || 'Chapter title'}," ${edStr}${pubStr}, ${year}, ${pp}`
    }
    case 'newspaper': {
      const mf = monthAbb(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` [Online]. Available: ${d.url.trim()}.` : '.'
      return `${ref} ${auth || 'Author'}, "${d.title.trim() || 'Article title'}," *${d.containerTitle.trim() || 'Newspaper'}*, ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${ref} ${channel}, "${d.title.trim() || 'Video title'}," YouTube. [Online Video]. Available: ${d.url.trim()}. (accessed ${dateStr}).`
    }
  }
}

// ─── APA 6 ───────────────────────────────────────────────────────────────────
// Key differences from APA 7:
//   • et al. after 6 authors (not 20)
//   • website uses "Retrieved from URL" not bare URL
//   • DOI prefix is "doi:" not "https://doi.org/"

function apa6AuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return apaAuthor(va[0])
  if (va.length === 2) return `${apaAuthor(va[0])}, & ${apaAuthor(va[1])}`
  if (va.length > 6) {
    const first6 = va.slice(0, 6).map(apaAuthor).join(', ')
    return `${first6}, . . . ${apaAuthor(va[va.length - 1])}`
  }
  const allButLast = va.slice(0, -1).map(apaAuthor).join(', ')
  return `${allButLast}, & ${apaAuthor(va[va.length - 1])}`
}

function formatAPA6(d: CitationData): string {
  const auth = apa6AuthorList(d.authors)
  const year = d.year.trim()
  const yearPart = year ? `(${year})` : '(n.d.)'

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? ` (${ordinalEd(d.edition)} ed.)` : ''
      const doi = d.doi.trim() ? ` doi:${normaliseDoi(d.doi)}` : d.url.trim() ? ` Retrieved from ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearPart}. *${d.title.trim() || 'Title'}*${ed}. ${d.publisher.trim() || 'Publisher'}.${doi}`
    }
    case 'journal': {
      const vol = d.volume.trim() ? `, *${d.volume}*` : ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `, ${d.pages}` : ''
      const doi = d.doi.trim() ? ` doi:${normaliseDoi(d.doi)}` : d.url.trim() ? ` Retrieved from ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearPart}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Journal'}*${vol}${iss}${pp}.${doi}`
    }
    case 'website': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const site = d.containerTitle.trim()
      const sitePart = site ? ` ${site}.` : ''
      const urlPart = d.url.trim() ? ` Retrieved from ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearSection}. *${d.title.trim() || 'Page title'}*.${sitePart}${urlPart}`
    }
    case 'chapter': {
      const eds = validAuthors(d.editors)
      const edList = eds.length ? apa6AuthorList(d.editors) : ''
      const edStr = edList ? `In ${edList} (${eds.length === 1 ? 'Ed.' : 'Eds.'}), ` : 'In '
      const pp = d.pages.trim() ? ` (pp. ${d.pages})` : ''
      return `${auth || 'Author'} ${yearPart}. ${d.title.trim() || 'Chapter title'}. ${edStr}*${d.containerTitle.trim() || 'Book title'}*${pp}. ${d.publisher.trim() || 'Publisher'}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const urlPart = d.url.trim() ? ` Retrieved from ${d.url.trim()}` : ''
      return `${auth || 'Author'} ${yearSection}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Newspaper'}*.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const fullDate = [mf, d.day.trim()].filter(Boolean).join(' ')
      const yearSection = year ? `(${year}${fullDate ? `, ${fullDate}` : ''})` : '(n.d.)'
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel} ${yearSection}. *${d.title.trim() || 'Video title'}* [Video file]. Retrieved from ${d.url.trim()}`
    }
  }
}

// ─── Vancouver ────────────────────────────────────────────────────────────────
// Numbered system; NO italics; author initials have no periods, no spaces

function vancouverAuthor(a: Author): string {
  const last = a.last.trim()
  if (!last) return ''
  const fi = a.first.trim() ? a.first.trim().split(/\s+/).filter(Boolean).map(p => p[0].toUpperCase()).join('') : ''
  return fi ? `${last} ${fi}` : last
}

function vancouverAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length <= 6) return va.map(vancouverAuthor).join(', ')
  return va.slice(0, 6).map(vancouverAuthor).join(', ') + ', et al.'
}

function formatVancouver(d: CitationData, refNum = 1): string {
  const auth = vancouverAuthorList(d.authors)
  const ref = `[${refNum}]`
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? ` ${ordinalEd(d.edition)} ed.` : ''
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${ref} ${auth || 'Author'}. ${d.title.trim() || 'Title'}${ed}. ${pubStr}; ${year}.`
    }
    case 'journal': {
      const vol = d.volume.trim() || ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `:${d.pages}` : ''
      const doi = d.doi.trim() ? ` doi:${normaliseDoi(d.doi)}` : ''
      return `${ref} ${auth || 'Author'}. ${d.title.trim() || 'Article title'}. ${d.containerTitle.trim() || 'Journal'}. ${year};${vol}${iss}${pp}.${doi}`
    }
    case 'website': {
      const site = d.containerTitle.trim() || 'Site Name'
      const mf = monthFull(d.accessMonth)
      const accDate = [mf, d.accessDay.trim(), d.accessYear.trim()].filter(Boolean).join(' ')
      const cited = accDate ? ` [cited ${accDate}]` : ''
      const urlPart = d.url.trim() ? ` Available from: ${d.url.trim()}` : ''
      return `${ref} ${auth || 'Author'}. ${d.title.trim() || 'Page title'} [Internet]. ${site}; ${year}${cited}.${urlPart}`
    }
    case 'chapter': {
      const eds = vancouverAuthorList(d.editors)
      const edCount = validAuthors(d.editors).length
      const edStr = eds ? `In: ${eds}, editor${edCount > 1 ? 's' : ''}. ` : 'In: '
      const pp = d.pages.trim() ? ` p. ${d.pages}` : ''
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${ref} ${auth || 'Author'}. ${d.title.trim() || 'Chapter title'}. ${edStr}${d.containerTitle.trim() || 'Book title'}.${pp} ${pubStr}; ${year}.`
    }
    case 'newspaper': {
      const mf = monthAbb(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` Available from: ${d.url.trim()}` : ''
      return `${ref} ${auth || 'Author'}. ${d.title.trim() || 'Article title'}. ${d.containerTitle.trim() || 'Newspaper'}. ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${ref} ${channel}. ${d.title.trim() || 'Video title'} [Video]. YouTube; ${dateStr}. Available from: ${d.url.trim()}`
    }
  }
}

// ─── AMA 11th ─────────────────────────────────────────────────────────────────
// Used in medicine; similar to Vancouver but periods after initials, italics on journal/book

function amaAuthor(a: Author): string {
  const last = a.last.trim()
  if (!last) return ''
  const fi = a.first.trim() ? initials(a.first) : ''
  // AMA uses no space: Smith AB not Smith A. B.
  const fiNoSpace = fi.replace(/\.\s+/g, '')
  return fi ? `${last} ${fiNoSpace}` : last
}

function amaAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length <= 6) return va.map(amaAuthor).join(', ')
  return va.slice(0, 6).map(amaAuthor).join(', ') + ', et al.'
}

function formatAMA(d: CitationData): string {
  const auth = amaAuthorList(d.authors)
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const ed = d.edition.trim() ? ` ${ordinalEd(d.edition)} ed.` : ''
      return `${auth || 'Author'}. *${d.title.trim() || 'Title'}*${ed}. ${d.publisher.trim() || 'Publisher'}; ${year}.`
    }
    case 'journal': {
      const vol = d.volume.trim() || ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `:${d.pages}` : ''
      const doi = d.doi.trim() ? ` doi:${normaliseDoi(d.doi)}` : ''
      return `${auth || 'Author'}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Journal'}*. ${year};${vol}${iss}${pp}.${doi}`
    }
    case 'website': {
      const mf = monthFull(d.month)
      const pubDate = [mf, d.day.trim() ? d.day.trim() + ',' : '', year].filter(Boolean).join(' ')
      const accMf = monthFull(d.accessMonth)
      const accDate = [accMf, d.accessDay.trim() ? d.accessDay.trim() + ',' : '', d.accessYear.trim()].filter(Boolean).join(' ')
      const pubPart = pubDate ? ` Published ${pubDate}.` : ''
      const accPart = accDate ? ` Accessed ${accDate}.` : ''
      const site = d.containerTitle.trim() || 'Site Name'
      return `${auth || 'Author'}. ${d.title.trim() || 'Page title'}. ${site}.${pubPart}${accPart} ${d.url.trim()}`
    }
    case 'chapter': {
      const eds = amaAuthorList(d.editors)
      const edCount = validAuthors(d.editors).length
      const edStr = eds ? `In: ${eds}, ed${edCount > 1 ? 's' : ''}. ` : 'In: '
      const pp = d.pages.trim() ? `:${d.pages}` : ''
      return `${auth || 'Author'}. ${d.title.trim() || 'Chapter title'}. ${edStr}*${d.containerTitle.trim() || 'Book title'}*${pp}. ${d.publisher.trim() || 'Publisher'}; ${year}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim() ? d.day.trim() + ',' : '', year].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` ${d.url.trim()}` : ''
      return `${auth || 'Author'}. ${d.title.trim() || 'Article title'}. *${d.containerTitle.trim() || 'Newspaper'}*. ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim() ? d.day.trim() + ',' : '', year].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel}. ${d.title.trim() || 'Video title'} [video]. YouTube. Published ${dateStr}. ${d.url.trim()}`
    }
  }
}

// ─── ASA 6th ──────────────────────────────────────────────────────────────────
// Sociology style; "First Last" for all-but-first author; "and" between last two

function asaAuthorFirst(a: Author): string {
  const last = a.last.trim()
  const first = a.first.trim()
  if (!last) return first
  return first ? `${last}, ${first}` : last
}

function asaAuthorSubsequent(a: Author): string {
  return [a.first.trim(), a.last.trim()].filter(Boolean).join(' ')
}

function asaAuthorList(authors: Author[]): string {
  const va = validAuthors(authors)
  if (!va.length) return ''
  if (va.length === 1) return asaAuthorFirst(va[0])
  if (va.length === 2) return `${asaAuthorFirst(va[0])} and ${asaAuthorSubsequent(va[1])}`
  const allButLast = [asaAuthorFirst(va[0]), ...va.slice(1, -1).map(asaAuthorSubsequent)].join(', ')
  return `${allButLast}, and ${asaAuthorSubsequent(va[va.length - 1])}`
}

function formatASA(d: CitationData): string {
  const auth = asaAuthorList(d.authors)
  const year = d.year.trim() || 'n.d.'

  switch (d.sourceType) {
    case 'book': {
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${auth || 'Author'}. ${year}. *${d.title.trim() || 'Title'}*. ${pubStr}.`
    }
    case 'journal': {
      const vol = d.volume.trim() || ''
      const iss = d.issue.trim() ? `(${d.issue})` : ''
      const pp = d.pages.trim() ? `:${d.pages}` : ''
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Journal'}* ${vol}${iss}${pp}.`
    }
    case 'website': {
      const mf = monthFull(d.accessMonth)
      const accDate = [mf, d.accessDay.trim(), d.accessYear.trim()].filter(Boolean).join(' ')
      const retrieved = accDate ? `Retrieved ${accDate}` : 'Retrieved'
      const urlPart = d.url.trim() ? ` (${d.url.trim()})` : ''
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Page title'}." *${d.containerTitle.trim() || 'Site Name'}*. ${retrieved}${urlPart}.`
    }
    case 'chapter': {
      const eds = asaAuthorList(d.editors)
      const edCount = validAuthors(d.editors).length
      const edStr = eds ? `edited by ${eds}. ` : ''
      const pp = d.pages.trim() ? `Pp. ${d.pages} in ` : 'In '
      const loc = d.location.trim()
      const pub = d.publisher.trim()
      const pubStr = loc && pub ? `${loc}: ${pub}` : pub || loc || 'Publisher'
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Chapter title'}." ${pp}*${d.containerTitle.trim() || 'Book title'}*, ${edStr}${pubStr}.`
    }
    case 'newspaper': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const urlPart = d.url.trim() ? ` Retrieved (${d.url.trim()}).` : '.'
      return `${auth || 'Author'}. ${year}. "${d.title.trim() || 'Article title'}." *${d.containerTitle.trim() || 'Newspaper'}*, ${dateStr}.${urlPart}`
    }
    case 'youtube': {
      const mf = monthFull(d.month)
      const dateStr = [mf, d.day.trim(), year].filter(Boolean).join(' ')
      const channel = (validAuthors(d.authors)[0]?.last || d.containerTitle || 'Channel').trim()
      return `${channel}. ${year}. "${d.title.trim() || 'Video title'}." YouTube, ${dateStr}. Retrieved (${d.url.trim()}).`
    }
  }
}

// ─── Turabian 9th ─────────────────────────────────────────────────────────────
// Student version of Chicago Notes-Bibliography; format is effectively identical
// to Chicago for bibliography entries, but labeled separately.

function formatTurabian(d: CitationData): string {
  // Delegate to Chicago — same bibliography format for student purposes
  return formatChicago(d)
}

// ─── Main composable ──────────────────────────────────────────────────────────

export function useCitationFormatter() {
  function format(style: CitationStyle, data: CitationData, refNum = 1): string {
    switch (style) {
      case 'apa7':      return formatAPA7(data)
      case 'apa6':      return formatAPA6(data)
      case 'mla9':      return formatMLA9(data)
      case 'chicago':   return formatChicago(data)
      case 'turabian':  return formatTurabian(data)
      case 'harvard':   return formatHarvard(data)
      case 'ieee':      return formatIEEE(data, refNum)
      case 'vancouver': return formatVancouver(data, refNum)
      case 'ama':       return formatAMA(data)
      case 'asa':       return formatASA(data)
    }
  }

  return { format }
}
