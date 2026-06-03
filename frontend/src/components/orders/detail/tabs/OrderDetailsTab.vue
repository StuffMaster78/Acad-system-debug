<template>
  <div class="space-y-4">
    <!-- Order specifications -->
    <div class="rounded-lg border border-slate-200 bg-white p-5">
      <h2 class="text-base font-semibold text-ink">Order specifications</h2>
      <dl class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-if="order.topic">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Topic</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.topic }}</dd>
        </div>
        <div v-if="order.academic_level">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Academic level</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.academic_level }}</dd>
        </div>
        <div v-if="order.paper_type">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Paper type</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.paper_type }}</dd>
        </div>
        <div v-if="order.type_of_work">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Type of work</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.type_of_work }}</dd>
        </div>
        <div v-if="order.subject">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Subject</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.subject }}</dd>
        </div>
        <div v-if="order.formatting_style">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Citation style</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.formatting_style }}</dd>
        </div>
        <div v-if="order.number_of_pages">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Pages</dt>
          <dd class="mt-1 text-sm text-ink">
            {{ order.number_of_pages }}
            <span v-if="order.spacing" class="text-graphite">({{ order.spacing }})</span>
          </dd>
        </div>
        <div v-if="order.number_of_slides">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Slides</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.number_of_slides }}</dd>
        </div>
        <div v-if="order.number_of_refereces">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Sources</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.number_of_refereces }}</dd>
        </div>
        <div v-if="order.english_type">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">English type</dt>
          <dd class="mt-1 text-sm text-ink">{{ order.english_type }}</dd>
        </div>
        <div v-if="role !== 'writer' && order.client_deadline">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Client deadline</dt>
          <dd class="mt-1 text-sm text-ink">{{ dateLabel(order.client_deadline) }}</dd>
        </div>
        <!-- Writer sees their own deadline; staff also see it separately -->
        <div v-if="(role === 'writer' || isStaffRole) && order.writer_deadline">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">{{ role === 'writer' ? 'Your deadline' : 'Writer deadline' }}</dt>
          <dd class="mt-1 text-sm text-ink">{{ dateLabel(order.writer_deadline) }}</dd>
        </div>
        <div v-if="isStaffRole && order.website">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Website ID</dt>
          <dd class="mt-1 font-mono text-sm text-ink">#{{ order.website }}</dd>
        </div>
        <div v-if="isStaffRole && order.discount_code_used">
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Discount code</dt>
          <dd class="mt-1 font-mono text-sm text-ink">{{ order.discount_code_used }}</dd>
        </div>
      </dl>

      <div v-if="order.order_instructions || order.instructions" class="mt-5 border-t border-slate-100 pt-4">
        <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Instructions</dt>
        <dd class="mt-2 whitespace-pre-wrap rounded-md bg-slate-50 p-4 text-sm leading-6 text-ink">
          {{ order.order_instructions ?? order.instructions }}
        </dd>
      </div>
    </div>

    <!-- Lifecycle snapshot (hidden from writer — no client signals exposed) -->
    <div v-if="role !== 'writer'" class="rounded-lg border border-slate-200 bg-white p-5">
      <h2 class="text-base font-semibold text-ink">Lifecycle</h2>
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-md border border-slate-100 p-3">
          <p class="text-xs font-semibold text-graphite">Assignment</p>
          <div class="mt-1 flex items-center justify-between gap-2">
            <p class="text-sm text-ink">
              {{ lifecycle?.has_current_assignment ? maskedWriter(lifecycle.current_writer_id) : "Awaiting assignment" }}
            </p>
            <button
              v-if="writerProfileRoute && lifecycle?.has_current_assignment"
              class="inline-flex items-center gap-1 text-xs font-semibold text-signal hover:underline"
              @click="router.push(writerProfileRoute)"
            >
              <ExternalLink class="h-3 w-3" /> Profile
            </button>
          </div>
        </div>
        <div class="rounded-md border border-slate-100 p-3">
          <p class="text-xs font-semibold text-graphite">Hold</p>
          <p class="mt-1 text-sm text-ink">
            {{ lifecycle?.has_active_hold ? `Hold #${lifecycle.active_hold_id}` : "No active hold" }}
          </p>
        </div>
        <div class="rounded-md border border-slate-100 p-3">
          <p class="text-xs font-semibold text-graphite">Dispute</p>
          <p class="mt-1 text-sm text-ink">
            {{ lifecycle?.has_active_dispute ? `Dispute #${lifecycle.active_dispute_id} active` : "No active dispute" }}
          </p>
        </div>
        <div class="rounded-md border border-slate-100 p-3">
          <p class="text-xs font-semibold text-graphite">Latest revision</p>
          <p class="mt-1 text-sm text-ink">{{ lifecycle?.latest_revision_status ?? "None" }}</p>
        </div>
      </div>
    </div>

    <!-- Client-only action panel -->
    <template v-if="role === 'client'">
      <!-- Dispute -->
      <div
        v-if="hasAction('raise_dispute')"
        class="rounded-lg border border-amber-200 bg-amber-50 p-5"
      >
        <div class="flex items-center gap-2">
          <AlertTriangle class="h-5 w-5 text-amber-700" />
          <h2 class="text-base font-semibold text-amber-950">Raise a dispute</h2>
        </div>
        <p class="mt-1 text-sm text-amber-900">Use only if the issue cannot be resolved through a revision request.</p>
        <form class="mt-3 flex flex-col gap-2 sm:flex-row" @submit.prevent="submitDispute">
          <input
            v-model.trim="disputeReason"
            class="focus-ring flex-1 rounded-md border border-amber-200 bg-white px-3 py-2 text-sm"
            placeholder="Describe the issue clearly"
          />
          <button
            class="focus-ring inline-flex items-center justify-center rounded-md bg-amber-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            type="submit"
            :disabled="isMutating || !disputeReason"
          >Raise dispute</button>
        </form>
      </div>
      <div v-else-if="lifecycle?.has_active_dispute" class="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        Dispute #{{ lifecycle.active_dispute_id }} is active. Our team is reviewing it.
      </div>

      <!-- Support ticket -->
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <LifeBuoy class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Open a support ticket</h2>
        </div>
        <div v-if="ticketError" class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">{{ ticketError }}</div>
        <div v-if="ticketNotice" class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">{{ ticketNotice }}</div>
        <form class="mt-4 grid gap-3" @submit.prevent="submitTicket">
          <input v-model.trim="ticketTitle" class="focus-ring w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Brief summary" />
          <textarea v-model.trim="ticketBody" class="focus-ring min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Describe the issue" />
          <button
            class="focus-ring inline-flex items-center justify-center gap-2 self-start rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="submit"
            :disabled="isTicketing || !ticketTitle || !ticketBody"
          >
            <Loader2 v-if="isTicketing" class="h-4 w-4 animate-spin" />
            Submit ticket
          </button>
        </form>
      </div>

      <!-- Tip writer (post-completion) -->
      <div v-if="canTip" class="rounded-lg border border-amber-200 bg-amber-50 p-5">
        <div class="flex items-center gap-2">
          <Gift class="h-5 w-5 text-amber-700" />
          <h2 class="text-base font-semibold text-amber-950">Tip your writer</h2>
        </div>
        <div v-if="tipSuccess" class="mt-3 text-sm text-emerald-800">Tip sent — thank you!</div>
        <template v-else>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="c in TIP_PRESETS"
              :key="c"
              type="button"
              :class="['focus-ring rounded-md border px-4 py-2 text-sm font-semibold', tipPreset === c ? 'border-amber-600 bg-amber-600 text-white' : 'border-amber-300 bg-white text-amber-900 hover:border-amber-500']"
              @click="selectPreset(c)"
            >{{ (c / 100).toFixed(0) === String(c / 100) ? `$${c / 100}` : `$${(c / 100).toFixed(2)}` }}</button>
            <input v-model="tipCustom" type="number" min="1" step="0.01" placeholder="Custom $" @input="tipPreset = null"
              class="focus-ring h-10 w-28 rounded-md border border-amber-300 bg-white px-3 text-sm placeholder-amber-400" />
          </div>
          <input v-model="tipMessage" class="focus-ring mt-3 w-full rounded-md border border-amber-300 bg-white px-3 py-2 text-sm placeholder-amber-400" placeholder="Message (optional)" maxlength="200" />
          <p v-if="tipError" class="mt-2 text-sm text-rose-700">{{ tipError }}</p>
          <button
            class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md bg-amber-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="isTipping || !tipAmount"
            @click="submitTip"
          >
            <Loader2 v-if="isTipping" class="h-4 w-4 animate-spin" />
            <Gift v-else class="h-4 w-4" />
            {{ tipAmount ? `Send $${(tipAmount / 100).toFixed(2)}` : "Select amount" }}
          </button>
        </template>
      </div>

      <!-- Rate writer (post-completion) -->
      <div v-if="canReview || existingReview" class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <Star class="h-5 w-5 text-saffron" />
          <h2 class="text-base font-semibold text-ink">Rate your writer</h2>
        </div>
        <template v-if="existingReview">
          <p class="mt-2 text-sm text-graphite">Your review: {{ existingReview.rating }}/5 — {{ existingReview.title }}</p>
        </template>
        <template v-else>
          <div class="mt-3 flex items-center gap-1">
            <button v-for="n in 5" :key="n" type="button" class="focus-ring rounded p-0.5" @click="reviewRating = n" @mouseenter="reviewHover = n" @mouseleave="reviewHover = 0">
              <Star class="h-7 w-7 transition-colors" :class="n <= (reviewHover || reviewRating) ? 'fill-saffron text-saffron' : 'text-slate-300'" />
            </button>
          </div>
          <div class="mt-3 grid gap-2">
            <input v-model.trim="reviewTitle" class="focus-ring w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Title (optional)" maxlength="120" />
            <textarea v-model.trim="reviewBody" class="focus-ring min-h-16 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Share your experience (optional)" maxlength="1000" />
          </div>
          <p v-if="reviewError" class="mt-2 text-sm text-berry">{{ reviewError }}</p>
          <button
            class="focus-ring mt-3 inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="reviewSubmitting || !reviewRating"
            @click="submitReview"
          >
            <Loader2 v-if="reviewSubmitting" class="h-4 w-4 animate-spin" />
            <Star v-else class="h-4 w-4" />
            Submit review
          </button>
        </template>
      </div>

      <!-- Cancel order -->
      <form v-if="hasAction('cancel_order')" class="rounded-lg border border-rose-200 bg-rose-50 p-5" @submit.prevent="submitCancel">
        <div class="flex items-center gap-2">
          <XCircle class="h-5 w-5 text-rose-700" />
          <h2 class="text-base font-semibold text-rose-950">Cancel order</h2>
        </div>
        <div class="mt-4 grid gap-3 lg:grid-cols-[1fr_200px_auto]">
          <input v-model.trim="cancelReason" class="focus-ring rounded-md border border-rose-200 px-3 py-2 text-sm" placeholder="Cancellation reason" />
          <select v-model="cancelDest" class="focus-ring rounded-md border border-rose-200 px-3 py-2 text-sm">
            <option value="wallet">Wallet refund</option>
            <option value="external">External refund</option>
          </select>
          <button class="focus-ring inline-flex items-center justify-center rounded-md bg-rose-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" type="submit" :disabled="isMutating || !cancelReason">Cancel</button>
        </div>
      </form>
    </template>

    <!-- Staff/admin operational notes -->
    <div v-if="isStaffRole" class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 class="text-sm font-semibold text-ink">Operational Notes</h2>
          <p class="mt-0.5 text-xs text-graphite">Internal staff notes — not visible to clients or writers.</p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
          :disabled="notesLoading"
          @click="loadNotes"
        >
          <RefreshCw class="size-3.5" :class="notesLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>

      <!-- Notes list -->
      <div v-if="notesLoading" class="space-y-px">
        <div v-for="n in 2" :key="n" class="animate-pulse px-5 py-3">
          <div class="h-3 w-3/4 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-1/3 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!notes.length" class="px-5 py-8 text-center">
        <p class="text-sm text-graphite">No notes yet.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div v-for="note in notes" :key="note.id" class="flex items-start gap-3 px-5 py-3">
          <Pin v-if="note.is_pinned" class="mt-0.5 size-3.5 shrink-0 text-amber-500" />
          <div class="min-w-0 flex-1">
            <p class="text-sm text-ink whitespace-pre-wrap">{{ note.body }}</p>
            <p class="mt-1 text-xs text-graphite">
              {{ note.author_username ? `@${note.author_username}` : "Staff" }}
              · {{ note.created_at ? fmtDate(note.created_at) : "" }}
            </p>
          </div>
          <div class="flex shrink-0 gap-1">
            <button
              class="rounded p-1 text-slate-400 hover:text-amber-500 transition-colors"
              :title="note.is_pinned ? 'Unpin' : 'Pin'"
              @click="togglePin(note)"
            >
              <Pin class="size-3.5" :class="note.is_pinned ? 'text-amber-500' : ''" />
            </button>
            <button
              class="rounded p-1 text-slate-400 hover:text-rose-500 transition-colors"
              title="Delete"
              @click="removeNote(note.id)"
            >
              <X class="size-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Add note form -->
      <form class="border-t border-slate-100 px-5 py-4 space-y-2" @submit.prevent="addNote">
        <textarea
          v-model.trim="noteBody"
          class="focus-ring min-h-16 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          placeholder="Add an internal note…"
        />
        <div v-if="noteError" class="text-xs text-berry">{{ noteError }}</div>
        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-slate-700 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          type="submit"
          :disabled="noteSaving || !noteBody"
        >
          <Loader2 v-if="noteSaving" class="size-3.5 animate-spin" />
          <Plus v-else class="size-3.5" />
          Add note
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { AlertTriangle, ExternalLink, Gift, LifeBuoy, Loader2, Pin, Plus, RefreshCw, Star, X, XCircle } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderNote, OrderSummary, OrderLifecycle } from "@/types/orders";
import type { Review } from "@/types/reviews";
import { reviewsApi } from "@/api/reviews";
import { supportApi } from "@/api/support";
import { tipsApi, type TipRecord } from "@/api/tips";
import { ordersApi } from "@/api/orders";
import { useOrderStore } from "@/stores/orders";
import { dateLabel, maskedWriter, isStaff } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const router = useRouter();
const orders = useOrderStore();
const isMutating = computed(() => orders.isMutating);
const isStaffRole = computed(() => isStaff(props.role));

