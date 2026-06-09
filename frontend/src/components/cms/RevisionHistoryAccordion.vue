<template>
  <div class="not-prose rounded-xl border border-slate-200 bg-white overflow-hidden">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-4 px-5 py-3.5 text-left transition-colors hover:bg-slate-50"
      @click="open = !open"
    >
      <div class="flex items-center gap-2.5">
        <History class="size-4 shrink-0 text-graphite" />
        <span class="text-sm font-semibold text-ink">Change history</span>
        <span
          v-if="history.updates.length"
          class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-graphite"
        >
          {{ history.updates.length }} {{ history.updates.length === 1 ? "entry" : "entries" }}
        </span>
      </div>
      <div class="flex items-center gap-3 shrink-0">
        <span v-if="history.revision_count" class="text-xs text-graphite">
          {{ history.revision_count }} editorial {{ history.revision_count === 1 ? "save" : "saves" }}
        </span>
        <ChevronDown
          class="size-4 text-slate-400 transition-transform duration-200"
          :class="open ? 'rotate-180' : ''"
        />
      </div>
    </button>

    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-96"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 max-h-96"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="open" class="overflow-hidden border-t border-slate-100">
        <ol class="px-5 py-4 space-y-3">
          <li
            v-for="(update, i) in [...history.updates].reverse()"
            :key="i"
            class="flex items-start gap-3"
          >
            <div class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full"
              :class="update.type === 'published'
                ? 'bg-brand-100 text-brand-700'
                : update.type === 'updated'
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-slate-100 text-graphite'"
            >
              <component :is="typeIcon(update.type)" class="size-2.5" />
            </div>
            <div>
              <p class="text-xs font-semibold text-ink">{{ update.label }}</p>
              <time class="text-xs text-graphite">{{ fmtDate(update.date) }}</time>
            </div>
          </li>
        </ol>

        <div v-if="history.revision_count > 2" class="border-t border-slate-100 bg-slate-50 px-5 py-3">
          <p class="text-xs text-graphite">
            <span class="font-medium text-ink">{{ history.revision_count }} editorial saves</span>
            — this article has been carefully reviewed and refined by our editorial team.
          </p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, h, ref } from "vue";
import { ChevronDown, History } from "@lucide/vue";
import type { BlogPostHistory, BlogPostHistoryUpdate } from "@/api/cms";

defineProps<{ history: BlogPostHistory }>();

const open = ref(false);

const PublishIcon = defineComponent({ setup() {
  return () => h("svg", { fill: "currentColor", viewBox: "0 0 20 20" }, [
    h("path", { d: "M10 12a2 2 0 100-4 2 2 0 000 4z" }),
    h("path", { "fill-rule": "evenodd", d: "M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z", "clip-rule": "evenodd" }),
  ]);
}});

const UpdateIcon = defineComponent({ setup() {
  return () => h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2.5" }, [
    h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" }),
  ]);
}});

const ReviewIcon = defineComponent({ setup() {
  return () => h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2.5" }, [
    h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" }),
  ]);
}});

function typeIcon(type: BlogPostHistoryUpdate["type"]) {
  if (type === "published") return PublishIcon;
  if (type === "updated") return UpdateIcon;
  return ReviewIcon;
}

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { dateStyle: "long" }).format(new Date(v));
}
</script>
