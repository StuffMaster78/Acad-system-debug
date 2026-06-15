<template>
  <div class="mx-auto max-w-2xl px-4 py-8 space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-ink">What's new</h1>
      <p class="mt-1 text-sm text-graphite">Latest updates, improvements, and fixes.</p>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="n in 3" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-5">
        <div class="h-4 w-24 rounded bg-slate-200" />
        <div class="mt-3 h-5 w-3/4 rounded bg-slate-200" />
        <div class="mt-2 h-3 w-full rounded bg-slate-100" />
        <div class="mt-1 h-3 w-5/6 rounded bg-slate-100" />
      </div>
    </div>

    <div v-else-if="!entries.length" class="rounded-xl border border-slate-200 bg-white p-10 text-center">
      <Newspaper class="mx-auto h-10 w-10 text-slate-300" />
      <p class="mt-3 text-sm text-graphite">No updates yet. Check back soon.</p>
    </div>

    <div v-else class="space-y-4">
      <article
        v-for="entry in entries"
        :key="entry.id"
        class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow"
        :class="entry.is_pinned ? 'border-signal/30 bg-signal/[0.02]' : ''"
      >
        <!-- Meta row -->
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <span
            class="rounded-full px-2 py-0.5 font-semibold capitalize"
            :class="typeClass(entry.entry_type)"
          >{{ typeLabel(entry.entry_type) }}</span>
          <span v-if="entry.version" class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-graphite">
            {{ entry.version }}
          </span>
          <span v-if="entry.is_pinned" class="flex items-center gap-1 text-signal font-semibold">
            <Pin class="h-3 w-3" /> Pinned
          </span>
          <span class="ml-auto text-graphite">{{ fmtDate(entry.published_at) }}</span>
        </div>

        <!-- Content -->
        <h2 class="mt-3 text-base font-semibold text-ink">{{ entry.title }}</h2>
        <!-- Simple Markdown-lite: convert **bold** and `code` and line breaks -->
        <div
          class="mt-2 text-sm leading-6 text-graphite"
          v-html="sanitize(renderBody(entry.body))"
        />
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { sanitize } from "@/composables/useSanitize";
import { onMounted, ref } from "vue";
import { Newspaper, Pin } from "@lucide/vue";
import { changelogApi, type ChangelogEntry } from "@/api/changelog";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();
const entries = ref<ChangelogEntry[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const surface = portalCtx.surface ?? "public";
    const { data } = await changelogApi.list({ surface, limit: 50 });
    entries.value = data;
  } catch {
    entries.value = [];
  } finally {
    loading.value = false;
  }
});

function fmtDate(d: string | null) {
  if (!d) return "";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(d));
}

function typeLabel(t: string) {
  return { feature: "New", improvement: "Improved", fix: "Fixed", maintenance: "Maintenance", notice: "Notice" }[t] ?? t;
}

function typeClass(t: string) {
  return {
    feature: "bg-signal/10 text-signal",
    improvement: "bg-blue-50 text-blue-700",
    fix: "bg-emerald-50 text-emerald-700",
    maintenance: "bg-amber-50 text-amber-700",
    notice: "bg-slate-100 text-slate-600",
  }[t] ?? "bg-slate-100 text-slate-600";
}

function renderBody(md: string): string {
  return md
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.*?)`/g, '<code class="rounded bg-slate-100 px-1 text-[12px] font-mono">$1</code>')
    .replace(/\n/g, "<br />");
}
</script>
