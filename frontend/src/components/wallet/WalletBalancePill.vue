<script setup lang="ts">
import { computed, onMounted } from "vue";
import { Wallet } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useWalletStore } from "@/stores/wallets";

const auth = useAuthStore();
const wallet = useWalletStore();

const shouldShow = computed(() => ["client", "writer"].includes(auth.role ?? ""));

const formattedBalance = computed(() =>
  new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: wallet.currency,
    maximumFractionDigits: 0,
  }).format(wallet.availableBalance),
);

onMounted(() => {
  if (shouldShow.value) wallet.fetchWallet().catch(() => undefined);
});
</script>

<template>
  <div
    v-if="shouldShow"
    class="hidden min-h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-ink md:inline-flex"
    title="Wallet balance"
  >
    <Wallet class="h-4 w-4 text-signal" />
    <span>{{ formattedBalance }}</span>
  </div>
</template>
