<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  Mail, Users, BarChart3, RefreshCw, UserX, UserCheck,
  ExternalLink, ChevronRight, Tag, Plus, X,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminNewslettersStore } from "@/stores/adminNewsletters";

const nl = useAdminNewslettersStore();
const activeTab = ref<"overview" | "subscribers" | "campaigns">("overview");

onMounted(async () => {
  await nl.loadStats();
  await nl.loadSubscribers();
  await nl.loadNewsletters();
  await nl.loadCategories();
});

// ── Helpers ──────────────────────────────────────────────────────────────────
const STATUS_TONE: Record<string, string> = {
  draft: "gray",
  scheduled: "yellow",
  sending: "blue",
  sent: "green",
  failed: "red",
};

function pct(n: number, d: number) {
  if (!d) return "0%";
  return `${((n / d) * 100).toFixed(1)}%`;
}

function dateLabel(v?: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat("en", {
    month: "short", day: "numeric", year: "numeric",
  }).format(new Date(v));
}

function sourceLabel(s: string) {
  return {
    attachment_gate: "Attachment gate",
    blog_form: "Blog form",
    order_optin: "Order opt-in",
    manual: "Manual",
    import: "Bulk import",
  }[s] ?? s;
}

// ── Newsletter detail panel ──────────────────────────────────────────────────
const panelOpen = ref(false);

async function openNewsletter(id: number) {
  await nl.selectNewsletter(id);
  panelOpen.value = true;
}

// ── Category creation ────────────────────────────────────────────────────────
const catModal = ref(false);
const newCatName = ref("");

