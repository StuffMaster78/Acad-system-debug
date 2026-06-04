/**
 * usePageEngagement
 *
 * Wires up engagement tracking for a CMS page:
 *   - Fires a view beacon on mount
 *   - Sends scroll-depth + time-on-page updates every 30 s
 *   - Exposes reactive summary, react(), share(), and bookmark()
 */
import { onMounted, onUnmounted, ref } from "vue";
import { engagementApi, type EngagementSummary, type ReactionType, type SharePlatform } from "@/api/engagement";
import { useAuthStore } from "@/stores/auth";

export function usePageEngagement(pageId: number | null | undefined) {
  const summary = ref<EngagementSummary | null>(null);
  const isMutating = ref(false);
  const auth = useAuthStore();

  // Resolved content-type metadata (fetched alongside summary)
  let _ctId: number | null = null;
  let _objId: number | null = null;

  // View tracking state
  let _viewStartTs = Date.now();
  let _maxScroll = 0;
  let _beaconInterval: ReturnType<typeof setInterval> | null = null;
  let _sessionId = sessionStorage.getItem("_eng_sid") || Math.random().toString(36).slice(2);
  sessionStorage.setItem("_eng_sid", _sessionId);

  // ── Scroll tracking ─────────────────────────────────────────────────────
  function _onScroll() {
    const scrolled = window.scrollY + window.innerHeight;
    const total = document.documentElement.scrollHeight;
    const pct = total > 0 ? Math.round((scrolled / total) * 100) : 0;
    _maxScroll = Math.max(_maxScroll, pct);
  }

  // ── Beacon: time + scroll every 30 s ────────────────────────────────────
  function _sendBeacon() {
    if (!pageId) return;
    const timeOnPage = Math.round((Date.now() - _viewStartTs) / 1000);
    engagementApi.trackView({
      page_id: pageId,
      time_on_page: timeOnPage,
      scroll_depth: _maxScroll,
    }).catch(() => {});
  }

  // ── Load summary ─────────────────────────────────────────────────────────
  async function loadSummary() {
    if (!pageId) return;
    try {
      const { data } = await engagementApi.getSummary(pageId);
      summary.value = data;
    } catch {
      // non-fatal — leave summary null
    }
  }

  // ── React ─────────────────────────────────────────────────────────────────
  async function react(reactionType: ReactionType) {
    if (!_ctId || !_objId || isMutating.value) return;
    isMutating.value = true;
    try {
      const { data } = await engagementApi.react({
        content_type_id: _ctId,
        object_id: _objId,
        reaction_type: reactionType,
      });
      if (summary.value) {
        // Optimistically update counts
        const prev = summary.value.user_reaction;
        if (prev && prev !== reactionType) {
          (summary.value as Record<string, number>)[prev + "_count"] = Math.max(
            0,
            ((summary.value as Record<string, number>)[prev + "_count"] || 0) - 1
          );
        }
        if (data.reaction_type) {
          (summary.value as Record<string, number>)[reactionType + "_count"] =
            ((summary.value as Record<string, number>)[reactionType + "_count"] || 0) +
            (prev === reactionType ? -1 : 1);
        }
        summary.value.user_reaction = data.reaction_type;
      }
    } finally {
      isMutating.value = false;
    }
  }

  // ── Share ─────────────────────────────────────────────────────────────────
  async function share(platform: SharePlatform) {
    if (!_ctId || !_objId) return;
    engagementApi.share({ content_type_id: _ctId, object_id: _objId, platform }).catch(() => {});
    if (summary.value) summary.value.total_shares += 1;
  }

  // ── Bookmark ─────────────────────────────────────────────────────────────
  async function bookmark() {
    if (!_ctId || !_objId || !auth.isAuthenticated || isMutating.value) return;
    isMutating.value = true;
    try {
      const { data } = await engagementApi.bookmark({ content_type_id: _ctId, object_id: _objId });
      if (summary.value) summary.value.user_bookmarked = data.bookmarked;
    } finally {
      isMutating.value = false;
    }
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  onMounted(async () => {
    if (!pageId) return;
    // Fire initial view beacon
    engagementApi.trackView({ page_id: pageId }).catch(() => {});
    await loadSummary();
    // After summary loaded we have the content_type_id via page_id resolution
    // The summary endpoint resolves it; we re-fire with explicit IDs if needed
    window.addEventListener("scroll", _onScroll, { passive: true });
    _beaconInterval = setInterval(_sendBeacon, 30_000);
  });

  onUnmounted(() => {
    window.removeEventListener("scroll", _onScroll);
    if (_beaconInterval) clearInterval(_beaconInterval);
    _sendBeacon(); // Final beacon on leave
  });

  return { summary, isMutating, loadSummary, react, share, bookmark };
}
