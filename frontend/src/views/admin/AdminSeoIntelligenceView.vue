<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  AlertTriangle, BarChart2, Brain, CheckCircle, ChevronRight,
  Globe, Layers, Loader2, Plus, RefreshCw, Save, Search,
  Sparkles, Trash2, X, Zap,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { api, apiPath } from "@/api/client";

// ── Tabs ───────────────────────────────────────────────────────────────────
type Tab = "answers" | "personalization" | "freshness" | "performance";
const activeTab = ref<Tab>("answers");

const notice = ref<{ type: "success" | "error"; msg: string } | null>(null);
function toast(type: "success" | "error", msg: string) {
  notice.value = { type, msg };
  setTimeout(() => { notice.value = null; }, 4000);
}

// ═══════════════════════════════════════════════════════════════════════════════
// AI ANSWER ENGINE — search analytics
// ═══════════════════════════════════════════════════════════════════════════════

interface TopQuery { query: string; count: number; }
interface SearchAnalytics {
  total_searches: number;
  period_days: number;
  top_queries: TopQuery[];
  zero_result_queries: TopQuery[];
}

const searchAnalytics = ref<SearchAnalytics | null>(null);
const searchLoading   = ref(false);
const searchDays      = ref(30);

async function loadSearchAnalytics() {
  searchLoading.value = true;
  try {
    const { data } = await api.get<SearchAnalytics>(
      apiPath(`/cms/intelligence/search-log/?days=${searchDays.value}`),
    );
    searchAnalytics.value = data;
  } catch { toast("error", "Failed to load search analytics."); }
  finally { searchLoading.value = false; }
}

// Live answer preview (admin test)
const previewQuery   = ref("");
const previewLoading = ref(false);
const previewResults = ref<{ title: string; url: string; excerpt: string }[]>([]);