// Writer profile link — available to all staff roles that can see the order detail
const writerProfileRoute = computed(() => {
  const rid = props.lifecycle?.current_writer_registration_id;
  if (!rid) return null;
  const prefix: Record<string, string> = {
    admin: '/admin', superadmin: '/superadmin',
    support: '/support', editor: '/editor',
  };
  const base = prefix[props.role];
  return base ? `${base}/writers/${rid}` : null;
});

const TERMINAL = ["completed", "reviewed", "rated", "approved", "archived", "cancelled"];

function hasAction(action: string): boolean {
  return props.lifecycle?.available_actions?.includes(action) ?? false;
}

// ── Dispute ─────────────────────────────────────────────────────────────────
const disputeReason = ref("");
async function submitDispute() {
  if (!disputeReason.value) return;
  await orders.raiseDispute(props.orderId, disputeReason.value);
  disputeReason.value = "";
}

// ── Support ticket ───────────────────────────────────────────────────────────
const ticketTitle = ref("");
const ticketBody = ref("");
const isTicketing = ref(false);
const ticketError = ref("");
const ticketNotice = ref("");
async function submitTicket() {
  if (!ticketTitle.value || !ticketBody.value) return;
  isTicketing.value = true;
  ticketError.value = "";
  ticketNotice.value = "";
  try {
    await supportApi.createTicket({ title: ticketTitle.value, description: ticketBody.value, category: "order", object_id: props.orderId });
    ticketNotice.value = "Ticket created. Our team will follow up.";
    ticketTitle.value = "";
    ticketBody.value = "";
  } catch {
    ticketError.value = "Unable to create ticket.";
  } finally {
    isTicketing.value = false;
  }
}

