export interface TocItem {
  id: string
  text: string
  level: string
}

export function slugifyHeading(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

export function extractToc(blocks: { type: string; value: unknown }[]): TocItem[] {
  return blocks
    .filter(b => b.type === 'heading')
    .map(b => {
      const v = b.value as { text: string; level: string }
      return { id: slugifyHeading(v.text), text: v.text, level: v.level || 'h2' }
    })
}
