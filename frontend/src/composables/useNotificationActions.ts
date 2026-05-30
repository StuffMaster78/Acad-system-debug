/**
 * useNotificationActions
 *
 * Watches the notification feed and dispatches store refreshes when
 * specific event keys arrive. Mount this once in the app layout so
 * file unlock, order state changes, and bid events update the UI
 * without requiring a full page reload.
 */
import { watch } from "vue";
import { useNotificationStore } from "@/stores/notifications";

// Lazy store imports to avoid circular dependency at module load time.
function getFilesStore() {
  const { useFilesStore } = require("@/stores/files");
  return useFilesStore();
}
function getOrderStore() {
  const { useOrderStore } = require("@/stores/orders");
  return useOrderStore();
}

// Event keys that should trigger a files store refresh.
const FILE_REFRESH_EVENTS = new Set([
  "file.delivery_unlocked",
  "file.uploaded",
  "file.approved",
]);

// Event keys that should trigger an order store refresh.
const ORDER_REFRESH_EVENTS = new Set([
  "order.on_hold",
  "order.reopened",
  "order.completed",
  "order.cancelled",
  "order.submitted",
  "order.assigned",
  "order.bid.accepted",
  "order.bid.rejected",
  "order.revision_requested",
]);

export function useNotificationActions() {
  const notifs = useNotificationStore();

  // Watch for new notifications (items grows when pollUnreadCount pushes one).
  watch(
    () => notifs.items.length,
    (newLen, oldLen) => {
      if (newLen <= oldLen) return;

      // The newest item is at index 0 (items are prepended).
      const latest = notifs.items[0];
      if (!latest?.event_key) return;

      const key = latest.event_key;

      if (FILE_REFRESH_EVENTS.has(key)) {
        try {
          const filesStore = getFilesStore();
          // fetchOrderAttachments requires an orderId — extract from notification metadata if available.
          // If unavailable, a broader refetch can be triggered by the parent component instead.
          // We just clear the delivery-blocked state so the UI is ready for re-download.
          filesStore.clearMessages();
        } catch {
          // Store not yet loaded — no-op.
        }
      }

      if (ORDER_REFRESH_EVENTS.has(key)) {
        try {
          const orderStore = getOrderStore();
          if (typeof orderStore.fetchOrders === "function") {
            orderStore.fetchOrders().catch(() => undefined);
          }
        } catch {
          // Store not yet loaded — no-op.
        }
      }
    },
  );
}