// ── Tip ──────────────────────────────────────────────────────────────────────
const TIP_PRESETS = [500, 1000, 2000, 5000];
const tipPreset = ref<number | null>(null);
const tipCustom = ref("");
const tipMessage = ref("");
const isTipping = ref(false);
const tipError = ref("");
const tipSuccess = ref<TipRecord | null>(null);

const canTip = computed(() =>
  TERMINAL.includes(props.order.status ?? "") &&
  props.lifecycle?.current_writer_id != null
);

const tipAmount = computed(() => {
  if (tipPreset.value !== null) return tipPreset.value;
  const n = Math.round(Number(tipCustom.value) * 100);
  return Number.isFinite(n) && n > 0 ? n : null;
});

function selectPreset(c: number) { tipPreset.value = tipPreset.value === c ? null : c; tipCustom.value = ""; }

async function submitTip() {
  const writerId = props.lifecycle?.current_writer_id;
  const amount = tipAmount.value;
  if (!writerId || !amount) return;
  isTipping.value = true;
  tipError.value = "";
  try {
    const { data } = await tipsApi.create({ receiver_id: writerId, gross_amount_cents: amount, currency: "USD", context_type: "order", message: tipMessage.value.trim() || undefined, idempotency_key: crypto.randomUUID() });
    tipSuccess.value = data;
    tipPreset.value = null;
    tipCustom.value = "";
    tipMessage.value = "";
  } catch {
    tipError.value = "Unable to send tip.";
  } finally {
    isTipping.value = false;
  }
}

