<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import { Search } from "@lucide/vue";
import { adminOpsApi } from "@/api/adminOps";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  role: UserRole;
}>();

const auth = useAuthStore();
const query = ref("");
const open = ref(false);
const isSearching = ref(false);
const error = ref("");
const results = ref<Record<string, Array<Record<string, unknown>>>>({
  users: [],
  orders: [],
  payments: [],
  messages: [],
});

const groups = computed(() =>
  ["users", "orders", "payments", "messages"]
    .map((key) => ({ key, rows: results.value[key] ?? [] }))
    .filter((group) => group.rows.length),
);

const hasResults = computed(() => groups.value.length > 0);

function previewResults() {
  results.value = {
    users: [
      { id: 101, title: "Nadia Morgan", email: "nadia@example.com", role: "client" },
    ],
    orders: [
      { id: 1042, title: "Healthcare policy brief", status: "assigned" },
    ],
    payments: [
      { id: 77, title: "Wallet payment", amount: "240.00", status: "completed" },
    ],
    messages: [
      { id: 18, title: "Support thread", snippet: "Nadia asked about order timing." },
    ],
  };
}

function resultTitle(item: Record<string, unknown>) {
  return String(item.title || item.full_name || item.username || item.email || item.topic || item.id || "Result");
}

function resultSubtitle(item: Record<string, unknown>) {
  return String(item.email || item.status || item.snippet || item.amount || item.role || item.reference || "Open result");
}

function targetFor(group: string, item: Record<string, unknown>) {
  if (group === "orders") {
    if (props.role === "client") return `/client/orders/${item.id}`;
    return `/${props.role}/orders`;
  }
  if (group === "users") return props.role === "admin" || props.role === "superadmin" ? `/${props.role}/access` : `/${props.role}/activity`;
  if (group === "payments") return props.role === "admin" || props.role === "superadmin" ? `/${props.role}/payments` : `/${props.role}`;
  if (group === "messages") return `/${props.role}/messages`;
  return `/${props.role}`;
}

async function runSearch() {
  const trimmed = query.value.trim();
  if (trimmed.length < 2) {
    open.value = false;
    return;
  }

  isSearching.value = true;
  error.value = "";
  open.value = true;

  try {
    if (auth.isPreviewSession) {
      previewResults();
      return;
    }

    const { data } = await adminOpsApi.search({
      q: trimmed,
      types: "users,orders,payments,messages",
      limit: 5,
    });
    results.value = {
      users: data.users ?? [],
      orders: data.orders ?? [],
      payments: data.payments ?? [],
      messages: data.messages ?? [],
    };
  } catch {
    error.value = "Search unavailable.";
    results.value = { users: [], orders: [], payments: [], messages: [] };
  } finally {
    isSearching.value = false;
  }
}
</script>

<template>
  <div class="relative max-w-xl flex-1">
    <form @submit.prevent="runSearch">
      <Search
        class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
      />
      <input
        v-model="query"
        class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm"
        placeholder="Search orders, users, payments, messages"
        type="search"
        @focus="open = hasResults"
        @keydown.enter.prevent="runSearch"
      >
    </form>

    <section
      v-if="open"
      class="absolute left-0 right-0 top-12 z-30 overflow-hidden rounded-md border border-slate-200 bg-white shadow-panel"
    >
      <div class="border-b border-slate-200 px-4 py-3">
        <p class="text-sm font-semibold text-ink">Search</p>
        <p class="mt-1 text-xs text-graphite">Press Enter to search across platform records.</p>
      </div>

      <div v-if="isSearching" class="px-4 py-5 text-sm text-graphite">Searching...</div>
      <div v-else-if="error" class="px-4 py-5 text-sm text-amber-800">{{ error }}</div>
      <div v-else-if="hasResults" class="max-h-96 overflow-y-auto">
        <div
          v-for="group in groups"
          :key="group.key"
          class="border-b border-slate-100 last:border-b-0"
        >
          <p class="bg-slate-50 px-4 py-2 text-xs font-semibold uppercase text-graphite">{{ group.key }}</p>
          <RouterLink
            v-for="item in group.rows"
            :key="`${group.key}-${item.id ?? resultTitle(item)}`"
            class="block px-4 py-3 hover:bg-slate-50"
            :to="targetFor(group.key, item)"
            @click="open = false"
          >
            <p class="truncate text-sm font-semibold text-ink">{{ resultTitle(item) }}</p>
            <p class="mt-1 truncate text-xs text-graphite">{{ resultSubtitle(item) }}</p>
          </RouterLink>
        </div>
      </div>
      <p v-else class="px-4 py-5 text-sm text-graphite">No results yet.</p>
    </section>
  </div>
</template>
