<template>
  <div class="not-prose mt-8 rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
    <!-- Reading time + view count -->
    <div class="flex flex-wrap items-center gap-4 text-xs text-graphite">
      <span v-if="readingTime" class="flex items-center gap-1.5">
        <Clock class="h-3.5 w-3.5" />
        {{ readingTime }} min read
      </span>
      <span v-if="summary?.total_views" class="flex items-center gap-1.5">
        <Eye class="h-3.5 w-3.5" />
        {{ fmtNum(summary.total_views) }} views
      </span>
      <span v-if="summary?.total_shares" class="flex items-center gap-1.5">
        <Share2 class="h-3.5 w-3.5" />
        {{ fmtNum(summary.total_shares) }} shares
      </span>
    </div>

    <!-- Divider -->
    <div class="my-3 border-t border-slate-100" />

    <!-- Reaction bar -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <p class="mb-2 text-xs font-semibold uppercase text-graphite">Was this helpful?</p>
        <div class="flex items-center gap-2">
          <button
            v-for="r in REACTIONS"
            :key="r.type"
            class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium transition-all"
            :class="summary?.user_reaction === r.type
              ? 'border-signal bg-signal/5 text-signal'
              : 'border-slate-200 text-graphite hover:border-slate-300 hover:bg-slate-50'"
            :disabled="isMutating"
            @click="emit('react', r.type)"
          >
            <span class="text-base leading-none">{{ r.emoji }}</span>
            <span>{{ reactionCount(r.type) }}</span>
          </button>
        </div>
      </div>

      <!-- Share + Bookmark -->
      <div class="flex items-center gap-2">
        <!-- Share buttons -->
        <button
          v-for="s in SHARES"
          :key="s.platform"
          class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:border-slate-300 hover:bg-slate-50"
          :title="s.label"
          @click="handleShare(s)"
        >
          <component :is="s.icon" class="h-4 w-4" />
        </button>

        <!-- Bookmark (auth only) -->
        <button
          v-if="isAuthenticated"
          class="flex h-9 w-9 items-center justify-center rounded-lg border transition-colors"
          :class="summary?.user_bookmarked
            ? 'border-signal bg-signal/5 text-signal'
            : 'border-slate-200 text-graphite hover:border-slate-300 hover:bg-slate-50'"
          title="Bookmark this article"
          :disabled="isMutating"
          @click="emit('bookmark')"
        >
          <Bookmark class="h-4 w-4" :class="summary?.user_bookmarked ? 'fill-current' : ''" />
        </button>
      </div>
    </div>

    <!-- Copy link toast -->
    <Transition name="fade">
      <div v-if="copiedToast" class="mt-3 rounded-md bg-ink px-3 py-2 text-xs text-white">
        Link copied to clipboard!
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref } from "vue";
import { Bookmark, Clock, Eye, Link, Share2 } from "@lucide/vue";
import type { EngagementSummary, ReactionType, SharePlatform } from "@/api/engagement";

const props = defineProps<{
  summary: EngagementSummary | null;
  isMutating: boolean;
  isAuthenticated: boolean;
  readingTime?: number | null;
  pageUrl?: string;
}>();

const emit = defineEmits<{
  (e: "react", type: ReactionType): void;
  (e: "share", platform: SharePlatform): void;
  (e: "bookmark"): void;
}>();

const copiedToast = ref(false);

const REACTIONS = [
  { type: "thumbs_up" as ReactionType, emoji: "👍", label: "Helpful" },
  { type: "love" as ReactionType, emoji: "❤️", label: "Love" },
  { type: "useful" as ReactionType, emoji: "💡", label: "Useful" },
  { type: "thumbs_down" as ReactionType, emoji: "👎", label: "Not helpful" },
];

// Twitter/X icon inline component
const TwitterIcon = defineComponent({
  setup() {
    return () => h("svg", { viewBox: "0 0 24 24", fill: "currentColor", class: "h-4 w-4" }, [
      h("path", { d: "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.261 5.635 5.903-5.635Zm-1.161 17.52h1.833L7.084 4.126H5.117z" }),
    ]);
  },
});

const LinkedInIcon = defineComponent({
  setup() {
    return () => h("svg", { viewBox: "0 0 24 24", fill: "currentColor", class: "h-4 w-4" }, [
      h("path", { d: "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" }),
    ]);
  },
});

const WhatsAppIcon = defineComponent({
  setup() {
    return () => h("svg", { viewBox: "0 0 24 24", fill: "currentColor", class: "h-4 w-4" }, [
      h("path", { d: "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" }),
    ]);
  },
});

const SHARES = [
  {
    platform: "twitter" as SharePlatform,
    label: "Share on X",
    icon: TwitterIcon,
    url: (u: string, t: string) => `https://twitter.com/intent/tweet?text=${encodeURIComponent(t)}&url=${encodeURIComponent(u)}`,
  },
  {
    platform: "linkedin" as SharePlatform,
    label: "Share on LinkedIn",
    icon: LinkedInIcon,
    url: (u: string) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(u)}`,
  },
  {
    platform: "whatsapp" as SharePlatform,
    label: "Share on WhatsApp",
    icon: WhatsAppIcon,
    url: (u: string, t: string) => `https://wa.me/?text=${encodeURIComponent(t + " " + u)}`,
  },
  {
    platform: "copy" as SharePlatform,
    label: "Copy link",
    icon: Link,
    url: null,
  },
];

function reactionCount(type: ReactionType): number {
  if (!props.summary) return 0;
  const s = props.summary as Record<string, number>;
  return s[type + "_count"] ?? 0;
}

async function handleShare(s: typeof SHARES[number]) {
  const url = props.pageUrl || window.location.href;
  const title = document.title;
  emit("share", s.platform);
  if (s.platform === "copy") {
    await navigator.clipboard.writeText(url).catch(() => {});
    copiedToast.value = true;
    setTimeout(() => { copiedToast.value = false; }, 2500);
    return;
  }
  if (s.url) {
    window.open(s.url(url, title), "_blank", "noopener,width=600,height=400");
  }
}

function fmtNum(n: number): string {
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
