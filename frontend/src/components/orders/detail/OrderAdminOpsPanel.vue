<script setup lang="ts">
import { ref, computed } from "vue";
import { Send } from "@lucide/vue";
import { useOrderOpsStore } from "@/stores/orderOps";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  orderId: number;
  role: UserRole;
}>();

const ops = useOrderOpsStore();
const auth = useAuthStore();

const writerId = ref("");
const note = ref("");

const canAct = computed(
  () => props.role === "admin" || props.role === "superadmin",
);
const needsNote = computed(() => note.value.trim().length >= 10);

async function run(action: () => Promise<unknown>) {
  try { await action(); note.value = ""; writerId.value = ""; }
  catch { /* errors surface via ops.error */ }
}
</script>

<template>
  <div v-if="canAct" class="rounded-lg border border-slate-200 bg-slate-50 p-4">
    <div class="mb-3 flex items-center gap-2">
      <Send class="h-3.5 w-3.5 text-signal" />
      <h3 class="text-sm font-semibold text-ink">Order flow controls</h3>
    </div>

    <div v-if="ops.notice" class="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
      {{ ops.notice }}
    </div>
    <div v-if="ops.error" class="mb-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
      {{ ops.error }}
    </div>

    <div class="grid gap-3 sm:grid-cols-2">
      <div>
        <label class="block text-xs font-medium text-graphite mb-1">Writer ID (for direct assign)</label>
        <input
          v-model.trim="writerId"
          inputmode="numeric"
          placeholder="e.g. 42"
          class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
        />
      </div>
      <div>
        <label class="block text-xs font-medium text-graphite mb-1">Operational note (≥10 chars for actions that need one)</label>
        <input
          v-model.trim="note"
          placeholder="Required for return / revision / cancel"
          class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
        />
      </div>
    </div>

    <div class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
      <button
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="ops.isMutating"
        @click="run(() => ops.routeToStaffing(orderId))"
      >Route to staffing</button>

      <button
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="ops.isMutating || !Number(writerId)"
        @click="run(() => ops.assignDirect(orderId, Number(writerId), note))"
      >Assign writer</button>

      <button
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="ops.isMutating"
        @click="run(() => ops.releaseToPool(orderId, note))"
      >Release to pool</button>

      <button
        class="focus-ring h-9 rounded-md border border-emerald-200 bg-white px-3 text-xs font-semibold text-emerald-800 disabled:opacity-50"
        :disabled="ops.isMutating"
        @click="run(() => ops.approveForDelivery(orderId, note))"
      >Approve delivery</button>

      <button
        class="focus-ring h-9 rounded-md border border-amber-200 bg-white px-3 text-xs font-semibold text-amber-900 disabled:opacity-50"
        :disabled="ops.isMutating || !needsNote"
        @click="run(() => ops.returnToWriter(orderId, note))"
      >Return to writer</button>

      <button
        class="focus-ring h-9 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-800 disabled:opacity-50"
        :disabled="ops.isMutating || !needsNote"
        @click="run(() => ops.cancel(orderId, note))"
      >Cancel order</button>
    </div>
  </div>
</template>
