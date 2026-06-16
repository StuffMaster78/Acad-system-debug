<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  Banknote,
  Briefcase,
  CalendarOff,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Loader2,
  PauseCircle,
  RefreshCw,
  Search,
  X,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import WriterOnboardingGate from "@/components/writer/WriterOnboardingGate.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";

const workspace = useWriterWorkspaceStore();

const levelLabel = computed(() => {
  const level = workspace.profile?.writer_level;
  if (!level) return "Writer";
  if (typeof level === "string") return level;
  return (level as { name?: string; label?: string }).name ?? (level as { name?: string; label?: string }).label ?? "Writer";
});

const activeAssignments = computed(() =>
  (workspace.assignments ?? []).filter((a) => ["in_progress", "revision_requested"].includes(String(a.status))),
);

const activeWindow = computed(() => workspace.availability?.active_window);
const upcomingWindows = computed(() => workspace.availability?.upcoming_windows ?? []);

function money(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === "") return "$0.00";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
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

function relativeDeadline(deadline?: string | null): string {
  if (!deadline) return "No deadline";
  const diff = new Date(deadline).getTime() - Date.now();
  const hours = Math.round(diff / (1000 * 60 * 60));
  if (hours < 0) return `${Math.abs(hours)}h overdue`;
  if (hours < 24) return `${hours}h left`;
  return `${Math.round(hours / 24)}d left`;
}

function deadlineTone(deadline?: string | null): "danger" | "warning" | "neutral" {
  if (!deadline) return "neutral";
  const hours = (new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60);
  if (hours < 0) return "danger";
  if (hours < 24) return "warning";
  return "neutral";
}

const showWindowForm = ref(false);
const windowForm = reactive({ start_at: "", end_at: "", reason: "" });
const windowFormError = ref("");

async function submitWindow() {
  windowFormError.value = "";
  if (!windowForm.start_at) {
    windowFormError.value = "Start date is required.";
    return;
  }
  try {
    await workspace.scheduleUnavailability({
      start_at: windowForm.start_at,
      end_at: windowForm.end_at || null,
      reason: windowForm.reason || undefined,
    });
    windowForm.start_at = "";
    windowForm.end_at = "";
    windowForm.reason = "";
    showWindowForm.value = false;
  } catch {
    windowFormError.value = "Failed to schedule. Check the dates and try again.";
  }
}

const onboardingStatus = computed(() => workspace.profile?.onboarding_status ?? null);
const isOnboarded = computed(() => onboardingStatus.value === "completed" || onboardingStatus.value === null);

onMounted(async () => {
  await workspace.hydrate();
  if (isOnboarded.value && !workspace.assignments.length) {
    workspace.fetchAssignments(1, "in_progress,revision_requested").catch(() => undefined);
  }
});
</script>

