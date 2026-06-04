<template>
  <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <template v-if="existing">
      <!-- Already reviewed -->
      <div class="flex items-start gap-3">
        <CheckCircle2 class="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" />
        <div>
          <p class="font-semibold text-ink">Your review</p>
          <div class="mt-1 flex items-center gap-1">
            <Star
              v-for="n in 5"
              :key="n"
              class="h-4 w-4"
              :class="n <= existing.rating ? 'text-amber-400' : 'text-slate-200'"
              fill="currentColor"
            />
            <span class="ml-1 text-sm text-graphite">{{ existing.rating }}/5</span>
          </div>
          <p v-if="existing.body" class="mt-1 text-sm text-graphite">{{ existing.body }}</p>
        </div>
      </div>
    </template>

    <template v-else-if="submitted">
      <div class="flex items-center gap-3 text-emerald-700">
        <CheckCircle2 class="h-5 w-5 shrink-0" />
        <p class="font-semibold">Thank you for your review!</p>
      </div>
    </template>

    <template v-else>
      <h3 class="font-semibold text-ink">Rate this order</h3>
      <p class="mt-0.5 text-sm text-graphite">How would you rate the quality of work delivered?</p>

      <!-- Star picker -->
      <div class="mt-3 flex items-center gap-1">
        <button
          v-for="n in 5"
          :key="n"
          type="button"
          class="focus-ring rounded p-0.5 transition-transform hover:scale-110"
          @click="form.rating = n"
          @mouseenter="hovered = n"
          @mouseleave="hovered = 0"
        >
          <Star
            class="h-7 w-7"
            :class="n <= (hovered || form.rating) ? 'text-amber-400' : 'text-slate-200'"
            fill="currentColor"
          />
        </button>
        <span v-if="form.rating" class="ml-2 text-sm font-medium text-graphite">
          {{ ratingLabel(form.rating) }}
        </span>
      </div>

      <!-- Comment -->
      <label class="mt-3 block">
        <span class="text-xs font-semibold uppercase text-graphite">Comment (optional)</span>
        <textarea
          v-model="form.comment"
          rows="3"
          placeholder="Share what went well or what could be improved…"
          class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
        />
      </label>

      <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>

      <button
        class="focus-ring mt-3 inline-flex h-10 items-center justify-center rounded-md bg-signal px-5 text-sm font-semibold text-white disabled:opacity-50"
        :disabled="!form.rating || submitting"
        @click="submit"
      >
        <span v-if="submitting">Submitting…</span>
        <span v-else>Submit review</span>
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { CheckCircle2, Star } from "@lucide/vue";
import { reviewsApi } from "@/api/reviews";
import type { Review } from "@/types/reviews";

const props = defineProps<{ orderId: number }>();

const existing = ref<Review | null>(null);
const submitted = ref(false);
const submitting = ref(false);
const error = ref("");
const hovered = ref(0);
const form = reactive({ rating: 0, comment: "" });

const LABELS = ["", "Poor", "Fair", "Good", "Very good", "Excellent"];
function ratingLabel(n: number) { return LABELS[n] ?? ""; }

onMounted(async () => {
  try {
    const { data } = await reviewsApi.forOrder(props.orderId);
    if (data) existing.value = data as Review;
  } catch {
    // no existing review — show form
  }
});

async function submit() {
  if (!form.rating) return;
  submitting.value = true;
  error.value = "";
  try {
    await reviewsApi.submit(props.orderId, {
      rating: form.rating,
      body: form.comment || undefined,
    });
    submitted.value = true;
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = detail ?? "Failed to submit review. Please try again.";
  } finally {
    submitting.value = false;
  }
}
</script>
