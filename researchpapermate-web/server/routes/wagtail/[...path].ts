import http from 'node:http'
import { URL } from 'node:url'

export default defineEventHandler(async (event) => {
  const config  = useRuntimeConfig()
  const django  = (config.apiBaseInternal as string) || 'http://localhost:8000'
  const path    = event.path.replace(/^\/wagtail/, '')
  const qs      = new URL(event.path, 'http://x').search

  const target  = new URL(`${path}${qs}`, django)

  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: target.hostname,
        port:     Number(target.port) || 80,
        path:     `${target.pathname}${target.search}`,
        method:   event.method,
        headers:  { Host: 'researchpapermate.com', Accept: 'application/json' },
      },
      (res) => {
        const chunks: Buffer[] = []
        res.on('data', (c: Buffer) => chunks.push(c))
        res.on('end', () => {
          const body = Buffer.concat(chunks).toString('utf8')
          setResponseStatus(event, res.statusCode ?? 200)
          setResponseHeader(event, 'content-type', 'application/json')
          resolve(body)
        })
      },
    )
    req.on('error', reject)
    req.end()
  })
})