// ── Review ───────────────────────────────────────────────────────────────────
const existingReview = ref<Review | null>(null);
const reviewRating = ref(0);
const reviewHover = ref(0);
const reviewTitle = ref("");
const reviewBody = ref("");
const reviewSubmitting = ref(false);
const reviewError = ref("");

const canReview = computed(() =>
  TERMINAL.includes(props.order.status ?? "") &&
  props.lifecycle?.current_writer_id != null &&
  existingReview.value === null
);

async function submitReview() {
  reviewError.value = "";
  if (!reviewRating.value) { reviewError.value = "Select a star rating."; return; }
  reviewSubmitting.value = true;
  try {
    const { data } = await reviewsApi.submit(props.orderId, { rating: reviewRating.value, title: reviewTitle.value.trim() || undefined, body: reviewBody.value.trim() || undefined, is_public: true });
    existingReview.value = data;
  } catch {
    reviewError.value = "Review submission failed.";
  } finally {
    reviewSubmitting.value = false;
  }
}

// ── Cancel ───────────────────────────────────────────────────────────────────
const cancelReason = ref("");
const cancelDest = ref<"wallet" | "external">("wallet");
async function submitCancel() {
  if (!cancelReason.value) return;
  await orders.cancelOrder(props.orderId, { reason: cancelReason.value, refund_destination: cancelDest.value });
  cancelReason.value = "";
}