async function createCat() {
  if (!newCatName.value.trim()) return;
  await nl.createCategory(newCatName.value.trim());
  newCatName.value = "";
  catModal.value = false;
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Newsletter Management</h1>
          <p class="text-sm text-gray-500 mt-0.5">Subscribers, campaigns, and engagement analytics</p>
        </div>
        <div class="flex gap-2">
          <button
            class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="nl.loadStats(); nl.loadSubscribers(); nl.loadNewsletters()"
          >
            <RefreshCw class="w-4 h-4" /> Refresh
          </button>
          <a
            href="/cms-admin/"
            target="_blank"
            class="flex items-center gap-2 px-3 py-2 text-sm text-indigo-600 border border-indigo-300 rounded-lg hover:bg-indigo-50"
          >
            <ExternalLink class="w-4 h-4" /> Compose in Wagtail
          </a>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 mt-4">
        <button
          v-for="tab in [
            { key: 'overview', label: 'Overview', icon: BarChart3 },
            { key: 'subscribers', label: 'Subscribers', icon: Users },
            { key: 'campaigns', label: 'Campaigns', icon: Mail },
          ]"
          :key="tab.key"
          class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
          :class="activeTab === tab.key
            ? 'bg-indigo-600 text-white'
            : 'text-gray-600 hover:bg-gray-100'"
          @click="activeTab = tab.key as typeof activeTab"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Notice -->
    <div
      v-if="nl.notice"
      class="mx-6 mt-4 px-4 py-3 rounded-lg text-sm font-medium"
      :class="nl.notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >
      {{ nl.notice.message }}
    </div>

    <!-- ── OVERVIEW ── -->
    <div v-if="activeTab === 'overview'" class="p-6 space-y-6">
      <!-- Stats cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">Total</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">{{ nl.stats?.total ?? "—" }}</div>
          <div class="text-xs text-gray-500 mt-1">subscribers</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">Active</div>
          <div class="text-2xl font-bold text-green-600 mt-1">{{ nl.stats?.active ?? "—" }}</div>
          <div class="text-xs text-gray-500 mt-1">subscribed</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">Inactive</div>
          <div class="text-2xl font-bold text-gray-400 mt-1">{{ nl.stats?.inactive ?? "—" }}</div>
          <div class="text-xs text-gray-500 mt-1">unsubscribed</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">Campaigns</div>
          <div class="text-2xl font-bold text-indigo-600 mt-1">{{ nl.newsletterTotal }}</div>
          <div class="text-xs text-gray-500 mt-1">total newsletters</div>
        </div>
      </div>

      <!-- Source breakdown -->
      <div class="bg-white rounded-xl border border-gray-200 p-5" v-if="nl.stats?.by_source">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Subscriber Sources</h3>
        <div class="space-y-2">
          <div
            v-for="(count, source) in nl.stats.by_source"
            :key="source"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-gray-500 w-32 flex-shrink-0">{{ sourceLabel(source) }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
              <div
                class="h-full bg-indigo-500 rounded-full"
                :style="{ width: pct(count, nl.stats!.total) }"
              />
            </div>
            <span class="text-xs font-medium text-gray-700 w-8 text-right">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Categories -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold text-gray-700">Subscriber Categories</h3>
          <button
            class="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
            @click="catModal = true"
          >
            <Plus class="w-3.5 h-3.5" /> Add category
          </button>
        </div>
        <div v-if="nl.categories.length === 0" class="text-sm text-gray-400">No categories yet.</div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="cat in nl.categories"
            :key="cat.id"
            class="flex items-center gap-1.5 px-3 py-1 text-xs font-medium bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200"
          >
            <Tag class="w-3 h-3" /> {{ cat.name }}
          </span>
        </div>
      </div>
    </div>

    <!-- ── SUBSCRIBERS ── -->
    <div v-else-if="activeTab === 'subscribers'" class="flex h-[calc(100vh-210px)]">
      <div class="flex-1 overflow-y-auto">
        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 flex flex-wrap gap-3 items-center bg-white">
          <input
            v-model="nl.subscriberSearch"
            type="text"
            placeholder="Search by email…"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
            @keyup.enter="nl.loadSubscribers()"
          />
          <select
            v-model="nl.subscriberStatusFilter"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none bg-white"
            @change="nl.loadSubscribers()"
          >
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select
            v-model="nl.subscriberSourceFilter"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none bg-white"
            @change="nl.loadSubscribers()"
          >
            <option value="all">All sources</option>
            <option value="attachment_gate">Attachment gate</option>
            <option value="blog_form">Blog form</option>
            <option value="order_optin">Order opt-in</option>
            <option value="manual">Manual</option>
            <option value="import">Bulk import</option>
          </select>
          <button
            class="px-3 py-2 text-sm text-indigo-600 border border-indigo-300 rounded-lg hover:bg-indigo-50"
            @click="nl.loadSubscribers()"
          >
            Search
          </button>
          <span class="text-xs text-gray-400 ml-auto">{{ nl.subscriberTotal }} total</span>
        </div>

        <div v-if="nl.loading" class="flex justify-center py-16">
          <RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="nl.subscribers.length === 0" class="flex flex-col items-center py-16 text-gray-400">
          <Users class="w-10 h-10 mb-3" />
          <p class="text-sm">No subscribers found.</p>
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left font-medium">Email</th>
              <th class="px-6 py-3 text-left font-medium">Source</th>
              <th class="px-6 py-3 text-left font-medium">Frequency</th>
              <th class="px-6 py-3 text-left font-medium">Engagement</th>
              <th class="px-6 py-3 text-left font-medium">Status</th>
              <th class="px-6 py-3 text-left font-medium">Subscribed</th>
              <th class="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="sub in nl.subscribers" :key="sub.id" class="bg-white hover:bg-gray-50">
              <td class="px-6 py-3 font-medium text-gray-900">{{ sub.email }}</td>
              <td class="px-6 py-3 text-gray-500 text-xs">{{ sourceLabel(sub.source) }}</td>
              <td class="px-6 py-3 text-gray-500 capitalize">{{ sub.frequency }}</td>
              <td class="px-6 py-3 text-gray-500">
                <span class="text-xs">{{ sub.open_count }} opens · {{ sub.click_count }} clicks</span>
              </td>
              <td class="px-6 py-3">
                <StatusPill
                  :status="sub.is_active ? 'active' : 'inactive'"
                  :tone="sub.is_active ? 'green' : 'gray'"
                  :label="sub.is_active ? 'Active' : 'Inactive'"
                />
              </td>
              <td class="px-6 py-3 text-gray-400 text-xs">{{ dateLabel(sub.created_at) }}</td>
              <td class="px-6 py-3 text-right">
                <button
                  v-if="sub.is_active"
                  :disabled="nl.actionLoading"
                  class="flex items-center gap-1 text-xs text-red-600 hover:text-red-800 disabled:opacity-50 ml-auto"
                  @click="nl.deactivateSubscriber(sub.id)"
                >
                  <UserX class="w-3.5 h-3.5" /> Deactivate
                </button>
                <button
                  v-else
                  :disabled="nl.actionLoading"
                  class="flex items-center gap-1 text-xs text-green-600 hover:text-green-800 disabled:opacity-50 ml-auto"
                  @click="nl.reactivateSubscriber(sub.id)"
                >
                  <UserCheck class="w-3.5 h-3.5" /> Reactivate
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── CAMPAIGNS ── -->
    <div v-else-if="activeTab === 'campaigns'" class="flex h-[calc(100vh-210px)]">
      <!-- List -->
      <div class="flex-1 overflow-y-auto">
        <!-- Filters -->
        <div class="px-6 py-3 border-b border-gray-100 flex gap-3 items-center bg-white">
          <input
            v-model="nl.newsletterSearch"
            type="text"
            placeholder="Search campaigns…"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
            @keyup.enter="nl.loadNewsletters()"
          />
          <select
            v-model="nl.newsletterStatusFilter"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none bg-white"
            @change="nl.loadNewsletters()"
          >
            <option value="all">All statuses</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="sending">Sending</option>
            <option value="sent">Sent</option>
            <option value="failed">Failed</option>
          </select>
          <span class="text-xs text-gray-400 ml-auto">{{ nl.newsletterTotal }} total</span>
        </div>

        <div v-if="nl.loading" class="flex justify-center py-16">
          <RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="nl.newsletters.length === 0" class="flex flex-col items-center py-16 text-gray-400">
          <Mail class="w-10 h-10 mb-3" />
          <p class="text-sm">No campaigns found.</p>
          <a href="/cms-admin/" target="_blank" class="mt-2 text-xs text-indigo-600 hover:underline">
            Create one in Wagtail →
          </a>
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left font-medium">Title</th>
              <th class="px-6 py-3 text-left font-medium">Subject</th>
              <th class="px-6 py-3 text-left font-medium">Status</th>
              <th class="px-6 py-3 text-left font-medium">Sent</th>
              <th class="px-6 py-3 text-left font-medium">Open rate</th>
              <th class="px-6 py-3 text-left font-medium">Click rate</th>
              <th class="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="n in nl.newsletters"
              :key="n.id"
              class="bg-white hover:bg-gray-50 cursor-pointer"
              :class="{ 'bg-indigo-50': nl.selectedNewsletter?.id === n.id }"
              @click="openNewsletter(n.id)"
            >
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900 truncate max-w-[180px]">{{ n.title }}</div>
                <div v-if="n.sender_name" class="text-xs text-gray-500">{{ n.sender_name }}</div>
              </td>
              <td class="px-6 py-4 text-gray-600 truncate max-w-[160px]">{{ n.subject_line }}</td>
              <td class="px-6 py-4">
                <StatusPill :status="n.status" :tone="STATUS_TONE[n.status]" :label="n.status" />
              </td>
              <td class="px-6 py-4 text-gray-500 text-xs">{{ dateLabel(n.sent_at) }}</td>
              <td class="px-6 py-4 text-gray-600">
                {{ n.analytics ? ((n.analytics.open_rate ?? 0) * 100).toFixed(1) + '%' : '—' }}
              </td>
              <td class="px-6 py-4 text-gray-600">
                {{ n.analytics ? ((n.analytics.click_rate ?? 0) * 100).toFixed(1) + '%' : '—' }}
              </td>
              <td class="px-6 py-4 text-right">
                <ChevronRight class="w-4 h-4 text-gray-400 ml-auto" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Newsletter detail panel -->
      <transition name="panel">
        <div
          v-if="panelOpen && nl.selectedNewsletter"
          class="w-96 border-l border-gray-200 bg-white overflow-y-auto flex-shrink-0"
        >
          <div class="px-5 py-4 border-b border-gray-100 flex items-start justify-between">
            <div>
              <h2 class="font-semibold text-gray-900">{{ nl.selectedNewsletter.title }}</h2>
              <StatusPill
                :status="nl.selectedNewsletter.status"
                :tone="STATUS_TONE[nl.selectedNewsletter.status]"
                :label="nl.selectedNewsletter.status"
                class="mt-1"
              />
            </div>
            <button class="text-gray-400 hover:text-gray-600 p-1" @click="panelOpen = false">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="px-5 py-4 space-y-5">
            <!-- Subject lines -->
            <div>
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Subject</h3>
              <p class="text-sm text-gray-700">{{ nl.selectedNewsletter.subject_line }}</p>
              <div v-if="nl.selectedNewsletter.subject_line_b" class="mt-1.5">
                <span class="text-xs bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-full px-2 py-0.5">A/B Variant B:</span>
                <p class="text-sm text-gray-600 mt-1">{{ nl.selectedNewsletter.subject_line_b }}</p>
              </div>
            </div>

            <!-- Analytics -->
            <div v-if="nl.selectedNewsletter.analytics">
              <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Performance</h3>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="(val, label) in {
                  'Sent': nl.selectedNewsletter.analytics.sent_count,
                  'Delivered': nl.selectedNewsletter.analytics.delivered_count,
                  'Opens': nl.selectedNewsletter.analytics.open_count,
                  'Clicks': nl.selectedNewsletter.analytics.click_count,
                  'Bounces': nl.selectedNewsletter.analytics.bounce_count,
                  'Unsubscribes': nl.selectedNewsletter.analytics.unsubscribe_count,
                }" :key="label" class="bg-gray-50 rounded-lg p-3 text-center">
                  <div class="text-lg font-bold text-gray-800">{{ val }}</div>
                  <div class="text-xs text-gray-500">{{ label }}</div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3 mt-3">
                <div class="bg-green-50 rounded-lg p-3 text-center">
                  <div class="text-lg font-bold text-green-700">{{ ((nl.selectedNewsletter.analytics.open_rate ?? 0) * 100).toFixed(1) }}%</div>
                  <div class="text-xs text-green-600">Open rate</div>
                </div>
                <div class="bg-indigo-50 rounded-lg p-3 text-center">
                  <div class="text-lg font-bold text-indigo-700">{{ ((nl.selectedNewsletter.analytics.click_rate ?? 0) * 100).toFixed(1) }}%</div>
                  <div class="text-xs text-indigo-600">Click rate</div>
                </div>
              </div>
              <div v-if="nl.selectedNewsletter.analytics.winning_subject" class="mt-3 text-xs text-yellow-700 bg-yellow-50 rounded-lg px-3 py-2">
                Winning subject: <strong>{{ nl.selectedNewsletter.analytics.winning_subject }}</strong>
              </div>
            </div>

            <!-- Meta -->
            <div class="border-t border-gray-100 pt-3 text-xs text-gray-400 space-y-1">
              <p v-if="nl.selectedNewsletter.sender_name">Sender: {{ nl.selectedNewsletter.sender_name }} &lt;{{ nl.selectedNewsletter.sender_email }}&gt;</p>
              <p v-if="nl.selectedNewsletter.category">Category: {{ nl.selectedNewsletter.category.name }}</p>
              <p>Created by: {{ nl.selectedNewsletter.created_by_name ?? "—" }}</p>
              <p>Created: {{ dateLabel(nl.selectedNewsletter.created_at) }}</p>
              <p v-if="nl.selectedNewsletter.sent_at">Sent: {{ dateLabel(nl.selectedNewsletter.sent_at) }}</p>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Category modal -->
    <div v-if="catModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-base font-semibold text-gray-900 mb-4">Add Subscriber Category</h3>
        <input
          v-model="newCatName"
          type="text"
          placeholder="e.g. Nursing Tips"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          @keyup.enter="createCat"
        />
        <div class="mt-4 flex gap-2 justify-end">
          <button
            class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="catModal = false; newCatName = ''"
          >Cancel</button>
          <button
            :disabled="!newCatName.trim()"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            @click="createCat"
          >Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-enter-active,
.panel-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.panel-enter-from,
.panel-leave-to {
  transform: translateX(1rem);
  opacity: 0;
}
</style>
