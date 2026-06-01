<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  ArrowDownLeft,
  ArrowUpRight,
  BookOpen,
  ChevronDown,
  ChevronRight,
  Loader2,
  RefreshCw,
  Scale,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import {
  ledgerApi,
  type JournalEntry,
  type LedgerAccount,
  type ReconciliationRecord,
} from "@/api/ledger";

const activeTab = ref<"accounts" | "journal" | "reconciliations">("accounts");

// Accounts
const accounts = ref<LedgerAccount[]>([]);
const accountsLoading = ref(false);
const accountsError = ref("");

// Journal entries
const entries = ref<JournalEntry[]>([]);
const entriesLoading = ref(false);
const entriesError = ref("");
const expandedEntry = ref<string | null>(null);
const entriesNext = ref<string | null>(null);
const entriesLoadingMore = ref(false);

// Reconciliations
const reconciliations = ref<ReconciliationRecord[]>([]);
const reconLoading = ref(false);
const reconError = ref("");
const reconFilter = ref<"" | "unreconciled" | "mismatched" | "matched" | "resolved">("");

function normalize<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : (data as { results: T[] }).results ?? [];
}

async function fetchAccounts() {
  accountsLoading.value = true;
  accountsError.value = "";
  try {
    const { data } = await ledgerApi.accounts({ ordering: "code" });
    accounts.value = normalize(data);
  } catch (err: unknown) {
    accountsError.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Could not load accounts.";
  } finally {
    accountsLoading.value = false;
  }
}

async function fetchEntries(reset = true) {
  if (reset) {
    entriesLoading.value = true;
    entriesError.value = "";
    entries.value = [];
    entriesNext.value = null;
  } else {
    entriesLoadingMore.value = true;
  }
  try {
    const { data } = reset
      ? await ledgerApi.journalEntries({ ordering: "-created_at", page_size: 50 })
      : await ledgerApi.journalEntries({ cursor: entriesNext.value });

    const list = normalize(data);
    if (reset) entries.value = list;
    else entries.value.push(...list);

    const paged = data as { next?: string | null };
    entriesNext.value = paged.next ?? null;
  } catch (err: unknown) {
    entriesError.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Could not load journal entries.";
  } finally {
    entriesLoading.value = false;
    entriesLoadingMore.value = false;
  }
}

async function fetchReconciliations() {
  reconLoading.value = true;
  reconError.value = "";
  try {
    const params: Record<string, string> = { ordering: "-created_at" };
    if (reconFilter.value) params.status = reconFilter.value;
    const { data } = await ledgerApi.reconciliations(params);
    reconciliations.value = normalize(data);
  } catch (err: unknown) {
    reconError.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Could not load reconciliations.";
  } finally {
    reconLoading.value = false;
  }
}

function refresh() {
  fetchAccounts();
  fetchEntries();
  fetchReconciliations();
}

function toggleEntry(id: string) {
  expandedEntry.value = expandedEntry.value === id ? null : id;
}

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s === "posted" || s === "matched" || s === "resolved" || s === "active") return "success";
  if (s === "failed" || s === "mismatched") return "danger";
  if (s === "pending" || s === "draft" || s === "unreconciled" || s === "partially_matched") return "warning";
  return "neutral";
}

function money(val: string | number, currency = "USD"): string {
  const n = Number(val);
  if (Number.isNaN(n)) return String(val);
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
}

function shortDate(val: string | null | undefined): string {
  if (!val) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(val));
}

function longDate(val: string | null | undefined): string {
  if (!val) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(val));
}

