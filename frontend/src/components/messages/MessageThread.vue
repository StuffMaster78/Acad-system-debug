<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { AlertTriangle, ArrowLeft, CheckCircle2, ClipboardList, ExternalLink, FileText, Image, Info, Inbox, Lock, Loader2, Paperclip, Pencil, RefreshCw, Search, Send, ShieldCheck, ShieldOff, Users, X } from "@lucide/vue";
import type { CommunicationMessage, CommunicationThread, CommunicationThreadKind } from "@/api/communications";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import { useCommunicationsStore } from "@/stores/communications";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

interface AttachmentFile {
  name: string;
  size: number;
  type: string;
  dataUrl: string;
  isImage: boolean;
}

const props = defineProps<{
  role: UserRole;
  orderBaseUrl: string;
}>();

const auth = useAuthStore();
const comms = useCommunicationsStore();

const composer = ref("");
const selectedRecipient = ref("");
const scrollEl = ref<HTMLElement | null>(null);

// ── File attachments ───────────────────────────────────────────────────────────
const attachments = ref<AttachmentFile[]>([]);
const fileInputEl = ref<HTMLInputElement | null>(null);
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_FILES = 5;

function openFilePicker() {
  fileInputEl.value?.click();
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function handleFilePick(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  input.value = "";

  const remaining = MAX_FILES - attachments.value.length;
  const toAdd = files.slice(0, remaining);

  for (const file of toAdd) {
    if (file.size > MAX_FILE_SIZE) continue;
    const dataUrl = await readFileAsDataUrl(file);
    attachments.value.push({
      name: file.name,
      size: file.size,
      type: file.type,
      dataUrl,
      isImage: file.type.startsWith("image/"),
    });
  }
}

function removeAttachment(index: number) {
  attachments.value.splice(index, 1);
}

function clearAttachments() {
  attachments.value = [];
}

// ── Mobile panel control ───────────────────────────────────────────────────────
const showMobilePane = ref(false); // false = list, true = message/compose pane

// ── Thread list search + filter ───────────────────────────────────────────────
const searchQuery = ref("");
const filterKind = ref("all");
const filterUnread = ref(false);

const availableKinds = computed(() => {
  const kinds = new Set(comms.inboxThreads.map((t) => t.kind));
  return Array.from(kinds);
});

const filteredThreads = computed(() => {
  let list = comms.inboxThreads;
  if (filterUnread.value) list = list.filter((t) => unreadCount(t) > 0);
  if (filterKind.value !== "all") list = list.filter((t) => t.kind === filterKind.value);
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase();
    list = list.filter(
      (t) =>
        (t.subject ?? "").toLowerCase().includes(q) ||
        String(t.target_id).includes(q),
    );
  }
  return list;
});

const totalUnread = computed(() =>
  comms.inboxThreads.reduce((sum, t) => sum + unreadCount(t), 0),
);

// ── Thread resolve ─────────────────────────────────────────────────────────────
const isResolving = ref(false);
async function resolveThread() {
  if (!comms.activeThread) return;
  isResolving.value = true;
  try {
    await comms.loadInboxThreads();
  } finally {
    isResolving.value = false;
  }
}

function pickThread(thread: CommunicationThread) {
  comms.selectThread(thread);
  showMobilePane.value = true;
}

// ── New message compose ────────────────────────────────────────────────────────
const showCompose = ref(false);
const composeError = ref("");
const isComposing = ref(false);
const composeForm = reactive({
  orderId: "",
  recipientRole: "",
  subject: "",
  body: "",
});

function openCompose() {
  composeForm.orderId = "";
  composeForm.recipientRole = newMessageRecipients.value[0]?.value ?? "";
  composeForm.subject = "";
  composeForm.body = "";
  composeError.value = "";
  showCompose.value = true;
  showMobilePane.value = true;
}

function closeCompose() {
  showCompose.value = false;
}

async function submitCompose() {
  if (!composeForm.orderId || !composeForm.recipientRole || !composeForm.body.trim()) {
    composeError.value = "Order ID, recipient, and message are all required.";
    return;
  }
  composeError.value = "";
  isComposing.value = true;
  try {
    const isInternal = composeForm.recipientRole === "internal";
    const kind = threadKindFor(composeForm.recipientRole);
    const subject = composeForm.subject.trim() || `Order #${composeForm.orderId}`;
    await comms.createOrderThread({ orderId: composeForm.orderId, kind, subject });
    await comms.sendMessage(composeForm.body.trim(), {
      isInternal,
      recipientRole: isInternal ? undefined : composeForm.recipientRole,
    });
    showCompose.value = false;
  } catch {
    composeError.value = "Could not send the message. Check the order ID and try again.";
  } finally {
    isComposing.value = false;
  }
}

// ── Role metadata ──────────────────────────────────────────────────────────────
const ROLE_STYLE: Record<string, { border: string; badge: string; activeBadge: string; label: string }> = {
  client:        { border: "border-l-blue-400",    badge: "bg-blue-100 text-blue-800",       activeBadge: "bg-blue-500 text-white",       label: "Client" },
  writer:        { border: "border-l-emerald-400", badge: "bg-emerald-100 text-emerald-800", activeBadge: "bg-emerald-600 text-white",    label: "Writer" },
  support:       { border: "border-l-amber-400",   badge: "bg-amber-100 text-amber-800",     activeBadge: "bg-amber-500 text-white",      label: "Support" },
  admin:         { border: "border-l-violet-400",  badge: "bg-violet-100 text-violet-800",   activeBadge: "bg-violet-600 text-white",     label: "Admin" },
  editor:        { border: "border-l-cyan-400",    badge: "bg-cyan-100 text-cyan-800",       activeBadge: "bg-cyan-600 text-white",       label: "Editor" },
  superadmin:    { border: "border-l-rose-400",    badge: "bg-rose-100 text-rose-800",       activeBadge: "bg-rose-600 text-white",       label: "Superadmin" },
  system:        { border: "border-l-slate-300",   badge: "bg-slate-100 text-slate-500",     activeBadge: "bg-slate-400 text-white",      label: "System" },
  internal:      { border: "border-l-slate-400",   badge: "bg-slate-100 text-slate-600",     activeBadge: "bg-slate-600 text-white",      label: "Staff note" },
  client_writer: { border: "border-l-violet-300",  badge: "bg-violet-100 text-violet-700",   activeBadge: "bg-violet-600 text-white",     label: "Client + Writer" },
};

