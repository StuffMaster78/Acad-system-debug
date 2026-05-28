<script setup lang="ts">
import { onMounted } from "vue";
import {
  CalendarDays,
  Copy,
  Gift,
  HandCoins,
  Percent,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  Users,
} from "@lucide/vue";
import BaseDataTable, { type DataTableColumn } from "@/components/ui/BaseDataTable.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminGrowthStore } from "@/stores/adminGrowth";
import type { GrowthLane, GrowthRecord } from "@/types/adminGrowth";

const growth = useAdminGrowthStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const laneIcons: Record<GrowthLane["key"], typeof Percent> = {
  discounts: Percent,
  referrals: Users,
  loyalty: Gift,
  holidays: CalendarDays,
};

const columns: DataTableColumn[] = [
  { key: "name", label: "Rule / campaign", sortable: true },
  { key: "category", label: "Category", sortable: true },
  { key: "value", label: "Value", sortable: true },
  { key: "owner", label: "Website", sortable: true },
  { key: "status", label: "Status", sortable: true },
  { key: "window", label: "Window", sortable: true },
  { key: "action", label: "Action" },
];

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
  }).format(new Date(value));
}

function statusTone(status: string) {
  const normalized = status.toLowerCase();
  if (["active", "approved", "scheduled"].includes(normalized)) return "success";
  if (["pending", "draft", "review"].some((value) => normalized.includes(value))) return "warning";
  if (["inactive", "archived", "rejected", "expired"].some((value) => normalized.includes(value))) return "danger";
  return "neutral";
}

function rows() {
  return growth.filteredRecords.map((record) => ({
    ...record,
    window: `${formatDate(record.startsAt)} → ${formatDate(record.endsAt)}`,
    value: record.value ?? "Configured",
    action: record.source === "campaigns" ? "toggle-campaign" : "review",
  }));
}

function canToggleCampaign(record: GrowthRecord) {
  return record.source === "campaigns" && typeof record.id !== "undefined";
}

