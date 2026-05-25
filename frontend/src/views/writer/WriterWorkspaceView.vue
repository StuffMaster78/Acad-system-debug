<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import {
  Banknote,
  CheckCircle2,
  Clock3,
  Hand,
  Loader2,
  PauseCircle,
  Send,
  Undo2,
} from "@lucide/vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";

const workspace = useWriterWorkspaceStore();

const actionForm = reactive({
  orderId: "",
  interestId: "",
  message: "",
});

const levelLabel = computed(() => {
  const level = workspace.profile?.writer_level;
  if (!level) return "Writer";
  if (typeof level === "string") return level;
  return level.name ?? level.label ?? "Writer";
});

const activeWindow = computed(() => workspace.availability?.active_window);
const upcomingWindows = computed(() => workspace.availability?.upcoming_windows ?? []);

function money(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === "") return "$0.00";
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) return String(value);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
}

function dateLabel(value: string | undefined | null): string {
  if (!value) return "Open ended";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function submitInterest() {
  if (!actionForm.orderId) return;
  await workspace.expressInterest(actionForm.orderId, actionForm.message);
  actionForm.message = "";
}

async function takeOrder() {
  if (!actionForm.orderId) return;
  await workspace.takeOrder(actionForm.orderId);
}

async function withdrawInterest() {
  if (!actionForm.interestId) return;
  await workspace.withdrawInterest(actionForm.interestId);
  actionForm.interestId = "";
}

onMounted(() => {
  void workspace.hydrate();
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">
          {{ workspace.profile?.display_name ?? "Assignment desk" }}
        </h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          {{ levelLabel }} desk with availability, assignment actions, and payout signals wired to the backend.
        </p>
      </div>

      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-ink px-4 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-graphite disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="workspace.isMutating"
        @click="workspace.toggleAcceptingOrders()"
      >
        <Loader2 v-if="workspace.isMutating" class="h-4 w-4 animate-spin" />
        <CheckCircle2 v-else-if="workspace.isAcceptingOrders" class="h-4 w-4" />
        <PauseCircle v-else class="h-4 w-4" />
        {{ workspace.isAcceptingOrders ? "Accepting orders" : "Paused" }}
      </button>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <MetricTile
        :metric="{
          label: 'Current window',
          value: money(workspace.currentWindow?.net),
          detail: `${workspace.currentWindow?.count ?? 0} events`,
          tone: 'good',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Pending balance',
          value: money(workspace.balance?.pending),
          detail: 'Not yet matured',
          tone: 'warn',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Lifetime balance',
          value: money(workspace.balance?.lifetime),
          detail: 'Matured and paid',
          tone: 'neutral',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Completed orders',
          value: String(workspace.summary?.completed_orders ?? 0),
          detail: 'Backend summary',
          tone: 'neutral',
        }"
      />
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-ink">Availability</h2>
            <p class="mt-1 text-sm text-graphite">Live capacity state from writer management.</p>
          </div>
          <StatusPill
            :label="workspace.isUnavailable ? 'Unavailable window active' : 'Available for routing'"
            :tone="workspace.isUnavailable ? 'warning' : 'success'"
          />
        </div>

        <div class="mt-5 grid gap-4 md:grid-cols-2">
          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2 text-sm font-semibold text-ink">
              <Clock3 class="h-4 w-4 text-signal" />
              Active window
            </div>
            <p class="mt-3 text-sm text-graphite">
              <template v-if="activeWindow">
                {{ dateLabel(activeWindow.start_at) }} to {{ dateLabel(activeWindow.end_at) }}
              </template>
              <template v-else>No active unavailability window.</template>
            </p>
          </div>

          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2 text-sm font-semibold text-ink">
              <Clock3 class="h-4 w-4 text-saffron" />
              Upcoming
            </div>
            <p class="mt-3 text-sm text-graphite">
              {{ upcomingWindows.length ? `${upcomingWindows.length} scheduled window(s)` : "Nothing scheduled." }}
            </p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Assignment actions</h2>
            <p class="mt-1 text-sm text-graphite">Use backend staffing actions while the marketplace feed is finalized.</p>
          </div>
          <Hand class="h-5 w-5 text-signal" />
        </div>

        <div class="mt-5 space-y-4">
          <label class="block text-sm font-medium text-ink">
            Order ID
            <input
              v-model.trim="actionForm.orderId"
              class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              inputmode="numeric"
              placeholder="Example: 4821"
            />
          </label>

          <label class="block text-sm font-medium text-ink">
            Interest message
            <textarea
              v-model.trim="actionForm.message"
              class="focus-ring mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="Short note for the assignment team"
            />
          </label>

          <div class="grid gap-3 sm:grid-cols-2">
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !actionForm.orderId"
              @click="submitInterest"
            >
              <Send class="h-4 w-4" />
              Express interest
            </button>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !actionForm.orderId"
              @click="takeOrder"
            >
              <CheckCircle2 class="h-4 w-4" />
              Take order
            </button>
          </div>

          <div class="border-t border-slate-200 pt-4">
            <label class="block text-sm font-medium text-ink">
              Interest ID
              <input
                v-model.trim="actionForm.interestId"
                class="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                inputmode="numeric"
                placeholder="Withdraw a pending interest"
              />
            </label>
            <button
              class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !actionForm.interestId"
              @click="withdrawInterest"
            >
              <Undo2 class="h-4 w-4" />
              Withdraw interest
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-ink">Recent earnings events</h2>
          <p class="mt-1 text-sm text-graphite">Compensation events from the writer payout service.</p>
        </div>
        <Banknote class="h-5 w-5 text-signal" />
      </div>

      <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
        <div class="grid grid-cols-[1fr_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <span>Event</span>
          <span>Status</span>
          <span class="text-right">Amount</span>
        </div>
        <div v-if="workspace.isLoading" class="px-4 py-6 text-sm text-graphite">Loading writer workspace...</div>
        <div v-else-if="!workspace.events.length" class="px-4 py-6 text-sm text-graphite">No earnings events yet.</div>
        <div
          v-for="event in workspace.events"
          v-else
          :key="String(event.id ?? event.created_at ?? event.event_type)"
          class="grid grid-cols-[1fr_auto_auto] gap-3 border-t border-slate-100 px-4 py-3 text-sm"
        >
          <span class="font-medium text-ink">{{ event.description ?? event.event_type ?? "Compensation event" }}</span>
          <StatusPill :label="event.status ?? 'recorded'" tone="neutral" />
          <span class="text-right font-semibold text-ink">{{ money(event.net_amount ?? event.amount) }}</span>
        </div>
      </div>
    </section>
  </div>
</template>
