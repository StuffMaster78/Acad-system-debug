<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  AlertCircle,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Clock,
  CreditCard,
  FileText,
  MessageSquare,
  Plus,
  RefreshCw,
  Sparkles,
  Star,
  Wallet,
  Zap,
} from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { useOrderStore } from "@/stores/orders";
import { useWalletStore } from "@/stores/wallets";
import { useCommunicationsStore } from "@/stores/communications";
import { useAuthStore } from "@/stores/auth";

const orders = useOrderStore();
const wallet = useWalletStore();
const comms = useCommunicationsStore();
const auth = useAuthStore();

const loyaltyPoints = ref(0);
const loyaltyTier = ref<string | null>(null);
const discountCount = ref(0);
const isLoading = ref(true);

// ── Derived data ──────────────────────────────────────────────────────────────

const firstName = computed(() => {
  const n = auth.user?.full_name;
  return n ? n.split(" ")[0] : "";
});

const greeting = computed(() => {
  const h = new Date().getHours();
  const base = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  return firstName.value ? `${base}, ${firstName.value}` : base;
});

const activeOrders = computed(() =>
  orders.openOrders.filter((o) =>
    ["in_progress", "under_editing", "assigned"].includes(o.status ?? ""),
  ),
);

const attentionItems = computed(() => {
  const items: Array<{
    type: "payment" | "approval" | "revision" | "urgent";
    label: string;
    sub: string;
    to: string;
    tone: "amber" | "rose" | "blue" | "emerald";
  }> = [];

  for (const o of orders.openOrders) {
    if (o.payment_status !== "paid" && o.payment_status != null) {
      items.push({
        type: "payment",
        label: `#${o.id} — Payment needed`,
        sub: o.topic || "Untitled order",
        to: `/client/orders/${o.id}`,
        tone: "rose",
      });
    } else if (["awaiting_approval", "submitted"].includes(o.status ?? "")) {
      items.push({
        type: "approval",
        label: `#${o.id} — Ready for your review`,
        sub: o.topic || "Untitled order",
        to: `/client/orders/${o.id}`,
        tone: "emerald",
      });
    } else if (o.status === "revision_requested") {
      items.push({
        type: "revision",
        label: `#${o.id} — Revision in progress`,
        sub: o.topic || "Untitled order",
        to: `/client/orders/${o.id}`,
        tone: "blue",
      });
    } else if (o.client_deadline) {
      const h = (new Date(o.client_deadline).getTime() - Date.now()) / 3_600_000;
      if (h > 0 && h < 12) {
        items.push({
          type: "urgent",
          label: `#${o.id} — Due in ${Math.round(h)}h`,
          sub: o.topic || "Untitled order",
          to: `/client/orders/${o.id}`,
          tone: "amber",
        });
      }
    }
  }

  return items.slice(0, 4);
});

const unreadMessages = computed(() =>
  comms.inboxThreads.filter((t) => (t.metadata as Record<string, unknown>)?.unread_count).length,
);

// ── Progress helpers ──────────────────────────────────────────────────────────

const STAGE_MAP: Record<string, number> = {
  placed: 0, payment_pending: 0, draft: 0,
  assigned: 1, in_progress: 1, under_editing: 1, revision_requested: 1,
  submitted: 2, awaiting_approval: 2,
  completed: 3, approved: 3,
};

function orderPct(status: string): number {
  return Math.round(((STAGE_MAP[status] ?? 0) / 3) * 100);
}

function deadlineLabel(v?: string | null): string {
  if (!v) return "";
  const h = (new Date(v).getTime() - Date.now()) / 3_600_000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

function deadlineTone(v?: string | null): "danger" | "warn" | "ok" {
  if (!v) return "ok";
  const h = (new Date(v).getTime() - Date.now()) / 3_600_000;
  if (h < 0 || h < 6) return "danger";
  if (h < 24) return "warn";
  return "ok";
}

function money(n: string | number | undefined): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: wallet.currency,
    maximumFractionDigits: 2,
  }).format(Number(n ?? 0));
}

function tierColor(tier: string | null): string {
  const t = (tier ?? "").toLowerCase();
  if (t.includes("gold") || t.includes("premium")) return "text-amber-500";
  if (t.includes("silver")) return "text-slate-400";
  if (t.includes("platinum") || t.includes("diamond")) return "text-cyan-500";
  return "text-berry";
}

// ── Attention tone classes ────────────────────────────────────────────────────

