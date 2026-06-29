// 301 redirects for old PHP service pages.
//
// Old site pattern:  gradecrest.com/essay-writing.php
// New site pattern:  gradecrest.com/essay-writing  (flat URL)
//
// Rule: /{slug}.php at the root level → /{slug}

const SLUG_OVERRIDES: Record<string, string> = {
  // Add entries here if the old filename differs from the new slug.
  // e.g. 'write-my-essay': 'essay-writing'
  // Left intentionally sparse — extend as you audit the 160 old URLs.
}

export default defineEventHandler((event) => {
  const url = event.path || ''

  // Only handle root-level .php files (not /admin/*.php etc.)
  if (!url.match(/^\/[^/]+\.php(\?.*)?$/)) return

  const withoutExt = url.replace(/\.php(\?.*)?$/, '').replace(/^\//, '')
  const slug = SLUG_OVERRIDES[withoutExt] ?? withoutExt

  return sendRedirect(event, `/${slug}`, 301)
})