// ── Thread access control ──────────────────────────────────────────────────────
const THREAD_ROLE_ACCESS: Record<string, string[]> = {
  client_support: ["client", "support", "admin", "superadmin"],
  client_writer:  ["client", "writer", "support", "admin", "superadmin"],
  revision:       ["client", "writer", "editor", "support", "admin", "superadmin"],
  dispute:        ["client", "support", "admin", "superadmin"],
  internal:       ["support", "admin", "editor", "superadmin"],
  moderation:     ["admin", "superadmin"],
  sensitive:      ["admin", "superadmin"],
};

function canAccessThread(thread: CommunicationThread): boolean {
  const allowed = THREAD_ROLE_ACCESS[thread.kind];
  if (!allowed) return true;
  return allowed.includes(props.role);
}

// ── Audience labels + chips ────────────────────────────────────────────────────
const AUDIENCE_LABELS: Record<string, string> = {
  internal:      "Staff only",
  client:        "Client only",
  writer:        "Writer only",
  client_writer: "Client + Writer",
};
const AUDIENCE_CHIP_CLASS: Record<string, string> = {
  internal:      "bg-slate-200 text-slate-600",
  client:        "bg-blue-100 text-blue-700",
  writer:        "bg-emerald-100 text-emerald-700",
  client_writer: "bg-violet-100 text-violet-700",
};

function msgAudience(msg: CommunicationMessage): string | null {
  if (msg.is_internal) return "internal";
  const raw = msg.audience ?? (msg.metadata?.recipient_role as string | undefined);
  return raw ?? null;
}
function audienceLabel(msg: CommunicationMessage): string | null {
  const aud = msgAudience(msg);
  return aud ? (AUDIENCE_LABELS[aud] ?? aud) : null;
}
function audienceChipClass(msg: CommunicationMessage): string {
  const aud = msgAudience(msg);
  return aud ? (AUDIENCE_CHIP_CLASS[aud] ?? "bg-slate-100 text-slate-600") : "";
}

// ── Message flags ──────────────────────────────────────────────────────────────
const FLAG_META: Record<string, { label: string; cls: string }> = {
  contact_leak:      { label: "Contact leak",     cls: "bg-amber-100 text-amber-800" },
  off_platform:      { label: "Off-platform",     cls: "bg-amber-100 text-amber-800" },
  risky_link:        { label: "Risky link",        cls: "bg-orange-100 text-orange-800" },
  unsafe_attachment: { label: "Unsafe attachment", cls: "bg-red-100 text-red-800" },
};

// ── Moderation status display ──────────────────────────────────────────────────
const MOD_STATUS_META: Record<string, { label: string; cls: string }> = {
  held:     { label: "Held",     cls: "bg-amber-100 text-amber-800" },
  blocked:  { label: "Blocked",  cls: "bg-red-100 text-red-800" },
  approved: { label: "Approved", cls: "bg-emerald-100 text-emerald-700" },
  warned:   { label: "Warned",   cls: "bg-orange-100 text-orange-800" },
};

// ── Attachment scan status ─────────────────────────────────────────────────────
const SCAN_META: Record<string, { label: string; cls: string }> = {
  clean:    { label: "Verified",  cls: "text-emerald-600" },
  blocked:  { label: "Blocked",   cls: "text-red-600" },
  scanning: { label: "Scanning…", cls: "text-slate-500" },
};

function roleStyle(role: string) {
  return ROLE_STYLE[role] ?? { border: "border-l-slate-300", badge: "bg-slate-100 text-slate-600", activeBadge: "bg-slate-500 text-white", label: role };
}

const STAFF_ROLES = new Set(["admin", "support", "editor", "superadmin"]);
const isStaff = computed(() => STAFF_ROLES.has(props.role));

// ── Recipient display label (audience-qualified for staff) ────────────────────
function recipientLabel(role: string): string {
  if (isStaff.value) {
    if (role === "client")        return "Client only";
    if (role === "writer")        return "Writer only";
    if (role === "internal")      return "Staff only";
    if (role === "client_writer") return "Client + Writer";
  }
  return roleStyle(role).label;
}

// ── New message recipient options (no thread context) ─────────────────────────
const newMessageRecipients = computed<RecipientOption[]>(() => {
  switch (props.role) {
    case "client":
      return [
        { value: "writer",  label: "Writer" },
        { value: "support", label: "Support" },
      ];
    case "writer":
      return [
        { value: "client",  label: "Client" },
        { value: "support", label: "Support" },
      ];
    case "editor":
      return [
        { value: "client",  label: "Client" },
        { value: "writer",  label: "Writer" },
        { value: "support", label: "Support" },
      ];
    case "support":
    case "admin":
    case "superadmin":
      return [
        { value: "client",   label: "Client only" },
        { value: "writer",   label: "Writer only" },
        { value: "editor",   label: "Editor" },
        { value: "internal", label: "Staff only" },
      ];
    default:
      return [];
  }
});

function threadKindFor(recipientRole: string): CommunicationThreadKind {
  const pair = new Set([props.role, recipientRole]);
  if (pair.has("client") && pair.has("writer"))  return "client_writer";
  if (pair.has("client"))                         return "client_support";
  if (pair.has("editor"))                         return "revision";
  return "client_support";
}

// ── Participant inference from thread kind ─────────────────────────────────────
const KIND_PARTICIPANTS: Record<string, string[]> = {
  client_writer:  ["client", "writer"],
  client_support: ["client", "support"],
  revision:       ["client", "writer", "editor"],
  dispute:        ["client", "support", "admin"],
  internal:       ["admin", "support"],
  moderation:     ["admin", "superadmin"],
  sensitive:      ["admin", "superadmin"],
};

