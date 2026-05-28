<template>
  <div class="space-y-4">

    <!-- Assignment summary -->
    <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-sm font-semibold text-ink">Assignment</h2>
      </div>
      <dl class="grid gap-px bg-slate-100 sm:grid-cols-2">
        <div class="bg-white px-5 py-3">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Assigned writer</dt>
          <dd class="mt-1 font-mono text-sm text-ink">
            {{ lifecycle?.has_current_assignment ? maskedWriter(lifecycle.current_writer_id) : "Unassigned" }}
          </dd>
        </div>
        <div class="bg-white px-5 py-3">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Assignment ID</dt>
          <dd class="mt-1 text-sm text-ink">{{ lifecycle?.current_assignment_id ?? "—" }}</dd>
        </div>
        <div class="bg-white px-5 py-3">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Preferred writer</dt>
          <dd class="mt-1 font-mono text-sm text-ink">
            {{ order.preferred_writer ? maskedWriter(order.preferred_writer as number) : "None" }}
          </dd>
        </div>
        <div class="bg-white px-5 py-3">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer payout</dt>
          <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.writer_compensation) }}</dd>
        </div>
        <div v-if="lifecycle?.has_pending_reassignment_request" class="bg-white px-5 py-3 sm:col-span-2">
          <dt class="text-xs font-semibold uppercase tracking-wide text-amber-600">Reassignment pending</dt>
          <dd class="mt-1 text-sm text-ink">#{{ lifecycle.pending_reassignment_request_id }}</dd>
        </div>
      </dl>
    </div>

    <!-- Bids / expressions of interest -->
    <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 class="text-sm font-semibold text-ink">Writer Bids</h2>
          <p class="text-xs text-graphite mt-0.5">Expressions of interest from pool writers</p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
          :disabled="loadingInterests"
          @click="loadInterests"
        >
          <RefreshCw class="size-3.5" :class="loadingInterests ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>

      <div v-if="loadingInterests" class="px-5 py-8 text-center text-sm text-graphite animate-pulse">
        Loading bids…
      </div>

      <div v-else-if="!interests.length" class="px-5 py-10 text-center">
        <Users class="mx-auto mb-2 size-7 text-slate-300" />
        <p class="text-sm text-graphite">No bids yet.</p>
        <p class="mt-1 text-xs text-slate-400">Writers who express interest in this order will appear here.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div
          v-for="bid in interests"
          :key="bid.id"
          class="flex items-start gap-4 px-5 py-3"
        >
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono text-sm font-semibold text-ink">
                Writer #W{{ String(bid.writer_id).padStart(4, "0") }}
              </span>
              <span
                class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
                :class="interestStatusClass(bid.status)"
              >
                {{ bid.status }}
              </span>
              <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite capitalize">
                {{ bid.interest_type.replace(/_/g, " ") }}
              </span>
            </div>
            <p v-if="bid.message" class="mt-1.5 text-sm text-graphite">{{ bid.message }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ fmtDate(bid.created_at) }}</p>
          </div>
          <button
            v-if="bid.status === 'pending' && canAssign"
            class="shrink-0 rounded-lg bg-ink px-3 py-1.5 text-xs font-semibold text-white hover:bg-ink/90 disabled:opacity-50"
            :disabled="assigning === bid.id"
            @click="assign(bid.id)"
          >
            {{ assigning === bid.id ? "Assigning…" : "Assign" }}
          </button>
        </div>
      </div>
    </div>

    <p v-if="assignError" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-700">
      {{ assignError }}
    </p>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { RefreshCw, Users } from "@lucide/vue";
import type { OrderSummary, OrderLifecycle, OrderInterestRecord } from "@/types/orders";
import type { UserRole } from "@/types/roles";
import { ordersApi } from "@/api/orders";
import { useAuthStore } from "@/stores/auth";
import { maskedWriter } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const emit = defineEmits<{ (e: "refresh"): void }>();

const auth = useAuthStore();
const interests = ref<OrderInterestRecord[]>([]);
const loadingInterests = ref(false);
const assigning = ref<number | null>(null);
const assignError = ref("");

const canAssign = computed(() => props.role === "admin" || props.role === "superadmin");

function money(v: string | number | null | undefined): string {
  if (v === null || v === undefined || v === "") return "USD 0.00";
  return `USD ${v}`;
}

function fmtDate(v: string | null): string {
  if (!v) return "—";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

function interestStatusClass(s: string): string {
  const map: Record<string, string> = {
    pending:   "bg-amber-100 text-amber-700",
    accepted:  "bg-emerald-100 text-emerald-700",
    withdrawn: "bg-slate-100 text-slate-500",
    rejected:  "bg-rose-100 text-rose-700",
  };
  return map[s] ?? "bg-slate-100 text-slate-600";
}

async function loadInterests() {
  loadingInterests.value = true;
  assignError.value = "";
  try {
    if (auth.isPreviewSession) {
      interests.value = [
        { id: 1, writer_id: 3201, writer_username: null, interest_type: "pool_bid", status: "pending",  message: "I have strong experience in this subject area.", created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), reviewed_at: null },
        { id: 2, writer_id: 4857, writer_username: null, interest_type: "pool_bid", status: "pending",  message: "", created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(), reviewed_at: null },
        { id: 3, writer_id: 1123, writer_username: null, interest_type: "pool_bid", status: "withdrawn", message: "Scheduling conflict.", created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(), reviewed_at: null },
      ];
      return;
    }
    const { data } = await ordersApi.interests(props.orderId);
    interests.value = data;
  } catch {
    interests.value = [];
  } finally {
    loadingInterests.value = false;
  }
}

async function assign(interestId: number) {
  assigning.value = interestId;
  assignError.value = "";
  try {
    if (auth.isPreviewSession) { emit("refresh"); return; }
    await ordersApi.assignFromInterest(interestId);
    emit("refresh");
    await loadInterests();
  } catch {
    assignError.value = "Failed to assign writer. Please try again.";
  } finally {
    assigning.value = null;
  }
}

onMounted(loadInterests);
</script>
