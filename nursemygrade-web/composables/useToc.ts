export interface TocEntry {
  level: 'h2' | 'h3'
  text: string
  anchor: string
}

/** Mirror of the backend generate_toc algorithm in cms_core/validators.py */
function toAnchor(text: string): string {
  return text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .slice(0, 60)
}

/** Strip HTML tags from a string to get plain text */
function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, '')
}

/**
 * Parses an HTML body string, extracts h2/h3 headings, generates anchor IDs,
 * injects `id` attributes into the heading tags, and returns both the TOC
 * entries and the modified HTML ready for v-html.
 *
 * Works in both Node (SSG build) and browser (no DOMParser needed).
 */
export function useToc(body: string) {
  const toc: TocEntry[] = []
  const anchorCount: Record<string, number> = {}

  // Replace every <h2> and <h3> in the body with an id-bearing version,
  // and collect TOC entries as we go.
  const processedBody = body.replace(
    /<(h[23])([^>]*)>([\s\S]*?)<\/h[23]>/gi,
    (match, tag: string, attrs: string, inner: string) => {
      const level = tag.toLowerCase() as 'h2' | 'h3'
      const text  = stripTags(inner).trim()
      if (!text) return match

      let anchor = toAnchor(text)

      // Deduplicate anchors (same algorithm browsers use for fragment nav)
      if (anchorCount[anchor] !== undefined) {
        anchorCount[anchor]++
        anchor = `${anchor}-${anchorCount[anchor]}`
      } else {
        anchorCount[anchor] = 0
      }

      toc.push({ level, text, anchor })

      // Inject id — preserve any existing attributes on the tag
      const attrsClean = attrs.replace(/\bid="[^"]*"/gi, '').trim()
      return `<${tag} id="${anchor}"${attrsClean ? ' ' + attrsClean : ''}>${inner}</${tag}>`
    },
  )

  return { toc, processedBody }
}

// ── Wagtail block-based TOC (for CMS posts) ────────────────────────────────

export interface TocItem {
  id: string
  text: string
  level: string
}

export function slugifyHeading(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '')
}

export function extractToc(blocks: { type: string; value: unknown }[]): TocItem[] {
  return blocks
    .filter(b => b.type === 'heading')
    .map(b => {
      const v = b.value as { text: string; level: string }
      return { id: slugifyHeading(v.text), text: v.text, level: v.level || 'h2' }
    })
}
