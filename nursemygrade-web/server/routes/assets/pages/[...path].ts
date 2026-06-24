// In dev, proxy /assets/pages/* from the live site — these are legacy static
// images embedded in imported content that don't live in public/ locally.
// In production nginx serves the same files from the deployed public dir.
import https from 'node:https'

export default defineEventHandler((event) => {
  if (!process.dev) return  // let nginx/static handler serve in production

  const hostname = 'nursemygrade.com'

  return new Promise<Buffer>((resolve, reject) => {
    const req = https.get(
      { hostname, path: event.path, headers: { 'User-Agent': 'Nuxt-Dev-Proxy/1.0' } },
      (res) => {
        const chunks: Buffer[] = []
        res.on('data', (c: Buffer) => chunks.push(c))
        res.on('end', () => {
          const buf = Buffer.concat(chunks)
          setResponseStatus(event, res.statusCode ?? 200)
          setResponseHeader(event, 'content-type', res.headers['content-type'] ?? 'image/webp')
          setResponseHeader(event, 'cache-control', 'public, max-age=604800, immutable')
          resolve(buf)
        })
      },
    )
    req.on('error', reject)
  })
})