onMounted(() => {
  growth.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Commercial ops</p>
        <h1 class="mt-2 text-3xl font-semibold">Growth & retention</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Portal controls for discounts, campaigns, referrals, loyalty tiers,
          redemption queues, and holiday promotions.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="growth.isLoading"
        @click="growth.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': growth.isLoading }" />
        Refresh
      </button>
    </section>

    <p
      v-if="growth.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ growth.error }} Preview mode will still show the commercial structure.
    </p>

    <p
      v-if="growth.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ growth.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in growth.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="rounded-md border border-slate-200 bg-white p-4">
      <div class="flex items-center gap-2">
        <Sparkles class="h-5 w-5 text-signal" />
        <h2 class="text-base font-semibold">Business logic flow</h2>
      </div>
      <div class="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="step in growth.workflow"
          :key="step.label"
          class="rounded-md border border-slate-200 bg-slate-50 p-3"
        >
          <StatusPill :label="step.owner" />
          <h3 class="mt-3 text-sm font-semibold text-ink">{{ step.label }}</h3>
          <p class="mt-2 text-xs leading-5 text-graphite">{{ step.detail }}</p>
        </div>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.85fr)]">
      <div class="rounded-md border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <TrendingUp class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">{{ growth.activeLane.label }}</h2>
            </div>
            <p class="mt-1 max-w-2xl text-sm leading-6 text-graphite">
              {{ growth.activeLane.description }}
            </p>
            <p class="mt-1 text-xs font-semibold text-graphite">{{ growth.activeLane.endpoint }}</p>
          </div>

          <label class="relative block min-w-72">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
            <input
              v-model="growth.query"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
              type="search"
              placeholder="Search rules, status, website"
            >
          </label>
        </div>

        <div class="grid gap-3 border-b border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 xl:grid-cols-4">
          <button
            v-for="lane in growth.lanes"
            :key="lane.key"
            class="focus-ring rounded-md border p-3 text-left"
            :class="growth.selectedLane === lane.key ? 'border-signal bg-white shadow-sm' : 'border-slate-200 bg-white/70'"
            type="button"
            @click="growth.selectedLane = lane.key"
          >
            <div class="flex items-center gap-2">
              <component :is="laneIcons[lane.key]" class="h-4 w-4 text-signal" />
              <span class="text-sm font-semibold text-ink">{{ lane.label }}</span>
            </div>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ lane.records.length }}</p>
            <p class="mt-1 text-xs leading-5 text-graphite">{{ lane.description }}</p>
          </button>
        </div>

        <BaseDataTable
          class="shadow-none"
          :columns="columns"
          :rows="rows()"
          :searchable="false"
          :loading="growth.isLoading"
          empty-title="No records loaded"
          empty-message="This business lane has no records yet or the backend endpoint is unavailable."
        >
          <template #cell-status="{ value }">
            <StatusPill :label="String(value)" :tone="statusTone(String(value))" />
          </template>

          <template #cell-action="{ row }">
            <button
              v-if="canToggleCampaign(row as unknown as GrowthRecord)"
              class="focus-ring inline-flex h-9 items-center justify-center rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
              type="button"
              :disabled="growth.isMutating"
              @click="growth.setCampaignState(row as unknown as GrowthRecord, String(row.status).toLowerCase() !== 'active').catch(() => undefined)"
            >
              {{ String(row.status).toLowerCase() === "active" ? "Deactivate" : "Activate" }}
            </button>
            <StatusPill v-else label="Review" />
          </template>
        </BaseDataTable>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Percent class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Create discount</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Empty client targeting means all users on the current website. Add client IDs to make it individual or selected-client only.
          </p>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Name</span>
              <input
                v-model="growth.discountForm.name"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Type</span>
                <select
                  v-model="growth.discountForm.discount_type"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >
                  <option value="percentage">Percentage</option>
                  <option value="fixed_amount">Fixed amount</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Value</span>
                <input
                  v-model.number="growth.discountForm.discount_value"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="0.01"
                  step="0.01"
                  type="number"
                >
              </label>
            </div>

            <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
              <label class="flex items-center gap-2 text-sm font-semibold text-ink">
                <input
                  v-model="growth.discountForm.generate_code"
                  class="h-4 w-4 rounded border-slate-300"
                  type="checkbox"
                >
                Generate code
              </label>
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <label class="block">
                  <span class="text-xs font-semibold uppercase text-graphite">
                    {{ growth.discountForm.generate_code ? "Code prefix" : "Manual code" }}
                  </span>
                  <input
                    v-if="growth.discountForm.generate_code"
                    v-model="growth.discountForm.code_prefix"
                    class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                    type="text"
                  >
                  <input
                    v-else
                    v-model="growth.discountForm.discount_code"
                    class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                    type="text"
                  >
                </label>
                <label class="block">
                  <span class="text-xs font-semibold uppercase text-graphite">Origin</span>
                  <select
                    v-model="growth.discountForm.origin"
                    class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  >
                    <option value="manual">Manual</option>
                    <option value="first_order">First order</option>
                    <option value="holiday">Holiday</option>
                    <option value="loyalty">Loyalty</option>
                    <option value="referral">Referral</option>
                    <option value="campaign">Campaign</option>
                    <option value="spend_tier">Spend tier</option>
                  </select>
                </label>
              </div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Starts</span>
                <input
                  v-model="growth.discountForm.starts_at"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="datetime-local"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Ends</span>
                <input
                  v-model="growth.discountForm.ends_at"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="datetime-local"
                >
              </label>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Usage limit</span>
                <input
                  v-model.number="growth.discountForm.usage_limit"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                  placeholder="Unlimited"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Per-client limit</span>
                <input
                  v-model.number="growth.discountForm.per_client_usage_limit"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                >
              </label>
            </div>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Campaign</span>
              <select
                v-model.number="growth.discountForm.campaign_id"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option :value="null">No campaign</option>
                <option
                  v-for="campaign in growth.campaignOptions"
                  :key="campaign.id"
                  :value="campaign.id"
                >
                  {{ campaign.name }}
                </option>
              </select>
            </label>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Audience</span>
              <select
                v-model="growth.discountForm.audience"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option value="all">All users on current website</option>
                <option value="clients">Selected client IDs</option>
              </select>
            </label>

            <label v-if="growth.discountForm.audience === 'clients'" class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Client IDs</span>
              <textarea
                v-model="growth.discountForm.eligible_client_ids"
                class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="101, 104, 128"
              />
            </label>

            <label class="flex items-center gap-2 text-sm font-semibold text-ink">
              <input
                v-model="growth.discountForm.first_order_only"
                class="h-4 w-4 rounded border-slate-300"
                type="checkbox"
              >
              First order only
            </label>
            <label class="flex items-center gap-2 text-sm font-semibold text-ink">
              <input
                v-model="growth.discountForm.is_active"
                class="h-4 w-4 rounded border-slate-300"
                type="checkbox"
              >
              Active immediately
            </label>
          </div>

          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="growth.isMutating"
            @click="growth.createDiscount().catch(() => undefined)"
          >
            <Percent class="h-4 w-4" />
            Create discount
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <CalendarDays class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Create campaign</h2>
          </div>
          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Name</span>
              <input
                v-model="growth.campaignForm.name"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Slug</span>
              <input
                v-model="growth.campaignForm.slug"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Description</span>
              <textarea
                v-model="growth.campaignForm.description"
                class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Starts</span>
                <input
                  v-model="growth.campaignForm.starts_at"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="datetime-local"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Ends</span>
                <input
                  v-model="growth.campaignForm.ends_at"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="datetime-local"
                >
              </label>
            </div>
            <label class="flex items-center gap-2 text-sm font-semibold text-ink">
              <input
                v-model="growth.campaignForm.is_active"
                class="h-4 w-4 rounded border-slate-300"
                type="checkbox"
              >
              Active immediately
            </label>
          </div>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold disabled:opacity-60"
            type="button"
            :disabled="growth.isMutating"
            @click="growth.createCampaign().catch(() => undefined)"
          >
            <CalendarDays class="h-4 w-4" />
            Create campaign
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Copy class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Clone across websites</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Use this for superadmin rollout: copy a discount or campaign into another website with a new code or slug.
          </p>
          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Clone type</span>
              <select
                v-model="growth.cloneForm.mode"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option value="discount">Discount</option>
                <option value="campaign">Campaign</option>
              </select>
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label v-if="growth.cloneForm.mode === 'discount'" class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Source discount ID</span>
                <input
                  v-model.number="growth.cloneForm.source_discount_id"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                >
              </label>
              <label v-else class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Source campaign ID</span>
                <input
                  v-model.number="growth.cloneForm.source_campaign_id"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Target website ID</span>
                <input
                  v-model.number="growth.cloneForm.target_website_id"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                >
              </label>
            </div>
            <label v-if="growth.cloneForm.mode === 'discount'" class="block">
              <span class="text-xs font-semibold uppercase text-graphite">New code</span>
              <input
                v-model="growth.cloneForm.new_code"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <div v-else class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">New name</span>
                <input
                  v-model="growth.cloneForm.new_name"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">New slug</span>
                <input
                  v-model="growth.cloneForm.new_slug"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
            </div>
          </div>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold disabled:opacity-60"
            type="button"
            :disabled="growth.isMutating"
            @click="growth.cloneToWebsite().catch(() => undefined)"
          >
            <Copy class="h-4 w-4" />
            Clone to website
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <HandCoins class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Decision queue</h2>
          </div>
          <div class="mt-4 space-y-3">
            <div class="rounded-md border border-amber-200 bg-amber-50 p-3">
              <p class="text-sm font-semibold text-ink">{{ growth.expiring.length }} expiring discounts</p>
              <p class="mt-1 text-xs leading-5 text-graphite">Renew, replace, or let them end before clients see stale offers.</p>
            </div>
            <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
              <p class="text-sm font-semibold text-ink">{{ growth.unused.length }} unused discounts</p>
              <p class="mt-1 text-xs leading-5 text-graphite">Archive dead coupons or adjust placement and eligibility.</p>
            </div>
            <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
              <p class="text-sm font-semibold text-ink">{{ growth.redemptionRequests.length }} redemption requests</p>
              <p class="mt-1 text-xs leading-5 text-graphite">Approve, reject, or reconcile loyalty liability with wallet operations.</p>
            </div>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Gift class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Engine ownership</h2>
          </div>
          <div class="mt-4 space-y-3 text-sm leading-6 text-graphite">
            <p><strong class="text-ink">Discounts:</strong> pricing-adjacent offers, campaigns, spend tiers, first-order logic.</p>
            <p><strong class="text-ink">Referrals:</strong> acquisition incentives, bonus configs, reports, and abuse signals.</p>
            <p><strong class="text-ink">Loyalty:</strong> tier rules, point conversion, awards, transfers, deductions, redemptions.</p>
            <p><strong class="text-ink">Holidays:</strong> special days, reminders, and seasonal discount campaigns.</p>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>
