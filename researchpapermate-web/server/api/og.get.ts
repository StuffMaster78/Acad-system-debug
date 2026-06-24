import { defineEventHandler, getQuery, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const { url } = getQuery(event)

  if (!url || typeof url !== 'string') {
    throw createError({ statusCode: 400, statusMessage: 'url parameter required' })
  }

  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    throw createError({ statusCode: 400, statusMessage: 'Invalid URL' })
  }

  // Block private/local addresses
  const host = parsed.hostname
  if (/^(localhost|127\.|192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.)/.test(host)) {
    throw createError({ statusCode: 400, statusMessage: 'Private addresses not allowed' })
  }

  let html: string
  try {
    html = await $fetch<string>(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; AcademicCitationBot/1.0)',
        'Accept': 'text/html',
      },
      responseType: 'text',
      timeout: 8000,
    })
  } catch {
    return { error: 'Could not fetch the page.' }
  }

  // Extract a <meta> tag value by property or name attribute
  function getMeta(key: string): string {
    // property="og:title" content="..."  OR  name="author" content="..."
    const re1 = new RegExp(`<meta[^>]+(?:property|name)=["']${key}["'][^>]+content=["']([^"']*?)["']`, 'i')
    const re2 = new RegExp(`<meta[^>]+content=["']([^"']*?)["'][^>]+(?:property|name)=["']${key}["']`, 'i')
    return (html.match(re1) ?? html.match(re2))?.[1]?.trim() ?? ''
  }

  // Page title: og:title → <title>
  const title = getMeta('og:title')
    || html.match(/<title[^>]*>([^<]+)<\/title>/i)?.[1]?.trim()
    || ''

  const siteName = getMeta('og:site_name') || parsed.hostname.replace(/^www\./, '')

  // Author: article:author → author meta tag
  const authorRaw = getMeta('article:author') || getMeta('author') || getMeta('twitter:creator') || ''

  // Published date
  const publishedRaw = getMeta('article:published_time')
    || getMeta('og:updated_time')
    || getMeta('datePublished')
    || ''

  let year = '', month = '', day = ''
  if (publishedRaw) {
    const d = new Date(publishedRaw)
    if (!isNaN(d.getTime())) {
      year  = String(d.getFullYear())
      month = String(d.getMonth() + 1)
      day   = String(d.getDate())
    }
  }

  return { title, siteName, authorRaw, year, month, day }
})
