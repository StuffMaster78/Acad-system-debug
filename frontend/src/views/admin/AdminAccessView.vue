<script setup lang="ts">
import { computed, onMounted } from "vue";
import {
  Ban,
  CheckCircle2,
  Fingerprint,
  KeyRound,
  LogOut,
  RefreshCw,
  Search,
  ShieldCheck,
  ShieldOff,
  UserPlus,
  UserCog,
  UsersRound,
} from "@lucide/vue";
import BaseDataTable, { type DataTableColumn } from "@/components/ui/BaseDataTable.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminAccessStore } from "@/stores/adminAccess";
import type { UserRole } from "@/types/roles";

const access = useAdminAccessStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filters = [
  { key: "all", label: "All" },
  { key: "client", label: "Clients" },
  { key: "writer", label: "Writers" },
  { key: "editor", label: "Editors" },
  { key: "support", label: "Support" },
  { key: "admin", label: "Admins" },
  { key: "suspended", label: "Suspended" },
  { key: "blacklisted", label: "Blacklisted" },
] as const;

const roleOptions: UserRole[] = ["client", "writer", "editor", "support", "admin"];

const userColumns: DataTableColumn[] = [
  { key: "id", label: "User", sortable: true },
  { key: "role", label: "Role", sortable: true },
  { key: "website", label: "Website" },
  { key: "last_login", label: "Last login", sortable: true },
  { key: "status", label: "Status" },
];

const rows = computed(() =>
  access.filteredUsers.map((user) => ({
    ...user,
    status: user.is_blacklisted ? "blacklisted" : user.is_suspended ? "suspended" : user.is_active ? "active" : "inactive",
  })) as unknown as Record<string, unknown>[],
);

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(status?: string | null) {
  if (status === "blacklisted" || status === "suspended") return "danger";
  if (status === "inactive") return "warning";
  return "success";
}

function roleTone(role?: string | null) {
  if (role === "admin" || role === "superadmin") return "warning";
  if (role === "support" || role === "editor") return "neutral";
  return "success";
}

function selectUser(row: Record<string, unknown>) {
  const id = Number(row.id);
  if (!Number.isNaN(id)) access.selectedUserId = id;
}

