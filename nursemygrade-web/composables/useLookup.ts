import type { CitationData, Author, SourceType } from './useCitationFormatter'

export type LookupType = 'doi' | 'isbn' | 'url'

export interface LookupResult {
  sourceType: SourceType
  authors: Author[]
  fields: Omit<CitationData, 'sourceType' | 'authors' | 'editors'>
  source: string
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function emptyFields(): Omit<CitationData, 'sourceType' | 'authors' | 'editors'> {
  return {
    year: '', month: '', day: '',
    title: '', containerTitle: '',
    publisher: '', edition: '', volume: '', issue: '', pages: '',
    doi: '', url: '',
    accessYear: '', accessMonth: '', accessDay: '',
    location: '',
  }
}

function parseFullName(name: string): Author {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return { first: '', last: '' }
  if (parts.length === 1) return { first: '', last: parts[0] }
  return { first: parts.slice(0, -1).join(' '), last: parts[parts.length - 1] }
}

// ── DOI → CrossRef ────────────────────────────────────────────────────────────

export async function lookupDOI(doi: string): Promise<LookupResult> {
  const cleaned = doi.trim().replace(/^https?:\/\/doi\.org\//i, '').replace(/^doi:/i, '')
  if (!cleaned) throw new Error('Enter a DOI first')

  const data = await $fetch<any>(
    `https://api.crossref.org/works/${encodeURIComponent(cleaned)}?mailto=tools@noreply.com`,
    { timeout: 8000 },
  ).catch(() => { throw new Error('Could not reach CrossRef. Check your DOI and try again.') })

  const msg = data?.message
  if (!msg) throw new Error('No result found for this DOI.')

  // Determine source type from CrossRef type
  const typeMap: Record<string, SourceType> = {
    'journal-article': 'journal',
    'book': 'book',
    'book-chapter': 'chapter',
    'proceedings-article': 'journal',
    'report': 'journal',
    'posted-content': 'journal',
    'monograph': 'book',
  }
  const sourceType: SourceType = typeMap[msg.type] ?? 'journal'

  // Authors: CrossRef uses { given, family }
  const authors: Author[] = (msg.author ?? []).map((a: any) => ({
    first: a.given ?? '',
    last: a.family ?? '',
  }))

  // Published date
  const parts = msg.published?.['date-parts']?.[0]
    ?? msg['published-print']?.['date-parts']?.[0]
    ?? msg['published-online']?.['date-parts']?.[0]
    ?? []

  const fields = emptyFields()
  fields.title          = (msg.title?.[0] ?? '').replace(/<[^>]+>/g, '')
  fields.containerTitle = msg['container-title']?.[0] ?? ''
  fields.publisher      = msg.publisher ?? ''
  fields.volume         = msg.volume ?? ''
  fields.issue          = msg.issue ?? ''
  fields.pages          = msg.page ?? ''
  fields.doi            = cleaned
  fields.year           = parts[0] ? String(parts[0]) : ''
  fields.month          = parts[1] ? String(parts[1]) : ''
  fields.day            = parts[2] ? String(parts[2]) : ''

  return { sourceType, authors, fields, source: 'CrossRef' }
}

// ── ISBN → OpenLibrary ────────────────────────────────────────────────────────

export async function lookupISBN(isbn: string): Promise<LookupResult> {
  const cleaned = isbn.trim().replace(/[-\s]/g, '')
  if (!cleaned) throw new Error('Enter an ISBN first')
  if (!/^\d{10}(\d{3})?$/.test(cleaned)) throw new Error('Enter a valid 10 or 13-digit ISBN')

  const data = await $fetch<any>(
    `https://openlibrary.org/api/books?bibkeys=ISBN:${cleaned}&format=json&jscmd=data`,
    { timeout: 8000 },
  ).catch(() => { throw new Error('Could not reach OpenLibrary. Check your ISBN and try again.') })

  const book = data?.[`ISBN:${cleaned}`]
  if (!book) throw new Error('No book found for this ISBN. Try filling fields manually.')

  const authors: Author[] = (book.authors ?? []).map((a: any) => parseFullName(a.name ?? ''))

  // parse year from publish_date string e.g. "2020", "Jan 2020", "2020-01-01"
  const pubDate: string = book.publish_date ?? ''
  const yearMatch = pubDate.match(/\b(19|20)\d{2}\b/)
  const year = yearMatch ? yearMatch[0] : ''

  const fields = emptyFields()
  fields.title     = book.title ?? ''
  fields.publisher = book.publishers?.[0]?.name ?? ''
  fields.year      = year
  fields.edition   = book.edition_name ?? ''
  fields.location  = book.publish_places?.[0]?.name ?? ''
  fields.url       = book.url ?? ''

  return { sourceType: 'book', authors, fields, source: 'OpenLibrary' }
}

// ── URL → OG tags (via Nuxt server route) ────────────────────────────────────

export async function lookupURL(url: string): Promise<LookupResult> {
  const trimmed = url.trim()
  if (!trimmed) throw new Error('Enter a URL first')
  try { new URL(trimmed) } catch { throw new Error('Enter a valid URL starting with https://') }

  const data = await $fetch<any>('/api/og', { query: { url: trimmed }, timeout: 10000 })
    .catch(() => { throw new Error('Could not fetch the page. Check the URL and try again.') })

  if (data?.error) throw new Error(data.error)

  const authors: Author[] = []
  if (data.authorRaw && !data.authorRaw.startsWith('http')) {
    authors.push(parseFullName(data.authorRaw))
  }

  const now = new Date()
  const fields = emptyFields()
  fields.title          = data.title ?? ''
  fields.containerTitle = data.siteName ?? ''
  fields.url            = trimmed
  fields.year           = data.year ?? ''
  fields.month          = data.month ?? ''
  fields.day            = data.day ?? ''
  fields.accessYear     = String(now.getFullYear())
  fields.accessMonth    = String(now.getMonth() + 1)
  fields.accessDay      = String(now.getDate())

  return { sourceType: 'website', authors, fields, source: 'webpage' }
}

// ── Composable ────────────────────────────────────────────────────────────────

export function useLookup() {
  return { lookupDOI, lookupISBN, lookupURL }
}
