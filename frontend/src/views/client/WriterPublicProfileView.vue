<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, CheckCircle2, Star } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { reviewsApi } from "@/api/reviews";
import type { Review, ReviewSummary } from "@/types/reviews";

const route = useRoute();
const router = useRouter();

interface WriterCard {
  public_uuid: string;
  registration_id: string;
  pen_name: string;
  bio: string;
  qualifications: Record<string, unknown>[] | null;
  years_of_experience: number | null;
  timezone: string | null;
  level_name: string | null;
  is_verified: boolean;
  joined_at: string | null;
  rating_average: number | null;
  review_count: number;
  completed_orders_count: number;
}

const uuid = computed(() => route.params.uuid as string);
const writer = ref<WriterCard | null>(null);
const reviews = ref<Review[]>([]);
const summary = ref<ReviewSummary | null>(null);
const loading = ref(true);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get<WriterCard>(
      apiPath(`/writer-management/writers/${uuid.value}/card/`),
    );
    writer.value = data;

    if (data.registration_id) {
      const [rv, rs] = await Promise.allSettled([
        reviewsApi.forWriter(data.registration_id),
        reviewsApi.summary(data.registration_id),
      ]);
      if (rv.status === "fulfilled") {
        const d = rv.value.data;
        reviews.value = Array.isArray(d) ? d : (d as any).results ?? [];
      }
      if (rs.status === "fulfilled") summary.value = rs.value.data;
    }
  } catch {
    error.value = "Writer profile not found.";
  } finally {
    loading.value = false;
  }
}

function starClass(n: number, avg: number | null) {
  if (!avg) return "text-slate-200";
  return n <= Math.round(avg) ? "text-amber-400" : "text-slate-200";
}

function formatDate(iso: string | null) {
  if (!iso) return "";
  return new Intl.DateTimeFormat(undefined, { month: "short", year: "numeric" }).format(new Date(iso));
}

onMounted(load);
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-8">
    <button
      class="mb-6 flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800"
      @click="router.back()"
    >
      <ArrowLeft class="h-4 w-4" />
      Back
    </button>

    <div v-if="loading" class="py-16 text-center text-sm text-gray-400">Loading writer profile…</div>
    <div v-else-if="error" class="py-16 text-center text-sm text-red-600">{{ error }}</div>

    <template v-else-if="writer">
      <!-- Header -->
      <div class="rounded-xl border border-gray-200 bg-white p-6">
        <div class="flex items-start gap-4">
          <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-700">
            {{ writer.pen_name?.[0]?.toUpperCase() ?? "W" }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="text-lg font-semibold text-gray-900">{{ writer.pen_name }}</h1>
              <span v-if="writer.is_verified" class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                <CheckCircle2 class="h-3 w-3" />
                Verified
              </span>
              <span v-if="writer.level_name" class="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                {{ writer.level_name }}
              </span>
            </div>
            <div class="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-500">
              <span v-if="writer.rating_average" class="flex items-center gap-1">
                <span v-for="n in 5" :key="n">
                  <Star class="h-3.5 w-3.5" :class="starClass(n, writer.rating_average)" fill="currentColor" />
                </span>
                <span class="font-medium text-gray-700">{{ writer.rating_average.toFixed(1) }}</span>
                <span class="text-gray-400">({{ writer.review_count }})</span>
              </span>
              <span v-if="writer.completed_orders_count">{{ writer.completed_orders_count }} orders completed</span>
              <span v-if="writer.years_of_experience">{{ writer.years_of_experience }} yr{{ writer.years_of_experience !== 1 ? "s" : "" }} experience</span>
              <span v-if="writer.joined_at">Member since {{ formatDate(writer.joined_at) }}</span>
            </div>
          </div>
        </div>

        <p v-if="writer.bio" class="mt-4 text-sm text-gray-700 leading-relaxed">{{ writer.bio }}</p>
        <p v-else class="mt-4 text-sm text-gray-400 italic">No bio provided.</p>

        <!-- Qualifications -->
        <div v-if="writer.qualifications?.length" class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="(q, i) in writer.qualifications"
            :key="i"
            class="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-700"
          >
            {{ typeof q === "string" ? q : (q.degree ?? q.name ?? JSON.stringify(q)) }}
          </span>
        </div>
      </div>

      <!-- Rating distribution -->
      <div v-if="summary && summary.total_reviews > 0" class="mt-4 rounded-xl border border-gray-200 bg-white p-5">
        <h2 class="text-sm font-semibold text-gray-900">Ratings</h2>
        <div class="mt-3 flex items-center gap-6">
          <div class="text-center">
            <p class="text-4xl font-bold text-gray-900">{{ summary.average_rating.toFixed(1) }}</p>
            <div class="mt-1 flex justify-center gap-0.5">
              <Star v-for="n in 5" :key="n" class="h-4 w-4" :class="starClass(n, summary.average_rating)" fill="currentColor" />
            </div>
            <p class="mt-1 text-xs text-gray-400">{{ summary.total_reviews }} review{{ summary.total_reviews !== 1 ? "s" : "" }}</p>
          </div>
          <div class="flex-1 space-y-1.5">
            <div v-for="star in [5,4,3,2,1]" :key="star" class="flex items-center gap-2">
              <span class="w-3 text-right text-xs text-gray-500">{{ star }}</span>
              <Star class="h-3 w-3 text-amber-400" fill="currentColor" />
              <div class="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden">
                <div
                  class="h-full rounded-full bg-amber-400 transition-all"
                  :style="{ width: summary.total_reviews ? `${((summary.rating_distribution?.[String(star)] ?? 0) / summary.total_reviews) * 100}%` : '0%' }"
                />
              </div>
              <span class="w-5 text-xs text-gray-400">{{ summary.rating_distribution?.[String(star)] ?? 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews -->
      <div v-if="reviews.length" class="mt-4 space-y-3">
        <h2 class="text-sm font-semibold text-gray-900">Client reviews</h2>
        <div
          v-for="review in reviews"
          :key="review.id"
          class="rounded-xl border border-gray-200 bg-white p-4"
        >
          <div class="flex items-center gap-2">
            <div class="flex gap-0.5">
              <Star v-for="n in 5" :key="n" class="h-3.5 w-3.5" :class="starClass(n, review.rating)" fill="currentColor" />
            </div>
            <span v-if="review.title" class="text-sm font-medium text-gray-800">{{ review.title }}</span>
          </div>
          <p v-if="review.body" class="mt-2 text-sm text-gray-700">{{ review.body }}</p>
          <p class="mt-2 text-xs text-gray-400">{{ formatDate(review.created_at) }}</p>
        </div>
      </div>

      <div v-else-if="!loading" class="mt-4 rounded-xl border border-gray-200 bg-white px-6 py-10 text-center">
        <p class="text-sm text-gray-500">No reviews yet.</p>
      </div>
    </template>
  </div>
</template>
