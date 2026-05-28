<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const title = ref("");
const description = ref("");
const deadline = ref("");
const isSaving = ref(false);
const error = ref<string | null>(null);

async function submit() {
  if (!title.value.trim() || !description.value.trim()) return;
  isSaving.value = true;
  error.value = null;
  try {
    if (auth.isPreviewSession) {
      router.push("/client/special-orders");
      return;
    }
    const res = await specialOrdersApi.createQuoted({
      title: title.value,
      inquiry_details: description.value,
    });
    router.push(`/client/special-orders/${res.data.id}`);
  } catch {
    error.value = "Failed to submit request. Please try again.";
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-2xl space-y-4">

      <div>
        <h1 class="text-xl font-bold text-ink">Request a Special Order</h1>
        <p class="text-sm text-graphite">Describe your project and we'll send you a custom quote.</p>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-6 space-y-4">

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Project Title <span class="text-rose-500">*</span></label>
          <input
            v-model="title"
            placeholder="e.g. Dissertation Editing + Formatting"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Project Description <span class="text-rose-500">*</span></label>
          <textarea
            v-model="description"
            rows="6"
            placeholder="Describe what you need in as much detail as possible. Include scope, requirements, formatting style, and any other relevant information…"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Deadline (optional)</label>
          <input
            v-model="deadline"
            type="date"
            class="rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
          />
        </div>

        <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ error }}
        </div>

        <div class="flex gap-3">
          <button
            class="rounded-lg bg-berry px-5 py-2 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
            :disabled="isSaving || !title.trim() || !description.trim()"
            @click="submit"
          >
            {{ isSaving ? "Submitting…" : "Submit Request" }}
          </button>
          <button
            class="rounded-lg border border-slate-200 px-5 py-2 text-sm text-graphite hover:text-ink"
            @click="router.back()"
          >
            Cancel
          </button>
        </div>

      </div>

      <div class="rounded-lg border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-graphite space-y-1">
        <p class="font-medium text-ink">What happens next?</p>
        <p>1. We review your request and assign an expert.</p>
        <p>2. You receive a detailed quote within 24 hours.</p>
        <p>3. Approve the quote to kick off your project.</p>
      </div>

    </div>
  </div>
</template>
