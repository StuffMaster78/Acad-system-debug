// Transparent proxy to Django/Wagtail that injects Host: gradecrest.com.
// In production nginx handles this; in local dev the Fetch API forbids
// setting Host manually, so we use Node.js http.request() instead.
// All Wagtail API calls in this app go through /wagtail/... which maps here.
import http from 'node:http'
import { URL } from 'node:url'

export default defineEventHandler(async (event) => {
  const config  = useRuntimeConfig()
  const django  = (config.apiBaseInternal as string) || 'http://localhost:8000'
  const path    = event.path.replace(/^\/wagtail/, '')   // strip our prefix
  const qs      = new URL(event.path, 'http://x').search // preserve query string

  // Build the target URL
  const target  = new URL(`${path}${qs}`, django)

  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: target.hostname,
        port:     Number(target.port) || 80,
        path:     `${target.pathname}${target.search}`,
        method:   event.method,
        // Node.js http.request allows setting Host — unlike fetch API
        headers:  { Host: 'gradecrest.com', Accept: 'application/json' },
      },
      (res) => {
        const chunks: Buffer[] = []
        res.on('data', (c: Buffer) => chunks.push(c))
        res.on('end', () => {
          const body = Buffer.concat(chunks).toString('utf8')
          setResponseStatus(event, res.statusCode ?? 200)
          setResponseHeader(event, 'content-type', 'application/json')
          try { resolve(JSON.parse(body)) } catch { resolve(body) }
        })
      },
    )
    req.on('error', reject)
    req.end()
  })
})
