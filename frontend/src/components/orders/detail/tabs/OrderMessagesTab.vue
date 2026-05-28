<template>
  <div class="space-y-4">
    <!-- Thread header -->
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 class="text-base font-semibold text-ink">
            {{ threadLabel }}
          </h2>
          <p class="mt-0.5 text-xs text-graphite">
            {{ comms.activeThread ? `${comms.activeThread.kind} · ${comms.activeThread.status}` : "No thread loaded" }}
          </p>
        </div>
        <div class="flex gap-2">
          <button
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
            type="button"
            :disabled="comms.isLoading"
            @click="comms.loadOrderThread(orderId)"
          >
            <RefreshCw class="h-3.5 w-3.5" />
            Refresh
          </button>
          <button
            v-if="!comms.activeThread"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
            type="button"
            :disabled="comms.isLoading"
            @click="startThread"
          >
            <MessageSquare class="h-3.5 w-3.5" />
            Start thread
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div class="min-h-48 max-h-96 space-y-3 overflow-y-auto bg-slate-50 p-4">
        <p v-if="comms.isLoading" class="text-sm text-graphite">Loading messages…</p>
        <p v-else-if="!comms.activeThread" class="text-sm text-graphite">Start a thread to send messages about this order.</p>
        <p v-else-if="!comms.messages.length" class="text-sm text-graphite">No messages yet.</p>
        <article v-for="msg in comms.messages" v-else :key="msg.id" class="rounded-lg border border-slate-200 bg-white p-3">
          <div class="flex items-center justify-between gap-2">
            <!-- Masked sender display — thread participant names are resolved server-side -->
            <p class="text-xs font-semibold text-ink">{{ msg.sender_display }}</p>
            <p class="text-xs text-graphite">
              {{ msg.created_at ? fmt(msg.created_at) : "" }}
            </p>
          </div>
          <p class="mt-2 whitespace-pre-wrap text-sm leading-5 text-graphite">{{ msg.body }}</p>
          <div v-if="msg.attachments?.length" class="mt-2 flex flex-wrap gap-2">
            <span v-for="(att, i) in msg.attachments" :key="i" class="text-xs text-graphite underline">{{ att.name }}</span>
          </div>
        </article>
      </div>

      <!-- Compose -->
      <form class="border-t border-slate-200 p-4" @submit.prevent="send">
        <textarea
          v-model.trim="body"
          class="focus-ring min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          :placeholder="placeholder"
        />
        <div v-if="comms.error" class="mt-2 text-xs text-berry">{{ comms.error }}</div>
        <button
          class="focus-ring mt-2 inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          type="submit"
          :disabled="comms.isSending || !comms.activeThread || !body"
        >
          <Loader2 v-if="comms.isSending" class="h-4 w-4 animate-spin" />
          <Send v-else class="h-4 w-4" />
          Send
        </button>
      </form>
    </div>

    <!-- Staff: internal notes thread indicator -->
    <div v-if="isStaffRole" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-4">
      <p class="text-xs font-semibold text-graphite">Internal staff notes</p>
      <p class="mt-1 text-sm text-graphite">
        <!-- TODO: wire internal notes thread separately — currently uses shared thread -->
        Internal staff notes thread not yet separated. Full thread isolation requires server-side thread-type enforcement.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Loader2, MessageSquare, RefreshCw, Send } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";
import { useCommunicationsStore } from "@/stores/communications";
import { isStaff } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

const comms = useCommunicationsStore();
const isStaffRole = computed(() => isStaff(props.role));
const body = ref("");

const threadLabel = computed(() => {
  if (props.role === "writer") return "Order thread (writer)";
  if (props.role === "client") return "Order thread";
  return "Order thread";
});

const placeholder = computed(() => {
  if (props.role === "writer") return "Write a message or ask about the brief…";
  if (props.role === "client") return "Write a message about this order…";
  return "Write a message…";
});

function fmt(value: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

async function startThread() {
  await comms.createOrderThread({ orderId: props.orderId, subject: props.order.topic || `Order #${props.orderId}` });
}

async function send() {
  if (!body.value.trim()) return;
  await comms.sendMessage(body.value.trim());
  body.value = "";
}
</script>
