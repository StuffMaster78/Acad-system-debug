<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Hero -->
    <div class="bg-white border-b border-slate-200 px-6 py-16 text-center">
      <h1 class="text-4xl font-bold text-ink">How can we help?</h1>
      <p class="mt-3 text-lg text-graphite">User guides, FAQs, and platform documentation.</p>
    </div>

    <div class="mx-auto max-w-5xl px-6 py-12 space-y-12">

      <!-- Loading -->
      <div v-if="isLoading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
        <div v-for="n in 6" :key="n" class="rounded-xl bg-white border border-slate-200 p-6">
          <div class="mb-3 size-8 rounded-full bg-slate-200" />
          <div class="h-4 w-3/4 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-full rounded bg-slate-100" />
        </div>
      </div>

      <template v-else>
        <!-- Featured articles -->
        <section v-if="featured.length">
          <h2 class="mb-4 text-xs font-semibold uppercase tracking-wider text-graphite">Featured guides</h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <RouterLink
              v-for="article in featured"
              :key="article.id"
              :to="`/help/articles/${article.slug}`"
              class="group rounded-xl border border-slate-200 bg-white p-5 hover:border-berry hover:shadow-sm transition-all"
            >
              <p class="font-semibold text-ink group-hover:text-berry">{{ article.title }}</p>
              <p class="mt-1 text-sm text-graphite line-clamp-2">{{ article.summary }}</p>
              <p class="mt-2 text-xs text-slate-400">{{ article.category_title }}</p>
            </RouterLink>
          </div>
        </section>

        <!-- Categories -->
        <section v-if="categories.length">
          <h2 class="mb-4 text-xs font-semibold uppercase tracking-wider text-graphite">Browse by topic</h2>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <RouterLink
              v-for="cat in categories"
              :key="cat.id"
              :to="`/help/category/${cat.slug}`"
              class="group flex items-start gap-4 rounded-xl border border-slate-200 bg-white p-5 hover:border-berry hover:shadow-sm transition-all"
            >
              <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-slate-100 group-hover:bg-berry/10">
                <component :is="icon(cat.icon)" class="size-5 text-graphite group-hover:text-berry" />
              </div>
              <div class="min-w-0">
                <p class="font-semibold text-ink group-hover:text-berry">{{ cat.title }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ cat.article_count }} article{{ cat.article_count !== 1 ? 's' : '' }}</p>
                <p v-if="cat.description" class="mt-1 text-xs text-slate-400 line-clamp-2">{{ cat.description }}</p>
              </div>
            </RouterLink>
          </div>
        </section>

        <!-- Empty -->
        <div v-if="!isLoading && !categories.length && !featured.length" class="py-20 text-center">
          <BookOpen class="mx-auto mb-4 size-10 text-slate-300" />
          <p class="text-sm font-medium text-graphite">Help articles are being prepared.</p>
          <p class="mt-1 text-xs text-slate-400">Check back soon or contact our support team.</p>
        </div>

        <!-- Legal footer -->
        <section class="border-t border-slate-200 pt-8">
          <h2 class="mb-4 text-xs font-semibold uppercase tracking-wider text-graphite">Legal documents</h2>
          <div class="flex flex-wrap gap-3">
            <RouterLink
              v-for="link in legalLinks"
              :key="link.to"
              :to="link.to"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-graphite hover:border-slate-300 hover:text-ink transition-colors"
            >
              {{ link.label }}
            </RouterLink>
          </div>
        </section>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  BookOpen, CreditCard, FileText, HelpCircle,
  LifeBuoy, MessageSquare, Settings, ShieldCheck, Users,
} from "@lucide/vue";
import { legalApi, type HelpArticleSummary, type HelpCategory } from "@/api/legal";

const isLoading = ref(true);
const categories = ref<HelpCategory[]>([]);
const featured = ref<HelpArticleSummary[]>([]);

const legalLinks = [
  { label: "Terms of Service",      to: "/legal/terms_of_service" },
  { label: "Privacy Policy",        to: "/legal/privacy_policy" },
  { label: "Refund Policy",         to: "/legal/refund_policy" },
  { label: "Cookie Policy",         to: "/legal/cookie_policy" },
  { label: "Acceptable Use Policy", to: "/legal/acceptable_use_policy" },
];

const ICON_MAP: Record<string, unknown> = {
  "book-open":     BookOpen,
  "credit-card":   CreditCard,
  "file-text":     FileText,
  "help-circle":   HelpCircle,
  "life-buoy":     LifeBuoy,
  "message-square": MessageSquare,
  "settings":      Settings,
  "shield-check":  ShieldCheck,
  "users":         Users,
};

function icon(name: string) {
  return ICON_MAP[name] ?? HelpCircle;
}

onMounted(async () => {
  try {
    const [catRes, artRes] = await Promise.all([
      legalApi.categories(),
      legalApi.articles({ featured: true }),
    ]);
    categories.value = catRes.data;
    featured.value = artRes.data;
  } catch {
    // Non-fatal — show empty state
  } finally {
    isLoading.value = false;
  }
});
</script>