<template>
  <div class="space-y-4">

    <!-- Onboarding gate — shown until admin approves the writer ─────────── -->
    <WriterOnboardingGate
      v-if="!isOnboarded && onboardingStatus"
      :status="onboardingStatus"
      :rejection-reason="workspace.profile?.rejection_reason as string | null | undefined"
    />

    <template v-else>
    <!-- Header + slim stats strip ──────────────────────────────────────── -->
    <section class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-ink">
          {{ workspace.profile?.display_name ?? "My workspace" }}
        </h1>
        <p class="mt-1 text-sm text-graphite">{{ levelLabel }}</p>
        <!-- Inline stats strip -->
        <div class="mt-3 flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-1.5 text-sm">
            <span class="font-bold text-ink tabular-nums">{{ money(workspace.currentWindow?.net) }}</span>
            <span class="text-graphite">this window</span>
          </div>
          <span class="text-slate-300">·</span>
          <div class="flex items-center gap-1.5 text-sm">
            <span class="font-bold text-ink tabular-nums">{{ activeAssignments.length }}</span>
            <span class="text-graphite">active {{ activeAssignments.length === 1 ? 'order' : 'orders' }}</span>
          </div>
          <span class="text-slate-300">·</span>
          <div class="flex items-center gap-1.5 text-sm">
            <span class="font-bold text-ink tabular-nums">{{ money(workspace.balance?.pending) }}</span>
            <span class="text-graphite">pending</span>
          </div>
        </div>
      </div>

      <div class="flex shrink-0 items-center gap-2">
        <button
          class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-50"
          type="button"
          :disabled="workspace.isLoading"
          title="Refresh"
          @click="workspace.hydrate()"
        >
          <RefreshCw class="h-4 w-4" :class="workspace.isLoading ? 'animate-spin' : ''" />
        </button>
        <button
          class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold shadow-sm transition-all disabled:opacity-60"
          :class="workspace.isAcceptingOrders
            ? 'bg-emerald-600 text-white hover:bg-emerald-700'
            : 'border border-slate-200 bg-white text-graphite hover:bg-slate-50'"
          type="button"
          :disabled="workspace.isMutating"
          @click="workspace.toggleAcceptingOrders()"
        >
          <Loader2 v-if="workspace.isMutating" class="h-4 w-4 animate-spin" />
          <CheckCircle2 v-else-if="workspace.isAcceptingOrders" class="h-4 w-4" />
          <PauseCircle v-else class="h-4 w-4" />
          {{ workspace.isAcceptingOrders ? "Accepting orders" : "Paused" }}
        </button>
      </div>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Active orders</h2>
            <p class="mt-1 text-sm text-graphite">In-progress and revision-requested assignments.</p>
          </div>
          <Briefcase class="h-5 w-5 text-signal" />
        </div>

        <div class="mt-5">
          <div v-if="workspace.isAssignmentsLoading" class="py-4 text-sm text-graphite">
            Loading assignments...
          </div>
          <div v-else-if="!activeAssignments.length" class="rounded-md border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-graphite">
            No active assignments — browse the
            <RouterLink class="font-semibold text-signal underline-offset-2 hover:underline" to="/writer/available">
              job pool
            </RouterLink>
            to pick up work.
          </div>
          <div v-else class="overflow-hidden rounded-md border border-slate-200">
            <div class="overflow-x-auto">
            <div class="min-w-[360px]">
            <div class="grid grid-cols-[1fr_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
              <span>Order</span>
              <span>Status</span>
              <span class="text-right">Deadline</span>
            </div>
            <RouterLink
              v-for="order in activeAssignments.slice(0, 5)"
              :key="String(order.id)"
              :to="`/writer/orders/${order.id}`"
              class="grid grid-cols-[1fr_auto_auto] gap-3 border-t border-slate-100 px-4 py-3 text-sm transition hover:bg-slate-50"
            >
              <span class="min-w-0">
                <span class="block truncate font-semibold text-ink">{{ order.topic ?? `Order #${order.id}` }}</span>
                <span class="mt-0.5 block truncate text-xs text-graphite">
                  #{{ order.id }} · {{ order.academic_level ?? "" }}
                </span>
              </span>
              <StatusPill :label="String(order.status ?? 'in_progress')" tone="warning" />
              <span class="text-right">
                <StatusPill
                  :label="relativeDeadline(order.writer_deadline)"
                  :tone="deadlineTone(order.writer_deadline)"
                />
              </span>
            </RouterLink>
            </div>
            </div>
          </div>

          <RouterLink
            class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-200 px-4 py-2.5 text-sm font-semibold text-ink hover:bg-slate-50"
            to="/writer/assignments"
          >
            View all assignments
            <ChevronRight class="h-4 w-4" />
          </RouterLink>
        </div>
      </div>

      <div class="space-y-4">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <!-- Header row: always visible -->
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-semibold text-ink">Availability</h2>
              <StatusPill
                :label="workspace.isUnavailable ? 'Unavailable' : 'Available'"
                :tone="workspace.isUnavailable ? 'warning' : 'success'"
              />
            </div>
            <button
              class="focus-ring inline-flex h-7 items-center gap-1 rounded-md border border-slate-200 px-2.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="showWindowForm = !showWindowForm"
            >
              <CalendarOff class="h-3.5 w-3.5" />
              Schedule off
            </button>
          </div>

          <!-- Schedule off form — expands inline -->
          <div v-if="showWindowForm" class="mt-4 space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">New unavailability window</p>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-medium text-graphite">Start</span>
                <input v-model="windowForm.start_at" class="focus-ring mt-1 h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm" type="datetime-local" />
              </label>
              <label class="block">
                <span class="text-xs font-medium text-graphite">End (optional)</span>
                <input v-model="windowForm.end_at" class="focus-ring mt-1 h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm" type="datetime-local" />
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-medium text-graphite">Reason (optional)</span>
              <input v-model="windowForm.reason" class="focus-ring mt-1 h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm" type="text" placeholder="e.g. Holiday, illness, personal leave" />
            </label>
            <p v-if="windowFormError" class="text-xs text-berry">{{ windowFormError }}</p>
            <div class="flex gap-2">
              <button class="focus-ring inline-flex items-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60" type="button" :disabled="workspace.isMutating || !windowForm.start_at" @click="submitWindow">
                <Loader2 v-if="workspace.isMutating" class="h-3 w-3 animate-spin" /><CheckCircle2 v-else class="h-3 w-3" /> Save
              </button>
              <button class="focus-ring rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-white" type="button" @click="showWindowForm = false; windowFormError = ''">Cancel</button>
            </div>
          </div>

          <!-- Active window — only shown when one exists -->
          <div v-if="activeWindow" class="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 text-xs font-semibold text-amber-800">
                <Clock3 class="h-3.5 w-3.5" /> Off until {{ dateLabel(activeWindow.end_at) }}
              </div>
              <button
                class="focus-ring inline-flex h-6 items-center gap-1 rounded px-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                type="button"
                :disabled="workspace.isMutating"
                @click="workspace.cancelAvailabilityWindow(activeWindow.id).catch(() => undefined)"
              >
                <X class="h-3 w-3" /> End now
              </button>
            </div>
            <p v-if="activeWindow.reason" class="mt-1 text-xs text-amber-700">{{ activeWindow.reason }}</p>
          </div>

          <!-- Upcoming windows — only shown when any exist -->
          <div v-if="upcomingWindows.length" class="mt-3 space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Upcoming</p>
            <div
              v-for="window in upcomingWindows"
              :key="window.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-slate-200 px-3 py-2.5"
            >
              <div class="min-w-0">
                <p class="text-sm text-ink">{{ dateLabel(window.start_at) }} – {{ dateLabel(window.end_at) }}</p>
                <p v-if="window.reason" class="mt-0.5 text-xs text-graphite">{{ window.reason }}</p>
              </div>
              <button
                class="focus-ring shrink-0 rounded p-1 text-xs font-semibold text-rose-700 hover:bg-rose-50 disabled:opacity-60"
                type="button"
                :disabled="workspace.isMutating"
                @click="workspace.cancelAvailabilityWindow(window.id).catch(() => undefined)"
              >
                <X class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        <RouterLink
          class="focus-ring flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-5 py-4 hover:bg-slate-50"
          to="/writer/available"
        >
          <div class="flex items-center gap-3">
            <Search class="h-5 w-5 text-signal" />
            <div>
              <p class="text-sm font-semibold text-ink">Job pool</p>
              <p class="mt-0.5 text-xs text-graphite">Browse and claim new orders</p>
            </div>
          </div>
          <ChevronRight class="h-4 w-4 text-graphite" />
        </RouterLink>

        <RouterLink
          class="focus-ring flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-5 py-4 hover:bg-slate-50"
          to="/writer/earnings"
        >
          <div class="flex items-center gap-3">
            <Banknote class="h-5 w-5 text-signal" />
            <div>
              <p class="text-sm font-semibold text-ink">Earnings & payouts</p>
              <p class="mt-0.5 text-xs text-graphite">Events, balance, and payout requests</p>
            </div>
          </div>
          <ChevronRight class="h-4 w-4 text-graphite" />
        </RouterLink>
      </div>
    </section>

    </template><!-- end v-else onboarded -->

  </div>
</template>