const toneClasses = {
  rose:    { card: "border-rose-200 bg-rose-50",    dot: "bg-rose-500",    text: "text-rose-800"    },
  amber:   { card: "border-amber-200 bg-amber-50",  dot: "bg-amber-500",   text: "text-amber-800"   },
  blue:    { card: "border-blue-200 bg-blue-50",    dot: "bg-blue-500",    text: "text-blue-800"    },
  emerald: { card: "border-emerald-200 bg-emerald-50", dot: "bg-emerald-500", text: "text-emerald-800" },
};

// ── Load ──────────────────────────────────────────────────────────────────────

async function load() {
  isLoading.value = true;
  await Promise.allSettled([
    orders.fetchOrders(1).catch(() => undefined),
    wallet.fetchWallet().catch(() => undefined),
    comms.loadInboxThreads().catch(() => undefined),
    api.get<{ loyalty_points?: number; tier?: string; total?: number }>(
      apiPath("/loyalty-management/loyalty/summary/"),
    ).then(({ data }) => {
      loyaltyPoints.value = data.loyalty_points ?? data.total ?? 0;
      loyaltyTier.value = data.tier ?? null;
    }).catch(() => undefined),
    api.get<{ count: number; results: unknown[] }>(
      apiPath("/discounts/client/available/"),
      { method: "post" } as never,
    ).catch(() =>
      api.post<{ count?: number; results?: unknown[] }>(
        apiPath("/discounts/client/available/"),
        {},
      ).then(({ data }) => { discountCount.value = data.results?.length ?? data.count ?? 0; })
      .catch(() => undefined),
    ),
  ]);
  isLoading.value = false;
}

onMounted(() => load());
</script>

