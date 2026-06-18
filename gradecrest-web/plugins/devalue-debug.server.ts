// TEMPORARY — remove this file once the remaining DevalueError is identified.
// Walks the SSR payload before devalue serialises it and logs any function reference found,
// telling you exactly which useAsyncData/useState key contains a non-serialisable value.
//
// How to use:
//  1. Run `nuxt dev` and visit every page.
//  2. Watch the server terminal for lines like:
//       [devalue-debug] function at data.gc-pricing-config.someKey: setup
//  3. The first segment after "data." or "state." is the useAsyncData/useState key.
//  4. Fix that key's fetcher/initial-value, then delete this file.

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('app:rendered', ({ ssrContext }) => {
    function findFn(v: unknown, path: string, seen = new Set<object>()): void {
      if (typeof v === 'function') {
        console.error(`[devalue-debug] function at ${path}: ${(v as { name?: string }).name || '<anon>'}`)
        return
      }
      if (v !== null && typeof v === 'object') {
        if (seen.has(v)) return
        seen.add(v)
        for (const [k, c] of Object.entries(v as Record<string, unknown>)) {
          findFn(c, `${path}.${k}`, seen)
        }
      }
    }
    findFn(ssrContext?.payload?.data,  'data')
    findFn(ssrContext?.payload?.state, 'state')
  })
})
