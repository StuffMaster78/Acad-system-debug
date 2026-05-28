<template>
  <div class="space-y-6">
    <!-- Revision history -->
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Revision history</h2>
        <p class="mt-0.5 text-xs text-graphite">Window: {{ lifecycle?.revision_window_days ?? 0 }} days · {{ lifecycle?.is_revision_window_open ? 'Open' : 'Closed' }}</p>
      </div>
      <div v-if="loading" class="px-5 py-6 text-sm text-graphite">Loading…</div>
      <div v-else-if="!revisions.length" class="px-5 py-8 text-center text-sm text-graphite">No revision requests on this order.</div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="rev in revisions" :key="rev.id" class="px-5 py-4">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-ink">{{ rev.reason }}</p>
              <p class="mt-1 text-xs text-graphite">{{ rev.scope_summary }}</p>
            </div>
            <span
              class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="revStatusClass(rev.status)"
            >{{ rev.status }}</span>
          </div>
          <div class="mt-2 flex items-center gap-3 text-xs text-graphite">
            <span :class="rev.is_within_original_scope ? 'text-signal' : 'text-amber-600'">
              {{ rev.is_within_original_scope ? 'Within scope' : 'Outside scope' }}
            </span>
            <span>·</span>
            <span>{{ new Date(rev.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Client: request revision form -->
    <form
      v-if="role === 'client' && lifecycle?.is_revision_window_open"
      class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel"
      @submit.prevent="submitRevision"
    >
      <div class="flex items-center gap-2">
        <RotateCcw class="h-5 w-5 text-saffron" />
        <h2 class="text-base font-semibold text-ink">Request a revision</h2>
      </div>
      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <label class="block text-sm font-medium text-ink">
          Reason
          <input v-model.trim="form.reason" class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="What needs to change?" />
        </label>
        <label class="flex items-center gap-3 rounded-md border border-slate-200 px-3 py-3 text-sm font-medium text-ink">
          <input v-model="form.is_within_original_scope" class="h-4 w-4" type="checkbox" />
          Within original scope
        </label>
      </div>
      <label class="mt-4 block text-sm font-medium text-ink">
        Scope summary
        <textarea v-model.trim="form.scope_summary" class="focus-ring mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Describe the exact revision scope" />
      </label>
      <button
        class="focus-ring mt-4 inline-flex items-center justify-center gap-2 rounded-md bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
        type="submit"
        :disabled="orders.isMutating || !form.reason || !form.scope_summary"
      >Submit revision request</button>
    </form>

    <div v-else-if="role === 'client' && !lifecycle?.is_revision_window_open" class="rounded-lg border border-slate-100 bg-slate-50 p-4 text-sm text-graphite">
      The revision window is closed for this order.
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { RotateCcw } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderLifecycle, RevisionRequest } from "@/types/orders";
import { ordersApi } from "@/api/orders";
import { useOrderStore } from "@/stores/orders";

const props = defineProps<{
  orderId: string;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const orders = useOrderStore();
const revisions = ref<RevisionRequest[]>([]);
const loading = ref(false);

const form = reactive({ reason: "", scope_summary: "", is_within_original_scope: true });

function revStatusClass(status: string): string {
  if (status === "resolved") return "bg-emerald-100 text-emerald-700";
  if (status === "pending") return "bg-amber-100 text-amber-700";
  if (status === "rejected") return "bg-rose-100 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

async function loadRevisions() {
  loading.value = true;
  try {
    const { data } = await ordersApi.revisions(props.orderId);
    revisions.value = Array.isArray(data) ? data : (data as { results: RevisionRequest[] }).results ?? [];
  } catch {
    revisions.value = [];
  } finally {
    loading.value = false;
  }
}

async function submitRevision() {
  if (!form.reason || !form.scope_summary) return;
  await orders.requestRevision(props.orderId, { ...form });
  form.reason = "";
  form.scope_summary = "";
  await loadRevisions();
}

onMounted(loadRevisions);
</script>