<template>
  <div class="space-y-6">

    <!-- ── Hero bar ──────────────────────────────────────────────────────── -->
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-ink">{{ greeting }}</h1>
        <p class="mt-1 text-sm text-graphite">
          <template v-if="isLoading">Loading your workspace…</template>
          <template v-else-if="attentionItems.length">
            <span class="font-semibold text-rose-600">{{ attentionItems.length }} item{{ attentionItems.length > 1 ? 's' : '' }} need{{ attentionItems.length === 1 ? 's' : '' }} your attention</span>
            <span class="text-slate-400"> · </span>
            <span>{{ orders.openOrders.length }} active order{{ orders.openOrders.length !== 1 ? 's' : '' }}</span>
          </template>
          <template v-else-if="orders.openOrders.length">
            {{ orders.openOrders.length }} active order{{ orders.openOrders.length !== 1 ? 's' : '' }} · everything looks good
          </template>
          <template v-else>
            No active orders — ready to start something new?
          </template>
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite hover:bg-slate-50"
          :class="{ 'opacity-50 pointer-events-none': isLoading }"
          title="Refresh"
          @click="load"
        >
          <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
        </button>
        <RouterLink
          to="/client/new-order"
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg bg-berry px-4 text-sm font-semibold text-white shadow-sm hover:bg-berry/90"
        >
          <Plus class="h-4 w-4" /> New order
        </RouterLink>
      </div>
    </div>

    <!-- ── Needs attention ────────────────────────────────────────────────── -->
    <section v-if="attentionItems.length" class="space-y-2">
      <h2 class="text-xs font-bold uppercase tracking-wider text-graphite">Needs your attention</h2>
      <div class="grid gap-2 sm:grid-cols-2">
        <RouterLink
          v-for="item in attentionItems"
          :key="item.to + item.type"
          :to="item.to"
          class="group flex items-center gap-3 rounded-xl border px-4 py-3 transition-shadow hover:shadow-sm"
          :class="toneClasses[item.tone].card"
        >
          <span class="mt-0.5 h-2 w-2 shrink-0 rounded-full" :class="toneClasses[item.tone].dot" />
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold" :class="toneClasses[item.tone].text">{{ item.label }}</p>
            <p class="truncate text-xs opacity-70" :class="toneClasses[item.tone].text">{{ item.sub }}</p>
          </div>
          <ChevronRight class="h-4 w-4 shrink-0 opacity-40 transition-opacity group-hover:opacity-70" :class="toneClasses[item.tone].text" />
        </RouterLink>
      </div>
    </section>

    <!-- ── Active orders ──────────────────────────────────────────────────── -->
    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-xs font-bold uppercase tracking-wider text-graphite">Active orders</h2>
        <RouterLink to="/client/orders" class="flex items-center gap-1 text-xs font-semibold text-berry hover:underline">
          View all <ArrowRight class="h-3.5 w-3.5" />
        </RouterLink>
      </div>

      <!-- Loading skeletons -->
      <div v-if="isLoading" class="space-y-2">
        <div v-for="n in 2" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-4">
            <div class="flex-1 space-y-2">
              <div class="h-3.5 w-3/5 rounded bg-slate-200" />
              <div class="h-2.5 w-2/5 rounded bg-slate-100" />
            </div>
            <div class="h-8 w-16 rounded-lg bg-slate-100" />
          </div>
          <div class="mt-3 h-1.5 w-full rounded-full bg-slate-100" />
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!activeOrders.length && !orders.openOrders.length"
        class="flex flex-col items-center rounded-xl border border-dashed border-slate-200 bg-white py-10 text-center">
        <FileText class="h-8 w-8 text-slate-300" />
        <p class="mt-2 text-sm font-semibold text-ink">No active orders</p>
        <p class="mt-0.5 text-xs text-graphite">Your orders and their progress will appear here.</p>
        <RouterLink
          to="/client/new-order"
          class="focus-ring mt-4 inline-flex h-9 items-center gap-2 rounded-lg bg-berry px-4 text-sm font-semibold text-white hover:bg-berry/90"
        >
          <Plus class="h-4 w-4" /> Place first order
        </RouterLink>
      </div>

      <!-- Order cards -->
      <div v-else class="space-y-2">
        <RouterLink
          v-for="order in orders.openOrders.slice(0, 4)"
          :key="order.id"
          :to="`/client/orders/${order.id}`"
          class="group block rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-slate-300 hover:shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-mono text-xs text-slate-400">#{{ order.id }}</span>
                <p class="truncate text-sm font-semibold text-ink group-hover:text-berry transition-colors">
                  {{ order.topic || "Untitled order" }}
                </p>
                <span
                  v-if="order.is_urgent"
                  class="inline-flex items-center gap-0.5 rounded-full bg-rose-100 px-1.5 py-0.5 text-xs font-bold text-rose-700"
                >
                  <Zap class="h-2.5 w-2.5" /> Urgent
                </span>
              </div>
              <p class="mt-0.5 text-xs text-graphite capitalize">{{ (order.status ?? "").replace(/_/g, " ") }}</p>
            </div>
            <!-- Deadline chip -->
            <div v-if="order.client_deadline" class="shrink-0 text-right">
              <span
                class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="{
                  'bg-rose-100 text-rose-700':   deadlineTone(order.client_deadline) === 'danger',
                  'bg-amber-100 text-amber-700': deadlineTone(order.client_deadline) === 'warn',
                  'bg-slate-100 text-graphite':  deadlineTone(order.client_deadline) === 'ok',
                }"
              >
                <Clock class="h-3 w-3" />
                {{ deadlineLabel(order.client_deadline) }}
              </span>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="mt-3">
            <div class="mb-1 flex items-center justify-between text-xs text-graphite">
              <span>{{ ["Placed", "In progress", "Delivered", "Complete"][STAGE_MAP[order.status ?? ""] ?? 0] }}</span>
              <span>{{ orderPct(order.status ?? "") }}%</span>
            </div>
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                class="h-full rounded-full transition-all duration-700"
                :class="{
                  'bg-berry':         !['completed','approved'].includes(order.status ?? '') && (order.status ?? '') !== '',
                  'bg-emerald-500':   ['completed','approved'].includes(order.status ?? ''),
                }"
                :style="{ width: `${Math.max(4, orderPct(order.status ?? ''))}%` }"
              />
            </div>
          </div>
        </RouterLink>

        <!-- "View more" link if truncated -->
        <RouterLink
          v-if="orders.openOrders.length > 4"
          to="/client/orders"
          class="flex items-center justify-center gap-1.5 rounded-xl border border-dashed border-slate-200 py-3 text-sm font-semibold text-graphite hover:border-slate-300 hover:text-ink"
        >
          +{{ orders.openOrders.length - 4 }} more orders <ArrowRight class="h-4 w-4" />
        </RouterLink>
      </div>
    </section>

    <!-- ── Quick actions ──────────────────────────────────────────────────── -->
    <section class="space-y-3">
      <h2 class="text-xs font-bold uppercase tracking-wider text-graphite">Start something new</h2>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <RouterLink
          to="/client/new-order"
          class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-4 transition-all hover:border-berry/40 hover:shadow-sm"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-berry/10 text-berry group-hover:bg-berry group-hover:text-white transition-colors">
            <FileText class="h-5 w-5" />
          </div>
          <div>
            <p class="text-sm font-semibold text-ink">New essay or paper</p>
            <p class="text-xs text-graphite">Academic writing, research</p>
          </div>
          <ChevronRight class="ml-auto h-4 w-4 text-slate-300 group-hover:text-berry transition-colors" />
        </RouterLink>

        <RouterLink
          to="/client/classes/new"
          class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-4 transition-all hover:border-violet-400/40 hover:shadow-sm"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-violet-50 text-violet-600 group-hover:bg-violet-600 group-hover:text-white transition-colors">
            <BookOpen class="h-5 w-5" />
          </div>
          <div>
            <p class="text-sm font-semibold text-ink">Full class help</p>
            <p class="text-xs text-graphite">Semester-long assistance</p>
          </div>
          <ChevronRight class="ml-auto h-4 w-4 text-slate-300 group-hover:text-violet-400 transition-colors" />
        </RouterLink>

        <RouterLink
          to="/client/special-orders/express"
          class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-4 transition-all hover:border-amber-400/40 hover:shadow-sm"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-amber-600 group-hover:bg-amber-500 group-hover:text-white transition-colors">
            <Sparkles class="h-5 w-5" />
          </div>
          <div>
            <p class="text-sm font-semibold text-ink">Express / special order</p>
            <p class="text-xs text-graphite">Rush, complex, or custom</p>
          </div>
          <ChevronRight class="ml-auto h-4 w-4 text-slate-300 group-hover:text-amber-400 transition-colors" />
        </RouterLink>
      </div>
    </section>

    <!-- ── Bottom strip: Money + Perks + Messages ────────────────────────── -->
    <div class="grid gap-4 sm:grid-cols-3">

      <!-- Wallet -->
      <RouterLink
        to="/client/money"
        class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-slate-300 hover:shadow-sm"
      >
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
          <Wallet class="h-5 w-5" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-xs text-graphite">Wallet balance</p>
          <p class="text-lg font-bold text-ink tabular-nums">{{ money(wallet.availableBalance) }}</p>
          <p v-if="wallet.pendingBalance > 0" class="text-xs text-graphite">
            + {{ money(wallet.pendingBalance) }} pending
          </p>
        </div>
        <CreditCard class="h-4 w-4 shrink-0 text-slate-300 group-hover:text-slate-500 transition-colors" />
      </RouterLink>

      <!-- Loyalty -->
      <RouterLink
        to="/client/loyalty"
        class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-slate-300 hover:shadow-sm"
      >
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-50">
          <Star class="h-5 w-5" :class="loyaltyTier ? tierColor(loyaltyTier) : 'text-amber-400'" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-xs text-graphite">Loyalty points</p>
          <p class="text-lg font-bold text-ink tabular-nums">{{ loyaltyPoints.toLocaleString() }}</p>
          <p v-if="loyaltyTier" class="text-xs font-semibold capitalize" :class="tierColor(loyaltyTier)">
            {{ loyaltyTier }} tier
          </p>
          <p v-else class="text-xs text-graphite">Earn on every order</p>
        </div>
        <ChevronRight class="h-4 w-4 shrink-0 text-slate-300 group-hover:text-slate-500 transition-colors" />
      </RouterLink>

      <!-- Messages -->
      <RouterLink
        to="/client/messages"
        class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-slate-300 hover:shadow-sm"
      >
        <div class="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
          <MessageSquare class="h-5 w-5" />
          <span
            v-if="unreadMessages > 0"
            class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white"
          >{{ unreadMessages }}</span>
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-xs text-graphite">Messages</p>
          <p class="text-lg font-bold text-ink tabular-nums">{{ comms.inboxThreads.length }}</p>
          <p class="text-xs text-graphite">
            {{ unreadMessages > 0 ? `${unreadMessages} unread` : "All caught up" }}
          </p>
        </div>
        <ChevronRight class="h-4 w-4 shrink-0 text-slate-300 group-hover:text-slate-500 transition-colors" />
      </RouterLink>
    </div>

    <!-- ── Discounts available ────────────────────────────────────────────── -->
    <div v-if="discountCount > 0"
      class="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
      <CheckCircle2 class="h-4 w-4 shrink-0 text-emerald-600" />
      <p class="flex-1 text-sm text-emerald-800">
        You have <strong>{{ discountCount }} discount code{{ discountCount > 1 ? 's' : '' }}</strong> available — use them on your next order.
      </p>
      <RouterLink
        to="/client/discounts"
        class="shrink-0 text-sm font-semibold text-emerald-700 hover:underline"
      >View codes</RouterLink>
    </div>

    <!-- ── Unread messages nudge ──────────────────────────────────────────── -->
    <div v-else-if="unreadMessages > 0"
      class="flex items-center gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3">
      <AlertCircle class="h-4 w-4 shrink-0 text-blue-600" />
      <p class="flex-1 text-sm text-blue-800">
        You have <strong>{{ unreadMessages }} unread message{{ unreadMessages > 1 ? 's' : '' }}</strong> from your writers.
      </p>
      <RouterLink to="/client/messages" class="shrink-0 text-sm font-semibold text-blue-700 hover:underline">
        Read now
      </RouterLink>
    </div>

  </div>
</template>
