<template>
  <div class="p-6 space-y-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Writer Rewards</h1>
      <p class="text-sm text-gray-500 mt-0.5">Leaderboard, reward analytics, rules, and payout reconciliation</p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex gap-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'pb-3 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >{{ tab.label }}</button>
      </nav>
    </div>

    <!-- ── Leaderboard ────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'leaderboard'" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Writers ranked by composite performance score.</p>
        <div class="flex items-center gap-3">
          <label class="text-xs text-gray-500">Limit</label>
          <select v-model.number="leaderboardLimit" @change="loadLeaderboard" class="input text-sm w-24">
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <button @click="loadLeaderboard" :disabled="loadingLeaderboard" class="btn-primary text-sm">Refresh</button>
        </div>
      </div>

      <div v-if="loadingLeaderboard" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!leaderboard.length" class="text-center py-10 text-gray-400 text-sm">No leaderboard data.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-center w-12">#</th>
              <th class="px-3 py-2 text-left">Writer</th>
              <th class="px-3 py-2 text-center">Rating</th>
              <th class="px-3 py-2 text-center">Trust</th>
              <th class="px-3 py-2 text-center">Percentile</th>
              <th class="px-3 py-2 text-center">Orders</th>
              <th class="px-3 py-2 text-left">Badges</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="entry in leaderboard"
              :key="entry.writer_id"
              :class="entry.leaderboard_position <= 3 ? 'bg-amber-50/40' : 'hover:bg-gray-50'"
            >
              <td class="px-3 py-2 text-center">
                <span v-if="entry.leaderboard_position === 1" class="text-lg"></span>
                <span v-else-if="entry.leaderboard_position === 2" class="text-lg"></span>
                <span v-else-if="entry.leaderboard_position === 3" class="text-lg"></span>
                <span v-else class="text-gray-500 font-mono text-xs">{{ entry.leaderboard_position }}</span>
              </td>
              <td class="px-3 py-2 font-medium text-gray-800">{{ entry.writer_name }}</td>
              <td class="px-3 py-2 text-center">
                <span class="font-semibold text-indigo-700">{{ parseFloat(entry.rating).toFixed(1) }}</span>
                <span class="text-xs text-gray-400 ml-1">({{ entry.review_count }})</span>
              </td>
              <td class="px-3 py-2 text-center">
                <span :class="trustScoreClass(entry.trust_score)" class="text-xs font-semibold px-2 py-0.5 rounded-full">
                  {{ parseFloat(entry.trust_score).toFixed(0) }}
                </span>
              </td>
              <td class="px-3 py-2 text-center text-gray-600 text-xs">
                {{ parseFloat(entry.percentile_rank).toFixed(1) }}%
              </td>
              <td class="px-3 py-2 text-center text-gray-700">{{ entry.completed_orders }}</td>
              <td class="px-3 py-2">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="badge in entry.badges.slice(0, 3)"
                    :key="badge"
                    class="text-xs bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded"
                  >{{ badge }}</span>
                  <span v-if="entry.badges.length > 3" class="text-xs text-gray-400">+{{ entry.badges.length - 3 }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>

    <!-- ── Analytics ──────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'analytics'" class="space-y-4">
      <div v-if="loadingAnalytics" class="text-center py-10 text-gray-400">Loading…</div>
      <template v-else-if="analytics">
        <!-- Summary cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg border border-gray-200 p-4 space-y-1">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Total Rewards</p>
            <p class="text-2xl font-bold text-gray-900">{{ analytics.total_rewards.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 space-y-1">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Issued</p>
            <p class="text-2xl font-bold text-green-700">{{ analytics.issued_rewards.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 space-y-1">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Revoked</p>
            <p class="text-2xl font-bold text-red-600">{{ analytics.revoked_rewards.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 space-y-1">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Total Amount</p>
            <p class="text-2xl font-bold text-indigo-700">${{ parseFloat(analytics.total_reward_amount).toLocaleString() }}</p>
            <p class="text-xs text-gray-400">avg ${{ parseFloat(analytics.average_reward_amount).toFixed(2) }}</p>
          </div>
        </div>

        <!-- Top reward rules -->
        <section class="bg-white rounded-lg border border-gray-200 p-5">
          <h2 class="font-semibold text-gray-800 mb-4">Top Reward Rules</h2>
          <div v-if="!analytics.top_reward_rules.length" class="text-sm text-gray-400">No data.</div>
          <div v-else class="space-y-2">
            <div
              v-for="rule in analytics.top_reward_rules"
              :key="rule.reward_rule__name"
              class="flex items-center gap-3"
            >
              <span class="text-sm text-gray-700 flex-1">{{ rule.reward_rule__name ?? '(unnamed)' }}</span>
              <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                <div
                  class="bg-indigo-500 h-2 rounded-full"
                  :style="{ width: barWidth(rule.total, analytics.top_reward_rules) + '%' }"
                />
              </div>
              <span class="text-xs text-gray-500 w-10 text-right">{{ rule.total }}</span>
            </div>
          </div>
        </section>

        <!-- Top writers -->
        <section class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div class="px-5 py-4 border-b border-gray-100">
            <h2 class="font-semibold text-gray-800">Top Rewarded Writers</h2>
          </div>
          <div v-if="!analytics.top_writers.length" class="p-5 text-sm text-gray-400">No data.</div>
          <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
            <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th class="px-3 py-2 text-left">Writer</th>
                <th class="px-3 py-2 text-right">Rewards</th>
                <th class="px-3 py-2 text-right">Total Amount</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="w in analytics.top_writers" :key="w.writer__id" class="hover:bg-gray-50">
                <td class="px-3 py-2 text-gray-800">{{ w.writer__display_name || `#${w.writer__id}` }}</td>
                <td class="px-3 py-2 text-right text-gray-600">{{ w.total_rewards }}</td>
                <td class="px-3 py-2 text-right font-semibold text-green-700">${{ parseFloat(w.total_amount).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        </section>
      </template>

      <!-- Rules list -->
      <section class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-semibold text-gray-800">Active Reward Rules</h2>
          <span class="text-xs text-gray-400">{{ rules.length }} rule{{ rules.length !== 1 ? 's' : '' }}</span>
        </div>
        <div v-if="loadingRules" class="p-5 text-center text-gray-400 text-sm">Loading…</div>
        <div v-else-if="!rules.length" class="p-5 text-sm text-gray-400">No active rules. Rules are scoped per website.</div>
        <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Name</th>
              <th class="px-3 py-2 text-left">Type</th>
              <th class="px-3 py-2 text-right">Reward</th>
              <th class="px-3 py-2 text-left">Badge</th>
              <th class="px-3 py-2 text-center">Repeatable</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="rule in rules" :key="rule.id" class="hover:bg-gray-50">
              <td class="px-3 py-2">
                <p class="font-medium text-gray-800">{{ rule.name }}</p>
                <p v-if="rule.description" class="text-xs text-gray-400 mt-0.5 truncate max-w-xs">{{ rule.description }}</p>
              </td>
              <td class="px-3 py-2 text-xs font-mono text-gray-600">{{ rule.rule_type }}</td>
              <td class="px-3 py-2 text-right font-semibold text-green-700">${{ parseFloat(rule.reward_amount).toFixed(2) }}</td>
              <td class="px-3 py-2">
                <span v-if="rule.badge_name" class="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded">{{ rule.badge_name }}</span>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
              <td class="px-3 py-2 text-center">
                <span :class="rule.is_repeatable ? 'text-green-600' : 'text-gray-400'" class="text-xs">{{ rule.is_repeatable ? '' : '' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </section>
    </div>

    <!-- ── Reconciliation ─────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'reconciliation'" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Reconcile payout batch totals against ledger and cleared amounts.</p>
        <button @click="showRunForm = true" class="btn-primary text-sm">Run Reconciliation</button>
      </div>

      <div v-if="loadingReports" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!reports.length" class="text-center py-10 text-gray-400 text-sm">No reconciliation reports yet.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Batch</th>
              <th class="px-3 py-2 text-right">Ledger</th>
              <th class="px-3 py-2 text-right">Payout</th>
              <th class="px-3 py-2 text-right">Cleared</th>
              <th class="px-3 py-2 text-right">Mismatch</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="r in reports" :key="r.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-700 font-mono text-xs">Batch #{{ r.payout_batch }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-700">${{ r.total_ledger_amount }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-700">${{ r.total_payout_amount }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-700">${{ r.total_cleared_amount }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs font-semibold" :class="parseFloat(r.mismatch_amount) === 0 ? 'text-green-600' : 'text-red-600'">
                {{ parseFloat(r.mismatch_amount) === 0 ? '—' : '$' + r.mismatch_amount }}
              </td>
              <td class="px-3 py-2">
                <span :class="reconcStatusClass(r.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ r.status }}</span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ fmtDate(r.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- Run reconciliation dialog -->
      <div v-if="showRunForm" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
          <h3 class="font-semibold text-gray-800">Run Reconciliation</h3>
          <div class="space-y-3">
            <WebsiteSelectorBar
              v-model="runForm.website_id"
              label="Website:"
            />
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Payout Batch ID</label>
              <input v-model.number="runForm.payout_batch_id" type="number" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Ledger Total ($)</label>
              <input v-model="runForm.ledger_total" type="number" step="0.01" class="input" placeholder="0.00" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Payout Total ($)</label>
              <input v-model="runForm.payout_total" type="number" step="0.01" class="input" placeholder="0.00" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Cleared Total ($)</label>
              <input v-model="runForm.cleared_total" type="number" step="0.01" class="input" placeholder="0.00" />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button @click="showRunForm = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
            <button
              @click="doRunReconciliation"
              :disabled="actioning || !runForm.website_id || !runForm.payout_batch_id"
              class="btn-primary text-sm"
            >{{ actioning ? 'Running…' : 'Run' }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <!-- ── Badge Management Tab ────────────────────────────────────────── -->
    <div v-if="activeTab === 'badges'" class="space-y-4">
      <p class="text-sm text-graphite">Manually award or revoke badges for individual writers.</p>

      <!-- Award form -->
      <div class="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
        <h3 class="text-sm font-semibold text-ink">Award a badge</h3>
        <div class="grid gap-3 sm:grid-cols-3">
          <div>
            <label class="block text-xs font-medium text-graphite mb-1">Writer registration ID</label>
            <input v-model="badgeForm.registration_id" type="text" placeholder="e.g. WR-00042"
              class="focus-ring h-9 w-full rounded-md border border-slate-200 px-3 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-graphite mb-1">Badge</label>
            <select v-model="badgeForm.badge_id"
              class="focus-ring h-9 w-full rounded-md border border-slate-200 px-3 text-sm bg-white">
              <option :value="null">— select badge —</option>
              <option v-for="b in availableBadges" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-graphite mb-1">Notes (optional)</label>
            <input v-model="badgeForm.notes" type="text" placeholder="Reason for manual award"
              class="focus-ring h-9 w-full rounded-md border border-slate-200 px-3 text-sm" />
          </div>
        </div>
        <button
          class="inline-flex items-center gap-1.5 rounded-md bg-berry px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          :disabled="badgeSaving || !badgeForm.registration_id || !badgeForm.badge_id"
          @click="awardBadge"
        >
          {{ badgeSaving ? "Awarding…" : "Award badge" }}
        </button>
        <p v-if="badgeNotice" class="text-sm text-emerald-700">{{ badgeNotice }}</p>
        <p v-if="badgeError" class="text-sm text-rose-700">{{ badgeError }}</p>
      </div>

      <!-- Writer badge lookup -->
      <div class="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
        <h3 class="text-sm font-semibold text-ink">Writer badge history</h3>
        <div class="flex gap-3">
          <input v-model="badgeLookupId" type="text" placeholder="Writer registration ID"
            class="focus-ring h-9 w-full max-w-xs rounded-md border border-slate-200 px-3 text-sm" />
          <button class="inline-flex items-center rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold hover:bg-slate-50"
            @click="loadWriterBadges">Lookup</button>
        </div>
        <div v-if="writerBadges.length" class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs text-graphite uppercase">
              <tr>
                <th class="px-3 py-2 text-left">Badge</th>
                <th class="px-3 py-2 text-left">Type</th>
                <th class="px-3 py-2 text-left">Issued</th>
                <th class="px-3 py-2 text-left">Source</th>
                <th class="px-3 py-2 text-left">Notes</th>
                <th class="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="wb in writerBadges" :key="wb.id" class="hover:bg-slate-50">
                <td class="px-3 py-2 font-medium">{{ wb.badge_name }}</td>
                <td class="px-3 py-2 capitalize text-graphite">{{ wb.badge_type }}</td>
                <td class="px-3 py-2 text-graphite">{{ wb.issued_at ? new Date(wb.issued_at).toLocaleDateString() : '—' }}</td>
                <td class="px-3 py-2">
                  <span class="rounded px-1.5 py-0.5 text-xs" :class="wb.is_auto_awarded ? 'bg-slate-100 text-graphite' : 'bg-berry/10 text-berry'">
                    {{ wb.is_auto_awarded ? 'Auto' : 'Manual' }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-graphite">{{ wb.notes || '—' }}</td>
                <td class="px-3 py-2">
                  <button class="text-xs text-rose-600 hover:underline" @click="revokeBadge(wb.id)">Revoke</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else-if="badgeLookupId" class="text-sm text-graphite">No badges found.</p>
      </div>
    </div>

    <div
      v-if="toast"
      class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-sm text-white"
      :class="toast.type === 'error' ? 'bg-red-600' : 'bg-green-600'"
    >{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import WebsiteSelectorBar from "@/components/ui/WebsiteSelectorBar.vue";
import { adminRewardsApi } from "@/api/adminRewards";
import type { LeaderboardEntry, RewardRule, RewardAnalyticsOverview, ReconciliationReport } from "@/api/adminRewards";

const tabs = [
  { key: "leaderboard", label: "Leaderboard" },
  { key: "analytics", label: "Analytics & Rules" },
  { key: "reconciliation", label: "Reconciliation" },
  { key: "badges", label: "Badge Management" },
] as const;

const activeTab = ref("leaderboard");

// ── Leaderboard ────────────────────────────────────────────────────────────
const leaderboard = ref<LeaderboardEntry[]>([]);
const loadingLeaderboard = ref(false);
const leaderboardLimit = ref(50);

async function loadLeaderboard() {
  loadingLeaderboard.value = true;
  try {
    const resp = await adminRewardsApi.leaderboard(leaderboardLimit.value);
    leaderboard.value = resp.data;
  } catch {
    showToast("Failed to load leaderboard", "error");
  } finally {
    loadingLeaderboard.value = false;
  }
}

function trustScoreClass(score: string) {
  const n = parseFloat(score);
  if (n >= 80) return "bg-green-100 text-green-700";
  if (n >= 60) return "bg-blue-100 text-blue-700";
  if (n >= 40) return "bg-amber-100 text-amber-700";
  return "bg-red-100 text-red-700";
}

// ── Analytics ──────────────────────────────────────────────────────────────
const analytics = ref<RewardAnalyticsOverview | null>(null);
const rules = ref<RewardRule[]>([]);
const loadingAnalytics = ref(false);
const loadingRules = ref(false);

async function loadAnalytics() {
  loadingAnalytics.value = true;
  try {
    const resp = await adminRewardsApi.analyticsOverview();
    analytics.value = resp.data;
  } catch {
    showToast("Failed to load analytics", "error");
  } finally {
    loadingAnalytics.value = false;
  }
}

async function loadRules() {
  loadingRules.value = true;
  try {
    const resp = await adminRewardsApi.rules();
    const data = resp.data;
    rules.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load rules", "error");
  } finally {
    loadingRules.value = false;
  }
}

function barWidth(value: number, items: { total: number }[]) {
  const max = Math.max(...items.map((i) => i.total), 1);
  return Math.round((value / max) * 100);
}

// ── Reconciliation ─────────────────────────────────────────────────────────
const reports = ref<ReconciliationReport[]>([]);
const loadingReports = ref(false);
const showRunForm = ref(false);
const actioning = ref(false);

const runForm = reactive({
  website_id: null as number | null,
  payout_batch_id: null as number | null,
  ledger_total: "",
  payout_total: "",
  cleared_total: "",
});

async function loadReports() {
  loadingReports.value = true;
  try {
    const resp = await adminRewardsApi.reconciliationReports();
    const data = resp.data;
    reports.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load reports", "error");
  } finally {
    loadingReports.value = false;
  }
}

async function doRunReconciliation() {
  if (!runForm.website_id || !runForm.payout_batch_id) return;
  actioning.value = true;
  try {
    const resp = await adminRewardsApi.runReconciliation({
      website_id: runForm.website_id,
      payout_batch_id: runForm.payout_batch_id,
      ledger_total: runForm.ledger_total || "0.00",
      payout_total: runForm.payout_total || "0.00",
      cleared_total: runForm.cleared_total || "0.00",
    });
    reports.value.unshift(resp.data);
    showRunForm.value = false;
    Object.assign(runForm, { payout_batch_id: null, ledger_total: "", payout_total: "", cleared_total: "" });
    showToast("Reconciliation complete");
  } catch {
    showToast("Reconciliation failed", "error");
  } finally {
    actioning.value = false;
  }
}

function reconcStatusClass(status: string) {
  const map: Record<string, string> = {
    matched: "bg-green-100 text-green-700",
    mismatch: "bg-red-100 text-red-700",
    pending: "bg-amber-100 text-amber-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

// ── Helpers ────────────────────────────────────────────────────────────────
const toast = ref<{ message: string; type: "success" | "error" } | null>(null);

function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

function fmtDate(ts: string) {
  return new Date(ts).toLocaleDateString(undefined, { dateStyle: "medium" });
}

onMounted(() => {
  loadLeaderboard();
  loadAnalytics();
  loadRules();
  loadReports();
  loadAvailableBadges();
});

// ── Badge Management ────────────────────────────────────────────────────────
import { api, apiPath } from "@/api/client";

interface BadgeDef { id: number; name: string; type: string }
interface WriterBadgeRecord {
  id: number; badge_id: number; badge_name: string; badge_type: string;
  is_auto_awarded: boolean; issued_at: string | null; notes: string | null;
}

const availableBadges = ref<BadgeDef[]>([]);
const badgeForm = reactive({ registration_id: "", badge_id: null as number | null, notes: "" });
const badgeSaving = ref(false);
const badgeNotice = ref("");
const badgeError = ref("");
const badgeLookupId = ref("");
const writerBadges = ref<WriterBadgeRecord[]>([]);

async function loadAvailableBadges() {
  try {
    const { data } = await api.get<BadgeDef[]>(apiPath("/writer-management/badges/"));
    availableBadges.value = Array.isArray(data) ? data : (data as { results: BadgeDef[] }).results ?? [];
  } catch { /* non-fatal */ }
}

async function awardBadge() {
  badgeNotice.value = "";
  badgeError.value = "";
  if (!badgeForm.registration_id || !badgeForm.badge_id) return;
  badgeSaving.value = true;
  try {
    await api.post(apiPath(`/writer-management/writers/${badgeForm.registration_id}/badges/award/`), {
      badge_id: badgeForm.badge_id,
      notes: badgeForm.notes,
    });
    badgeNotice.value = "Badge awarded successfully.";
    Object.assign(badgeForm, { registration_id: "", badge_id: null, notes: "" });
    if (badgeLookupId.value) await loadWriterBadges();
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    badgeError.value = msg || "Failed to award badge.";
  } finally {
    badgeSaving.value = false;
  }
}

async function loadWriterBadges() {
  if (!badgeLookupId.value) return;
  try {
    const { data } = await api.get<WriterBadgeRecord[]>(
      apiPath(`/writer-management/writers/${badgeLookupId.value}/badges/`)
    );
    writerBadges.value = Array.isArray(data) ? data : (data as { results: WriterBadgeRecord[] }).results ?? [];
  } catch { writerBadges.value = []; }
}

async function revokeBadge(writerbadgeId: number) {
  const reason = prompt("Reason for revoking this badge:");
  if (reason === null) return;
  try {
    await api.post(apiPath(`/writer-management/writer-badges/${writerbadgeId}/revoke/`), { reason });
    showToast("Badge revoked.", "success");
    if (badgeLookupId.value) await loadWriterBadges();
  } catch {
    showToast("Failed to revoke badge.", "error");
  }
}
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent;
}
.btn-primary {
  @apply px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition;
}
</style>
