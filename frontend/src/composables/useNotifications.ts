import { onUnmounted, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notifications";
import { useWalletStore } from "@/stores/wallets";

const POLL_INTERVAL_MS = 30_000;
const WS_RECONNECT_DELAY_MS = 5_000;

function wsBaseUrl(): string {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  const host = import.meta.env.VITE_API_BASE_URL
    ? new URL(import.meta.env.VITE_API_BASE_URL as string).host
    : window.location.host;
  return `${proto}://${host}`;
}

export function useNotifications() {
  const auth = useAuthStore();
  const notifications = useNotificationStore();
  const wallet = useWalletStore();
  const isConnected = ref(false);
  const error = ref("");

  let pollTimer: ReturnType<typeof setInterval> | null = null;
  let ws: WebSocket | null = null;
  let wsTimer: ReturnType<typeof setTimeout> | null = null;
  let stopped = false;

  // ── Polling (fallback / unread count sync) ────────────────────────────────
  async function tick() {
    if (!auth.accessToken || auth.isPreviewSession) return;
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

  function stopPolling() {
    if (pollTimer !== null) { clearInterval(pollTimer); pollTimer = null; }
  }

  function startPolling() {
    stopPolling();
    if (!auth.accessToken) return;
    tick();
    pollTimer = setInterval(tick, POLL_INTERVAL_MS);
  }

  // ── WebSocket (real-time push) ────────────────────────────────────────────
  function stopWs() {
    if (wsTimer !== null) { clearTimeout(wsTimer); wsTimer = null; }
    if (ws) { ws.onclose = null; ws.close(); ws = null; }
  }

  function connectWs() {
    if (stopped || !auth.accessToken) return;
    stopWs();
    try {
      const url = `${wsBaseUrl()}/ws/notifications/?token=${encodeURIComponent(auth.accessToken)}`;
      ws = new WebSocket(url);

      ws.onopen = () => {
        isConnected.value = true;
        error.value = "";
      };

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data && data.id) {
            notifications.push({
              id: data.id,
              event_key: data.event_key ?? "",
              category: data.category ?? "info",
              priority: data.priority ?? "normal",
              title: data.title ?? "",
              message: data.message ?? "",
              is_read: false,
              is_pinned: false,
              is_critical: data.is_critical ?? false,
              created_at: data.created_at ?? new Date().toISOString(),
              time_ago: "just now",
            });
            if (data.event_key === "wallet_update") {
              wallet.fetchWallet().catch(() => undefined);
            }
          }
        } catch { /* ignore malformed frames */ }
      };

      ws.onerror = () => {
        error.value = "Notification stream disconnected.";
        isConnected.value = false;
      };

      ws.onclose = (evt) => {
        isConnected.value = false;
        // 4001 = server rejected due to invalid/expired token — don't reconnect,
        // let the response interceptor handle session expiry and redirect to login.
        if (!stopped && auth.accessToken && evt.code !== 4001) {
          wsTimer = setTimeout(connectWs, WS_RECONNECT_DELAY_MS);
        }
      };
    } catch {
      // WebSocket not available (server-side render, test env, etc.)
    }
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  function start() {
    stopped = false;
    startPolling();
    connectWs();
  }

  function stop() {
    stopped = true;
    stopPolling();
    stopWs();
    isConnected.value = false;
  }

  watch(() => auth.accessToken, (token) => {
    if (token) start();
    else stop();
  }, { immediate: true });

  onUnmounted(stop);

  return { notifications, isConnected, error, connect: start, disconnect: stop };
}
