<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  Bell,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Megaphone,
  Pin,
  RefreshCw,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { announcementsApi, type AnnouncementRecord } from "@/api/announcements";
import type { UserRole } from "@/types/roles";

defineProps<{ role: UserRole }>();

const items = ref<AnnouncementRecord[]>([]);
const loading = ref(false);
const error = ref("");
const acknowledging = ref<Set<number>>(new Set());

async function fetchAnnouncements() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await announcementsApi.list({ ordering: "-broadcast__pinned,-created_at" });
    const list = Array.isArray(data) ? data : (data as { results: AnnouncementRecord[] }).results ?? [];
    items.value = list;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = detail ?? "Could not load announcements.";
  } finally {
    loading.value = false;
  }
}

async function markRead(item: AnnouncementRecord) {
  if (item.is_read) return;
  try {
    await announcementsApi.trackView(item.id);
    item.is_read = true;
  } catch {
    // non-critical
  }
}

async function acknowledge(item: AnnouncementRecord) {
  if (item.is_acknowledged || acknowledging.value.has(item.id)) return;
  acknowledging.value = new Set([...acknowledging.value, item.id]);
  try {
    await announcementsApi.acknowledge(item.id);
    item.is_acknowledged = true;
    item.is_read = true;
  } catch {
    // non-critical
  } finally {
    acknowledging.value.delete(item.id);
    acknowledging.value = new Set(acknowledging.value);
  }
}

function categoryTone(category: string): "neutral" | "warning" | "danger" | "success" {
  switch (category) {
    case "maintenance": return "warning";
    case "update": return "success";
    case "promotion": return "success";
    case "news": return "neutral";
    default: return "neutral";
  }
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

onMounted(async () => {
  await fetchAnnouncements();
  // Silently track views for already-visible items
  items.value.filter((a) => !a.is_read).forEach((a) => markRead(a));
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">{{ role }}</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Announcements</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Platform news, updates, and important notices from the team.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="loading"
        @click="fetchAnnouncements"
      >
        <Loader2 v-if="loading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p v-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ error }}
    </p>

    <div v-if="loading && !items.length" class="space-y-4">
      <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-6">
        <div class="h-5 w-1/2 rounded bg-slate-200" />
        <div class="mt-3 h-3 w-full rounded bg-slate-100" />
        <div class="mt-2 h-3 w-3/4 rounded bg-slate-100" />
      </div>
    </div>

    <EmptyState
      v-else-if="!items.length"
      :icon="Bell"
      title="No announcements"
      message="Platform announcements will appear here."
    />

    <div v-else class="space-y-4">
      <article
        v-for="item in items"
        :key="item.id"
        class="rounded-lg border bg-white transition-opacity"
        :class="[
          item.is_pinned ? 'border-signal/30' : 'border-slate-200',
          !item.is_read ? 'ring-1 ring-signal/20' : '',
        ]"
      >
        <!-- Pinned banner -->
        <div v-if="item.is_pinned" class="flex items-center gap-1.5 rounded-t-lg bg-signal/5 px-5 py-2 text-xs font-semibold text-signal">
          <Pin class="h-3.5 w-3.5" />
          Pinned announcement
        </div>

        <div class="p-5">
          <div class="flex items-start gap-4">
            <div class="mt-0.5 shrink-0 rounded-lg bg-slate-100 p-2.5">
              <Megaphone class="h-5 w-5 text-graphite" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-start gap-2">
                <h2 class="text-base font-semibold text-ink leading-snug">{{ item.title }}</h2>
                <span
                  v-if="!item.is_read"
                  class="inline-block h-2 w-2 shrink-0 rounded-full bg-signal mt-1.5"
                  title="Unread"
                />
              </div>
              <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-graphite">
                <StatusPill :label="item.category" :tone="categoryTone(item.category)" />
                <span>{{ formatDate(item.created_at) }}</span>
                <span v-if="item.created_by_name">· {{ item.created_by_name }}</span>
                <span v-if="item.expires_at">· Expires {{ formatDate(item.expires_at) }}</span>
              </div>

              <div class="mt-3 text-sm leading-6 text-graphite prose prose-sm max-w-none" v-html="item.message" />

              <div class="mt-4 flex flex-wrap items-center gap-3">
                <a
                  v-if="item.read_more_url"
                  :href="item.read_more_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="focus-ring inline-flex items-center gap-1.5 text-sm font-semibold text-signal hover:underline"
                >
                  Read more
                  <ExternalLink class="h-3.5 w-3.5" />
                </a>

                <button
                  v-if="!item.is_acknowledged"
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
                  type="button"
                  :disabled="acknowledging.has(item.id)"
                  @click="acknowledge(item)"
                >
                  <Loader2 v-if="acknowledging.has(item.id)" class="h-3.5 w-3.5 animate-spin" />
                  <CheckCircle2 v-else class="h-3.5 w-3.5" />
                  Acknowledge
                </button>
                <span v-else class="inline-flex items-center gap-1.5 text-xs font-semibold text-signal">
                  <CheckCircle2 class="h-3.5 w-3.5" />
                  Acknowledged
                </span>

                <span class="ml-auto text-xs text-slate-400">{{ item.view_count }} views</span>
              </div>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>
