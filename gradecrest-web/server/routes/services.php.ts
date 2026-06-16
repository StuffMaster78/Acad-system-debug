// 301 redirect handler for the old PHP service pages.
// Old URLs: /services.php              → /services
//           /services.php?service=X    → /services/X
//           /services.php?type=X       → /services/X
//           /services.php?page=X       → /services/X  (some CMS variants)
export default defineEventHandler((event) => {
  const query = getQuery(event)

  const slug = (query.service || query.type || query.page || '') as string

  const target = slug.trim()
    ? `/services/${encodeURIComponent(slug.trim())}`
    : '/services'

  return sendRedirect(event, target, 301)
})