function participantsFromKind(kind: string): string[] {
  return KIND_PARTICIPANTS[kind] ?? ["client", "support"];
}

function threadParticipants(thread: CommunicationThread): string[] {
  if (thread.participants?.length) {
    const seen = new Set<string>();
    return thread.participants
      .map((p) => p.role)
      .filter((r) => (seen.has(r) ? false : (seen.add(r), true)));
  }
  return participantsFromKind(thread.kind);
}

// ── Recipient options based on sender role + thread participants ───────────────
interface RecipientOption {
  value: string;
  label: string;
}

const availableRecipients = computed<RecipientOption[]>(() => {
  if (!comms.activeThread) return [];
  const participants = threadParticipants(comms.activeThread);
  const others = participants.filter((r) => r !== props.role);

  const options: RecipientOption[] = others.map((r) => ({
    value: r,
    label: recipientLabel(r),
  }));

  if (isStaff.value) {
    if (others.includes("client") && others.includes("writer")) {
      options.unshift({ value: "client_writer", label: "Client + Writer" });
    }
    options.push({ value: "internal", label: "Staff only" });
  }

  return options;
});

function defaultRecipient(thread: CommunicationThread): string {
  const participants = threadParticipants(thread);
  const others = participants.filter((r) => r !== props.role);
  // prefer client or writer over other staff roles
  const preferred = others.find((r) => r === "client" || r === "writer");
  return preferred ?? others[0] ?? "";
}

watch(
  () => comms.activeThread,
  (thread) => {
    selectedRecipient.value = thread ? defaultRecipient(thread) : "";
  },
  { immediate: true },
);