// ── Operational notes ────────────────────────────────────────────────────────
const notes = ref<OrderNote[]>([]);
const notesLoading = ref(false);
const noteBody = ref("");
const noteSaving = ref(false);
const noteError = ref("");

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

async function loadNotes() {
  notesLoading.value = true;
  try {
    const { data } = await ordersApi.notes(props.orderId);
    notes.value = data;
  } catch {
    notes.value = [];
  } finally {
    notesLoading.value = false;
  }
}

async function addNote() {
  if (!noteBody.value) return;
  noteSaving.value = true;
  noteError.value = "";
  try {
    const { data } = await ordersApi.createNote(props.orderId, noteBody.value);
    notes.value = [data, ...notes.value];
    noteBody.value = "";
  } catch {
    noteError.value = "Failed to save note.";
  } finally {
    noteSaving.value = false;
  }
}

async function togglePin(note: OrderNote) {
  try {
    const { data } = await ordersApi.patchNote(props.orderId, note.id, { is_pinned: !note.is_pinned });
    const idx = notes.value.findIndex((n) => n.id === note.id);
    if (idx !== -1) notes.value[idx] = data;
    notes.value = [...notes.value].sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0));
  } catch { /* keep current state */ }
}

async function removeNote(noteId: number) {
  try {
    await ordersApi.deleteNote(props.orderId, noteId);
    notes.value = notes.value.filter((n) => n.id !== noteId);
  } catch { /* keep current state */ }
}

// Load existing review on mount
import { onMounted } from "vue";
onMounted(async () => {
  if (props.role === "client") {
    try { const { data } = await reviewsApi.forOrder(props.orderId); existingReview.value = data; }
    catch { existingReview.value = null; }
  }
  if (isStaff(props.role)) {
    loadNotes();
  }
});
</script>
