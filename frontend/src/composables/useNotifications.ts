import { onUnmounted, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notifications";
import { useWalletStore } from "@/stores/wallets";

export function useNotifications() {
  const auth = useAuthStore();
  const notifications = useNotificationStore();
  const wallet = useWalletStore();
  const isConnected = ref(false);
  const error = ref("");
  let eventSource: EventSource | null = null;

  function disconnect() {
    eventSource?.close();
    eventSource = null;
    isConnected.value = false;
  }

  function connect() {
    disconnect();
    if (!auth.accessToken) return;

    const base =
      import.meta.env.VITE_SSE_URL ||
      "http://localhost:8000/api/v1/notifications/stream/";
    const url = new URL(base);
    url.searchParams.set("token", auth.accessToken);

    eventSource = new EventSource(url.toString());
    eventSource.onopen = () => {
      isConnected.value = true;
      error.value = "";
    };
    eventSource.onerror = () => {
      isConnected.value = false;
      error.value = "Notification stream disconnected.";
    };
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const eventType = String(payload.type ?? payload.event_type ?? "");
        if (eventType === "wallet_update") {
          wallet.fetchWallet().catch(() => undefined);
        } else if (!notifications.isDndActive) {
          notifications.push(payload);
        }
      } catch {
        if (!notifications.isDndActive) notifications.push({ message: event.data });
      }
    };
  }

  watch(() => auth.accessToken, connect, { immediate: true });
  onUnmounted(disconnect);

  return {
    notifications,
    isConnected,
    error,
    connect,
    disconnect,
  };
}
