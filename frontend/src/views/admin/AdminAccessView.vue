<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Ban,
  ChevronLeft,
  ChevronRight,
  Fingerprint,
  RefreshCw,
  Search,
  UserPlus,
  UsersRound,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminAccessStore } from "@/stores/adminAccess";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const access = useAdminAccessStore();
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const routePrefix = computed(() => route.path.startsWith("/superadmin") ? "/superadmin" : "/admin");

const PAGE_SIZE = 20;
const page = ref(1);

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const roleFilters = computed(() => {
  const base = [
    { key: "all", label: "All" },
    { key: "client", label: "Clients" },
    { key: "writer", label: "Writers" },
    { key: "editor", label: "Editors" },
    { key: "support", label: "Support" },
    { key: "admin", label: "Admins" },
    { key: "suspended", label: "Suspended" },
    { key: "blacklisted", label: "Blacklisted" },
  ];
  if (auth.role === "superadmin") {
    base.splice(6, 0, { key: "superadmin", label: "Superadmins" });
  }
  return base;
});

const roleOptions = computed<UserRole[]>(() => {
  const base: UserRole[] = ["client", "writer", "editor", "support", "admin"];
  if (auth.role === "superadmin") base.push("superadmin");
  return base;
});

const totalPages = computed(() => Math.ceil(access.filteredUsers.length / PAGE_SIZE));
const pagedUsers = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return access.filteredUsers.slice(start, start + PAGE_SIZE);
});

function setFilter(key: string) {
  access.filter = key as typeof access.filter;
  page.value = 1;
}

function setQuery(q: string) {
  access.query = q;
  page.value = 1;
}

function formatDate(v?: string | null) {
  if (!v) return "Never";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(v));
}

function statusTone(u: { is_blacklisted?: boolean; is_suspended?: boolean; is_active?: boolean }) {
  if (u.is_blacklisted) return "danger";
  if (u.is_suspended) return "danger";
  if (!u.is_active) return "warning";
  return "success";
}

function statusLabel(u: { is_blacklisted?: boolean; is_suspended?: boolean; is_active?: boolean }) {
  if (u.is_blacklisted) return "blacklisted";
  if (u.is_suspended) return "suspended";
  if (!u.is_active) return "inactive";
  return "active";
}

function roleTone(role?: string | null) {
  if (role === "superadmin") return "danger";
  if (role === "admin") return "warning";
  if (role === "support" || role === "editor") return "neutral";
  return "success";
}

function openProfile(userId: number) {
  router.push(`${routePrefix.value}/users/${userId}`);
}

const pageTitle = computed(() => {
  const f = access.filter;
  if (f === "editor") return "Editors";
  if (f === "support") return "Support Staff";
  if (f === "writer") return "Writers";
  if (f === "client") return "Clients";
  if (f === "admin") return "Admins";
  if (f === "superadmin") return "Superadmins";
  return "User directory";
});

const pageDescription = computed(() => {
  const f = access.filter;
  if (f === "editor") return "All editor accounts. Click a row to open the full profile.";
  if (f === "support") return "All support staff accounts. Click a row to open the full profile.";
  if (f === "writer") return "All writer accounts. Click a row to open the full profile.";
  if (f === "client") return "All client accounts. Click a row to open the full profile.";
  if (f === "admin") return "All admin accounts. Click a row to open the full profile.";
  return "Browse all users across every role. Click any row to open the full profile.";
});

function applyRouteFilter() {
  const roleFilter = route.meta?.roleFilter as string | undefined;
  access.filter = (roleFilter ?? "all") as typeof access.filter;
  page.value = 1;
}

// Defensive wrapper: guards against stale HMR store instances where
// scanDuplicates may not yet exist on the cached singleton.
async function runScan() {
  if (typeof access.scanDuplicates === "function") {
    await access.scanDuplicates().catch(() => undefined);
  } else {
    // Fallback: full lifecycle re-fetch (pre-scanDuplicates behaviour)
    await access.hydrateLifecycle().catch(() => undefined);
  }
}

