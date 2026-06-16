<script setup lang="ts">
import { computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { Wallet } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useWalletStore } from "@/stores/wallets";

const auth = useAuthStore();
const wallet = useWalletStore();

const shouldShow = computed(() => ["client", "writer"].includes(auth.role ?? ""));

const destination = computed(() =>
  auth.role === "writer" ? "/writer/earnings" : "/client/wallet",
);

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
  <RouterLink
    v-if="shouldShow"
    :to="destination"
    class="hidden min-h-8 min-w-[5rem] items-center gap-1.5 whitespace-nowrap rounded-full border border-emerald-200 bg-emerald-50 px-4 text-sm font-semibold tabular-nums text-emerald-800 transition-colors hover:border-emerald-300 hover:bg-emerald-100 md:inline-flex"
    title="Go to earnings"
  >
    <Wallet class="h-3.5 w-3.5 text-emerald-600" />
    <span>{{ formattedBalance }}</span>
  </RouterLink>
</template>
