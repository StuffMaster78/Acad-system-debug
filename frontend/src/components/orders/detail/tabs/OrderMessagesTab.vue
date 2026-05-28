<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import {
  Inbox, Lock, Loader2, MessageSquarePlus, Plus, RefreshCw, Send, X,
} from "@lucide/vue";
import type { CommunicationMessage, CommunicationThread, CommunicationThreadKind } from "@/api/communications";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import { useCommunicationsStore } from "@/stores/communications";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";
import { isStaff } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

const auth = useAuthStore();
const comms = useCommunicationsStore();

const isStaffRole = computed(() => isStaff(props.role));
const scrollEl = ref<HTMLElement | null>(null);

// ── Role style map ─────────────────────────────────────────────────────────────
const ROLE_STYLE: Record<string, { border: string; badge: string; activeBadge: string; label: string }> = {
  client:     { border: "border-l-blue-400",    badge: "bg-blue-100 text-blue-800",       activeBadge: "bg-blue-500 text-white",    label: "Client" },
  writer:     { border: "border-l-emerald-400", badge: "bg-emerald-100 text-emerald-800", activeBadge: "bg-emerald-600 text-white", label: "Writer" },
  support:    { border: "border-l-amber-400",   badge: "bg-amber-100 text-amber-800",     activeBadge: "bg-amber-500 text-white",   label: "Support" },
  admin:      { border: "border-l-violet-400",  badge: "bg-violet-100 text-violet-800",   activeBadge: "bg-violet-600 text-white",  label: "Admin" },
  editor:     { border: "border-l-cyan-400",    badge: "bg-cyan-100 text-cyan-800",       activeBadge: "bg-cyan-600 text-white",    label: "Editor" },
  superadmin: { border: "border-l-rose-400",    badge: "bg-rose-100 text-rose-800",       activeBadge: "bg-rose-600 text-white",    label: "Superadmin" },
  internal:   { border: "border-l-slate-400",   badge: "bg-slate-100 text-slate-600",     activeBadge: "bg-slate-600 text-white",   label: "Staff note" },
  system:     { border: "border-l-slate-300",   badge: "bg-slate-100 text-slate-500",     activeBadge: "bg-slate-400 text-white",   label: "System" },
};

function roleStyle(role: string) {
  return ROLE_STYLE[role] ?? { border: "border-l-slate-300", badge: "bg-slate-100 text-slate-600", activeBadge: "bg-slate-500 text-white", label: role };
}

// ── Thread metadata helpers ────────────────────────────────────────────────────
const KIND_LABEL: Record<string, string> = {
  client_writer:  "Client ↔ Writer",
  client_support: "Client ↔ Support",
  revision:       "Revision",
  dispute:        "Dispute",
  internal:       "Internal",
};

function kindLabel(kind: string) {
  return KIND_LABEL[kind] ?? kind.replace(/_/g, " ");
}

const KIND_PARTICIPANTS: Record<string, string[]> = {
  client_writer:  ["client", "writer"],
  client_support: ["client", "support"],
  revision:       ["client", "writer", "editor"],
  dispute:        ["client", "support", "admin"],
  internal:       ["admin", "support"],
};

function participantsFromKind(kind: string): string[] {
  return KIND_PARTICIPANTS[kind] ?? ["client", "support"];
}

function threadParticipants(thread: CommunicationThread): string[] {
  if (thread.participants?.length) {
    const seen = new Set<string>();
    return thread.participants.map((p) => p.role).filter((r) => (seen.has(r) ? false : (seen.add(r), true)));
  }
  return participantsFromKind(thread.kind);
}

function unreadCount(thread: CommunicationThread): number {
  const raw = thread.metadata?.unread_count;
  return typeof raw === "number" ? raw : 0;
}

