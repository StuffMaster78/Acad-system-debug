import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
  reputationApi,
  type LeaderboardEntry,
  type WriterSnapshot,
  type WriterRank,
} from "@/api/reputation";

export const useReputationStore = defineStore("reputation", () => {
  // ── Leaderboard ─────────────────────────────────────────────────────────────
  const leaderboard = ref<LeaderboardEntry[]>([]);
  const leaderboardTotal = ref(0);
  const isLoadingLeaderboard = ref(false);

  async function fetchLeaderboard(limit = 50) {
    isLoadingLeaderboard.value = true;
    try {
      const res = await reputationApi.leaderboard(limit);
      leaderboard.value = res.data.results;
      leaderboardTotal.value = res.data.count;
    } catch { leaderboard.value = []; }
    finally { isLoadingLeaderboard.value = false; }
  }

  // ── Derived stats ────────────────────────────────────────────────────────────
  const topRating = computed(() =>
    leaderboard.value.length ? leaderboard.value[0].rating : null,
  );
  const avgRating = computed(() => {
    if (!leaderboard.value.length) return null;
    const sum = leaderboard.value.reduce((acc, e) => acc + parseFloat(e.rating), 0);
    return (sum / leaderboard.value.length).toFixed(2);
  });
  const avgTrustScore = computed(() => {
    if (!leaderboard.value.length) return null;
    const sum = leaderboard.value.reduce((acc, e) => acc + parseFloat(e.trust_score), 0);
    return (sum / leaderboard.value.length).toFixed(2);
  });

  // ── Writer lookup ────────────────────────────────────────────────────────────
  const writerSnapshot = ref<WriterSnapshot | null>(null);
  const writerRank = ref<WriterRank | null>(null);
  const isLoadingWriter = ref(false);
  const writerError = ref("");

  async function lookupWriter(writerId: string) {
    isLoadingWriter.value = true;
    writerSnapshot.value = null;
    writerRank.value = null;
    writerError.value = "";
    try {
      const [snapRes, rankRes] = await Promise.all([
        reputationApi.writerSnapshot(writerId),
        reputationApi.writerRank(writerId),
      ]);
      writerSnapshot.value = snapRes.data;
      writerRank.value = rankRes.data;
    } catch {
      writerError.value = "No reputation record found for this writer ID.";
    } finally {
      isLoadingWriter.value = false;
    }
  }

  function clearWriterLookup() {
    writerSnapshot.value = null;
    writerRank.value = null;
    writerError.value = "";
  }

  return {
    leaderboard,
    leaderboardTotal,
    isLoadingLeaderboard,
    fetchLeaderboard,
    topRating,
    avgRating,
    avgTrustScore,
    writerSnapshot,
    writerRank,
    isLoadingWriter,
    writerError,
    lookupWriter,
    clearWriterLookup,
  };
});
