<script setup lang="ts">
/**
 * Unified money view — wallet + billing in one place.
 * Replaces the separate /client/wallet and /client/billing routes.
 */
import { ref } from "vue";
import { CreditCard, Wallet } from "@lucide/vue";
import ClientWalletView from "./ClientWalletView.vue";
import ClientBillingView from "./ClientBillingView.vue";

type Tab = "wallet" | "billing";
const activeTab = ref<Tab>("wallet");
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-ink">Billing & Wallet</h1>
      <p class="mt-1 text-sm text-graphite">Manage your balance, invoices, and payment history in one place.</p>
    </div>

    <!-- Tab switcher -->
    <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition-all"
        :class="activeTab === 'wallet' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="activeTab = 'wallet'"
      >
        <Wallet class="h-4 w-4" /> Wallet
      </button>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition-all"
        :class="activeTab === 'billing' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="activeTab = 'billing'"
      >
        <CreditCard class="h-4 w-4" /> Invoices & receipts
      </button>
    </div>

    <!-- Tab content -->
    <ClientWalletView v-if="activeTab === 'wallet'" />
    <ClientBillingView v-else />
  </div>
</template>
