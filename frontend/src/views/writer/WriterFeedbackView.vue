<template>
  <div class="mx-auto max-w-3xl space-y-6 px-4 py-8">
    <div>
      <h1 class="text-2xl font-bold text-ink">Feedback & Requests</h1>
      <p class="mt-1 text-sm text-graphite">
        Help us improve the writer experience. Suggest features, report bugs, or ask questions.
      </p>
    </div>

    <p v-if="fb.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ fb.notice }}</p>
    <p v-if="fb.error" class="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{{ fb.error }}</p>

    <!-- Submit form -->
    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 class="text-base font-semibold text-ink">Submit a request</h2>
      <div class="mt-4 space-y-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-semibold uppercase text-graphite">Type</span>
            <select v-model="form.request_type" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm">
              <option value="feature_request">Feature Request</option>
              <option value="improvement">Improvement</option>
              <option value="bug_report">Bug Report</option>
              <option value="question">Question</option>
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase text-graphite">Category</span>
            <select v-model="form.category" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm">
              <option v-for="cat in fb.categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
            </select>
          </label>
        </div>

        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Title <span class="text-red-500">*</span></span>
          <input v-model="form.title" type="text" placeholder="e.g. Allow writers to see deadline buffer time"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
        </label>

        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Details <span class="text-red-500">*</span></span>
          <textarea v-model="form.description" rows="5"
            placeholder="Describe the problem or idea and how it would improve your workflow"
            class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
        </label>

        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Priority</span>
          <select v-model="form.priority" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </label>

        <button
          class="focus-ring inline-flex h-10 items-center justify-center rounded-md bg-signal px-5 text-sm font-semibold text-white disabled:opacity-50"
          :disabled="fb.isMutating || !form.title.trim() || !form.description.trim()"
          @click="handleSubmit"
        >
          <span v-if="fb.isMutating">Submitting…</span>
          <span v-else>Submit</span>
        </button>
      </div>
    </section>

    <!-- My submissions -->
    <section>
      <h2 class="text-base font-semibold text-ink">My submissions</h2>
      <div v-if="fb.isLoading" class="mt-4 text-sm text-graphite">Loading…</div>
      <div v-else-if="!fb.items.length" class="mt-4 text-sm text-graphite">You haven't submitted any requests yet.</div>
      <div v-else class="mt-4 space-y-3">
        <article v-for="item in fb.items" :key="item.id"
          class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate font-semibold text-ink">{{ item.title }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ item.category }} · {{ item.request_type }}</p>
            </div>
            <span
              class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="statusClass(item.status)"
            >{{ item.status.replace("_", " ") }}</span>
          </div>
          <div v-if="item.public_response"
            class="mt-3 rounded-md border border-emerald-100 bg-emerald-50 p-3 text-sm text-emerald-900">
            <p class="text-xs font-semibold uppercase text-emerald-700">Response from team</p>
            <p class="mt-1">{{ item.public_response }}</p>
          </div>
          <div class="mt-3 flex items-center gap-3 text-xs text-graphite">
            <button
              class="flex items-center gap-1 rounded px-2 py-0.5 transition-colors hover:bg-slate-50"
              :class="item.has_voted ? 'text-signal font-semibold' : ''"
              @click="fb.vote(item.id)"
            >▲ {{ item.upvote_count }}</button>
            <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { useFeedbackStore } from "@/stores/feedback";
import type { FeedbackType, FeedbackPriority } from "@/api/feedback";

const fb = useFeedbackStore();

const form = reactive({
  title: "",
  description: "",
  request_type: "feature_request" as FeedbackType,
  category: "writer_workflow",
  priority: "medium" as FeedbackPriority,
});

onMounted(async () => {
  await Promise.all([fb.loadCategories(), fb.load(true)]);
  if (fb.categories.length && !fb.categories.find(c => c.value === form.category)) {
    form.category = fb.categories[0].value;
  }
});

async function handleSubmit() {
  const result = await fb.submit({ ...form });
  if (result) {
    form.title = "";
    form.description = "";
  }
}

function statusClass(s: string) {
  const m: Record<string, string> = {
    new: "bg-slate-100 text-slate-700",
    triaging: "bg-blue-50 text-blue-700",
    planned: "bg-indigo-50 text-indigo-700",
    in_progress: "bg-amber-50 text-amber-700",
    released: "bg-emerald-50 text-emerald-700",
    declined: "bg-red-50 text-red-700",
    duplicate: "bg-slate-100 text-slate-500",
  };
  return m[s] ?? "bg-slate-100 text-slate-700";
}
</script>