onMounted(refresh);
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Finance</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Ledger</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Double-entry journal entries, chart of accounts, and reconciliation records.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold"
        type="button"
        @click="refresh"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <!-- Tabs -->
    <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 w-fit">
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'accounts' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'accounts'"
      >
        <span class="flex items-center gap-1.5"><BookOpen class="h-3.5 w-3.5" /> Accounts</span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'journal' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'journal'"
      >
        Journal
        <span v-if="entries.length" class="ml-1.5 rounded-full bg-slate-200 px-1.5 text-xs">{{ entries.length }}</span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'reconciliations' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'reconciliations'"
      >
        <span class="flex items-center gap-1.5"><Scale class="h-3.5 w-3.5" /> Reconciliations</span>
      </button>
    </div>

    <!-- ─── ACCOUNTS ──────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'accounts'">
      <p v-if="accountsError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ accountsError }}</p>

      <div v-if="accountsLoading" class="space-y-2">
        <div v-for="n in 6" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex gap-4">
            <div class="h-3 w-16 rounded bg-slate-200" />
            <div class="h-3 w-40 rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <EmptyState v-else-if="!accounts.length" :icon="BookOpen" title="No accounts" message="Ledger accounts will appear here once the system has been initialised." />

      <div v-else class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-3 py-2">Code</th>
              <th class="px-3 py-2">Name</th>
              <th class="px-3 py-2">Type</th>
              <th class="px-3 py-2">Currency</th>
              <th class="px-3 py-2">Status</th>
              <th class="px-3 py-2">System</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="acc in accounts" :key="acc.id" class="hover:bg-slate-50">
              <td class="px-3 py-2 font-mono text-xs font-semibold text-ink">{{ acc.code }}</td>
              <td class="px-3 py-2">
                <p class="font-medium text-ink">{{ acc.name }}</p>
                <p v-if="acc.description" class="mt-0.5 text-xs text-graphite">{{ acc.description }}</p>
              </td>
              <td class="px-3 py-2 text-graphite">{{ acc.account_type.replace(/_/g, " ") }}</td>
              <td class="px-3 py-2 font-mono text-xs text-graphite">{{ acc.currency }}</td>
              <td class="px-3 py-2">
                <StatusPill :label="acc.status" :tone="statusTone(acc.status)" />
              </td>
              <td class="px-3 py-2 text-center text-xs text-graphite">{{ acc.is_system_account ? "" : "—" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- ─── JOURNAL ENTRIES ───────────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'journal'">
      <p v-if="entriesError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ entriesError }}</p>

      <div v-if="entriesLoading" class="space-y-2">
        <div v-for="n in 6" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
          <div class="h-3 w-1/3 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <EmptyState v-else-if="!entries.length" :icon="BookOpen" title="No journal entries" message="Journal entries will appear here once transactions are processed." />

      <div v-else class="space-y-2">
        <div
          v-for="entry in entries"
          :key="entry.id"
          class="rounded-lg border border-slate-200 bg-white"
        >
          <button
            class="focus-ring w-full text-left"
            type="button"
            @click="toggleEntry(entry.id)"
          >
            <div class="flex items-start gap-3 px-5 py-4">
              <span class="mt-0.5 shrink-0">
                <ChevronDown v-if="expandedEntry === entry.id" class="h-4 w-4 text-graphite" />
                <ChevronRight v-else class="h-4 w-4 text-graphite" />
              </span>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-mono text-xs font-semibold text-graphite">{{ entry.entry_number }}</span>
                  <StatusPill :label="entry.status" :tone="statusTone(entry.status)" />
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">{{ entry.entry_type.replace(/_/g, " ") }}</span>
                </div>
                <p v-if="entry.description" class="mt-1 text-sm text-ink">{{ entry.description }}</p>
                <p class="mt-1 text-xs text-graphite">
                  <span v-if="entry.source_app">{{ entry.source_app }}<span v-if="entry.source_model"> / {{ entry.source_model }}</span> · </span>
                  <span v-if="entry.reference">Ref: {{ entry.reference }} · </span>
                  {{ longDate(entry.posted_at ?? entry.effective_at ?? entry.created_at) }}
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-xs text-graphite">{{ entry.currency }}</p>
                <p class="text-sm font-semibold text-ink">{{ entry.lines.length }} lines</p>
              </div>
            </div>
          </button>

          <!-- Lines expansion -->
          <div v-if="expandedEntry === entry.id" class="border-t border-dashed border-slate-200 px-6 py-4">
            <div class="overflow-x-auto">
              <table class="min-w-full text-xs">
                <thead class="text-left text-graphite">
                  <tr>
                    <th class="pb-2 pr-4 font-semibold uppercase">Account</th>
                    <th class="pb-2 pr-4 font-semibold uppercase">Side</th>
                    <th class="pb-2 pr-4 text-right font-semibold uppercase">Amount</th>
                    <th class="pb-2 font-semibold uppercase">Description</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="line in entry.lines" :key="line.id">
                    <td class="py-2 pr-4">
                      <span class="font-mono font-semibold text-ink">{{ line.ledger_account_code }}</span>
                      <span class="ml-1.5 text-graphite">{{ line.ledger_account_name }}</span>
                    </td>
                    <td class="py-2 pr-4">
                      <span class="inline-flex items-center gap-1 font-semibold" :class="line.is_debit ? 'text-berry' : 'text-signal'">
                        <ArrowUpRight v-if="line.is_debit" class="h-3 w-3" />
                        <ArrowDownLeft v-else class="h-3 w-3" />
                        {{ line.entry_side }}
                      </span>
                    </td>
                    <td class="py-2 pr-4 text-right font-mono font-semibold text-ink">{{ money(line.amount, line.currency) }}</td>
                    <td class="py-2 text-graphite">{{ line.description ?? "—" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="entry.failure_reason" class="mt-3 rounded-md border border-rose-100 bg-rose-50 px-3 py-2 text-xs text-berry">
              Failure: {{ entry.failure_reason }}
            </div>
          </div>
        </div>

        <div v-if="entriesNext" class="text-center pt-2">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold hover:bg-slate-50 disabled:opacity-60"
            type="button"
            :disabled="entriesLoadingMore"
            @click="fetchEntries(false)"
          >
            <Loader2 v-if="entriesLoadingMore" class="h-4 w-4 animate-spin" />
            Load more
          </button>
        </div>
      </div>
    </template>

    <!-- ─── RECONCILIATIONS ───────────────────────────────────────────────── -->
    <template v-else>
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="opt in [
            { key: '', label: 'All' },
            { key: 'unreconciled', label: 'Unreconciled' },
            { key: 'mismatched', label: 'Mismatched' },
            { key: 'matched', label: 'Matched' },
            { key: 'resolved', label: 'Resolved' },
          ]"
          :key="opt.key"
          class="focus-ring rounded-md border px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="reconFilter === opt.key
            ? 'border-signal bg-signal/5 text-signal'
            : 'border-slate-200 bg-white text-graphite hover:text-ink'"
          type="button"
          @click="reconFilter = opt.key as typeof reconFilter; fetchReconciliations()"
        >
          {{ opt.label }}
        </button>
      </div>

      <p v-if="reconError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ reconError }}</p>

      <div v-if="reconLoading" class="space-y-2">
        <div v-for="n in 4" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
          <div class="h-3 w-1/3 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <EmptyState v-else-if="!reconciliations.length" :icon="Scale" title="No reconciliation records" message="Reconciliations appear here once payment processing runs." />

      <div v-else class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-3 py-2">Journal entry</th>
              <th class="px-3 py-2">Status</th>
              <th class="px-3 py-2 text-right">Expected</th>
              <th class="px-3 py-2 text-right">Actual</th>
              <th class="px-3 py-2 text-right">Variance</th>
              <th class="px-3 py-2">Reference</th>
              <th class="px-3 py-2">Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="rec in reconciliations" :key="rec.id" class="hover:bg-slate-50">
              <td class="px-3 py-2 font-mono text-xs font-semibold text-graphite">{{ rec.journal_entry_number }}</td>
              <td class="px-3 py-2">
                <StatusPill :label="rec.status.replace(/_/g, ' ')" :tone="statusTone(rec.status)" />
              </td>
              <td class="px-3 py-2 text-right font-mono text-ink">{{ money(rec.expected_amount, rec.currency) }}</td>
              <td class="px-3 py-2 text-right font-mono text-ink">{{ money(rec.actual_amount, rec.currency) }}</td>
              <td
                class="px-5 py-3 text-right font-mono font-semibold"
                :class="Number(rec.variance_amount) !== 0 ? 'text-berry' : 'text-signal'"
              >
                {{ money(rec.variance_amount, rec.currency) }}
              </td>
              <td class="px-3 py-2 font-mono text-xs text-graphite">{{ rec.reference ?? rec.external_reference ?? "—" }}</td>
              <td class="px-3 py-2 text-graphite">{{ shortDate(rec.resolved_at ?? rec.created_at) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Mismatch summary -->
        <div
          v-if="reconciliations.some(r => r.is_mismatched)"
          class="border-t border-slate-200 bg-rose-50 px-5 py-3 text-xs font-semibold text-berry"
        >
          {{ reconciliations.filter(r => r.is_mismatched).length }} mismatched records require attention
        </div>
      </div>
    </template>
  </div>
</template>
