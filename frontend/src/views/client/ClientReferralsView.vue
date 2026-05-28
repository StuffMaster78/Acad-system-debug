<script setup lang="ts">
import { onMounted, ref } from "vue";
import { CheckCircle2, ClipboardCopy, Loader2, RefreshCw, Users } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { referralsApi, type ReferralCodeRecord, type ReferralRecord } from "@/api/referrals";

const code = ref<ReferralCodeRecord | null>(null);
const codeLoading = ref(false);
const codeError = ref("");
const copied = ref(false);

const referrals = ref<ReferralRecord[]>([]);
const referralsLoading = ref(false);

async function fetchMyCode() {
  codeLoading.value = true;
  codeError.value = "";
  try {
    const { data } = await referralsApi.myCode();
    code.value = data;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { error?: string; detail?: string } } })?.response?.data;
    codeError.value = detail?.error ?? detail?.detail ?? "Could not load your referral code.";
  } finally {
    codeLoading.value = false;
  }
}

async function fetchReferrals() {
  referralsLoading.value = true;
  try {
    const { data } = await referralsApi.myReferrals();
    referrals.value = Array.isArray(data) ? data : (data as { results: ReferralRecord[] }).results ?? [];
  } catch {
    // non-critical
  } finally {
    referralsLoading.value = false;
  }
}

async function copyLink() {
  const link = code.value?.referral_link ?? code.value?.code;
  if (!link) return;
  try {
    await navigator.clipboard.writeText(link);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2500);
  } catch {
    // fallback: select text
  }
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

onMounted(() => {
  fetchMyCode();
  fetchReferrals();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Referrals</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Share your referral link and earn bonuses when friends place their first order.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="codeLoading"
        @click="fetchMyCode(); fetchReferrals()"
      >
        <Loader2 v-if="codeLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p v-if="codeError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ codeError }}
    </p>

    <!-- Referral code card -->
    <div v-if="codeLoading && !code" class="animate-pulse rounded-lg border border-slate-200 bg-white p-6">
      <div class="h-5 w-32 rounded bg-slate-200" />
      <div class="mt-4 h-10 w-full rounded bg-slate-100" />
    </div>

    <section v-else-if="code" class="rounded-lg border border-slate-200 bg-white">
      <div class="px-6 py-5">
        <h2 class="text-base font-semibold text-ink">Your referral code</h2>
        <div class="mt-4 flex items-center gap-3">
          <div class="flex-1 rounded-md border border-slate-200 bg-slate-50 px-4 py-3">
            <p class="text-lg font-mono font-semibold tracking-widest text-ink">{{ code.code }}</p>
            <p v-if="code.referral_link" class="mt-0.5 truncate text-xs text-graphite">{{ code.referral_link }}</p>
          </div>
          <button
            class="focus-ring inline-flex shrink-0 items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
            type="button"
            @click="copyLink"
          >
            <CheckCircle2 v-if="copied" class="h-4 w-4 text-signal" />
            <ClipboardCopy v-else class="h-4 w-4" />
            {{ copied ? "Copied!" : "Copy link" }}
          </button>
        </div>
      </div>

      <!-- Usage stats -->
      <div v-if="code.usage_stats" class="grid grid-cols-2 divide-x divide-y divide-slate-200 border-t border-slate-200 sm:grid-cols-4">
        <div class="px-5 py-4 text-center">
          <p class="text-2xl font-semibold text-ink">{{ code.usage_stats.total_referrals }}</p>
          <p class="mt-1 text-xs text-graphite">Total referred</p>
        </div>
        <div class="px-5 py-4 text-center">
          <p class="text-2xl font-semibold text-signal">{{ code.usage_stats.successful_referrals }}</p>
          <p class="mt-1 text-xs text-graphite">Bonuses earned</p>
        </div>
        <div class="px-5 py-4 text-center">
          <p class="text-2xl font-semibold text-ink">{{ code.usage_stats.orders_placed }}</p>
          <p class="mt-1 text-xs text-graphite">Orders placed</p>
        </div>
        <div class="px-5 py-4 text-center">
          <p class="text-2xl font-semibold text-ink">{{ code.usage_stats.conversion_rate }}%</p>
          <p class="mt-1 text-xs text-graphite">Conversion rate</p>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="rounded-lg border border-slate-200 bg-white p-6">
      <h2 class="text-base font-semibold text-ink">How it works</h2>
      <ol class="mt-4 space-y-3">
        <li class="flex items-start gap-3 text-sm text-graphite">
          <span class="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-signal/10 text-xs font-semibold text-signal">1</span>
          Share your referral link or code with a friend.
        </li>
        <li class="flex items-start gap-3 text-sm text-graphite">
          <span class="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-signal/10 text-xs font-semibold text-signal">2</span>
          Your friend signs up and places their first order using your code.
        </li>
        <li class="flex items-start gap-3 text-sm text-graphite">
          <span class="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-signal/10 text-xs font-semibold text-signal">3</span>
          Once their order completes successfully, you both receive a bonus credited to your wallets.
        </li>
      </ol>
    </section>

    <!-- Referrals table -->
    <section class="rounded-lg border border-slate-200 bg-white">
      <div class="flex items-center gap-2 border-b border-slate-200 px-6 py-4">
        <Users class="h-5 w-5 text-signal" />
        <h2 class="text-base font-semibold text-ink">People you've referred</h2>
        <span class="ml-auto text-sm text-graphite">{{ referrals.length }} total</span>
      </div>

      <div v-if="referralsLoading" class="px-6 py-8 text-center">
        <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
      </div>

      <div v-else-if="!referrals.length" class="px-6 py-12 text-center">
        <Users class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No referrals yet</p>
        <p class="mt-1 text-sm text-graphite">Share your link to get started.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-6 py-3">Referee</th>
              <th class="px-6 py-3">Referred on</th>
              <th class="px-6 py-3">Bonus</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="ref in referrals" :key="ref.id" class="hover:bg-slate-50">
              <td class="px-6 py-4">
                <p class="font-medium text-ink">{{ ref.referee?.email ?? ref.referee?.username ?? "Unknown" }}</p>
                <p v-if="ref.referral_code" class="mt-0.5 text-xs text-graphite">Code: {{ ref.referral_code }}</p>
              </td>
              <td class="px-6 py-4 text-graphite">{{ formatDate(ref.created_at) }}</td>
              <td class="px-6 py-4">
                <StatusPill
                  :label="ref.bonus_awarded ? 'Bonus awarded' : 'Pending'"
                  :tone="ref.bonus_awarded ? 'success' : 'neutral'"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