// ── Sender role inference ──────────────────────────────────────────────────────
function inferSenderRole(msg: CommunicationMessage): string {
  if (msg.sender_role) return msg.sender_role;
  const d = (msg.sender_display ?? "").toLowerCase();
  if (d.includes("support") || d.includes("desk") || d.includes("agent")) return "support";
  if (d.includes("writer")) return "writer";
  if (d.includes("admin")) return "admin";
  if (d.includes("editor")) return "editor";
  if (d.includes("client")) return "client";
  if (msg.is_system_generated) return "system";
  return "staff";
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

// ── Active order link ─────────────────────────────────────────────────────────
const orderUrl = computed(() => {
  const t = comms.activeThread;
  if (!t || t.target_type !== "order") return null;
  return `${props.orderBaseUrl}/${t.target_id}`;
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function dateLabel(value?: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function unreadCount(thread: CommunicationThread): number {
  const raw = thread.metadata?.unread_count;
  return typeof raw === "number" ? raw : 0;
}

function kindLabel(kind: string): string {
  const map: Record<string, string> = {
    client_writer:  "Client ↔ Writer",
    client_support: "Client ↔ Support",
    revision:       "Revision",
    dispute:        "Dispute",
    internal:       "Internal",
    moderation:     "Moderation",
    sensitive:      "Sensitive",
  };
  return map[kind] ?? kind.replace(/_/g, " ");
}

// ── Moderation thread guard ────────────────────────────────────────────────────
const isModerationThread = computed(
  () => comms.activeThread?.kind === "moderation",
);

// ── Identity masking for moderation/sensitive threads ─────────────────────────
function maskedDisplay(group: { isOwn: boolean; senderRole: string; senderId: number | null | undefined; senderDisplay: string }): string {
  if (group.isOwn) return "You";
  const kind = comms.activeThread?.kind;
  if (kind === "moderation" || kind === "sensitive") {
    if (group.senderRole === "client") return `Client #C${group.senderId ?? "?"}`;
    if (group.senderRole === "writer") return `Writer #W${group.senderId ?? "?"}`;
  }
  return group.senderDisplay;
}

// ── Moderation actions ─────────────────────────────────────────────────────────
async function moderateMsg(msgId: number, action: "approve" | "reject" | "warn") {
  await comms.moderateMessage(msgId, action);
  auditLog.value.unshift({ action, messageId: msgId, at: new Date().toISOString() });
}

// ── Scroll to bottom on new messages ─────────────────────────────────────────
watch(
  () => comms.messages.length,
  () => nextTick(() => { if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight; }),
);

// ── Send ──────────────────────────────────────────────────────────────────────
async function sendMessage() {
  if (!composer.value.trim() && !attachments.value.length) return;
  const isInternal = selectedRecipient.value === "internal";
  const recipientRole = isInternal ? undefined : selectedRecipient.value;
  const attachmentPayload = attachments.value.length
    ? attachments.value.map((a) => ({ name: a.name, type: a.type, dataUrl: a.dataUrl }))
    : undefined;
  await comms.sendMessage(composer.value.trim(), { isInternal, recipientRole, attachments: attachmentPayload });
  composer.value = "";
  clearAttachments();
}

// ── Polling (10s interval, paused when tab hidden) ────────────────────────────
const POLL_INTERVAL = 10_000;
let pollTimer: ReturnType<typeof setInterval> | null = null;

async function pollRefresh() {
  if (document.hidden || comms.isSending) return;
  try {
    const prevActive = comms.activeThread?.id;
    await comms.loadInboxThreads();
    if (prevActive && comms.activeThread?.id === prevActive) {
      await comms.loadMessages(prevActive);
    }
  } catch {
    // non-fatal — network may be unavailable
  }
}

function onVisibilityChange() {
  if (document.hidden) {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  } else {
    if (!pollTimer) pollTimer = setInterval(pollRefresh, POLL_INTERVAL);
  }
}

onMounted(() => {
  pollTimer = setInterval(pollRefresh, POLL_INTERVAL);
  document.addEventListener("visibilitychange", onVisibilityChange);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
  document.removeEventListener("visibilitychange", onVisibilityChange);
});

// ── Right panel (staff) ────────────────────────────────────────────────────────
const showRightPanel = ref(false);

interface AuditEntry {
  action: "approve" | "reject" | "warn";
  messageId: number;
  at: string;
}
const auditLog = ref<AuditEntry[]>([]);

watch(
  () => comms.activeThread?.id,
  () => { auditLog.value = []; },
);

const flagsSummary = computed(() => {
  const counts: Record<string, number> = {};
  for (const msg of comms.messages) {
    for (const flag of msg.flags ?? []) {
      counts[flag] = (counts[flag] ?? 0) + 1;
    }
  }
  return Object.entries(counts).map(([flag, count]) => ({
    flag,
    count,
    label: FLAG_META[flag]?.label ?? flag,
    cls: FLAG_META[flag]?.cls ?? "bg-slate-100 text-slate-600",
  }));
});

const auditActionLabel: Record<string, string> = {
  approve: "Approved",
  reject: "Rejected",
  warn: "Warned sender",
};
const auditActionClass: Record<string, string> = {
  approve: "text-emerald-700",
  reject: "text-red-700",
  warn: "text-amber-700",
};

// ── Stub avatar user shape for UserAvatar ─────────────────────────────────────
function senderUser(group: MessageGroup) {
  const display = maskedDisplay(group);
  return {
    id: group.senderId ?? 0,
    email: display,
    full_name: group.isOwn ? (auth.user?.full_name ?? display) : display,
    avatar_url: group.isOwn ? auth.user?.avatar_url : null,
  };
}
</script>

<template>
  <section
    class="grid min-h-[640px] gap-4"
    :class="showRightPanel && isStaff
      ? 'xl:grid-cols-[280px_minmax(0,1fr)_256px]'
      : 'xl:grid-cols-[320px_minmax(0,1fr)]'"
  >
    <!-- ── Thread list (inbox sidebar) ──────────────────────────────────────── -->
    <aside
      class="flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white"
      :class="showMobilePane ? 'hidden xl:flex' : 'flex'"
    >
      <!-- Sidebar header -->
      <div class="border-b border-slate-200 px-4 py-3">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <h2 class="text-sm font-semibold text-ink">Inbox</h2>
            <span
              v-if="totalUnread"
              class="rounded-full bg-signal px-2 py-0.5 text-xs font-bold text-white"
            >{{ totalUnread }}</span>
          </div>
          <div class="flex items-center gap-1">
            <button
              class="focus-ring rounded-md p-1.5 text-slate-400 hover:text-ink disabled:opacity-40"
              type="button"
              :title="comms.isLoading ? 'Loading…' : 'Refresh'"
              :disabled="comms.isLoading"
              @click="comms.loadInboxThreads()"
            >
              <RefreshCw class="h-3.5 w-3.5" :class="comms.isLoading ? 'animate-spin' : ''" />
            </button>
            <button
              class="focus-ring inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors"
              :class="showCompose
                ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                : 'bg-signal text-white hover:bg-signal/90'"
              type="button"
              @click="showCompose ? closeCompose() : openCompose()"
            >
              <X v-if="showCompose" class="h-3 w-3" />
              <Pencil v-else class="h-3 w-3" />
              {{ showCompose ? "Cancel" : "New" }}
            </button>
          </div>
        </div>

        <!-- Search -->
        <div class="relative mt-2.5">
          <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            class="focus-ring h-8 w-full rounded-md border border-slate-200 bg-slate-50 pl-8 pr-3 text-xs placeholder:text-slate-400"
            type="search"
            placeholder="Search by subject or order ID…"
          />
        </div>

        <!-- Filter pills -->
        <div class="mt-2 flex flex-wrap items-center gap-1.5">
          <button
            class="rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors"
            :class="filterUnread ? 'bg-signal/10 text-signal' : 'text-graphite hover:text-ink'"
            type="button"
            @click="filterUnread = !filterUnread"
          >
            {{ filterUnread ? "Unread only" : "All" }}
          </button>
          <span class="h-3 w-px bg-slate-200" />
          <button
            class="rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors"
            :class="filterKind === 'all' ? 'bg-slate-100 text-ink font-semibold' : 'text-graphite hover:text-ink'"
            type="button"
            @click="filterKind = 'all'"
          >All</button>
          <button
            v-for="kind in availableKinds"
            :key="kind"
            class="rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors"
            :class="filterKind === kind ? 'bg-slate-100 text-ink font-semibold' : 'text-graphite hover:text-ink'"
            type="button"
            @click="filterKind = kind"
          >{{ kindLabel(kind) }}</button>
        </div>
      </div>

      <!-- Thread list body -->
      <div v-if="comms.isLoading && !comms.inboxThreads.length" class="space-y-px p-2">
        <div v-for="n in 4" :key="n" class="animate-pulse rounded-md p-4" aria-hidden="true">
          <div class="h-3.5 w-2/3 rounded bg-slate-200" />
          <div class="mt-2 flex gap-1.5">
            <div class="h-5 w-14 rounded-full bg-slate-100" />
            <div class="h-5 w-14 rounded-full bg-slate-100" />
          </div>
          <div class="mt-2 h-3 w-1/3 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!comms.inboxThreads.length" class="flex flex-1 items-center justify-center p-6 text-center">
        <div>
          <Inbox class="mx-auto h-8 w-8 text-slate-300" />
          <p class="mt-2 text-sm font-medium text-ink">No conversations yet</p>
          <p class="mt-1 text-xs text-graphite">Start a new message to begin.</p>
        </div>
      </div>

      <div v-else-if="filteredThreads.length === 0" class="flex flex-1 items-center justify-center p-6 text-center">
        <div>
          <Search class="mx-auto h-7 w-7 text-slate-300" />
          <p class="mt-2 text-sm text-graphite">No threads match your filter.</p>
          <button class="mt-2 text-xs text-signal hover:underline" type="button" @click="searchQuery = ''; filterKind = 'all'; filterUnread = false">
            Clear filters
          </button>
        </div>
      </div>

      <div v-else class="flex-1 divide-y divide-slate-100 overflow-y-auto">
        <button
          v-for="thread in filteredThreads"
          :key="thread.id"
          class="focus-ring w-full px-4 py-3.5 text-left transition-colors"
          :class="[
            !canAccessThread(thread) ? 'cursor-not-allowed opacity-50 bg-white' :
              thread.id === comms.activeThread?.id ? 'bg-slate-50' : 'bg-white hover:bg-slate-50',
          ]"
          type="button"
          :disabled="!canAccessThread(thread)"
          @click="canAccessThread(thread) && pickThread(thread)"
        >
          <div class="flex items-start justify-between gap-2">
            <p class="line-clamp-2 text-sm font-semibold leading-5"
               :class="canAccessThread(thread) ? 'text-ink' : 'text-graphite'">
              <Lock v-if="!canAccessThread(thread)" class="mr-1 inline-block h-3 w-3 align-middle" />
              {{ canAccessThread(thread) ? (thread.subject || `Thread #${thread.id}`) : 'Access restricted' }}
            </p>
            <span
              v-if="unreadCount(thread) && canAccessThread(thread)"
              class="shrink-0 rounded-full bg-signal px-2 py-0.5 text-xs font-bold text-white"
            >{{ unreadCount(thread) }}</span>
          </div>
          <div v-if="canAccessThread(thread)" class="mt-1.5 flex flex-wrap gap-1">
            <span
              v-for="p in threadParticipants(thread)"
              :key="p"
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="roleStyle(p).badge"
            >{{ roleStyle(p).label }}</span>
          </div>
          <p v-if="canAccessThread(thread)" class="mt-1.5 text-xs text-slate-400">
            #{{ thread.target_id }} · {{ dateLabel(thread.last_message_at) || "No messages" }}
          </p>
          <p v-else class="mt-1 text-xs text-slate-400">
            {{ kindLabel(thread.kind) }} · visible to {{ (THREAD_ROLE_ACCESS[thread.kind] ?? []).join(", ") || "admins" }} only
          </p>
        </button>
      </div>
    </aside>

    <!-- ── Compose pane (replaces message pane when composing) ───────────────── -->
    <main
      v-if="showCompose"
      class="flex min-h-[640px] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white"
      :class="showMobilePane ? 'flex' : 'hidden xl:flex'"
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div class="flex items-center gap-3">
          <button
            class="focus-ring xl:hidden rounded-md p-1 text-slate-400 hover:text-ink"
            type="button"
            @click="showMobilePane = false; closeCompose()"
          >
            <ArrowLeft class="h-4 w-4" />
          </button>
          <div>
            <h2 class="text-base font-semibold text-ink">New message</h2>
            <p class="mt-0.5 text-xs text-graphite">Start a new conversation about an order.</p>
          </div>
        </div>
        <button class="focus-ring rounded-md p-1.5 text-slate-400 hover:text-ink" type="button" @click="closeCompose">
          <X class="h-4 w-4" />
        </button>
      </div>

      <form class="flex flex-1 flex-col gap-4 overflow-y-auto p-5" @submit.prevent="submitCompose">
        <!-- Order ID -->
        <label class="block">
          <span class="text-sm font-medium text-ink">Order ID <span class="text-berry">*</span></span>
          <input
            v-model.trim="composeForm.orderId"
            class="focus-ring mt-1.5 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
            type="number"
            min="1"
            placeholder="e.g. 1042"
            required
          />
        </label>

        <!-- Recipient -->
        <div>
          <span class="text-sm font-medium text-ink">To <span class="text-berry">*</span></span>
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="option in newMessageRecipients"
              :key="option.value"
              type="button"
              class="focus-ring inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors"
              :class="composeForm.recipientRole === option.value
                ? roleStyle(option.value).activeBadge
                : `${roleStyle(option.value).badge} opacity-60 hover:opacity-100`"
              @click="composeForm.recipientRole = option.value"
            >
              <Lock v-if="option.value === 'internal'" class="h-3 w-3" />
              {{ option.label }}
            </button>
          </div>
          <p v-if="composeForm.recipientRole === 'internal'" class="mt-2 text-xs text-slate-500">
            Only staff will see this thread.
          </p>
        </div>

        <!-- Subject (optional) -->
        <label class="block">
          <span class="text-sm font-medium text-ink">Subject <span class="text-graphite font-normal">(optional)</span></span>
          <input
            v-model.trim="composeForm.subject"
            class="focus-ring mt-1.5 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
            type="text"
            :placeholder="`Order #${composeForm.orderId || '…'}`"
          />
        </label>

        <!-- Message -->
        <label class="block flex-1">
          <span class="text-sm font-medium text-ink">Message <span class="text-berry">*</span></span>
          <textarea
            v-model.trim="composeForm.body"
            class="focus-ring mt-1.5 min-h-40 w-full rounded-md border border-slate-200 px-3 py-2 text-sm leading-6"
            :class="composeForm.recipientRole === 'internal' ? 'bg-slate-50' : ''"
            placeholder="Write your message…"
            required
          />
        </label>

        <p v-if="composeError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
          {{ composeError }}
        </p>

        <div class="flex items-center justify-end gap-3 border-t border-slate-100 pt-2">
          <button
            class="focus-ring rounded-md border border-slate-200 px-4 py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50"
            type="button"
            @click="closeCompose"
          >
            Cancel
          </button>
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            :class="composeForm.recipientRole === 'internal' ? 'bg-slate-600' : 'bg-signal'"
            type="submit"
            :disabled="isComposing || !composeForm.orderId || !composeForm.recipientRole || !composeForm.body"
          >
            <Loader2 v-if="isComposing" class="h-4 w-4 animate-spin" />
            <Send v-else class="h-4 w-4" />
            {{ isComposing ? "Sending…" : "Send message" }}
          </button>
        </div>
      </form>
    </main>

    <!-- ── Message pane ──────────────────────────────────────────────────────── -->
    <main
      v-else
      class="flex min-h-[640px] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white"
      :class="showMobilePane ? 'flex' : 'hidden xl:flex'"
    >
      <!-- Thread header -->
      <div class="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex min-w-0 items-center gap-2">
          <!-- Mobile back button -->
          <button
            class="focus-ring xl:hidden shrink-0 rounded-md p-1 text-slate-400 hover:text-ink"
            type="button"
            title="Back to inbox"
            @click="showMobilePane = false"
          >
            <ArrowLeft class="h-4 w-4" />
          </button>
          <div class="min-w-0">
            <h2 class="truncate text-sm font-semibold text-ink">
              {{ comms.activeThread?.subject || "Select a conversation" }}
            </h2>
            <div v-if="comms.activeThread" class="mt-1 flex flex-wrap items-center gap-1.5">
              <span
                v-for="p in threadParticipants(comms.activeThread)"
                :key="p"
                class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                :class="roleStyle(p).badge"
              >{{ roleStyle(p).label }}</span>
              <span class="text-xs text-slate-300">·</span>
              <span class="text-xs text-graphite capitalize">{{ kindLabel(comms.activeThread.kind) }}</span>
              <span
                class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                :class="comms.activeThread.status === 'open' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'"
              >{{ comms.activeThread.status }}</span>
            </div>
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <button
            v-if="comms.activeThread?.status === 'open'"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite transition-colors hover:border-emerald-300 hover:text-emerald-700 disabled:opacity-50"
            type="button"
            :disabled="isResolving"
            title="Mark as resolved"
            @click="resolveThread"
          >
            <Loader2 v-if="isResolving" class="h-3.5 w-3.5 animate-spin" />
            <CheckCircle2 v-else class="h-3.5 w-3.5" />
            Resolve
          </button>
          <RouterLink
            v-if="orderUrl"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
            :to="orderUrl"
          >
            <ExternalLink class="h-3.5 w-3.5" />
            Open order
          </RouterLink>
          <!-- Thread details panel toggle (staff only) -->
          <button
            v-if="isStaff && comms.activeThread"
            class="focus-ring hidden rounded-md border p-1.5 xl:block"
            :class="showRightPanel
              ? 'border-signal bg-signal/5 text-signal'
              : 'border-slate-200 text-slate-400 hover:text-ink'"
            type="button"
            :title="showRightPanel ? 'Hide thread details' : 'Show thread details'"
            @click="showRightPanel = !showRightPanel"
          >
            <Info class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <!-- Messages scroll area -->
      <div ref="scrollEl" class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-4">
        <!-- Loading skeleton -->
        <div v-if="comms.isLoading && !comms.messages.length" class="space-y-4">
          <div v-for="n in 3" :key="n" class="animate-pulse">
            <div class="flex items-end gap-2" :class="n % 2 === 0 ? 'flex-row-reverse' : ''">
              <div class="h-8 w-8 shrink-0 rounded-full bg-slate-200" />
              <div class="max-w-sm space-y-1.5">
                <div class="h-3 w-20 rounded bg-slate-200" :class="n % 2 === 0 ? 'ml-auto' : ''" />
                <div class="h-16 w-64 rounded-lg bg-slate-200" />
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!comms.activeThread" class="flex h-full items-center justify-center text-sm text-graphite">
          Select a conversation to get started.
        </div>
        <div v-else-if="!comms.messages.length && !comms.isLoading" class="flex h-full items-center justify-center text-sm text-graphite">
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

            <div class="flex max-w-[72%] flex-col gap-1" :class="group.isOwn ? 'items-end' : 'items-start'">
              <!-- Sender identity row -->
              <div class="flex items-center gap-2" :class="group.isOwn ? 'flex-row-reverse' : 'flex-row'">
                <span class="text-xs font-semibold text-ink">
                  {{ maskedDisplay(group) }}
                </span>
                <span
                  class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                  :class="group.isOwn ? roleStyle(role).badge : roleStyle(group.senderRole).badge"
                >
                  {{ group.isOwn ? role : roleStyle(group.senderRole).label }}
                </span>
                <!-- Internal badge -->
                <span
                  v-if="group.messages[0]?.is_internal"
                  class="inline-flex items-center gap-1 rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600"
                >
                  <Lock class="h-3 w-3" />
                  Internal
                </span>
              </div>

              <!-- Message bubbles -->
              <div
                v-for="msg in group.messages"
                :key="msg.id"
                class="w-full"
                :class="group.isOwn ? 'flex flex-col items-end' : ''"
              >
                <div
                  class="relative max-w-full rounded-2xl px-4 py-2.5 text-sm leading-6"
                  :class="[
                    msg.moderation_status === 'held' || msg.moderation_status === 'blocked'
                      ? 'border border-dashed border-amber-300 bg-amber-50 text-amber-900'
                      : msg.is_internal
                        ? 'border border-dashed border-slate-300 bg-slate-100 text-slate-600 italic'
                        : group.isOwn
                          ? 'rounded-br-sm bg-ink text-white'
                          : `rounded-bl-sm border border-slate-200 border-l-4 bg-white text-graphite ${roleStyle(group.senderRole).border}`,
                  ]"
                >
                  <!-- Flag pills (shown inside bubble header when flagged) -->
                  <div v-if="msg.flags?.length" class="mb-2 flex flex-wrap gap-1">
                    <span
                      v-for="flag in msg.flags"
                      :key="flag"
                      class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold"
                      :class="FLAG_META[flag]?.cls ?? 'bg-slate-100 text-slate-600'"
                    >
                      <AlertTriangle class="h-3 w-3" />
                      {{ FLAG_META[flag]?.label ?? flag }}
                    </span>
                  </div>

                  <p v-if="msg.body" class="whitespace-pre-wrap">{{ msg.body }}</p>

                  <!-- Attachments -->
                  <div v-if="msg.attachments?.length" class="mt-2 flex flex-wrap gap-2">
                    <a
                      v-for="(att, ai) in (msg.attachments as Array<{name: string; type: string; url?: string; dataUrl?: string; scan_status?: string}>)"
                      :key="ai"
                      :href="att.scan_status === 'blocked' ? '#' : (att.url ?? att.dataUrl ?? '#')"
                      :target="att.scan_status === 'blocked' ? '_self' : '_blank'"
                      class="flex items-center gap-1.5 rounded-lg border border-white/20 bg-white/10 px-2 py-1 text-xs hover:bg-white/20"
                      :class="att.scan_status === 'blocked' ? 'cursor-not-allowed opacity-60' : ''"
                    >
                      <ShieldOff v-if="att.scan_status === 'blocked'" class="h-3.5 w-3.5 shrink-0 text-red-500" />
                      <ShieldCheck v-else-if="att.scan_status === 'clean'" class="h-3.5 w-3.5 shrink-0 text-emerald-500" />
                      <Image v-else-if="att.type?.startsWith('image/')" class="h-3.5 w-3.5 shrink-0" />
                      <FileText v-else class="h-3.5 w-3.5 shrink-0" />
                      <span class="max-w-[120px] truncate">{{ att.name }}</span>
                      <span
                        v-if="att.scan_status && SCAN_META[att.scan_status]"
                        class="text-xs font-medium"
                        :class="SCAN_META[att.scan_status]?.cls"
                      >{{ SCAN_META[att.scan_status]?.label }}</span>
                    </a>
                  </div>

                  <!-- Bubble footer: timestamp + audience chip + mod status -->
                  <div class="mt-1 flex flex-wrap items-center justify-end gap-2">
                    <!-- Audience chip (skip for internal — already badged above) -->
                    <span
                      v-if="audienceLabel(msg) && !msg.is_internal"
                      class="rounded-full px-2 py-0.5 text-xs font-medium"
                      :class="audienceChipClass(msg)"
                    >{{ audienceLabel(msg) }}</span>
                    <!-- Moderation status pill -->
                    <span
                      v-if="msg.moderation_status && MOD_STATUS_META[msg.moderation_status]"
                      class="rounded-full px-2 py-0.5 text-xs font-semibold"
                      :class="MOD_STATUS_META[msg.moderation_status]?.cls"
                    >{{ MOD_STATUS_META[msg.moderation_status]?.label }}</span>
                    <p
                      class="text-xs"
                      :class="group.isOwn && !msg.is_internal && !msg.moderation_status ? 'text-white/60' : 'text-slate-400'"
                    >
                      {{ dateLabel(msg.created_at) }}
                      <span v-if="msg.is_edited"> · edited</span>
                    </p>
                  </div>
                </div>

                <!-- Moderation actions (staff only, held/blocked messages) -->
                <div
                  v-if="isStaff && (msg.moderation_status === 'held' || msg.moderation_status === 'blocked')"
                  class="mt-1.5 flex items-center gap-1.5"
                  :class="group.isOwn ? 'justify-end' : ''"
                >
                  <button
                    type="button"
                    class="focus-ring inline-flex items-center gap-1 rounded-md border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                    @click="moderateMsg(msg.id, 'approve')"
                  >
                    <ShieldCheck class="h-3 w-3" />
                    Approve
                  </button>
                  <button
                    type="button"
                    class="focus-ring inline-flex items-center gap-1 rounded-md border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700 hover:bg-red-100"
                    @click="moderateMsg(msg.id, 'reject')"
                  >
                    <ShieldOff class="h-3 w-3" />
                    Reject
                  </button>
                  <button
                    type="button"
                    class="focus-ring inline-flex items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-100"
                    @click="moderateMsg(msg.id, 'warn')"
                  >
                    <AlertTriangle class="h-3 w-3" />
                    Warn
                  </button>
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
          class="flex h-24 items-center justify-center rounded-lg border border-dashed border-slate-200 text-sm text-slate-400"
        >
          Select a thread to reply
        </div>

        <!-- Moderation threads are read-only — show notice instead of composer -->
        <div
          v-else-if="isModerationThread"
          class="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          <Lock class="h-4 w-4 shrink-0" />
          Moderation threads are read-only. Use the Approve / Reject / Warn buttons on flagged messages above.
        </div>

        <form v-else class="flex flex-col gap-3" @submit.prevent="sendMessage">
          <!-- ── Recipient selector ──────────────────────────────────────── -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-medium text-graphite">To:</span>

            <template v-if="availableRecipients.length">
              <button
                v-for="option in availableRecipients"
                :key="option.value"
                type="button"
                class="focus-ring inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-colors"
                :class="selectedRecipient === option.value
                  ? roleStyle(option.value).activeBadge
                  : `${roleStyle(option.value).badge} opacity-60 hover:opacity-100`"
                @click="selectedRecipient = option.value"
              >
                <Lock v-if="option.value === 'internal'" class="h-3 w-3" />
                {{ option.label }}
              </button>
            </template>

            <span v-else class="text-xs text-slate-400">No recipients available</span>

            <!-- Sender identity -->
            <span class="ml-auto text-xs text-graphite">
              From:
              <span
                class="ml-1 rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                :class="roleStyle(role).badge"
              >{{ role }}</span>
            </span>
          </div>

          <!-- Internal note hint -->
          <p v-if="selectedRecipient === 'internal'" class="text-xs text-slate-500">
            This message will only be visible to staff — clients and writers will not see it.
          </p>

          <!-- Attachment previews -->
          <div v-if="attachments.length" class="flex flex-wrap gap-2">
            <div
              v-for="(att, i) in attachments"
              :key="i"
              class="group relative flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-graphite"
            >
              <!-- Thumbnail or file icon -->
              <img
                v-if="att.isImage"
                :src="att.dataUrl"
                :alt="att.name"
                class="h-8 w-8 rounded object-cover"
              />
              <FileText v-else class="h-4 w-4 shrink-0 text-slate-400" />
              <div class="min-w-0">
                <p class="max-w-[120px] truncate font-medium text-ink">{{ att.name }}</p>
                <p class="text-slate-400">{{ formatFileSize(att.size) }}</p>
              </div>
              <button
                type="button"
                class="ml-1 rounded-full p-0.5 text-slate-400 hover:text-rose-500"
                @click="removeAttachment(i)"
              >
                <X class="h-3 w-3" />
              </button>
            </div>
          </div>

          <!-- Textarea + send button -->
          <div class="flex items-end gap-2">
            <div class="relative flex-1">
              <textarea
                v-model.trim="composer"
                class="focus-ring min-h-[80px] w-full resize-none rounded-lg border border-slate-200 px-4 py-3 pr-10 text-sm leading-6 placeholder:text-slate-400"
                :class="selectedRecipient === 'internal' ? 'bg-slate-50' : ''"
                placeholder="Write a message…"
                @keydown.enter.exact.prevent="sendMessage"
              />
              <!-- Attach button inside textarea -->
              <button
                type="button"
                class="absolute bottom-2.5 right-2.5 rounded-md p-1 text-slate-400 hover:text-signal disabled:opacity-40"
                :disabled="attachments.length >= MAX_FILES"
                :title="attachments.length >= MAX_FILES ? `Max ${MAX_FILES} files` : 'Attach files'"
                @click="openFilePicker"
              >
                <Paperclip class="h-4 w-4" />
              </button>
            </div>
            <button
              class="focus-ring mb-0.5 inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white disabled:opacity-50"
              :class="selectedRecipient === 'internal' ? 'bg-slate-500' : 'bg-signal'"
              type="submit"
              :disabled="comms.isSending || (!composer && !attachments.length) || !selectedRecipient"
              :title="comms.isSending ? 'Sending…' : 'Send (Enter)'"
            >
              <Loader2 v-if="comms.isSending" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
            </button>
          </div>
          <p class="text-right text-xs text-slate-400">Enter to send · Shift+Enter for new line · Max 5 files, 10MB each</p>

          <!-- Hidden file input -->
          <input
            ref="fileInputEl"
            type="file"
            multiple
            accept="image/*,.pdf,.doc,.docx,.txt,.xlsx,.pptx,.zip"
            class="hidden"
            @change="handleFilePick"
          />
        </form>
      </div>
    </main>

    <!-- ── Staff right panel ───────────────────────────────────────────────── -->
    <aside
      v-if="isStaff && showRightPanel && comms.activeThread"
      class="hidden flex-col gap-4 overflow-y-auto xl:flex"
    >
      <!-- Thread overview -->
      <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-2 border-b border-slate-200 px-4 py-3">
          <Info class="h-3.5 w-3.5 shrink-0 text-signal" />
          <h3 class="text-xs font-semibold uppercase tracking-wide text-graphite">Thread info</h3>
        </div>
        <dl class="divide-y divide-slate-100 text-xs">
          <div class="flex items-start justify-between gap-2 px-4 py-2.5">
            <dt class="text-graphite">Kind</dt>
            <dd class="font-medium text-ink capitalize">{{ kindLabel(comms.activeThread.kind) }}</dd>
          </div>
          <div class="flex items-start justify-between gap-2 px-4 py-2.5">
            <dt class="text-graphite">Status</dt>
            <dd>
              <span
                class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                :class="comms.activeThread.status === 'open' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'"
              >{{ comms.activeThread.status }}</span>
            </dd>
          </div>
          <div class="flex items-start justify-between gap-2 px-4 py-2.5">
            <dt class="text-graphite">Order</dt>
            <dd class="font-medium text-ink">#{{ comms.activeThread.target_id }}</dd>
          </div>
          <div class="flex items-start justify-between gap-2 px-4 py-2.5">
            <dt class="text-graphite">Created</dt>
            <dd class="text-ink">{{ dateLabel(comms.activeThread.created_at) }}</dd>
          </div>
        </dl>
      </div>

      <!-- Participants & visibility -->
      <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-2 border-b border-slate-200 px-4 py-3">
          <Users class="h-3.5 w-3.5 shrink-0 text-signal" />
          <h3 class="text-xs font-semibold uppercase tracking-wide text-graphite">Visibility</h3>
        </div>
        <div class="px-4 py-3 space-y-2">
          <p class="text-xs text-graphite">Participants</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="p in threadParticipants(comms.activeThread)"
              :key="p"
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="roleStyle(p).badge"
            >{{ roleStyle(p).label }}</span>
          </div>
          <p class="pt-1 text-xs text-graphite">Access restricted to</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="r in (THREAD_ROLE_ACCESS[comms.activeThread.kind] ?? ['all roles'])"
              :key="r"
              class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium capitalize text-slate-600"
            >{{ r }}</span>
          </div>
        </div>
      </div>

      <!-- Flags summary (only shown when messages have flags) -->
      <div v-if="flagsSummary.length" class="overflow-hidden rounded-lg border border-amber-200 bg-white">
        <div class="flex items-center gap-2 border-b border-amber-200 bg-amber-50 px-4 py-3">
          <AlertTriangle class="h-3.5 w-3.5 shrink-0 text-amber-600" />
          <h3 class="text-xs font-semibold uppercase tracking-wide text-amber-700">Flags detected</h3>
        </div>
        <ul class="divide-y divide-slate-100 text-xs">
          <li
            v-for="entry in flagsSummary"
            :key="entry.flag"
            class="flex items-center justify-between gap-2 px-4 py-2.5"
          >
            <span class="rounded-full px-2 py-0.5 font-semibold" :class="entry.cls">{{ entry.label }}</span>
            <span class="font-medium text-ink">{{ entry.count }} msg{{ entry.count !== 1 ? 's' : '' }}</span>
          </li>
        </ul>
      </div>

      <!-- Audit log (moderation actions taken this session) -->
      <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-2 border-b border-slate-200 px-4 py-3">
          <ClipboardList class="h-3.5 w-3.5 shrink-0 text-signal" />
          <h3 class="text-xs font-semibold uppercase tracking-wide text-graphite">Audit log</h3>
        </div>
        <div v-if="!auditLog.length" class="px-4 py-4 text-center text-xs text-slate-400">
          No actions taken yet.
        </div>
        <ul v-else class="divide-y divide-slate-100 text-xs">
          <li
            v-for="(entry, i) in auditLog"
            :key="i"
            class="px-4 py-2.5"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="font-semibold" :class="auditActionClass[entry.action]">
                {{ auditActionLabel[entry.action] }}
              </span>
              <span class="text-slate-400">msg #{{ entry.messageId }}</span>
            </div>
            <p class="mt-0.5 text-slate-400">{{ dateLabel(entry.at) }}</p>
          </li>
        </ul>
      </div>
    </aside>
  </section>
</template>
