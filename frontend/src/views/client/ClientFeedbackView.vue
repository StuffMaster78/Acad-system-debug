<template>
  <div class="mx-auto max-w-3xl space-y-6 px-4 py-8">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-ink">Feedback & Requests</h1>
      <p class="mt-1 text-sm text-graphite">
        Share ideas, report bugs, or suggest improvements. We read everything.
      </p>
    </div>

    <!-- Notice / Error -->
    <p v-if="fb.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ fb.notice }}
    </p>
    <p v-if="fb.error" class="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      {{ fb.error }}
    </p>

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
              <option v-for="cat in fb.categories" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
          </label>
        </div>

        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Title <span class="text-red-500">*</span></span>
          <input
            v-model="form.title"
            type="text"
            placeholder="Short summary of your request"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
          />
        </label>

        <label class="block">
          <span class="text-xs font-semibold uppercase text-graphite">Details <span class="text-red-500">*</span></span>
          <textarea
            v-model="form.description"
            rows="5"
            placeholder="Describe what you'd like and why it would help you"
            class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          />
        </label>

        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-semibold uppercase text-graphite">Priority</span>
            <select v-model="form.priority" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-semibold uppercase text-graphite">Related order ID (optional)</span>
            <input
              v-model.number="form.linked_order_id"
              type="number"
              placeholder="e.g. 1042"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
            />
          </label>
        </div>

        <button
          class="focus-ring inline-flex h-10 items-center justify-center rounded-md bg-signal px-5 text-sm font-semibold text-white disabled:opacity-50"
          :disabled="fb.isMutating || !form.title.trim() || !form.description.trim()"
          @click="handleSubmit"
        >
          <span v-if="fb.isMutating">Submitting…</span>
          <span v-else>Submit request</span>
        </button>
      </div>
    </section>

    <!-- My submissions -->
    <section>
      <h2 class="text-base font-semibold text-ink">My submissions</h2>
      <div v-if="fb.isLoading" class="mt-4 text-sm text-graphite">Loading…</div>
      <div v-else-if="!fb.items.length" class="mt-4 text-sm text-graphite">No submissions yet.</div>
      <div v-else class="mt-4 space-y-3">
        <article
          v-for="item in fb.items"
          :key="item.id"
          class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate font-semibold text-ink">{{ item.title }}</p>
              <p class="mt-0.5 text-xs text-graphite">
                {{ categoryLabel(item.category) }} · {{ typeLabel(item.request_type) }}
              </p>
            </div>
            <StatusBadge :status="item.status" />
          </div>

          <!-- Public response -->
          <div
            v-if="item.public_response"
            class="mt-3 rounded-md border border-emerald-100 bg-emerald-50 p-3 text-sm text-emerald-900"
          >
            <p class="text-xs font-semibold uppercase text-emerald-700">Team response</p>
            <p class="mt-1">{{ item.public_response }}</p>
          </div>

          <div class="mt-3 flex items-center gap-4 text-xs text-graphite">
            <button
              class="flex items-center gap-1 rounded-md px-2 py-1 transition-colors hover:bg-slate-50"
              :class="item.has_voted ? 'text-signal font-semibold' : ''"
              @click="fb.vote(item.id)"
            >
              <span>▲</span>
              <span>{{ item.upvote_count }}</span>
            </button>
            <span>{{ formatDate(item.created_at) }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize"
              :class="priorityClass(item.priority)"
            >{{ item.priority }}</span>
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
  category: "orders",
  priority: "medium" as FeedbackPriority,
  linked_order_id: null as number | null,
});

onMounted(async () => {
  await Promise.all([fb.loadCategories(), fb.load(true)]);
  if (fb.categories.length && !form.category) {
    form.category = fb.categories[0].value;
  }
});

async function handleSubmit() {
  const result = await fb.submit({ ...form });
  if (result) {
    form.title = "";
    form.description = "";
    form.linked_order_id = null;
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString();
}

function categoryLabel(code: string) {
  return fb.categories.find((c) => c.value === code)?.label ?? code;
}

function typeLabel(t: string) {
  const map: Record<string, string> = {
    feature_request: "Feature request",
    improvement: "Improvement",
    bug_report: "Bug",
    question: "Question",
  };
  return map[t] ?? t;
}

function priorityClass(p: string) {
  return {
    low: "bg-slate-100 text-slate-600",
    medium: "bg-blue-50 text-blue-700",
    high: "bg-amber-50 text-amber-700",
    critical: "bg-red-50 text-red-700",
  }[p] ?? "bg-slate-100 text-slate-600";
}

// Inline minimal status badge
import { defineComponent, h } from "vue";
const StatusBadge = defineComponent({
  props: { status: String },
  setup(props) {
    const map: Record<string, string> = {
      new: "bg-slate-100 text-slate-700",
      triaging: "bg-blue-50 text-blue-700",
      planned: "bg-indigo-50 text-indigo-700",
      in_progress: "bg-amber-50 text-amber-700",
      released: "bg-emerald-50 text-emerald-700",
      declined: "bg-red-50 text-red-700",
      duplicate: "bg-slate-100 text-slate-500",
    };
    const label: Record<string, string> = {
      new: "New", triaging: "Triaging", planned: "Planned",
      in_progress: "In progress", released: "Released",
      declined: "Declined", duplicate: "Duplicate",
    };
    return () => h(
      "span",
      { class: `rounded-full px-2 py-0.5 text-xs font-semibold whitespace-nowrap ${map[props.status ?? ""] ?? "bg-slate-100 text-slate-700"}` },
      label[props.status ?? ""] ?? props.status,
    );
  },
});
</script>