function dateLabel(value?: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

// ── Sender inference ───────────────────────────────────────────────────────────
function inferSenderRole(msg: CommunicationMessage): string {
  if (msg.sender_role) return msg.sender_role;
  const d = (msg.sender_display ?? "").toLowerCase();
  if (d.includes("support") || d.includes("desk")) return "support";
  if (d.includes("writer")) return "writer";
  if (d.includes("admin")) return "admin";
  if (d.includes("editor")) return "editor";
  if (d.includes("client")) return "client";
  if (msg.is_system_generated) return "system";
  return "support";
}

function isOwnMessage(msg: CommunicationMessage): boolean {
  if (auth.user?.id && msg.sender != null) return msg.sender === auth.user.id;
  return msg.sender === 0;
}

// ── Message grouping ───────────────────────────────────────────────────────────
interface MessageGroup {
  senderId: number | null | undefined;
  senderDisplay: string;
  senderRole: string;
  isOwn: boolean;
  messages: CommunicationMessage[];
}

const messageGroups = computed<MessageGroup[]>(() => {
  const groups: MessageGroup[] = [];
  for (const msg of comms.messages) {
    const own = isOwnMessage(msg);
    const sRole = inferSenderRole(msg);
    const last = groups[groups.length - 1];
    if (last && last.senderId === msg.sender && last.senderRole === sRole && last.messages[0]?.is_internal === msg.is_internal) {
      last.messages.push(msg);
    } else {
      groups.push({
        senderId: msg.sender,
        senderDisplay: msg.sender_name ?? msg.sender_display,
        senderRole: sRole,
        isOwn: own,
        messages: [msg],
      });
    }
  }
  return groups;
});

function senderUser(group: MessageGroup) {
  return {
    id: group.senderId ?? 0,
    email: group.senderDisplay,
    full_name: group.isOwn ? (auth.user?.full_name ?? group.senderDisplay) : group.senderDisplay,
    avatar_url: group.isOwn ? (auth.user?.avatar_url ?? null) : null,
  };
}

// ── Recipient selector ─────────────────────────────────────────────────────────
interface RecipientOption { value: string; label: string }

const selectedRecipient = ref("");

const availableRecipients = computed<RecipientOption[]>(() => {
  if (!comms.activeThread) return [];
  const participants = threadParticipants(comms.activeThread);
  const others = participants.filter((r) => r !== props.role);
  const options: RecipientOption[] = others.map((r) => ({ value: r, label: roleStyle(r).label }));
  if (isStaffRole.value) options.push({ value: "internal", label: "Staff note" });
  return options;
});

function defaultRecipient(thread: CommunicationThread): string {
  const participants = threadParticipants(thread);
  const others = participants.filter((r) => r !== props.role);
  const preferred = others.find((r) => r === "client" || r === "writer");
  return preferred ?? others[0] ?? "";
}

watch(
  () => comms.activeThread,
  (thread) => { selectedRecipient.value = thread ? defaultRecipient(thread) : ""; },
  { immediate: true },
);

// ── Composer ───────────────────────────────────────────────────────────────────
const composer = ref("");

async function sendMessage() {
  if (!composer.value.trim()) return;
  const isInternal = selectedRecipient.value === "internal";
  const recipientRole = isInternal ? undefined : selectedRecipient.value;
  await comms.sendMessage(composer.value.trim(), { isInternal, recipientRole });
  composer.value = "";
}

// ── Thread start overlay ───────────────────────────────────────────────────────
const showStartThread = ref(false);
const startingThread = ref(false);
const selectedKind = ref<CommunicationThreadKind>("client_support");

const ALLOWED_KINDS: Record<string, CommunicationThreadKind[]> = {
  client:     ["client_support", "client_writer"],
  writer:     ["client_writer", "client_support"],
  support:    ["client_support", "internal"],
  editor:     ["revision", "client_support", "internal"],
  admin:      ["client_support", "client_writer", "revision", "dispute", "internal"],
  superadmin: ["client_support", "client_writer", "revision", "dispute", "internal"],
};

const availableKinds = computed<CommunicationThreadKind[]>(() => {
  const allowed = ALLOWED_KINDS[props.role] ?? ["client_support"];
  const existing = new Set(comms.orderThreads.map((t) => t.kind));
  return allowed.filter((k) => !existing.has(k));
});

function openStartThread() {
  selectedKind.value = availableKinds.value[0] ?? "client_support";
  showStartThread.value = true;
}

async function confirmStartThread() {
  startingThread.value = true;
  try {
    await comms.createOrderThread({
      orderId: props.orderId,
      kind: selectedKind.value,
      subject: props.order.topic || `Order #${props.orderId}`,
    });
    showStartThread.value = false;
  } finally {
    startingThread.value = false;
  }
}

// ── Polling ────────────────────────────────────────────────────────────────────
const POLL_INTERVAL = 10_000;
let pollTimer: ReturnType<typeof setInterval> | null = null;

async function pollMessages() {
  if (document.hidden || comms.isSending || !comms.activeThread) return;
  try {
    await comms.loadMessages(comms.activeThread.id);
  } catch {
    // non-fatal
  }
}

function onVisibilityChange() {
  if (document.hidden) {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  } else {
    if (!pollTimer) pollTimer = setInterval(pollMessages, POLL_INTERVAL);
  }
}

// ── Scroll to bottom on new messages ──────────────────────────────────────────
watch(
  () => comms.messages.length,
  () => nextTick(() => { if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight; }),
);

// ── Load on mount ──────────────────────────────────────────────────────────────
onMounted(async () => {
  await comms.loadOrderThread(props.orderId);
  pollTimer = setInterval(pollMessages, POLL_INTERVAL);
  document.addEventListener("visibilitychange", onVisibilityChange);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  document.removeEventListener("visibilitychange", onVisibilityChange);
});
</script>

<template>
  <section class="grid min-h-[600px] gap-4 xl:grid-cols-[280px_minmax(0,1fr)]">
    <!-- ── Thread list sidebar ─────────────────────────────────────────────── -->
    <aside class="flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="flex min-h-14 items-center justify-between gap-2 border-b border-slate-200 px-4">
        <h2 class="text-sm font-semibold text-ink">Threads</h2>
        <div class="flex items-center gap-1.5">
          <button
            class="focus-ring rounded-md p-1.5 text-slate-400 hover:text-ink disabled:opacity-40"
            type="button"
            :disabled="comms.isLoading"
            :title="comms.isLoading ? 'Loading…' : 'Refresh'"
            @click="comms.loadOrderThread(orderId)"
          >
            <RefreshCw class="h-4 w-4" :class="comms.isLoading ? 'animate-spin' : ''" />
          </button>
          <button
            v-if="availableKinds.length"
            class="focus-ring inline-flex items-center gap-1 rounded-md bg-signal px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-signal/90"
            type="button"
            @click="openStartThread"
          >
            <Plus class="h-3.5 w-3.5" />
            New
          </button>
        </div>
      </div>

      <!-- Skeleton -->
      <div v-if="comms.isLoading && !comms.orderThreads.length" class="space-y-px p-2">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-md p-4" aria-hidden="true">
          <div class="h-3.5 w-3/4 rounded bg-slate-200" />
          <div class="mt-2 flex gap-1.5">
            <div class="h-5 w-14 rounded-full bg-slate-100" />
            <div class="h-5 w-14 rounded-full bg-slate-100" />
          </div>
          <div class="mt-2 h-3 w-1/3 rounded bg-slate-100" />
        </div>
      </div>

      <!-- Empty -->
      <div
        v-else-if="!comms.orderThreads.length"
        class="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-center"
      >
        <Inbox class="h-8 w-8 text-slate-300" />
        <p class="text-sm text-graphite">No threads yet for this order.</p>
        <button
          v-if="availableKinds.length"
          class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-2 text-xs font-semibold text-white hover:bg-signal/90"
          type="button"
          @click="openStartThread"
        >
          <MessageSquarePlus class="h-3.5 w-3.5" />
          Start a thread
        </button>
      </div>

      <!-- Thread list -->
      <div v-else class="flex-1 divide-y divide-slate-100 overflow-y-auto">
        <button
          v-for="thread in comms.orderThreads"
          :key="thread.id"
          class="focus-ring w-full px-4 py-3.5 text-left transition-colors hover:bg-slate-50"
          :class="thread.id === comms.activeThread?.id ? 'bg-slate-50' : 'bg-white'"
          type="button"
          @click="comms.selectThread(thread)"
        >
          <div class="flex items-start justify-between gap-2">
            <p class="line-clamp-1 text-xs font-semibold text-ink">
              {{ kindLabel(thread.kind) }}
            </p>
            <span
              v-if="unreadCount(thread)"
              class="shrink-0 rounded-full bg-signal px-1.5 py-0.5 text-xs font-semibold text-white"
            >
              {{ unreadCount(thread) }}
            </span>
          </div>
          <div class="mt-1.5 flex flex-wrap gap-1">
            <span
              v-for="p in threadParticipants(thread)"
              :key="p"
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="roleStyle(p).badge"
            >
              {{ roleStyle(p).label }}
            </span>
          </div>
          <p class="mt-1.5 flex items-center gap-1.5 text-xs text-slate-400">
            <span
              class="rounded-full px-1.5 py-0.5 text-xs font-medium capitalize"
              :class="thread.status === 'open' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ thread.status }}
            </span>
            <span v-if="thread.last_message_at">· {{ dateLabel(thread.last_message_at) }}</span>
          </p>
        </button>
      </div>
    </aside>

    <!-- ── Message pane ────────────────────────────────────────────────────── -->
    <main class="flex min-h-[600px] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-panel">
      <!-- Thread header -->
      <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
        <div class="min-w-0">
          <h2 class="truncate text-sm font-semibold text-ink">
            {{ comms.activeThread ? kindLabel(comms.activeThread.kind) : "Select a thread" }}
          </h2>
          <div v-if="comms.activeThread" class="mt-1.5 flex flex-wrap items-center gap-2">
            <span
              v-for="p in threadParticipants(comms.activeThread)"
              :key="p"
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="roleStyle(p).badge"
            >
              {{ roleStyle(p).label }}
            </span>
            <span class="text-xs text-slate-400">·</span>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="comms.activeThread.status === 'open' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ comms.activeThread.status }}
            </span>
          </div>
        </div>
      </div>

      <!-- Messages scroll area -->
      <div ref="scrollEl" class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-4">
        <!-- Skeleton -->
        <div v-if="comms.isLoading && !comms.messages.length" class="space-y-4">
          <div v-for="n in 3" :key="n" class="animate-pulse">
            <div class="flex items-end gap-2" :class="n % 2 === 0 ? 'flex-row-reverse' : ''">
              <div class="h-8 w-8 shrink-0 rounded-full bg-slate-200" />
              <div class="max-w-xs space-y-1.5">
                <div class="h-3 w-20 rounded bg-slate-200" :class="n % 2 === 0 ? 'ml-auto' : ''" />
                <div class="h-16 w-56 rounded-lg bg-slate-200" />
              </div>
            </div>
          </div>
        </div>

        <div
          v-else-if="!comms.activeThread"
          class="flex h-full items-center justify-center text-sm text-graphite"
        >
          Select a thread to read messages.
        </div>
        <div
          v-else-if="!comms.messages.length && !comms.isLoading"
          class="flex h-full items-center justify-center text-sm text-graphite"
        >
          No messages yet — start the conversation below.
        </div>

        <!-- Message groups -->
        <div v-else class="space-y-4">
          <div
            v-for="(group, gi) in messageGroups"
            :key="gi"
            class="flex items-end gap-2.5"
            :class="group.isOwn ? 'flex-row-reverse' : 'flex-row'"
          >
            <UserAvatar :user="senderUser(group)" size="sm" class="shrink-0 self-end" />

            <div
              class="flex max-w-[72%] flex-col gap-1"
              :class="group.isOwn ? 'items-end' : 'items-start'"
            >
              <!-- Identity row -->
              <div class="flex items-center gap-2" :class="group.isOwn ? 'flex-row-reverse' : 'flex-row'">
                <span class="text-xs font-semibold text-ink">
                  {{ group.isOwn ? "You" : group.senderDisplay }}
                </span>
                <span
                  class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                  :class="group.isOwn ? roleStyle(role).badge : roleStyle(group.senderRole).badge"
                >
                  {{ group.isOwn ? role : roleStyle(group.senderRole).label }}
                </span>
                <span
                  v-if="group.messages[0]?.is_internal"
                  class="inline-flex items-center gap-1 rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600"
                >
                  <Lock class="h-3 w-3" />
                  Internal
                </span>
              </div>

              <!-- Bubbles -->
              <div
                v-for="msg in group.messages"
                :key="msg.id"
                class="w-full"
                :class="group.isOwn ? 'flex justify-end' : ''"
              >
                <div
                  class="max-w-full rounded-2xl px-4 py-2.5 text-sm leading-6"
                  :class="[
                    msg.is_internal
                      ? 'border border-dashed border-slate-300 bg-slate-100 text-slate-600 italic'
                      : group.isOwn
                        ? 'rounded-br-sm bg-ink text-white'
                        : `rounded-bl-sm border border-slate-200 border-l-4 bg-white text-graphite ${roleStyle(group.senderRole).border}`,
                  ]"
                >
                  <p class="whitespace-pre-wrap">{{ msg.body }}</p>
                  <p
                    class="mt-1 text-right text-xs"
                    :class="group.isOwn && !msg.is_internal ? 'text-white/60' : 'text-slate-400'"
                  >
                    {{ dateLabel(msg.created_at) }}
                    <span v-if="msg.is_edited"> · edited</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Composer ──────────────────────────────────────────────────────── -->
      <div class="border-t border-slate-200 bg-white px-4 py-3">
        <div
          v-if="!comms.activeThread"
          class="flex h-20 items-center justify-center rounded-lg border border-dashed border-slate-200 text-sm text-slate-400"
        >
          Select a thread to reply
        </div>

        <form v-else class="flex flex-col gap-2.5" @submit.prevent="sendMessage">
          <!-- Recipient pills -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-medium text-graphite">To:</span>
            <button
              v-for="option in availableRecipients"
              :key="option.value"
              type="button"
              class="focus-ring inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold transition-colors"
              :class="selectedRecipient === option.value
                ? roleStyle(option.value).activeBadge
                : `${roleStyle(option.value).badge} opacity-60 hover:opacity-100`"
              @click="selectedRecipient = option.value"
            >
              <Lock v-if="option.value === 'internal'" class="h-3 w-3" />
              {{ option.label }}
            </button>
            <span v-if="!availableRecipients.length" class="text-xs text-slate-400">No recipients available</span>
            <span class="ml-auto text-xs text-graphite">
              From:
              <span
                class="ml-1 rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                :class="roleStyle(role).badge"
              >{{ role }}</span>
            </span>
          </div>

          <p v-if="selectedRecipient === 'internal'" class="text-xs text-slate-500">
            Only staff will see this message — clients and writers cannot.
          </p>

          <!-- Textarea + send -->
          <div class="flex items-end gap-2">
            <textarea
              v-model.trim="composer"
              class="focus-ring min-h-[72px] flex-1 resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm leading-6 placeholder:text-slate-400"
              :class="selectedRecipient === 'internal' ? 'bg-slate-50' : ''"
              placeholder="Write a message…"
              @keydown.enter.exact.prevent="sendMessage"
            />
            <button
              class="focus-ring mb-0.5 inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white disabled:opacity-50"
              :class="selectedRecipient === 'internal' ? 'bg-slate-500' : 'bg-signal'"
              type="submit"
              :disabled="comms.isSending || !composer || !selectedRecipient"
              :title="comms.isSending ? 'Sending…' : 'Send (Enter)'"
            >
              <Loader2 v-if="comms.isSending" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
            </button>
          </div>
          <p v-if="comms.error" class="text-xs text-berry">{{ comms.error }}</p>
          <p class="text-right text-xs text-slate-400">Enter to send · Shift+Enter for new line</p>
        </form>
      </div>
    </main>
  </section>

  <!-- ── Start thread overlay ────────────────────────────────────────────────── -->
  <Teleport to="body">
    <div
      v-if="showStartThread"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      @click.self="showStartThread = false"
    >
      <div class="w-full max-w-sm rounded-xl border border-slate-200 bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <h3 class="text-sm font-semibold text-ink">Start a thread</h3>
          <button
            class="focus-ring rounded-md p-1 text-slate-400 hover:text-ink"
            type="button"
            @click="showStartThread = false"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <div class="p-5 space-y-4">
          <div>
            <p class="mb-2 text-xs font-medium text-graphite">Thread type</p>
            <div class="space-y-2">
              <label
                v-for="kind in availableKinds"
                :key="kind"
                class="flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors"
                :class="selectedKind === kind ? 'border-signal bg-signal/5' : 'border-slate-200 hover:border-slate-300'"
              >
                <input
                  v-model="selectedKind"
                  :value="kind"
                  type="radio"
                  class="accent-signal"
                />
                <div>
                  <p class="text-sm font-medium text-ink">{{ kindLabel(kind) }}</p>
                  <div class="mt-1 flex flex-wrap gap-1">
                    <span
                      v-for="p in participantsFromKind(kind)"
                      :key="p"
                      class="rounded-full px-1.5 py-0.5 text-xs font-medium"
                      :class="roleStyle(p).badge"
                    >
                      {{ roleStyle(p).label }}
                    </span>
                  </div>
                </div>
              </label>
            </div>
            <p v-if="!availableKinds.length" class="text-sm text-graphite">
              All available thread types already exist for this order.
            </p>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t border-slate-200 px-5 py-4">
          <button
            class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50"
            type="button"
            @click="showStartThread = false"
          >
            Cancel
          </button>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-50 hover:bg-signal/90"
            type="button"
            :disabled="startingThread || !availableKinds.length"
            @click="confirmStartThread"
          >
            <Loader2 v-if="startingThread" class="h-4 w-4 animate-spin" />
            <MessageSquarePlus v-else class="h-4 w-4" />
            {{ startingThread ? "Starting…" : "Start thread" }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
