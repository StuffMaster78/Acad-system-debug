// Client-side only — engagement data is not baked into SSG.
// Looks up the Wagtail page ID from the slug, then tracks the view and
// fetches live stats. Falls back silently if the slug is not in the CMS
// (e.g. static seed posts not yet published to Wagtail).

export interface EngagementStats {
  views: number
  shares: number
  reactions: { type: string; count: number }[]
}

export type ReactionType = 'helpful' | 'love' | 'insightful'

export function useEngagement(slug: string) {
  const api = useApi()

  const pageId    = ref<number | null>(null)
  const stats     = ref<EngagementStats | null>(null)
  const myReact   = ref<ReactionType | null>(null)
  const bookmarked = ref(false)
  const ready     = ref(false)   // true once CMS lookup resolves (pass or fail)

  const REACT_KEY    = `nmg-react-${slug}`
  const BOOKMARK_KEY = `nmg-bm-${slug}`

  onMounted(async () => {
    myReact.value   = (localStorage.getItem(REACT_KEY) as ReactionType | null)
    bookmarked.value = localStorage.getItem(BOOKMARK_KEY) === '1'

    try {
      // Resolve slug → Wagtail page ID
      const result = await $fetch<{ items: { id: number }[] }>(
        `/api/v2/pages/?type=cms_blog.BlogPostPage&slug=${slug}&fields=id`,
      )
      if (result?.items?.[0]?.id) {
        pageId.value = result.items[0].id
        // Fire-and-forget view track; fetch stats in parallel
        trackView()
        await fetchStats()
      }
    } catch {
      // Not in CMS yet — engagement UI stays hidden
    } finally {
      ready.value = true
    }
  })

  async function trackView() {
    if (!pageId.value) return
    try {
      await api('/cms-api/engagement/track-view/', {
        method: 'POST',
        body: { page_id: pageId.value },
      })
    } catch { /* silent */ }
  }

  async function fetchStats() {
    if (!pageId.value) return
    try {
      stats.value = await api<EngagementStats>(
        `/cms-api/engagement/page/?page_id=${pageId.value}`,
      )
    } catch { /* silent */ }
  }

  async function react(type: ReactionType) {
    if (!pageId.value) return
    const prev = myReact.value
    const undo = prev === type

    // Optimistic: update selection
    myReact.value = undo ? null : type
    if (myReact.value) localStorage.setItem(REACT_KEY, myReact.value)
    else               localStorage.removeItem(REACT_KEY)

    // Optimistic: update counts
    const statsSnapshot = stats.value
    if (stats.value) {
      stats.value = {
        ...stats.value,
        reactions: stats.value.reactions.map(r => {
          if (r.type === type) return { ...r, count: r.count + (undo ? -1 : 1) }
          if (r.type === prev && prev !== type) return { ...r, count: Math.max(0, r.count - 1) }
          return r
        }),
      }
    } else {
      // Stats not loaded yet — seed a minimal object so the count is visible immediately
      const TYPES: ReactionType[] = ['helpful', 'love', 'insightful']
      stats.value = {
        views: 0, shares: 0,
        reactions: TYPES.map(t => ({ type: t, count: t === type && !undo ? 1 : 0 })),
      }
    }

    try {
      await api('/cms-api/engagement/react/', {
        method: 'POST',
        body: { page_id: pageId.value, reaction: type },
      })
      // Don't re-fetch: EngagementSummary is a nightly aggregate — fetching
      // immediately would overwrite the optimistic count with stale data.
    } catch {
      // Rollback both selection and counts
      myReact.value = prev
      if (prev) localStorage.setItem(REACT_KEY, prev)
      else      localStorage.removeItem(REACT_KEY)
      stats.value = statsSnapshot
    }
  }

  async function toggleBookmark() {
    if (!pageId.value) return
    bookmarked.value = !bookmarked.value
    localStorage.setItem(BOOKMARK_KEY, bookmarked.value ? '1' : '0')
    try {
      await api('/cms-api/engagement/bookmark/', {
        method: 'POST',
        body: { page_id: pageId.value, bookmarked: bookmarked.value },
      })
    } catch {
      bookmarked.value = !bookmarked.value
    }
  }

  function reactionCount(type: ReactionType): number {
    return stats.value?.reactions?.find(r => r.type === type)?.count ?? 0
  }

  function fmtCount(n: number): string {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
    return String(n)
  }

  return {
    pageId,
    stats,
    myReact,
    bookmarked,
    ready,
    react,
    toggleBookmark,
    reactionCount,
    fmtCount,
  }
}
