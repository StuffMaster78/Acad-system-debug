<template>
  <div class="space-y-5 py-2">

    <!-- Rate card snapshot -->
    <div class="rounded-lg border border-slate-200 bg-white p-5">
      <h2 class="mb-4 text-base font-semibold text-ink">Rate card at assignment</h2>

      <div v-if="rateCardLoading" class="text-sm text-graphite">Loading…</div>
      <div v-else-if="rateCardError" class="text-sm text-berry">{{ rateCardError }}</div>
      <template v-else-if="rateCard">
        <dl class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Level</dt>
            <dd class="mt-1 text-sm font-medium text-ink">{{ rateCard.level_name }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Earning mode</dt>
            <dd class="mt-1 text-sm text-ink capitalize">{{ rateCard.earning_mode.replace(/_/g, " ") }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Currency</dt>
            <dd class="mt-1 text-sm text-ink">{{ rateCard.currency }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Per page</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(rateCard.rates.base_pay_per_page) }}</dd>
          </div>
          <div v-if="parseFloat(rateCard.rates.base_pay_per_slide) > 0">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Per slide</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(rateCard.rates.base_pay_per_slide) }}</dd>
          </div>
          <div v-if="parseFloat(rateCard.rates.base_pay_per_chart) > 0">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Per chart</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(rateCard.rates.base_pay_per_chart) }}</dd>
          </div>
        </dl>

        <div v-if="parseFloat(rateCard.urgency.urgent_order_surcharge) > 0" class="mt-4 border-t border-slate-100 pt-4">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Urgency uplift</p>
          <dl class="grid gap-3 sm:grid-cols-2">
            <div>
              <dt class="text-xs text-graphite">Threshold</dt>
              <dd class="mt-0.5 text-sm text-ink">≤ {{ rateCard.urgency.urgent_time_threshold_hours }}h deadline</dd>
            </div>
            <div>
              <dt class="text-xs text-graphite">Surcharge</dt>
              <dd class="mt-0.5 text-sm font-medium text-ink">
                {{ money(rateCard.urgency.urgent_order_surcharge) }} / page
                <span v-if="parseFloat(rateCard.urgency.urgent_multiplier) > 1">
                  + {{ rateCard.urgency.urgent_multiplier }}× multiplier
                </span>
              </dd>
            </div>
          </dl>
        </div>

        <p class="mt-3 text-xs text-graphite">
          Snapshotted {{ dateLabel(rateCard.snapshotted_at) }}
        </p>
      </template>
      <p v-else class="text-sm text-graphite">No rate card on file — order may not have been assigned yet.</p>
    </div>

    <!-- Compensation events for this order -->
    <div class="rounded-lg border border-slate-200 bg-white p-5">
      <h2 class="mb-4 text-base font-semibold text-ink">Compensation events</h2>

      <div v-if="eventsLoading" class="text-sm text-graphite">Loading…</div>
      <div v-else-if="eventsError" class="text-sm text-berry">{{ eventsError }}</div>
      <template v-else-if="events.length">
        <ul class="divide-y divide-slate-100">
          <li
            v-for="event in events"
            :key="event.id"
            class="flex items-start justify-between gap-4 py-3"
          >
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-ink">
                {{ event.title || eventLabel(event.event_type) }}
              </p>
              <p v-if="event.description || event.notes" class="mt-0.5 text-xs text-graphite">
                {{ event.description || event.notes }}
              </p>
              <div class="mt-1 flex flex-wrap gap-2">
                <span class="inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">
                  {{ event.window_label || "—" }}
                </span>
                <span
                  class="inline-block rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="statusClass(event.status)"
                >
                  {{ event.status?.replace(/_/g, " ") ?? "—" }}
                </span>
              </div>
            </div>
            <p
              class="shrink-0 text-sm font-semibold"
              :class="event.is_positive ? 'text-signal' : 'text-berry'"
            >
              {{ event.is_positive ? "+" : "" }}{{ money(String(event.amount ?? 0)) }}
            </p>
          </li>
        </ul>

        <!-- Totals -->
        <div class="mt-4 border-t border-slate-200 pt-4">
          <dl class="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div>
              <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Gross</dt>
              <dd class="mt-1 text-sm font-semibold text-signal">+{{ money(String(totals.gross)) }}</dd>
            </div>
            <div v-if="totals.deductions > 0">
              <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Deductions</dt>
              <dd class="mt-1 text-sm font-semibold text-berry">−{{ money(String(totals.deductions)) }}</dd>
            </div>
            <div>
              <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Net</dt>
              <dd class="mt-1 text-sm font-semibold text-ink">{{ money(String(totals.net)) }}</dd>
            </div>
          </dl>
        </div>
      </template>
      <p v-else class="text-sm text-graphite">No compensation events recorded for this order yet.</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { writerApi } from "@/api/writer";
import type { WriterEvent } from "@/types/writer";
import { dateLabel } from "../types";

const props = defineProps<{ orderId: string | number }>();

// ── Rate card ──────────────────────────────────────────────────────────────
type RateCard = Awaited<ReturnType<typeof writerApi.orderRateCard>>["data"];

const rateCard = ref<RateCard | null>(null);
const rateCardLoading = ref(true);
const rateCardError = ref<string | null>(null);

async function loadRateCard() {
  rateCardLoading.value = true;
  rateCardError.value = null;
  try {
    const res = await writerApi.orderRateCard(props.orderId);
    rateCard.value = res.data;
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } }).response?.status;
    if (status === 404) {
      rateCard.value = null; // not yet assigned — not an error
    } else {
      rateCardError.value = "Could not load rate card.";
    }
  } finally {
    rateCardLoading.value = false;
  }
}

// ── Compensation events ────────────────────────────────────────────────────
const events = ref<WriterEvent[]>([]);
const eventsLoading = ref(true);
const eventsError = ref<string | null>(null);

async function loadEvents() {
  eventsLoading.value = true;
  eventsError.value = null;
  try {
    const res = await writerApi.eventsForOrder(props.orderId);
    const raw = res.data;
    events.value = Array.isArray(raw) ? raw : (raw as { results: WriterEvent[] }).results ?? [];
  } catch {
    eventsError.value = "Could not load compensation events.";
  } finally {
    eventsLoading.value = false;
  }
}

const totals = computed(() => {
  let gross = 0;
  let deductions = 0;
  for (const e of events.value) {
    const amt = parseFloat(String(e.amount ?? 0));
    if (amt > 0) gross += amt;
    else deductions += Math.abs(amt);
  }
  return { gross, deductions, net: gross - deductions };
});

onMounted(() => {
  loadRateCard();
  loadEvents();
});

// ── Helpers ────────────────────────────────────────────────────────────────
function money(value: string | number): string {
  const n = parseFloat(String(value));
  if (isNaN(n)) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

function eventLabel(type?: string): string {
  if (!type) return "Event";
  return type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function statusClass(s?: string): string {
  switch (s) {
    case "paid": return "bg-emerald-100 text-emerald-800";
    case "matured": return "bg-blue-100 text-blue-800";
    case "pending_confirmation": return "bg-amber-100 text-amber-800";
    case "voided":
    case "reversed": return "bg-slate-100 text-graphite";
    default: return "bg-slate-100 text-graphite";
  }
}
</script>
