<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { LifeBuoy, Loader2, Plus, X } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { supportApi } from "@/api/support";
import { useAuthStore } from "@/stores/auth";
import type { SupportTicketRecord } from "@/types/support";

const auth = useAuthStore();
const tickets = ref<SupportTicketRecord[]>([]);
const isLoading = ref(true);
const loadError = ref("");

const showForm = ref(false);
const form = reactive({
  title: "",
  description: "",
  category: "general",
});
const isCreating = ref(false);
const createError = ref("");
const createNotice = ref("");

function statusTone(status?: string | null): "danger" | "warning" | "success" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s.includes("closed") || s.includes("resolved")) return "success";
  if (s.includes("open") || s.includes("progress") || s.includes("pending")) return "warning";
  return "neutral";
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

async function fetchTickets() {
  isLoading.value = true;
  loadError.value = "";
  if (auth.isPreviewSession) {
    tickets.value = [];
    isLoading.value = false;
    return;
  }
  try {
    const { data } = await supportApi.tickets();
    tickets.value = Array.isArray(data) ? data : (data as { results?: SupportTicketRecord[] }).results ?? [];
  } catch (err: unknown) {
    const status = (err as { response?: { status?: number } })?.response?.status;
    if (status !== 401) loadError.value = "Could not load your support tickets.";
  } finally {
    isLoading.value = false;
  }
}

async function submitTicket() {
  if (!form.title || !form.description) return;
  isCreating.value = true;
  createError.value = "";
  createNotice.value = "";
  try {
    const { data } = await supportApi.createTicket({
      title: form.title,
      description: form.description,
      category: form.category,
    });
    tickets.value = [data, ...tickets.value];
    createNotice.value = "Ticket submitted. Our support team will respond within 24 hours.";
    form.title = "";
    form.description = "";
    showForm.value = false;
  } catch {
    createError.value = "Could not submit the ticket. Please try again.";
  } finally {
    isCreating.value = false;
  }
}

onMounted(() => {
  void fetchTickets();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">My tickets</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Track your open support requests and raise a new ticket if you need help.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white"
        type="button"
        @click="showForm = !showForm"
      >
        <component :is="showForm ? X : Plus" class="h-4 w-4" />
        {{ showForm ? "Cancel" : "Open ticket" }}
      </button>
    </section>

    <div
      v-if="createNotice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ createNotice }}
    </div>

    <section v-if="showForm" class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="flex items-center gap-2">
        <LifeBuoy class="h-5 w-5 text-signal" />
        <h2 class="text-base font-semibold text-ink">New support ticket</h2>
      </div>
      <form class="mt-5 grid gap-4" @submit.prevent="submitTicket">
        <label class="block text-sm font-medium text-ink">
          Subject
          <input
            v-model.trim="form.title"
            class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Briefly describe your issue"
          />
        </label>
        <label class="block text-sm font-medium text-ink">
          Category
          <select v-model="form.category" class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
            <option value="general">General</option>
            <option value="order">Order issue</option>
            <option value="billing">Billing</option>
            <option value="files">Files &amp; delivery</option>
            <option value="account">Account</option>
          </select>
        </label>
        <label class="block text-sm font-medium text-ink">
          Description
          <textarea
            v-model.trim="form.description"
            class="focus-ring mt-2 min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Describe the issue in detail so our team can help you efficiently"
          />
        </label>
        <div
          v-if="createError"
          class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
        >
          {{ createError }}
        </div>
        <button
          class="focus-ring inline-flex items-center gap-2 self-start rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          :disabled="isCreating || !form.title || !form.description"
        >
          <Loader2 v-if="isCreating" class="h-4 w-4 animate-spin" />
          Submit ticket
        </button>
      </form>
    </section>

    <div
      v-if="loadError"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ loadError }}
    </div>

    <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div v-if="isLoading" class="space-y-px">
        <div
          v-for="n in 3"
          :key="n"
          class="animate-pulse border-b border-slate-100 px-5 py-4"
          aria-hidden="true"
        >
          <div class="flex items-start gap-4">
            <div class="flex-1 space-y-2">
              <div class="h-4 w-2/3 rounded bg-slate-200" />
              <div class="h-3 w-1/3 rounded bg-slate-100" />
            </div>
            <div class="h-6 w-20 rounded-full bg-slate-100" />
          </div>
        </div>
      </div>

      <div v-else-if="!tickets.length" class="p-8">
        <EmptyState
          :icon="LifeBuoy"
          title="No support tickets"
          message="Use the button above to open a ticket if you need help. Our team responds within 24 hours."
        />
      </div>

      <div v-else class="divide-y divide-slate-100">
        <article
          v-for="ticket in tickets"
          :key="ticket.id"
          class="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-start sm:justify-between"
        >
          <div class="min-w-0">
            <p class="font-semibold text-ink">{{ ticket.title }}</p>
            <p class="mt-1 text-sm text-graphite">
              <span class="capitalize">{{ ticket.category || "general" }}</span>
              <template v-if="ticket.object_id"> · Order #{{ ticket.object_id }}</template>
              · {{ formatDate(ticket.created_at) }}
            </p>
            <p v-if="ticket.description" class="mt-1 max-w-xl truncate text-sm text-graphite">
              {{ ticket.description }}
            </p>
          </div>
          <div class="flex flex-shrink-0 flex-wrap gap-2">
            <StatusPill :label="ticket.status" :tone="statusTone(ticket.status)" />
            <StatusPill :label="ticket.priority" tone="neutral" />
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
