<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-4">

      <div v-if="isLoading" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="order">
        <!-- Back + header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Special Orders
          </button>

          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass[order.status] ?? 'bg-slate-100 text-graphite'">
                    {{ statusLabel[order.status] ?? order.status.replace(/_/g, ' ') }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ order.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ order.title }}</h1>
                <p class="mt-1 text-sm leading-5 text-graphite">{{ order.inquiry_details || order.description }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="order.writer_compensation?.type === 'fixed_amount'" class="text-2xl font-bold text-ink">
                  {{ order.writer_compensation.currency }} {{ order.writer_compensation.amount }}
                </p>
                <p v-else-if="order.writer_compensation?.type === 'percentage'" class="text-2xl font-bold text-ink">
                  {{ order.writer_compensation.percentage }}% share
                </p>
              </div>
            </div>

            <!-- Milestone progress -->
            <div v-if="order.total_milestones > 0" class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ order.completed_milestones }} of {{ order.total_milestones }} milestones complete</span>
                <span class="font-semibold text-ink">{{ milestonePct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="milestonePct === 100 ? 'bg-emerald-500' : 'bg-purple-500'"
                  :style="{ width: `${milestonePct}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Milestones -->
        <div class="space-y-3">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-graphite">Milestones</h2>

          <div v-if="milestonesLoading" class="py-10 text-center text-sm text-graphite animate-pulse">Loading milestones…</div>

          <div v-else-if="!milestones.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No milestones set yet.
          </div>

          <div
            v-for="m in milestones"
            :key="m.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ m.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="milestoneStatusClass[m.status] ?? 'bg-slate-100 text-graphite'">
                    {{ m.status.replace(/_/g, ' ') }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ m.label }}</h3>
                <p v-if="m.description" class="mt-0.5 text-sm text-graphite">{{ m.description }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="m.due_date" class="mt-0.5 text-xs text-graphite">Due {{ fmtDate(m.due_date) }}</p>
              </div>
            </div>

            <!-- Revision notes -->
            <div v-if="m.revision_notes" class="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-800">
              <span class="font-semibold">Revision requested:</span> {{ m.revision_notes }}
            </div>

            <!-- Already delivered -->
            <div v-if="m.delivery_notes && (m.deliverable_status === 'uploaded' || m.deliverable_status === 'approved')" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Your delivery notes:</span> {{ m.delivery_notes }}
            </div>
            <div v-if="m.delivery_file_url && (m.deliverable_status === 'uploaded' || m.deliverable_status === 'approved')" class="mt-2">
              <a :href="m.delivery_file_url" target="_blank" rel="noreferrer" class="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:underline">
                <ExternalLink class="size-3" /> View uploaded file
              </a>
            </div>
            <div v-if="m.deliverable_status === 'approved'" class="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-xs text-emerald-700">
              Client approved this milestone.
            </div>

            <!-- Delivery form -->
            <div
              v-if="canDeliverMilestone(m)"
              class="mt-4 border-t border-slate-100 pt-4"
            >
              <template v-if="deliveringId !== m.id">
                <button
                  class="inline-flex items-center gap-1.5 rounded-md bg-purple-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-purple-700"
                  @click="openDelivery(m.id)"
                >
                  <Upload class="size-3.5" />
                  {{ m.deliverable_status === 'rejected' ? 'Submit revision' : 'Deliver milestone' }}
                </button>
              </template>
              <template v-else>
                <p class="mb-2 text-xs font-semibold text-ink">
                  {{ m.deliverable_status === 'rejected' ? 'Submit your revision' : 'Deliver milestone #' + m.sequence }}
                </p>
                <textarea
                  v-model="deliveryNotes"
                  class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  rows="3"
                  placeholder="Describe what you've completed, any issues, or notes for the client…"
                />
                <input
                  v-model="deliveryFileUrl"
                  class="focus-ring mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  type="url"
                  placeholder="Link to delivery file (Google Drive, Dropbox, etc.) — optional"
                />
                <p v-if="deliveryError" class="mt-2 text-xs text-berry">{{ deliveryError }}</p>
                <div class="mt-3 flex gap-2">
                  <button
                    class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-purple-600 px-4 py-2 text-xs font-semibold text-white disabled:opacity-60"
                    :disabled="isDelivering"
                    @click="confirmDelivery(m.id)"
                  >
                    <Loader2 v-if="isDelivering" class="size-3.5 animate-spin" />
                    <CheckCircle v-else class="size-3.5" />
                    Confirm delivery
                  </button>
                  <button
                    class="focus-ring rounded-md border border-slate-200 px-3 py-2 text-xs text-graphite hover:bg-slate-50"
                    @click="cancelDelivery"
                  >
                    Cancel
                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="py-20 text-center text-sm text-graphite">Special order not found.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, CheckCircle, ExternalLink, Loader2, Upload } from "@lucide/vue";
import { specialOrdersApi } from "@/api/specialOrders";
import type { SpecialOrder, SpecialOrderMilestone, MilestoneStatus, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const router = useRouter();
const orderId = route.params.id as string;

const isLoading = ref(false);
const order = ref<SpecialOrder | null>(null);
const milestones = ref<SpecialOrderMilestone[]>([]);
const milestonesLoading = ref(false);

onMounted(async () => {
  isLoading.value = true;
  try {
    const { data } = await specialOrdersApi.get(orderId);
    order.value = data;
    await loadMilestones();
  } catch { /* show empty state */ }
  finally { isLoading.value = false; }
});

async function loadMilestones() {
  milestonesLoading.value = true;
  try {
    const { data } = await specialOrdersApi.milestones.list(orderId);
    milestones.value = Array.isArray(data) ? data : (data as { results: SpecialOrderMilestone[] }).results ?? [];
  } catch { milestones.value = []; }
  finally { milestonesLoading.value = false; }
}

const milestonePct = computed(() => {
  const d = order.value;
  if (!d || !d.total_milestones) return 0;
  return Math.round((d.completed_milestones / d.total_milestones) * 100);
});

// ── Delivery form ────────────────────────────────────────────────────────────
const deliveringId = ref<number | null>(null);
const deliveryNotes = ref("");
const deliveryFileUrl = ref("");
const isDelivering = ref(false);
const deliveryError = ref("");

function openDelivery(milestoneId: number) {
  deliveringId.value = milestoneId;
  deliveryNotes.value = "";
  deliveryFileUrl.value = "";
  deliveryError.value = "";
}

function cancelDelivery() {
  deliveringId.value = null;
}

async function confirmDelivery(milestoneId: number) {
  isDelivering.value = true;
  deliveryError.value = "";
  try {
    const { data: updated } = await specialOrdersApi.milestones.deliver(orderId, milestoneId, {
      delivery_notes: deliveryNotes.value || undefined,
      delivery_file_url: deliveryFileUrl.value || undefined,
    });
    const idx = milestones.value.findIndex((m) => m.id === milestoneId);
    if (idx !== -1) milestones.value[idx] = updated;
    deliveringId.value = null;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    deliveryError.value = detail ?? "Delivery failed. Please try again.";
  } finally {
    isDelivering.value = false;
  }
}

// ── Labels / classes ─────────────────────────────────────────────────────────
function canDeliverMilestone(m: SpecialOrderMilestone): boolean {
  if (m.status === "cancelled" || m.status === "refunded") return false;
  return !m.deliverable_status || m.deliverable_status === "pending" || m.deliverable_status === "rejected";
}

function fmtDate(v: string | null) {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

const statusLabel: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "Inquiry",
  quote_pending: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Accepted",
  awaiting_payment: "Awaiting Payment",
  partially_funded: "Partially Funded",
  ready_for_staffing: "Ready for Staffing",
  assigned: "Assigned",
  on_hold: "On Hold",
  submitted: "Submitted",
  in_progress: "In Progress",
  ready_for_delivery: "Ready for Delivery",
  completed: "Completed",
  cancelled: "Cancelled",
  approved: "Approved",
  revision_requested: "Revision Requested",
  on_revision: "On Revision",
  refunded: "Refunded",
};

const statusClass: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "bg-slate-100 text-slate-600",
  quote_pending: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  awaiting_payment: "bg-amber-100 text-amber-700",
  partially_funded: "bg-amber-100 text-amber-700",
  ready_for_staffing: "bg-blue-100 text-blue-700",
  assigned: "bg-blue-100 text-blue-700",
  on_hold: "bg-slate-100 text-graphite",
  submitted: "bg-purple-100 text-purple-700",
  in_progress: "bg-purple-100 text-purple-700",
  ready_for_delivery: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
  approved: "bg-emerald-100 text-emerald-700",
  revision_requested: "bg-rose-100 text-rose-700",
  on_revision: "bg-amber-100 text-amber-700",
  refunded: "bg-slate-100 text-slate-400",
};

const milestoneStatusClass: Partial<Record<MilestoneStatus, string>> = {
  pending: "bg-slate-100 text-graphite",
  partially_paid: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  cancelled: "bg-slate-100 text-slate-400",
  refunded: "bg-slate-100 text-slate-400",
};
</script>