onMounted(() => {
  applyRouteFilter();
  access.hydrate().catch(() => undefined);
  access.hydrateLifecycle().catch(() => undefined);
});

watch(() => route.meta?.roleFilter, applyRouteFilter);
</script>

<template>
  <div class="space-y-8">

    <!-- Page header -->
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">People</p>
        <h1 class="mt-2 text-3xl font-semibold">{{ pageTitle }}</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">{{ pageDescription }}</p>
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

    <!-- Notices -->
    <p v-if="access.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ access.error }}
    </p>
    <p v-if="access.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ access.notice }}
    </p>

    <!-- Summary metrics -->
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

    <!-- User table -->
    <section class="rounded-xl border border-slate-200 bg-white">
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div class="flex items-center gap-2">
          <UsersRound class="h-5 w-5 text-signal" />
          <div>
            <h2 class="text-base font-semibold text-ink">{{ pageTitle }}</h2>
            <p class="text-xs text-graphite">{{ access.filteredUsers.length }} matching — click a row to open the full profile.</p>
          </div>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
        <div class="flex flex-wrap gap-1">
          <button
            v-for="option in roleFilters"
            :key="option.key"
            class="focus-ring h-8 shrink-0 rounded-lg px-3 text-xs font-semibold transition-colors"
            :class="access.filter === option.key ? 'bg-ink text-white shadow-sm' : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
            type="button"
            @click="setFilter(option.key)"
          >
            {{ option.label }}
          </button>
        </div>
        <label class="relative ml-auto block w-52">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            :value="access.query"
            class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
            type="search"
            placeholder="Search by name, email…"
            @input="setQuery(($event.target as HTMLInputElement).value)"
          />
        </label>
      </div>

      <!-- Loading -->
      <div v-if="access.isLoading" class="p-6">
        <LoadingSpinner label="Loading users…" />
      </div>

      <!-- Empty state -->
      <div v-else-if="!access.filteredUsers.length" class="p-8">
        <EmptyState :icon="UsersRound" title="No users found" message="Try a different filter or search term." />
      </div>

      <!-- Scrollable table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="whitespace-nowrap px-4 py-3 text-left">User</th>
              <th class="whitespace-nowrap px-4 py-3 text-left">Email</th>
              <th class="whitespace-nowrap px-4 py-3 text-left">Role</th>
              <th class="whitespace-nowrap px-4 py-3 text-left">Website</th>
              <th class="whitespace-nowrap px-4 py-3 text-left">Status</th>
              <th class="whitespace-nowrap px-4 py-3 text-left">Last active</th>
              <th class="whitespace-nowrap px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="user in pagedUsers"
              :key="user.id"
              class="cursor-pointer transition-colors hover:bg-slate-50"
              @click="openProfile(user.id)"
            >
              <td class="px-4 py-3">
                <p class="font-semibold text-ink">{{ user.full_name || user.username }}</p>
                <p class="mt-0.5 text-xs text-graphite">@{{ user.username }} · #{{ user.id }}</p>
              </td>
              <td class="px-4 py-3 text-graphite">{{ user.email }}</td>
              <td class="px-4 py-3">
                <StatusPill :label="user.role_display || user.role" :tone="roleTone(user.role)" />
              </td>
              <td class="px-4 py-3">
                <p class="font-medium text-ink">{{ user.website?.name || '—' }}</p>
                <p v-if="user.website?.domain" class="mt-0.5 text-xs text-graphite">{{ user.website.domain }}</p>
              </td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-1">
                  <StatusPill :label="statusLabel(user)" :tone="statusTone(user)" />
                  <StatusPill v-if="user.is_on_probation" label="probation" tone="warning" />
                </div>
              </td>
              <td class="px-4 py-3 text-graphite">{{ formatDate(user.last_login) }}</td>
              <td class="px-4 py-3 text-right">
                <button
                  class="focus-ring inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-signal hover:border-signal"
                  type="button"
                  @click.stop="openProfile(user.id)"
                >
                  View profile
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-slate-200 px-4 py-3">
        <p class="text-xs text-graphite">
          Page {{ page }} of {{ totalPages }} · {{ access.filteredUsers.length }} users
        </p>
        <div class="flex gap-2">
          <button
            class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40"
            type="button"
            :disabled="page <= 1"
            @click="page--"
          >
            <ChevronLeft class="h-4 w-4" />
          </button>
          <button
            class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40"
            type="button"
            :disabled="page >= totalPages"
            @click="page++"
          >
            <ChevronRight class="h-4 w-4" />
          </button>
        </div>
      </div>
    </section>

    <!-- Bottom row: Create user + Email blacklist + Duplicate detection -->
    <section class="grid gap-6 xl:grid-cols-[minmax(360px,0.8fr)_minmax(0,1.2fr)]">

      <div class="space-y-4">
        <!-- Create user -->
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <UserPlus class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Create user</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Create client, writer, editor, support, or staff accounts.
          </p>
          <div class="mt-4 space-y-3">
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">First name</span>
                <input v-model="access.createUserForm.first_name" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="text" />
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Last name</span>
                <input v-model="access.createUserForm.last_name" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="text" />
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Username</span>
              <input v-model="access.createUserForm.username" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="text" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Email</span>
              <input v-model="access.createUserForm.email" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="email" />
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Role</span>
                <select v-model="access.createUserForm.role" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
                  <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Website</span>
                <select
                  v-model.number="access.createUserForm.website"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >
                  <option :value="null">— select website —</option>
                  <option v-for="site in access.websites" :key="site.id" :value="site.id">
                    {{ site.name }}{{ site.domain ? ` (${site.domain})` : '' }}
                  </option>
                </select>
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Password</span>
              <input v-model="access.createUserForm.password" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="Leave empty to auto-generate" type="password" />
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

        <!-- Email blacklist -->
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Ban class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Email blacklist</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Block risky emails before they register again.
          </p>
          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Email</span>
              <input v-model="access.blacklistForm.email" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="email" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Reason</span>
              <textarea v-model="access.blacklistForm.reason" class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
            </label>
          </div>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-4 text-sm font-semibold text-rose-700 disabled:opacity-60"
            type="button"
            :disabled="access.isMutating"
            @click="access.addBlacklistedEmail().catch(() => undefined)"
          >
            <Ban class="h-4 w-4" />
            Add to blacklist
          </button>
        </section>
      </div>

      <div class="space-y-4">
        <!-- Lifecycle metrics -->
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

        <!-- Duplicate account detection -->
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
              <select v-model="access.duplicateFilters.role" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
                <option value="">All roles</option>
                <option value="client">Clients</option>
                <option value="writer">Writers</option>
              </select>
              <select v-model="access.duplicateFilters.min_confidence" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
                <option value="low">Low+</option>
                <option value="medium">Medium+</option>
                <option value="high">High</option>
              </select>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-50"
                type="button"
                :disabled="access.isDuplicatesLoading"
                @click="runScan"
              >
                <RefreshCw class="h-4 w-4" :class="access.isDuplicatesLoading ? 'animate-spin' : ''" />
                {{ access.isDuplicatesLoading ? 'Scanning…' : 'Scan' }}
              </button>
            </div>
          </div>
          <p v-if="access.duplicatesError" class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-800">
            {{ access.duplicatesError }}
          </p>
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
                <StatusPill
                  :label="group.confidence"
                  :tone="group.confidence === 'high' ? 'danger' : group.confidence === 'medium' ? 'warning' : 'neutral'"
                />
              </div>
              <div class="mt-3 grid gap-2 md:grid-cols-2">
                <button
                  v-for="user in group.users"
                  :key="user.id"
                  class="focus-ring rounded-md border border-slate-200 bg-white p-3 text-left"
                  type="button"
                  @click="openProfile(user.id)"
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

        <!-- Blacklisted emails -->
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
      </div>
    </section>
  </div>
</template>