onMounted(() => {
  access.hydrate().catch(() => undefined);
  access.hydrateLifecycle().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin security</p>
        <h1 class="mt-2 text-3xl font-semibold">Access control</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Manage users, roles, account restrictions, lockouts, sessions, and impersonation workflows from one operator console.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="access.isLoading"
        @click="access.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="access.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ access.error }} Preview mode will still show the access workflow.
    </p>

    <p
      v-if="access.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ access.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in access.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.85fr)]">
      <div class="rounded-md border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex items-center gap-2">
            <UsersRound class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold">User directory</h2>
              <p class="text-sm text-graphite">Search by account, role, website, or risk state.</p>
            </div>
          </div>

          <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div class="flex max-w-full gap-1 overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                v-for="option in filters"
                :key="option.key"
                class="focus-ring min-h-9 shrink-0 rounded px-3 text-xs font-semibold"
                :class="access.filter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
                type="button"
                @click="access.filter = option.key"
              >
                {{ option.label }}
              </button>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="access.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search users"
              >
            </label>
          </div>
        </div>

        <div v-if="access.isLoading" class="p-6">
          <LoadingSpinner label="Loading users" />
        </div>
        <BaseDataTable
          v-else
          :columns="userColumns"
          :rows="rows"
          :searchable="false"
          empty-title="No users found"
          empty-message="Users will appear here when the backend user-management endpoint responds."
        >
          <template #cell-id="{ row }">
            <button
              class="focus-ring rounded text-left font-semibold text-signal"
              type="button"
              @click="selectUser(row)"
            >
              {{ row.full_name || row.username }}
            </button>
            <p class="mt-1 text-xs text-graphite">{{ row.email }}</p>
            <p class="mt-1 text-xs text-graphite">#{{ row.id }} · @{{ row.username }}</p>
          </template>
          <template #cell-role="{ value }">
            <StatusPill :label="`${value}`" :tone="roleTone(value as string)" />
          </template>
          <template #cell-website="{ row }">
            <p class="font-medium text-ink">{{ (row.website as any)?.name || row.website_name || "No website" }}</p>
            <p class="mt-1 text-xs text-graphite">{{ (row.website as any)?.domain || "Tenant context pending" }}</p>
          </template>
          <template #cell-last_login="{ value }">{{ formatDate(value as string) }}</template>
          <template #cell-status="{ value, row }">
            <div class="flex flex-wrap gap-2">
              <StatusPill :label="`${value}`" :tone="statusTone(value as string)" />
              <StatusPill
                v-if="row.is_on_probation"
                label="probation"
                tone="warning"
              />
            </div>
          </template>
        </BaseDataTable>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <UserCog class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Selected account</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Role, restriction, and session controls.</p>
          </div>

          <template v-if="access.selectedUser">
            <div class="space-y-4 p-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ access.selectedUser.full_name || access.selectedUser.username }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ access.selectedUser.email }}</p>
                  <p class="mt-1 text-xs text-graphite">Joined {{ formatDate(access.selectedUser.date_joined) }}</p>
                </div>
                <StatusPill :label="access.selectedUser.role" :tone="roleTone(access.selectedUser.role)" />
              </div>

              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Action reason</span>
                <textarea
                  v-model="access.reason"
                  class="focus-ring mt-1 min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                />
              </label>

              <div class="grid gap-2 sm:grid-cols-2">
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('suspend').catch(() => undefined)"
                >
                  <ShieldOff class="h-4 w-4" />
                  Suspend
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 text-sm font-semibold text-emerald-900 disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('unsuspend').catch(() => undefined)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Unsuspend
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('unlock').catch(() => undefined)"
                >
                  <ShieldCheck class="h-4 w-4" />
                  Unlock
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('kickout').catch(() => undefined)"
                >
                  <LogOut class="h-4 w-4" />
                  Kick out
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('reset').catch(() => undefined)"
                >
                  <KeyRound class="h-4 w-4" />
                  Reset password
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('promote').catch(() => undefined)"
                >
                  <Ban class="h-4 w-4" />
                  Promote admin
                </button>
              </div>

              <div class="rounded-md border border-slate-200 p-3">
                <label class="block">
                  <span class="text-xs font-semibold uppercase text-graphite">Change role</span>
                  <select
                    v-model="access.newRole"
                    class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  >
                    <option
                      v-for="role in roleOptions"
                      :key="role"
                      :value="role"
                    >
                      {{ role }}
                    </option>
                  </select>
                </label>
                <button
                  class="focus-ring mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white disabled:opacity-60"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.runUserAction('role').catch(() => undefined)"
                >
                  Apply role
                </button>
              </div>
            </div>
          </template>

          <div v-else class="p-4">
            <EmptyState
              :icon="UsersRound"
              title="Select a user"
              message="Choose a user to manage account access."
            />
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <KeyRound class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Impersonation</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Generate a short-lived token before starting a support session.</p>
          </div>
          <div class="space-y-4 p-4">
            <div class="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-950">
              Use only for support, QA, or account rescue. Actions remain audit-sensitive and should include a clear reason.
            </div>
            <button
              class="focus-ring inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="access.isMutating || !access.selectedUser"
              @click="access.createImpersonationToken().catch(() => undefined)"
            >
              Generate token
            </button>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Token</span>
              <input
                v-model="access.generatedToken"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <button
              class="focus-ring inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-signal px-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="access.isMutating || !access.generatedToken"
              @click="access.startImpersonation().catch(() => undefined)"
            >
              Start impersonation
            </button>
          </div>
        </section>
      </aside>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(360px,0.8fr)_minmax(0,1.2fr)]">
      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <UserPlus class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Create user</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Create client, writer, editor, support, or staff accounts. Admin roles remain superadmin-sensitive in the backend.
          </p>
          <div class="mt-4 space-y-3">
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">First name</span>
                <input
                  v-model="access.createUserForm.first_name"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Last name</span>
                <input
                  v-model="access.createUserForm.last_name"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Username</span>
              <input
                v-model="access.createUserForm.username"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Email</span>
              <input
                v-model="access.createUserForm.email"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="email"
              >
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Role</span>
                <select
                  v-model="access.createUserForm.role"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >
                  <option
                    v-for="role in roleOptions"
                    :key="role"
                    :value="role"
                  >
                    {{ role }}
                  </option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Website ID</span>
                <input
                  v-model.number="access.createUserForm.website"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  placeholder="Current website"
                  type="number"
                >
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Password</span>
              <input
                v-model="access.createUserForm.password"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                placeholder="Leave empty if backend generates one"
                type="password"
              >
            </label>
          </div>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="access.isMutating"
            @click="access.createUser().catch(() => undefined)"
          >
            <UserPlus class="h-4 w-4" />
            Create user
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Ban class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Email blacklist</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Block risky emails before they register again. This is separate from suspending an existing account.
          </p>
          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Email</span>
              <input
                v-model="access.blacklistForm.email"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="email"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Reason</span>
              <textarea
                v-model="access.blacklistForm.reason"
                class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </label>
          </div>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-4 text-sm font-semibold text-rose-700 disabled:opacity-60"
            type="button"
            :disabled="access.isMutating"
            @click="access.addBlacklistedEmail().catch(() => undefined)"
          >
            <Ban class="h-4 w-4" />
            Add blacklist
          </button>
        </section>
      </aside>

      <div class="space-y-4">
        <section class="grid gap-4 sm:grid-cols-3">
          <div
            v-for="metric in access.lifecycleMetrics"
            :key="metric.label"
            class="min-h-28 rounded-md border p-4"
            :class="metricToneClasses[metric.tone]"
          >
            <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ metric.value }}</p>
            <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div class="flex items-center gap-2">
              <Fingerprint class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Duplicate account review</h2>
                <p class="text-sm text-graphite">Signals from email, IP, names, and cross-website patterns.</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <select
                v-model="access.duplicateFilters.role"
                class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option value="">All roles</option>
                <option value="client">Clients</option>
                <option value="writer">Writers</option>
              </select>
              <select
                v-model="access.duplicateFilters.min_confidence"
                class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option value="low">Low+</option>
                <option value="medium">Medium+</option>
                <option value="high">High</option>
              </select>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
                type="button"
                @click="access.hydrateLifecycle().catch(() => undefined)"
              >
                <RefreshCw class="h-4 w-4" />
                Scan
              </button>
            </div>
          </div>

          <div class="mt-4 space-y-3">
            <article
              v-for="group in access.duplicateGroups"
              :key="group.user_ids.join('-')"
              class="rounded-md border border-slate-200 bg-slate-50 p-3"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p class="text-sm font-semibold text-ink">{{ group.user_ids.length }} linked accounts</p>
                  <p class="mt-1 text-xs text-graphite">
                    {{ Array.isArray(group.signals) ? group.signals.join(', ') : JSON.stringify(group.signals) }}
                  </p>
                </div>
                <StatusPill :label="group.confidence" :tone="group.confidence === 'high' ? 'danger' : group.confidence === 'medium' ? 'warning' : 'neutral'" />
              </div>
              <div class="mt-3 grid gap-2 md:grid-cols-2">
                <button
                  v-for="user in group.users"
                  :key="user.id"
                  class="focus-ring rounded-md border border-slate-200 bg-white p-3 text-left"
                  type="button"
                  @click="access.selectedUserId = user.id"
                >
                  <p class="text-sm font-semibold text-signal">{{ user.email }}</p>
                  <p class="mt-1 text-xs text-graphite">#{{ user.id }} · {{ user.role }} · {{ user.website?.name || 'No website' }}</p>
                </button>
              </div>
            </article>
            <EmptyState
              v-if="!access.duplicateGroups.length"
              :icon="Fingerprint"
              title="No duplicate groups"
              message="Run a scan or lower the confidence threshold."
            />
          </div>
        </section>

        <section class="grid gap-6 xl:grid-cols-2">
          <section class="rounded-md border border-slate-200 bg-white p-4">
            <h2 class="text-base font-semibold">Profile update requests</h2>
            <div class="mt-4 space-y-3">
              <article
                v-for="request in access.profileUpdateRequests.slice(0, 6)"
                :key="request.id"
                class="rounded-md border border-slate-200 bg-slate-50 p-3"
              >
                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm font-semibold text-ink">Request #{{ request.id }}</p>
                  <StatusPill :label="request.status || 'pending'" :tone="request.status === 'rejected' ? 'danger' : request.status === 'approved' ? 'success' : 'warning'" />
                </div>
                <p class="mt-2 text-xs leading-5 text-graphite">
                  {{ JSON.stringify(request.requested_changes || request.changes || {}).slice(0, 180) }}
                </p>
              </article>
              <EmptyState
                v-if="!access.profileUpdateRequests.length"
                :icon="UserCog"
                title="No profile requests"
                message="Profile update approvals will appear here."
              />
            </div>
          </section>

          <section class="rounded-md border border-slate-200 bg-white p-4">
            <h2 class="text-base font-semibold">Blacklisted emails</h2>
            <div class="mt-4 space-y-3">
              <article
                v-for="item in access.blacklistedEmails.slice(0, 8)"
                :key="item.id ?? item.email"
                class="flex items-start justify-between gap-3 rounded-md border border-slate-200 bg-slate-50 p-3"
              >
                <div>
                  <p class="text-sm font-semibold text-ink">{{ item.email }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ item.reason || 'No reason recorded' }}</p>
                </div>
                <button
                  class="focus-ring inline-flex h-8 items-center rounded-md border border-slate-200 bg-white px-2 text-xs font-semibold"
                  type="button"
                  :disabled="access.isMutating"
                  @click="access.removeBlacklistedEmail(item.email).catch(() => undefined)"
                >
                  Remove
                </button>
              </article>
              <EmptyState
                v-if="!access.blacklistedEmails.length"
                :icon="Ban"
                title="No blacklisted emails"
                message="Emails added to the blacklist will appear here."
              />
            </div>
          </section>
        </section>
      </div>
    </section>
  </div>
</template>
