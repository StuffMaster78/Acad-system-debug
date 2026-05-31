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
import { useFilesStore } from "@/stores/files";
import { useOrderStore } from "@/stores/orders";

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
  const filesStore = useFilesStore();
  const orderStore = useOrderStore();

  watch(
    () => notifs.items.length,
    (newLen, oldLen) => {
      if (newLen <= oldLen) return;

      const latest = notifs.items[0];
      if (!latest?.event_key) return;

      const key = latest.event_key;

      if (FILE_REFRESH_EVENTS.has(key)) {
        filesStore.clearMessages();
      }

      if (ORDER_REFRESH_EVENTS.has(key)) {
        if (typeof orderStore.fetchOrders === "function") {
          orderStore.fetchOrders().catch(() => undefined);
        }
      }
    },
  );
}
