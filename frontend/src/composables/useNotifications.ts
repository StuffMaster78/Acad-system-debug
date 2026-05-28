import { onUnmounted, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notifications";
import { useWalletStore } from "@/stores/wallets";

const POLL_INTERVAL_MS = 30_000;

export function useNotifications() {
  const auth = useAuthStore();
  const notifications = useNotificationStore();
  const wallet = useWalletStore();
  const isConnected = ref(false);
  const error = ref("");
  let timer: ReturnType<typeof setInterval> | null = null;

  function stop() {
    if (timer !== null) {
      clearInterval(timer);
      timer = null;
    }
    isConnected.value = false;
  }

  async function tick() {
    if (!auth.accessToken) return;
    try {
      const latest = await notifications.pollUnreadCount();
      if (latest && (latest as unknown as Record<string, unknown>).type === "wallet_update") {
        wallet.fetchWallet().catch(() => undefined);
      }
      error.value = "";
      isConnected.value = true;
    } catch {
      error.value = "Notification polling failed.";
      isConnected.value = false;
    }
  }

  function start() {
    stop();
    if (!auth.accessToken) return;
    tick();
    timer = setInterval(tick, POLL_INTERVAL_MS);
  }

  watch(() => auth.accessToken, start, { immediate: true });
  onUnmounted(stop);

  return {
    notifications,
    isConnected,
    error,
    connect: start,
    disconnect: stop,
  };
}
