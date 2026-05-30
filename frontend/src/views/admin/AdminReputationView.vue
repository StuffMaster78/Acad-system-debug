<script setup lang="ts">
import { ref, onMounted } from "vue";
import { RefreshCw, Search, X, Trophy, Star, ShieldCheck, Users } from "@lucide/vue";
import { useReputationStore } from "@/stores/reputation";

const store = useReputationStore();

const limit = ref(50);
const lookupId = ref("");

onMounted(() => store.fetchLeaderboard(limit.value));

function refresh() {
  store.fetchLeaderboard(limit.value);
}

async function runLookup() {
  const id = lookupId.value.trim();
  if (!id) return;
  await store.lookupWriter(id);
}

function clearLookup() {
  lookupId.value = "";
  store.clearWriterLookup();
}

function ratingColor(rating: string) {
  const r = parseFloat(rating);
  if (r >= 4.5) return "text-emerald-600";
  if (r >= 3.5) return "text-amber-600";
  return "text-rose-600";
}

function trustColor(score: string) {
  const s = parseFloat(score);
  if (s >= 80) return "text-emerald-600";
  if (s >= 50) return "text-amber-600";
  return "text-rose-600";
}

function rankMedal(rank: number) {
  return rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : null;
}
</script>

<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-ink">Writer Reputation</h1>
        <p class="text-sm text-graphite mt-0.5">Live snapshot of writer ratings, trust scores, and global rankings.</p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <select
          v-model.number="limit"
          @change="refresh"
          class="focus-ring rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
        >
          <option :value="25">Top 25</option>
          <option :value="50">Top 50</option>
          <option :value="100">Top 100</option>
          <option :value="200">Top 200</option>
        </select>
        <button
          @click="refresh"
          :disabled="store.isLoadingLeaderboard"
          class="focus-ring flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm text-graphite hover:text-ink disabled:opacity-50 transition-colors"
        >
          <RefreshCw class="size-4" :class="{ 'animate-spin': store.isLoadingLeaderboard }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Stat chips -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 space-y-1">
        <div class="flex items-center gap-2 text-xs font-medium text-graphite">
          <Trophy class="size-3.5 text-amber-500" /> Total ranked
        </div>
        <p class="text-2xl font-bold text-ink">
          {{ store.isLoadingLeaderboard ? "—" : store.leaderboardTotal }}
        </p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 space-y-1">
        <div class="flex items-center gap-2 text-xs font-medium text-graphite">
          <Star class="size-3.5 text-amber-400" /> Highest rating
        </div>
        <p class="text-2xl font-bold" :class="store.topRating ? ratingColor(store.topRating) : 'text-ink'">
          {{ store.topRating ?? "—" }}
        </p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 space-y-1">
        <div class="flex items-center gap-2 text-xs font-medium text-graphite">
          <Star class="size-3.5 text-slate-400" /> Avg rating (shown)
        </div>
        <p class="text-2xl font-bold text-ink">{{ store.avgRating ?? "—" }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 space-y-1">
        <div class="flex items-center gap-2 text-xs font-medium text-graphite">
          <ShieldCheck class="size-3.5 text-signal" /> Avg trust score
        </div>
        <p class="text-2xl font-bold text-ink">{{ store.avgTrustScore ?? "—" }}</p>
      </div>
    </div>

    <!-- Writer lookup -->
    <div class="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
      <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
        <Search class="size-4 text-graphite" /> Writer lookup
      </h2>
      <div class="flex gap-2">
        <input
          v-model="lookupId"
          type="text"
          placeholder="Paste writer UUID…"
          class="focus-ring flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono"
          @keydown.enter="runLookup"
        />
        <button
          @click="runLookup"
          :disabled="!lookupId.trim() || store.isLoadingWriter"
          class="focus-ring rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-50"
        >
          {{ store.isLoadingWriter ? "Looking up…" : "Look up" }}
        </button>
        <button
          v-if="store.writerSnapshot || store.writerError"
          @click="clearLookup"
          class="focus-ring rounded-lg border border-slate-200 px-3 py-2 text-sm text-graphite hover:text-ink"
        >
          <X class="size-4" />
        </button>
      </div>

      <!-- Error -->
      <p v-if="store.writerError" class="text-sm text-rose-600">{{ store.writerError }}</p>

      <!-- Result -->
      <div v-if="store.writerSnapshot" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 space-y-0.5">
          <p class="text-xs text-graphite">Rating</p>
          <p class="text-xl font-bold" :class="ratingColor(store.writerSnapshot.rating)">
            {{ store.writerSnapshot.rating }}
          </p>
        </div>
        <div class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 space-y-0.5">
          <p class="text-xs text-graphite">Trust score</p>
          <p class="text-xl font-bold" :class="trustColor(store.writerSnapshot.trust_score)">
            {{ store.writerSnapshot.trust_score }}
          </p>
        </div>
        <div class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 space-y-0.5">
          <p class="text-xs text-graphite">Reviews</p>
          <p class="text-xl font-bold text-ink">{{ store.writerSnapshot.review_count }}</p>
          <p class="text-xs text-graphite">{{ store.writerSnapshot.verified_review_count }} verified</p>
        </div>
        <div v-if="store.writerRank" class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 space-y-0.5">
          <p class="text-xs text-graphite">Global rank</p>
          <p class="text-xl font-bold text-ink">
            {{ store.writerRank.rank !== null ? `#${store.writerRank.rank}` : "Unranked" }}
          </p>
        </div>
        <div v-if="store.writerRank?.percentile" class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 space-y-0.5">
          <p class="text-xs text-graphite">Percentile</p>
          <p class="text-xl font-bold text-ink">{{ store.writerRank.percentile }}%</p>
        </div>
      </div>
    </div>

    <!-- Leaderboard table -->
    <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
        <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
          <Users class="size-4 text-graphite" /> Global leaderboard
        </h2>
        <span class="text-xs text-graphite">{{ store.leaderboard.length }} writers shown</span>
      </div>

      <div v-if="store.isLoadingLeaderboard" class="py-16 text-center text-graphite animate-pulse">
        Loading leaderboard…
      </div>
      <div v-else-if="!store.leaderboard.length" class="py-16 text-center text-sm text-graphite">
        No reputation data yet. Run the snapshot task to populate rankings.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-xs font-semibold text-graphite uppercase tracking-wide">
            <tr>
              <th class="w-12 px-4 py-3 text-center">Rank</th>
              <th class="px-4 py-3 text-left">Writer ID</th>
              <th class="px-4 py-3 text-center">Rating</th>
              <th class="px-4 py-3 text-center">Reviews</th>
              <th class="px-4 py-3 text-center">Trust score</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="entry in store.leaderboard"
              :key="entry.writer_id"
              :class="entry.rank <= 3 ? 'bg-amber-50/40' : 'hover:bg-slate-50'"
              class="transition-colors"
            >
              <!-- Rank -->
              <td class="px-4 py-3 text-center">
                <span v-if="rankMedal(entry.rank)" class="text-base leading-none">{{ rankMedal(entry.rank) }}</span>
                <span v-else class="text-xs font-mono text-graphite">#{{ entry.rank }}</span>
              </td>

              <!-- Writer ID -->
              <td class="px-4 py-3">
                <span class="font-mono text-xs text-graphite select-all">{{ entry.writer_id }}</span>
              </td>

              <!-- Rating -->
              <td class="px-4 py-3 text-center">
                <span class="font-semibold" :class="ratingColor(entry.rating)">{{ entry.rating }}</span>
                <span class="ml-1 text-amber-400 text-xs">★</span>
              </td>

              <!-- Reviews -->
              <td class="px-4 py-3 text-center">
                <span class="font-mono text-ink">{{ entry.review_count }}</span>
              </td>

              <!-- Trust score -->
              <td class="px-4 py-3 text-center">
                <span
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                  :class="
                    parseFloat(entry.trust_score) >= 80
                      ? 'bg-emerald-100 text-emerald-700'
                      : parseFloat(entry.trust_score) >= 50
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-rose-100 text-rose-700'
                  "
                >
                  {{ entry.trust_score }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
