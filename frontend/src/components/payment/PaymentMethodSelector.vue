<script setup lang="ts">
import { computed, onMounted } from "vue";
import { CheckCircle2, CreditCard, Wallet, Zap } from "@lucide/vue";
import { useWalletStore } from "@/stores/wallets";
import { useAuthStore } from "@/stores/auth";

export type PaymentMethod = "wallet" | "stripe" | "mock";

const props = withDefaults(
  defineProps<{
    modelValue: PaymentMethod;
    price?: number | null;
  }>(),
  { price: null },
);

const emit = defineEmits<{ "update:modelValue": [value: PaymentMethod] }>();

const wallets = useWalletStore();
const auth = useAuthStore();

const walletSufficient = computed(() => {
  if (props.price == null) return true;
  return wallets.availableBalance >= props.price;
});

interface MethodOption {
  key: PaymentMethod;
  label: string;
  desc: string;
  disabled: boolean;
  badge: string | null;
  icon: unknown;
}

const methods = computed<MethodOption[]>(() => {
  const list: MethodOption[] = [
    {
      key: "wallet",
      label: "Pay from wallet",
      desc: wallets.isLoading
        ? "Loading balance…"
        : `${wallets.currency} ${wallets.availableBalance.toFixed(2)} available`,
      disabled: !walletSufficient.value,
      badge: !walletSufficient.value && props.price != null ? "Insufficient" : null,
      icon: Wallet,
    },
    {
      key: "stripe",
      label: "Pay by card",
      desc: "Visa, Mastercard via Stripe — you'll be redirected to checkout",
      disabled: false,
      badge: null,
      icon: CreditCard,
    },
  ];
  if (auth.isPreviewSession) {
    list.push({
      key: "mock",
      label: "Mock payment",
      desc: "Dev / preview mode — simulates a successful payment",
      disabled: false,
      badge: "Dev",
      icon: Zap,
    });
  }
  return list;
});

onMounted(() => {
  if (!wallets.wallet) wallets.fetchWallet().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-2">
    <p class="text-sm font-medium text-ink">Payment method</p>
    <label
      v-for="method in methods"
      :key="method.key"
      class="flex cursor-pointer items-start gap-3 rounded-md border p-3 transition-colors"
      :class="[
        method.disabled
          ? 'cursor-not-allowed opacity-50'
          : 'hover:border-slate-400',
        modelValue === method.key
          ? 'border-ink bg-slate-50 ring-1 ring-ink'
          : 'border-slate-200 bg-white',
      ]"
    >
      <input
        class="sr-only"
        type="radio"
        name="payment_method"
        :value="method.key"
        :checked="modelValue === method.key"
        :disabled="method.disabled"
        @change="emit('update:modelValue', method.key)"
      />
      <component :is="method.icon" class="mt-0.5 h-4 w-4 shrink-0 text-slate-500" aria-hidden="true" />
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-semibold text-ink">{{ method.label }}</span>
          <span
            v-if="method.badge"
            class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-graphite"
          >
            {{ method.badge }}
          </span>
        </div>
        <p class="mt-0.5 text-xs text-graphite">{{ method.desc }}</p>
      </div>
      <CheckCircle2
        v-if="modelValue === method.key"
        class="h-4 w-4 shrink-0 text-ink"
        aria-hidden="true"
      />
    </label>

    <p
      v-if="!walletSufficient && price != null"
      class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900"
    >
      Your wallet balance is below the order total. Top up your wallet via the client portal or choose card payment.
    </p>
  </div>
</template>