async function runPreview() {
  const q = previewQuery.value.trim();
  if (q.length < 3) return;
  previewLoading.value = true;
  previewResults.value = [];
  try {
    const { data } = await api.get<{ results: typeof previewResults.value }>(
      apiPath(`/cms/intelligence/answers/?q=${encodeURIComponent(q)}`),
    );
    previewResults.value = data.results ?? [];
  } catch { toast("error", "Preview search failed."); }
  finally { previewLoading.value = false; }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONTENT PERSONALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

interface PersonalizationRule {
  id: number; persona: string; persona_display: string;
  utm_source: string; utm_medium: string; utm_campaign: string;
  hero_headline: string; hero_subheadline: string;
  cta_label: string; cta_url: string; trust_badge: string;
  is_active: boolean; priority: number;
}

const PERSONA_OPTIONS = [
  { value: "organic_search", label: "Organic Search" },
  { value: "paid_search",    label: "Paid Search (CPC/PPC)" },
  { value: "social",         label: "Social Media" },
  { value: "email",          label: "Email Campaign" },
  { value: "referral",       label: "Referral / Partner" },
  { value: "affiliate",      label: "Affiliate" },
  { value: "direct",         label: "Direct / Brand" },
  { value: "custom",         label: "Custom UTM Match" },
];

const rules        = ref<PersonalizationRule[]>([]);
const rulesLoading = ref(false);
const savingRule   = ref(false);
const ruleModal    = ref(false);
const editingRuleId = ref<number | null>(null);
const deleteRuleConfirm = ref<number | null>(null);

const ruleDraft = reactive({
  persona: "organic_search", utm_source: "", utm_medium: "", utm_campaign: "",
  hero_headline: "", hero_subheadline: "", cta_label: "", cta_url: "",
  trust_badge: "", is_active: true, priority: 10,
});

async function loadRules() {
  rulesLoading.value = true;
  try {
    const { data } = await api.get<PersonalizationRule[]>(apiPath("/cms/intelligence/personalization/"));
    rules.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { toast("error", "Failed to load personalization rules."); }
  finally { rulesLoading.value = false; }
}

function openNewRule() {
  editingRuleId.value = null;
  Object.assign(ruleDraft, {
    persona: "organic_search", utm_source: "", utm_medium: "", utm_campaign: "",
    hero_headline: "", hero_subheadline: "", cta_label: "", cta_url: "",
    trust_badge: "", is_active: true, priority: 10,
  });
  ruleModal.value = true;
}

function openEditRule(rule: PersonalizationRule) {
  editingRuleId.value = rule.id;
  Object.assign(ruleDraft, {
    persona: rule.persona, utm_source: rule.utm_source, utm_medium: rule.utm_medium,
    utm_campaign: rule.utm_campaign, hero_headline: rule.hero_headline,
    hero_subheadline: rule.hero_subheadline, cta_label: rule.cta_label,
    cta_url: rule.cta_url, trust_badge: rule.trust_badge,
    is_active: rule.is_active, priority: rule.priority,
  });
  ruleModal.value = true;
}

async function saveRule() {
  savingRule.value = true;
  try {
    if (editingRuleId.value) {
      await api.patch(apiPath(`/cms/intelligence/personalization/${editingRuleId.value}/`), ruleDraft);
      toast("success", "Rule updated.");
    } else {
      await api.post(apiPath("/cms/intelligence/personalization/"), ruleDraft);
      toast("success", "Rule created.");
    }
    ruleModal.value = false;
    await loadRules();
  } catch (err: any) {
    toast("error", err?.response?.data?.detail ?? "Failed to save rule.");
  } finally { savingRule.value = false; }
}

async function deleteRule(id: number) {
  try {
    await api.delete(apiPath(`/cms/intelligence/personalization/${id}/`));
    deleteRuleConfirm.value = null;
    await loadRules();
    toast("success", "Rule deleted.");
  } catch { toast("error", "Failed to delete rule."); }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FRESHNESS ALERTS
// ═══════════════════════════════════════════════════════════════════════════════

interface FreshnessAlert {
  id: number; alert_type: string; severity: number; detail: Record<string, unknown>;
  raised_at: string; acknowledged_at: string | null; resolved_at: string | null;
  resolution: string;
  content_object_title?: string;
}

const alerts        = ref<FreshnessAlert[]>([]);
const alertsLoading = ref(false);
const alertsFilter  = ref<"unresolved" | "resolved" | "all">("unresolved");

async function loadAlerts() {
  alertsLoading.value = true;
  try {
    const status = alertsFilter.value === "all" ? "" : `?status=${alertsFilter.value}`;
    const { data } = await api.get<{ results?: FreshnessAlert[]; count?: number } | FreshnessAlert[]>(
      apiPath(`/cms/intelligence/freshness/${status}`),
    );
    alerts.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { toast("error", "Failed to load freshness alerts."); }
  finally { alertsLoading.value = false; }
}

async function resolveAlert(id: number, resolution: string) {
  try {
    await api.post(apiPath(`/cms/intelligence/freshness/${id}/resolve/`), { resolution });
    await loadAlerts();
    toast("success", "Alert resolved.");
  } catch { toast("error", "Failed to resolve alert."); }
}

const SEVERITY_COLOR: Record<number, string> = {
  1: "text-gray-500", 2: "text-blue-600", 3: "text-amber-600", 4: "text-orange-600", 5: "text-red-700",
};

const ALERT_TYPE_LABEL: Record<string, string> = {
  age_threshold:    "Age threshold exceeded",
  position_decline: "Search position declined",
  click_decline:    "Click traffic declined",
  engagement_decline: "Engagement declined",
  editor_flagged:   "Manually flagged",
  topic_event:      "External topic event",
};

// ═══════════════════════════════════════════════════════════════════════════════
// CONTENT PERFORMANCE
// ═══════════════════════════════════════════════════════════════════════════════

interface PerformanceSnapshot {
  id: number; page_title: string; page_slug: string;
  gsc_clicks_30d: number; gsc_impressions_30d: number; gsc_avg_position_30d: number;
  ga4_page_views_30d: number; internal_conversions_30d: number;
  attributed_revenue_30d: string; clicks_delta_pct: number;
  ai_overview_appearances_30d: number; diagnosis: string;
}

const snapshots        = ref<PerformanceSnapshot[]>([]);
const snapshotsLoading = ref(false);
const snapshotMetric   = ref<"clicks" | "views" | "conversions" | "revenue">("clicks");

async function loadSnapshots() {
  snapshotsLoading.value = true;
  try {
    const { data } = await api.get<{ results?: PerformanceSnapshot[] } | PerformanceSnapshot[]>(
      apiPath(`/cms/intelligence/performance/top_performers/?metric=${snapshotMetric.value}`),
    );
    snapshots.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch { toast("error", "Failed to load performance data."); }
  finally { snapshotsLoading.value = false; }
}

const DIAGNOSIS_TONE: Record<string, string> = {
  healthy:            "bg-green-50 text-green-700 border-green-200",
  low_ctr:            "bg-amber-50 text-amber-700 border-amber-200",
  low_engagement:     "bg-orange-50 text-orange-700 border-orange-200",
  no_conversion_path: "bg-red-50 text-red-700 border-red-200",
  declining_position: "bg-rose-50 text-rose-700 border-rose-200",
  not_visible:        "bg-gray-50 text-gray-600 border-gray-200",
};

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(() => {
  loadSearchAnalytics();
  loadRules();
});

watch(activeTab, (t) => {
  if (t === "freshness" && !alerts.value.length) loadAlerts();
  if (t === "performance" && !snapshots.value.length) loadSnapshots();
});

watch(alertsFilter, loadAlerts);
watch(snapshotMetric, loadSnapshots);
watch(searchDays, loadSearchAnalytics);

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <Brain class="w-5 h-5 text-indigo-600" /> SEO &amp; Intelligence
          </h1>
          <p class="text-sm text-gray-500 mt-0.5">AI answer engine, content personalization, freshness alerts, and performance data.</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 mt-4 flex-wrap">
        <button
          v-for="t in [
            { key: 'answers',         label: 'AI Answer Engine', icon: 'Sparkles' },
            { key: 'personalization', label: 'Personalization',  icon: 'Zap' },
            { key: 'freshness',       label: 'Freshness Alerts', icon: 'AlertTriangle' },
            { key: 'performance',     label: 'Performance',      icon: 'BarChart2' },
          ]"
          :key="t.key"
          class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
          :class="activeTab === t.key ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
          @click="activeTab = t.key as Tab"
        >{{ t.label }}</button>
      </div>
    </div>

    <!-- Notice -->
    <div
      v-if="notice"
      class="mx-6 mt-4 px-4 py-3 rounded-lg text-sm font-medium"
      :class="notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >{{ notice.msg }}</div>

    <!-- ══ AI ANSWER ENGINE ═══════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'answers'" class="p-6 space-y-6 max-w-4xl">

      <!-- Live preview -->
      <section class="rounded-xl border border-indigo-100 bg-white p-5">
        <h2 class="text-sm font-semibold text-gray-900 mb-1 flex items-center gap-1.5">
          <Search class="w-4 h-4 text-indigo-500" /> Test the answer engine
        </h2>
        <p class="text-xs text-gray-400 mb-3">Type a question to see what your content returns. This is exactly what visitors see on blog posts.</p>
        <div class="flex gap-2">
          <input
            v-model="previewQuery" type="text" placeholder="e.g. How do I format an APA bibliography?"
            @keydown.enter="runPreview"
            class="flex-1 rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            :disabled="previewLoading || previewQuery.trim().length < 3"
            class="flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-40"
            @click="runPreview"
          >
            <Loader2 v-if="previewLoading" class="w-4 h-4 animate-spin" />
            <Search v-else class="w-4 h-4" />
            Search
          </button>
        </div>
        <div v-if="previewResults.length" class="mt-3 space-y-2">
          <a
            v-for="r in previewResults" :key="r.url" :href="r.url" target="_blank"
            class="flex items-start gap-3 rounded-xl border border-gray-100 p-3 hover:border-indigo-200 hover:bg-indigo-50 transition-all"
          >
            <Globe class="mt-0.5 w-4 h-4 shrink-0 text-indigo-400" />
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-900 line-clamp-1">{{ r.title }}</p>
              <p v-if="r.excerpt" class="text-xs text-gray-500 mt-0.5 line-clamp-2">{{ r.excerpt }}</p>
            </div>
            <ChevronRight class="mt-0.5 w-4 h-4 shrink-0 text-gray-400" />
          </a>
        </div>
        <p v-else-if="previewQuery && !previewLoading" class="mt-3 text-sm text-gray-400">
          No results — add more content or improve blog post excerpts for better matches.
        </p>
      </section>

      <!-- Analytics -->
      <section class="rounded-xl border border-gray-200 bg-white p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
            <BarChart2 class="w-4 h-4 text-gray-500" /> Search analytics
          </h2>
          <div class="flex items-center gap-2">
            <select
              v-model.number="searchDays"
              class="rounded-lg border border-gray-300 px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option :value="7">Last 7 days</option>
              <option :value="30">Last 30 days</option>
              <option :value="90">Last 90 days</option>
            </select>
            <button class="rounded-lg border border-gray-300 p-1 hover:bg-gray-50" @click="loadSearchAnalytics">
              <RefreshCw class="w-4 h-4" :class="searchLoading ? 'animate-spin text-indigo-500' : 'text-gray-400'" />
            </button>
          </div>
        </div>

        <div v-if="searchLoading" class="flex justify-center py-8">
          <Loader2 class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="searchAnalytics" class="space-y-5">
          <!-- Summary stat -->
          <div class="rounded-lg bg-indigo-50 px-4 py-3 flex items-center gap-3">
            <Search class="w-5 h-5 text-indigo-500" />
            <div>
              <p class="text-2xl font-bold text-indigo-900">{{ searchAnalytics.total_searches.toLocaleString() }}</p>
              <p class="text-xs text-indigo-600">searches in the last {{ searchAnalytics.period_days }} days</p>
            </div>
          </div>

          <div class="grid gap-5 sm:grid-cols-2">
            <!-- Top queries -->
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Most searched questions</p>
              <div v-if="searchAnalytics.top_queries.length" class="space-y-1.5">
                <div
                  v-for="q in searchAnalytics.top_queries" :key="q.query"
                  class="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm"
                >
                  <span class="text-gray-700 truncate mr-2">{{ q.query }}</span>
                  <span class="text-xs font-semibold text-indigo-700 shrink-0">{{ q.count }}×</span>
                </div>
              </div>
              <p v-else class="text-sm text-gray-400">No searches yet. Embed AskWidget on blog posts to start collecting queries.</p>
            </div>

            <!-- Zero-result queries -->
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">No-result gaps (content opportunities)</p>
              <div v-if="searchAnalytics.zero_result_queries.length" class="space-y-1.5">
                <div
                  v-for="q in searchAnalytics.zero_result_queries" :key="q.query"
                  class="flex items-center justify-between rounded-lg bg-red-50 border border-red-100 px-3 py-2 text-sm"
                >
                  <span class="text-gray-700 truncate mr-2">{{ q.query }}</span>
                  <span class="text-xs font-semibold text-red-700 shrink-0">{{ q.count }}×</span>
                </div>
                <p class="text-xs text-gray-400 mt-2">These queries return no results — consider writing content that answers them.</p>
              </div>
              <p v-else class="text-sm text-gray-400">No zero-result queries.</p>
            </div>
          </div>
        </div>
        <p v-else class="text-sm text-gray-400 text-center py-6">Search analytics will appear once visitors use the AskWidget on blog posts.</p>
      </section>
    </div>

    <!-- ══ PERSONALIZATION ════════════════════════════════════════════════════ -->
    <div v-else-if="activeTab === 'personalization'" class="p-6 space-y-5 max-w-4xl">

      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">
            Define copy variants per traffic source. When a visitor arrives from a matching UTM channel,
            the homepage and landing pages swap in the personalized headline and CTA.
          </p>
        </div>
        <button
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
          @click="openNewRule"
        >
          <Plus class="w-4 h-4" /> New rule
        </button>
      </div>

      <!-- How it works callout -->
      <div class="rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
        <p class="font-semibold mb-1">How personalization works</p>
        <ol class="list-decimal ml-4 space-y-0.5 text-xs">
          <li>A visitor clicks a campaign link with UTM parameters (e.g., <code>utm_medium=social&utm_source=facebook</code>).</li>
          <li>Their UTM is stored locally on first touch (30-day window).</li>
          <li>The frontend composable matches their UTM to the highest-priority active rule.</li>
          <li>Hero headlines, subheadlines, and CTAs on public pages are swapped out.</li>
        </ol>
      </div>

      <div v-if="rulesLoading" class="flex justify-center py-12">
        <Loader2 class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="rule in rules" :key="rule.id"
          class="rounded-xl border bg-white p-5"
          :class="rule.is_active ? 'border-gray-200' : 'border-dashed border-gray-200 opacity-60'"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <span class="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
                  <Zap class="w-3 h-3" /> {{ rule.persona_display }}
                </span>
                <span v-if="!rule.is_active" class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">Inactive</span>
                <span class="text-xs text-gray-400">Priority {{ rule.priority }}</span>
              </div>
              <p v-if="rule.hero_headline" class="font-semibold text-gray-900">{{ rule.hero_headline }}</p>
              <p v-if="rule.hero_subheadline" class="text-sm text-gray-500 mt-0.5">{{ rule.hero_subheadline }}</p>
              <div v-if="rule.cta_label || rule.trust_badge" class="mt-2 flex flex-wrap gap-2">
                <span v-if="rule.cta_label" class="rounded-full bg-green-50 border border-green-200 px-2.5 py-0.5 text-xs text-green-700 font-medium">CTA: {{ rule.cta_label }}</span>
                <span v-if="rule.trust_badge" class="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-xs text-amber-700">✦ {{ rule.trust_badge }}</span>
              </div>
              <p v-if="rule.utm_source || rule.utm_medium" class="mt-1.5 text-xs text-gray-400">
                Match:
                <span v-if="rule.utm_source">source={{ rule.utm_source }}</span>
                <span v-if="rule.utm_medium"> medium={{ rule.utm_medium }}</span>
                <span v-if="rule.utm_campaign"> campaign={{ rule.utm_campaign }}</span>
              </p>
            </div>
            <div class="flex gap-2 shrink-0">
              <button class="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50" @click="openEditRule(rule)">Edit</button>
              <button
                class="text-xs px-3 py-1.5 border rounded-lg transition-colors"
                :class="deleteRuleConfirm === rule.id ? 'border-red-300 text-red-700 bg-red-50' : 'border-gray-200 text-red-500 hover:bg-red-50'"
                @click="deleteRuleConfirm === rule.id ? deleteRule(rule.id) : (deleteRuleConfirm = rule.id)"
              >{{ deleteRuleConfirm === rule.id ? 'Confirm' : 'Delete' }}</button>
              <button v-if="deleteRuleConfirm === rule.id" class="text-xs text-gray-400 hover:text-gray-700 px-1" @click="deleteRuleConfirm = null">×</button>
            </div>
          </div>
        </div>

        <div v-if="!rules.length" class="rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400 text-sm">
          No personalization rules yet. Create one to start customizing your landing page copy per traffic source.
        </div>
      </div>
    </div>

    <!-- ══ FRESHNESS ALERTS ═══════════════════════════════════════════════════ -->
    <div v-else-if="activeTab === 'freshness'" class="p-6 space-y-5 max-w-4xl">

      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Content pages that have triggered freshness signals and may need updating.</p>
        <div class="flex items-center gap-2">
          <select
            v-model="alertsFilter"
            class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="unresolved">Unresolved</option>
            <option value="resolved">Resolved</option>
            <option value="all">All</option>
          </select>
          <button class="rounded-lg border border-gray-300 p-1.5 hover:bg-gray-50" @click="loadAlerts">
            <RefreshCw class="w-4 h-4" :class="alertsLoading ? 'animate-spin text-indigo-500' : 'text-gray-400'" />
          </button>
        </div>
      </div>

      <div v-if="alertsLoading" class="flex justify-center py-12">
        <Loader2 class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <div v-else class="space-y-3">
        <div v-for="alert in alerts" :key="alert.id" class="rounded-xl border border-gray-200 bg-white p-5">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <span
                  class="inline-flex items-center gap-1 text-xs font-bold"
                  :class="SEVERITY_COLOR[alert.severity] ?? 'text-gray-500'"
                >
                  <AlertTriangle class="w-3.5 h-3.5" /> Severity {{ alert.severity }}
                </span>
                <span class="text-xs text-gray-500">{{ ALERT_TYPE_LABEL[alert.alert_type] ?? alert.alert_type }}</span>
              </div>
              <p v-if="alert.content_object_title" class="font-semibold text-gray-900">{{ alert.content_object_title }}</p>
              <p class="text-xs text-gray-400 mt-0.5">Raised {{ fmtDate(alert.raised_at) }}</p>
              <div v-if="Object.keys(alert.detail).length" class="mt-2 flex flex-wrap gap-2">
                <span
                  v-for="(v, k) in alert.detail" :key="k"
                  class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                >{{ k }}: {{ v }}</span>
              </div>
            </div>
            <div v-if="!alert.resolved_at" class="flex gap-2 shrink-0">
              <button
                class="text-xs px-3 py-1.5 border border-green-200 text-green-700 rounded-lg hover:bg-green-50"
                @click="resolveAlert(alert.id, 'updated')"
              >Mark updated</button>
              <button
                class="text-xs px-3 py-1.5 border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50"
                @click="resolveAlert(alert.id, 'dismissed')"
              >Dismiss</button>
            </div>
            <StatusPill v-else label="Resolved" tone="success" />
          </div>
        </div>

        <div v-if="!alerts.length" class="rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400 text-sm">
          <CheckCircle class="w-8 h-8 mx-auto mb-2 text-green-400" />
          No {{ alertsFilter === "unresolved" ? "unresolved" : "" }} freshness alerts.
        </div>
      </div>
    </div>

    <!-- ══ PERFORMANCE ════════════════════════════════════════════════════════ -->
    <div v-else-if="activeTab === 'performance'" class="p-6 space-y-5 max-w-4xl">

      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Top-performing content pages ranked by 30-day metrics.</p>
        <div class="flex items-center gap-2">
          <select
            v-model="snapshotMetric"
            class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="clicks">GSC Clicks</option>
            <option value="views">Page Views</option>
            <option value="conversions">Conversions</option>
            <option value="revenue">Revenue</option>
          </select>
          <button class="rounded-lg border border-gray-300 p-1.5 hover:bg-gray-50" @click="loadSnapshots">
            <RefreshCw class="w-4 h-4" :class="snapshotsLoading ? 'animate-spin text-indigo-500' : 'text-gray-400'" />
          </button>
        </div>
      </div>

      <div v-if="snapshotsLoading" class="flex justify-center py-12">
        <Loader2 class="w-6 h-6 text-gray-400 animate-spin" />
      </div>

      <div v-else class="space-y-2">
        <div v-for="(snap, i) in snapshots" :key="snap.id" class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-start gap-4">
            <div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-xs font-bold text-indigo-700">#{{ i + 1 }}</div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 line-clamp-1">{{ snap.page_title }}</p>
              <p class="text-xs text-gray-400 mt-0.5">/{{ snap.page_slug }}</p>
              <div class="mt-2 grid grid-cols-3 gap-2 sm:grid-cols-5 text-center">
                <div class="rounded-lg bg-gray-50 p-2">
                  <p class="text-xs text-gray-400">Clicks</p>
                  <p class="text-sm font-bold text-gray-800">{{ snap.gsc_clicks_30d.toLocaleString() }}</p>
                </div>
                <div class="rounded-lg bg-gray-50 p-2">
                  <p class="text-xs text-gray-400">Views</p>
                  <p class="text-sm font-bold text-gray-800">{{ snap.ga4_page_views_30d.toLocaleString() }}</p>
                </div>
                <div class="rounded-lg bg-gray-50 p-2">
                  <p class="text-xs text-gray-400">Avg position</p>
                  <p class="text-sm font-bold" :class="snap.gsc_avg_position_30d <= 5 ? 'text-green-700' : 'text-gray-800'">
                    {{ snap.gsc_avg_position_30d.toFixed(1) }}
                  </p>
                </div>
                <div class="rounded-lg bg-gray-50 p-2">
                  <p class="text-xs text-gray-400">Conversions</p>
                  <p class="text-sm font-bold text-gray-800">{{ snap.internal_conversions_30d }}</p>
                </div>
                <div v-if="snap.ai_overview_appearances_30d > 0" class="rounded-lg bg-purple-50 p-2">
                  <p class="text-xs text-purple-400">AI overview</p>
                  <p class="text-sm font-bold text-purple-700">{{ snap.ai_overview_appearances_30d }}</p>
                </div>
              </div>
            </div>
            <span
              class="shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium"
              :class="DIAGNOSIS_TONE[snap.diagnosis] ?? 'bg-gray-50 text-gray-500 border-gray-200'"
            >{{ snap.diagnosis.replace(/_/g, ' ') }}</span>
          </div>
        </div>

        <div v-if="!snapshots.length" class="rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400 text-sm">
          No performance data yet. This populates once GSC/GA4 ingestion tasks run.
        </div>
      </div>
    </div>

  </div>

  <!-- ══ PERSONALIZATION RULE MODAL ══════════════════════════════════════════ -->
  <div v-if="ruleModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <h3 class="font-semibold text-gray-900">{{ editingRuleId ? 'Edit' : 'New' }} personalization rule</h3>
        <button class="text-gray-400 hover:text-gray-700" @click="ruleModal = false"><X class="w-5 h-5" /></button>
      </div>

      <div class="p-6 space-y-5">
        <!-- Persona + priority -->
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Persona / traffic source</span>
            <select v-model="ruleDraft.persona" class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option v-for="o in PERSONA_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Priority</span>
            <input v-model.number="ruleDraft.priority" type="number" min="1" max="100"
              class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            <p class="text-xs text-gray-400">Higher = matched first. 1–100.</p>
          </label>
        </div>

        <!-- Optional UTM fine-grained match -->
        <div class="rounded-lg bg-gray-50 p-4 space-y-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Fine-grained UTM match (optional)</p>
          <div class="grid gap-3 sm:grid-cols-3">
            <label class="block space-y-1">
              <span class="text-xs text-gray-500">utm_source</span>
              <input v-model="ruleDraft.utm_source" type="text" placeholder="e.g. facebook"
                class="h-8 w-full rounded-lg border border-gray-300 px-3 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
            <label class="block space-y-1">
              <span class="text-xs text-gray-500">utm_medium</span>
              <input v-model="ruleDraft.utm_medium" type="text" placeholder="e.g. social"
                class="h-8 w-full rounded-lg border border-gray-300 px-3 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
            <label class="block space-y-1">
              <span class="text-xs text-gray-500">utm_campaign</span>
              <input v-model="ruleDraft.utm_campaign" type="text" placeholder="e.g. spring_promo"
                class="h-8 w-full rounded-lg border border-gray-300 px-3 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
          </div>
          <p class="text-xs text-gray-400">Leave blank to match all visitors in this persona category.</p>
        </div>

        <!-- Copy variants -->
        <div class="space-y-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Copy variants</p>
          <label class="block space-y-1">
            <span class="text-xs text-gray-500">Hero headline</span>
            <input v-model="ruleDraft.hero_headline" type="text" maxlength="200" placeholder="e.g. Get expert help for your next deadline"
              class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs text-gray-500">Hero sub-headline</span>
            <input v-model="ruleDraft.hero_subheadline" type="text" maxlength="300"
              class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </label>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block space-y-1">
              <span class="text-xs text-gray-500">CTA button label</span>
              <input v-model="ruleDraft.cta_label" type="text" maxlength="80" placeholder="e.g. Claim 10% off"
                class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
            <label class="block space-y-1">
              <span class="text-xs text-gray-500">CTA URL override</span>
              <input v-model="ruleDraft.cta_url" type="text" placeholder="/auth/register?ref=social"
                class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
          </div>
          <label class="block space-y-1">
            <span class="text-xs text-gray-500">Trust badge text</span>
            <input v-model="ruleDraft.trust_badge" type="text" maxlength="200" placeholder="e.g. Trusted by 12,000+ students"
              class="h-9 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </label>
        </div>

        <!-- Active toggle -->
        <label class="flex items-center gap-3 cursor-pointer">
          <input v-model="ruleDraft.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
          <span class="text-sm font-medium text-gray-700">Rule is active</span>
        </label>
      </div>

      <div class="flex gap-2 justify-end px-6 py-4 border-t border-gray-100">
        <button class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50" @click="ruleModal = false">Cancel</button>
        <button
          :disabled="savingRule"
          class="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          @click="saveRule"
        >
          <Loader2 v-if="savingRule" class="w-4 h-4 animate-spin" />
          <Save v-else class="w-4 h-4" />
          {{ editingRuleId ? 'Update rule' : 'Create rule' }}
        </button>
      </div>
    </div>
  </div>
</template>
