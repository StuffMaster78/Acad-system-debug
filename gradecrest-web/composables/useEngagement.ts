export interface EngagementStats {
  views: number
  shares: number
  reactions: { type: string; count: number }[]
}

export type ReactionType = 'helpful' | 'love' | 'insightful'

export function useEngagement(slug: string) {
  const api = useApi()

  const pageId   = ref<number | null>(null)
  const stats    = ref<EngagementStats | null>(null)
  const myReact  = ref<ReactionType | null>(null)
  const ready    = ref(false)

  const REACT_KEY = `gc-react-${slug}`

  onMounted(async () => {
    myReact.value = (localStorage.getItem(REACT_KEY) as ReactionType | null)

    try {
      const result = await api<{ items: { id: number }[] }>(
        `/wagtail/api/v2/pages/?type=cms_blog.BlogPostPage&slug=${slug}&fields=id`,
      )
      if (result?.items?.[0]?.id) {
        pageId.value = result.items[0].id
        trackView()
        await fetchStats()
      }
    } catch {
      // Not in CMS — engagement stays hidden
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

    myReact.value = undo ? null : type
    if (myReact.value) localStorage.setItem(REACT_KEY, myReact.value)
    else               localStorage.removeItem(REACT_KEY)

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
    } catch {
      myReact.value = prev
      if (prev) localStorage.setItem(REACT_KEY, prev)
      else      localStorage.removeItem(REACT_KEY)
      stats.value = statsSnapshot
    }
  }

  function reactionCount(type: ReactionType): number {
    return stats.value?.reactions?.find(r => r.type === type)?.count ?? 0
  }

  function fmtCount(n: number): string {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
    return String(n)
  }

  return { pageId, stats, myReact, ready, react, reactionCount, fmtCount }
}
