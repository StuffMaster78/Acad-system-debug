<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeft, Activity, BadgeCheck, CreditCard, Globe,
  Mail, Shield, ShieldOff, Star, User, Wallet,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminClientsStore } from "@/stores/adminClients";
import { useAuthStore } from "@/stores/auth";
import type { AdminClient } from "@/types/adminClients";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const clientsStore = useAdminClientsStore();

const clientId = computed(() => Number(route.params.id));
const loading = ref(false);
const notice = ref("");
const error = ref("");

const isSuperadmin = computed(
  () => auth.role === "superadmin",
);

const client = computed<AdminClient | null>(
  () => clientsStore.clients.find((c) => c.id === clientId.value) ?? null,
);

onMounted(async () => {
  if (!clientsStore.clients.length) {
    loading.value = true;
    await clientsStore.hydrate().catch(() => undefined);
    loading.value = false;
  }
});

function fmt(v: string | null | undefined) {
  return v || "—";
}

function fmtDate(v: string | null | undefined) {
  if (!v) return "—";
  return new Date(v).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function money(v: string | number | null | undefined) {
  if (v == null || v === "") return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(v));
}

function goBack() {
  const prefix = isSuperadmin.value ? "/superadmin" : "/admin";
  router.push(`${prefix}/clients`);
}

async function doAction(action: "activate" | "suspend" | "deactivate") {
  notice.value = "";
  error.value = "";
  try {
    clientsStore.selectedClient = client.value;
    await clientsStore.runClientAction(action);
    notice.value = `Client ${action}d successfully.`;
  } catch {
    error.value = `Failed to ${action} client.`;
  }
}

async function doResetPassword() {
  notice.value = "";
  error.value = "";
  try {
    clientsStore.selectedClient = client.value;
    await clientsStore.resetPassword();
    notice.value = "Password reset email sent.";
  } catch {
    error.value = "Failed to reset password.";
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Back -->
    <button
      class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink"
      @click="goBack"
    >
      <ArrowLeft class="h-3.5 w-3.5" />
      Back to clients
    </button>

    <div v-if="loading" class="py-16 text-center text-graphite animate-pulse">Loading client…</div>

    <div v-else-if="!client" class="py-16 text-center">
      <p class="text-graphite">Client not found. The list may not be loaded yet.</p>
      <button class="mt-3 text-sm text-signal underline" @click="clientsStore.hydrate().catch(() => undefined)">Retry</button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-berry/10">
              <User class="h-6 w-6 text-berry" />
            </div>
            <div>
              <h1 class="text-lg font-semibold text-ink">{{ client.fullName || client.username }}</h1>
              <p class="text-sm text-graphite">{{ client.email }}</p>
              <div class="mt-1 flex flex-wrap gap-1.5">
                <StatusPill :label="client.isSuspended ? 'Suspended' : client.isActive ? 'Active' : 'Inactive'"
                  :tone="client.isSuspended ? 'danger' : client.isActive ? 'success' : 'warning'" />
                <StatusPill v-if="client.isBlacklisted" label="Blacklisted" tone="danger" />
                <StatusPill v-if="client.loyaltyTier" :label="client.loyaltyTier" tone="neutral" />
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap gap-2">
            <button
              v-if="client.isSuspended"
              class="focus-ring h-8 rounded-md border border-emerald-200 bg-emerald-50 px-3 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 disabled:opacity-60"
              :disabled="clientsStore.isMutating"
              @click="doAction('activate')"
            >Activate</button>
            <button
              v-else-if="client.isActive"
              class="focus-ring h-8 rounded-md border border-amber-200 bg-amber-50 px-3 text-xs font-semibold text-amber-900 hover:bg-amber-100 disabled:opacity-60"
              :disabled="clientsStore.isMutating"
              @click="doAction('suspend')"
            >Suspend</button>
            <button
              class="focus-ring h-8 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-60"
              :disabled="clientsStore.isMutating"
              @click="doResetPassword"
            >Reset password</button>
          </div>
        </div>

        <div v-if="notice" class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{{ notice }}</div>
        <div v-if="error" class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">{{ error }}</div>
      </div>

      <!-- Stat cards -->
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
            <Wallet class="h-3.5 w-3.5" /> Wallet balance
          </div>
          <p class="mt-2 text-2xl font-semibold text-ink">{{ money(client.walletBalance) }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
            <CreditCard class="h-3.5 w-3.5" /> Total spent
          </div>
          <p class="mt-2 text-2xl font-semibold text-ink">{{ money(client.totalSpent) }}</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
            <Star class="h-3.5 w-3.5" /> Loyalty points
          </div>
          <p class="mt-2 text-2xl font-semibold text-ink">{{ client.loyaltyPoints.toLocaleString() }}</p>
          <p v-if="client.loyaltyTier" class="mt-0.5 text-xs text-graphite">{{ client.loyaltyTier }} tier</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2 text-xs font-semibold uppercase text-graphite">
            <Activity class="h-3.5 w-3.5" /> Preferred writers
          </div>
          <p class="mt-2 text-2xl font-semibold text-ink">{{ client.preferredWriters?.length ?? 0 }}</p>
        </div>
      </div>

      <!-- Identity details -->
      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-lg border border-slate-200 bg-white p-5">
          <h2 class="mb-3 text-sm font-semibold uppercase text-graphite">Account details</h2>
          <dl class="space-y-2.5 text-sm">
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Mail class="h-3.5 w-3.5" />Email</dt>
              <dd class="font-medium text-ink">{{ fmt(client.email) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><User class="h-3.5 w-3.5" />Username</dt>
              <dd class="font-medium text-ink">{{ fmt(client.username) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Globe class="h-3.5 w-3.5" />Country</dt>
              <dd class="font-medium text-ink">{{ fmt(client.country) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Globe class="h-3.5 w-3.5" />Timezone</dt>
              <dd class="font-medium text-ink">{{ fmt(client.timezone) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Globe class="h-3.5 w-3.5" />Website</dt>
              <dd class="font-medium text-ink">{{ fmt(client.website) }}</dd>
            </div>
          </dl>
        </div>

        <div class="rounded-lg border border-slate-200 bg-white p-5">
          <h2 class="mb-3 text-sm font-semibold uppercase text-graphite">Activity & security</h2>
          <dl class="space-y-2.5 text-sm">
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><BadgeCheck class="h-3.5 w-3.5" />Joined</dt>
              <dd class="font-medium text-ink">{{ fmtDate(client.dateJoined) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Activity class="h-3.5 w-3.5" />Last login</dt>
              <dd class="font-medium text-ink">{{ fmtDate(client.lastLogin) }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><Shield class="h-3.5 w-3.5" />Status</dt>
              <dd>
                <StatusPill :label="client.isSuspended ? 'Suspended' : client.isActive ? 'Active' : 'Inactive'"
                  :tone="client.isSuspended ? 'danger' : client.isActive ? 'success' : 'warning'" />
              </dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="flex items-center gap-1.5 text-graphite"><ShieldOff class="h-3.5 w-3.5" />Blacklisted</dt>
              <dd>
                <StatusPill :label="client.isBlacklisted ? 'Yes' : 'No'"
                  :tone="client.isBlacklisted ? 'danger' : 'success'" />
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </template>
  </div>
</template>
