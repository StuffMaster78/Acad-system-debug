<script setup lang="ts">
import { onMounted } from "vue";
import { Eye, EyeOff, MessageSquare, Search } from "@lucide/vue";
import StarRating from "@/components/ui/StarRating.vue";
import { useReviewsStore } from "@/stores/reviews";

const reviews = useReviewsStore();

onMounted(() => reviews.loadAll());

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

const ratingOptions = [null, 5, 4, 3, 2, 1];
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-200 pb-6">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Reviews</h1>
        <p class="mt-2 text-sm text-graphite">Client reviews of writer performance across all orders.</p>
      </div>
      <div class="text-right">
        <p class="text-2xl font-bold text-ink">{{ reviews.allReviews.length }}</p>
        <p class="text-xs text-graphite">total reviews</p>
      </div>
    </div>

    <p v-if="reviews.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ reviews.notice }}</p>
    <p v-if="reviews.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ reviews.error }}</p>

    <!-- Filters -->
    <div class="flex items-center gap-3 flex-wrap">
      <div class="relative flex-1 max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-graphite" />
        <input
          v-model="reviews.query"
          type="text"
          placeholder="Search reviews…"
          class="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
        />
      </div>
      <div class="flex items-center gap-1 rounded-lg border border-slate-200 p-1">
        <button
          v-for="star in ratingOptions"
          :key="star ?? 'all'"
          class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
          :class="reviews.ratingFilter === star ? 'bg-ink text-white' : 'text-graphite hover:text-ink'"
          type="button"
          @click="reviews.ratingFilter = star"
        >
          {{ star === null ? 'All' : `${star}★` }}
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="reviews.isLoading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-24 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="!reviews.filteredAll.length"
      class="flex flex-col items-center gap-3 rounded-lg border border-slate-200 py-16 text-center"
    >
      <MessageSquare class="h-8 w-8 text-graphite" />
      <p class="text-sm font-medium text-ink">No reviews found</p>
      <p class="text-xs text-graphite">Reviews appear here once clients rate completed orders.</p>
    </div>

    <!-- Review list -->
    <div v-else class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="grid grid-cols-[1fr_120px_140px_100px_80px] gap-3 bg-slate-50 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-graphite border-b border-slate-100">
        <span>Order / Writer</span>
        <span>Rating</span>
        <span>Client</span>
        <span>Date</span>
        <span>Actions</span>
      </div>
      <div
        v-for="review in reviews.filteredAll"
        :key="review.id"
        class="grid grid-cols-[1fr_120px_140px_100px_80px] items-start gap-3 px-5 py-4 border-b border-slate-50 last:border-0"
        :class="review.is_hidden ? 'opacity-50' : ''"
      >
        <div class="min-w-0">
          <p class="text-sm font-semibold text-ink truncate">{{ review.order_topic }}</p>
          <p class="text-xs text-graphite mt-0.5">{{ review.writer_pen_name }}</p>
          <p v-if="review.title" class="text-xs text-graphite mt-1 italic">{{ review.title }}</p>
          <p v-if="review.body" class="text-xs text-graphite mt-0.5 line-clamp-2">{{ review.body }}</p>
        </div>
        <div class="pt-0.5">
          <StarRating :rating="review.rating" size="sm" />
        </div>
        <div>
          <p class="text-sm text-graphite">{{ review.client_username }}</p>
        </div>
        <div>
          <p class="text-xs text-graphite">{{ formatDate(review.created_at) }}</p>
          <span
            v-if="!review.is_public"
            class="mt-1 inline-block rounded-full bg-slate-100 px-1.5 py-0.5 text-xs text-graphite"
          >
            Private
          </span>
        </div>
        <div>
          <button
            class="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-xs font-medium transition-colors"
            :class="review.is_hidden ? 'text-signal hover:bg-signal/5' : 'text-graphite hover:text-rose-600'"
            type="button"
            :disabled="reviews.isSaving"
            :title="review.is_hidden ? 'Unhide review' : 'Hide review'"
            @click="reviews.toggleHide(review)"
          >
            <Eye v-if="review.is_hidden" class="h-3.5 w-3.5" />
            <EyeOff v-else class="h-3.5 w-3.5" />
            {{ review.is_hidden ? "Unhide" : "Hide" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
