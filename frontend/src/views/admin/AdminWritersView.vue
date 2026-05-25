<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import { AlertTriangle, RefreshCw, ShieldOff, UserCheck, Users } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminWritersStore } from "@/stores/adminWriters";

const writers = useAdminWritersStore();
const actionForm = reactive({
  reason: "Staff review action from writer operations console.",
});

const selected = computed(() => writers.selectedWriter);

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function riskTone(writer: {
  is_suspended?: boolean;
  is_on_probation?: boolean;
  active_strike_count?: number;
}) {
  if (writer.is_suspended || (writer.active_strike_count ?? 0) >= 2) return "danger";
  if (writer.is_on_probation || (writer.active_strike_count ?? 0) > 0) return "warning";
  return "success";
}

onMounted(() => {
  writers.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Writers</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Writer roster, verification, capacity, and discipline controls.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="writers.isLoading"
        @click="writers.hydrate()"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="writers.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ writers.error }}
    </div>
    <div v-if="writers.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ writers.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
        <p class="text-sm font-medium text-graphite">Roster</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ writers.writers.length }}</p>
        <p class="mt-2 text-sm text-graphite">{{ writers.activeWriters.length }} active profiles</p>
      </div>
      <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4 shadow-panel">
        <p class="text-sm font-medium text-emerald-900">Verified</p>
        <p class="mt-3 text-3xl font-semibold text-emerald-950">{{ writers.verifiedWriters.length }}</p>
        <p class="mt-2 text-sm text-emerald-900">Ready for assignment</p>
      </div>
      <div class="rounded-md border border-amber-200 bg-amber-50 p-4 shadow-panel">
        <p class="text-sm font-medium text-amber-900">Risk watch</p>
        <p class="mt-3 text-3xl font-semibold text-amber-950">{{ writers.riskWriters.length }}</p>
        <p class="mt-2 text-sm text-amber-900">Discipline or capacity flags</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
        <p class="text-sm font-medium text-graphite">Selected</p>
        <p class="mt-3 text-xl font-semibold text-ink">{{ selected?.pen_name || "None" }}</p>
        <p class="mt-2 text-sm text-graphite">{{ selected?.registration_id || "Choose a writer" }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_420px]">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-ink">Writer roster</h2>
            <p class="mt-1 text-sm text-graphite">Filter and inspect platform writers.</p>
          </div>
          <form class="flex gap-2" @submit.prevent="writers.hydrate()">
            <input
              v-model.trim="writers.query"
              class="focus-ring h-10 rounded-md border border-slate-300 px-3 text-sm"
              placeholder="Search writers"
            />
            <button class="focus-ring rounded-md bg-ink px-4 text-sm font-semibold text-white" type="submit">
              Search
            </button>
          </form>
        </div>

        <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
          <div class="grid grid-cols-[1fr_120px_140px_120px_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Writer</span>
            <span>Level</span>
            <span>Verification</span>
            <span>Risk</span>
            <span class="text-right">Action</span>
          </div>
          <div v-if="writers.isLoading" class="px-4 py-6 text-sm text-graphite">Loading writers...</div>
          <div v-else-if="!writers.writers.length" class="px-4 py-6 text-sm text-graphite">No writers loaded.</div>
          <button
            v-for="writer in writers.writers"
            v-else
            :key="writer.registration_id"
            class="focus-ring grid w-full grid-cols-[1fr_120px_140px_120px_auto] items-center gap-3 border-t border-slate-100 px-4 py-3 text-left text-sm hover:bg-slate-50"
            :class="writer.registration_id === selected?.registration_id ? 'bg-slate-50' : 'bg-white'"
            type="button"
            @click="writers.selectWriter(writer.registration_id)"
          >
            <div>
              <p class="font-semibold text-ink">{{ writer.pen_name || writer.full_name || writer.registration_id }}</p>
              <p class="mt-1 text-xs text-graphite">{{ writer.full_name || writer.registration_id }} · joined {{ dateLabel(writer.joined_at) }}</p>
            </div>
            <span class="text-graphite">{{ writer.level_name || "Unleveled" }}</span>
            <StatusPill :label="writer.verification_status" :tone="writer.is_verified ? 'success' : 'warning'" />
            <StatusPill :label="(writer as any).is_suspended ? 'suspended' : (writer as any).is_on_probation ? 'probation' : 'clear'" :tone="riskTone(writer as any)" />
            <span class="text-right text-xs font-semibold text-signal">Inspect</span>
          </button>
        </div>
      </div>

      <aside class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">{{ selected?.pen_name || "Writer detail" }}</h2>
            <p class="mt-1 text-sm text-graphite">{{ selected?.email || "Select a writer from the roster" }}</p>
          </div>
          <UserCheck class="h-5 w-5 text-signal" />
        </div>

        <template v-if="selected">
          <div class="mt-5 grid grid-cols-2 gap-3">
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs text-graphite">Capacity</p>
              <p class="mt-1 font-semibold text-ink">{{ selected.active_orders_count ?? 0 }} active</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs text-graphite">Availability</p>
              <p class="mt-1 font-semibold text-ink">{{ selected.is_accepting_orders ? "Accepting" : "Paused" }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs text-graphite">Warnings</p>
              <p class="mt-1 font-semibold text-ink">{{ writers.discipline?.active_warning_count ?? selected.active_warning_count ?? 0 }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs text-graphite">Strikes</p>
              <p class="mt-1 font-semibold text-ink">{{ writers.discipline?.active_strike_count ?? selected.active_strike_count ?? 0 }}</p>
            </div>
          </div>

          <div class="mt-5 space-y-2 rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2">
              <AlertTriangle class="h-4 w-4 text-saffron" />
              <p class="text-sm font-semibold text-ink">Discipline state</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <StatusPill :label="writers.discipline?.is_suspended ? 'suspended' : 'not suspended'" :tone="writers.discipline?.is_suspended ? 'danger' : 'success'" />
              <StatusPill :label="writers.discipline?.is_on_probation ? 'probation' : 'no probation'" :tone="writers.discipline?.is_on_probation ? 'warning' : 'success'" />
              <StatusPill :label="writers.discipline?.is_blacklisted ? 'blacklisted' : 'not blacklisted'" :tone="writers.discipline?.is_blacklisted ? 'danger' : 'success'" />
            </div>
            <p class="text-xs text-graphite">
              Last event: {{ dateLabel(writers.discipline?.last_discipline_event_at) }}
            </p>
          </div>

          <label class="mt-5 block text-sm font-medium text-ink">
            Action reason
            <textarea
              v-model.trim="actionForm.reason"
              class="focus-ring mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </label>

          <div class="mt-4 grid gap-2">
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-amber-300 px-4 py-3 text-sm font-semibold text-amber-900 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="writers.isMutating || actionForm.reason.length < 10"
              @click="writers.issueWarning(actionForm.reason)"
            >
              <AlertTriangle class="h-4 w-4" />
              Issue warning
            </button>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-3 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="writers.isMutating || actionForm.reason.length < 10"
              @click="writers.toggleSuspension(actionForm.reason)"
            >
              <ShieldOff class="h-4 w-4" />
              {{ selected.is_suspended ? "Lift suspension" : "Suspend writer" }}
            </button>
            <button
              class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-rose-300 px-4 py-3 text-sm font-semibold text-rose-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="writers.isMutating || actionForm.reason.length < 10"
              @click="writers.toggleDeleted(actionForm.reason)"
            >
              <Users class="h-4 w-4" />
              {{ selected.is_deleted ? "Restore writer" : "Remove writer" }}
            </button>
          </div>
        </template>
      </aside>
    </section>
  </div>
</template>
