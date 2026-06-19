import { computed, ref } from "vue";
import type { MetricDefinition, WorkItem } from "@/config/dashboard";
import type { UserRole } from "@/types/roles";
import { api, apiPath } from "@/api/client";
import { useCommunicationsStore } from "@/stores/communications";
import { useAdminWorkStore } from "@/stores/adminWork";
import { useEditorWorkspaceStore } from "@/stores/editorWorkspace";
import { useOrderStore } from "@/stores/orders";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";
import { useWalletStore } from "@/stores/wallets";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import { useSuperadminWorkspaceStore } from "@/stores/superadminWorkspace";

function money(v: string | number | null | undefined): string {
  if (!v) return "$0.00";
  const n = Number(v);
  if (Number.isNaN(n)) return String(v);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

export function useDashboardData(role: UserRole) {
  const orders = useOrderStore();
  const wallets = useWalletStore();
  const comms = useCommunicationsStore();
  const writerWs = useWriterWorkspaceStore();
  const editorWs = useEditorWorkspaceStore();
  const supportWs = useSupportWorkspaceStore();
  const adminWork = useAdminWorkStore();
  const superadminWs = useSuperadminWorkspaceStore();

  // Client loyalty summary — loaded once on dashboard mount.
  const loyaltyTier = ref<string | null>(null);
  const loyaltyPoints = ref<number>(0);

  const isLoading = computed(() => {
    if (role === "client") return orders.isLoading || wallets.isLoading;
    if (role === "writer") return writerWs.isLoading;
    if (role === "editor") return editorWs.isLoading;
    if (role === "support") return supportWs.isLoading;
    if (role === "superadmin") return superadminWs.isLoading;
    return adminWork.isLoading;
  });

  const error = computed(() => {
    if (role === "client") return orders.error;
    if (role === "writer") return writerWs.error;
    if (role === "editor") return editorWs.error;
    if (role === "support") return supportWs.error;
    if (role === "superadmin") return superadminWs.error;
    return adminWork.error;
  });

  const metrics = computed<MetricDefinition[]>(() => {
    if (role === "client") {
      const awaitingPayment = orders.openOrders.filter((o) => o.payment_status !== "paid").length;
      const completed = orders.orders.filter((o) => o.status === "completed").length;
      return [
        {
          label: "Active orders",
          value: String(orders.openOrders.length),
          detail: awaitingPayment ? `${awaitingPayment} awaiting payment` : "All payments current",
          tone: awaitingPayment ? "warn" : "neutral",
        },
        {
          label: "Completed",
          value: String(completed),
          detail: "Historical orders",
          tone: "good",
        },
        {
          label: "Wallet",
          value: `${wallets.currency} ${wallets.availableBalance.toFixed(2)}`,
          detail: "Available balance",
          tone: "neutral",
        },
        {
          label: loyaltyTier.value ? `${loyaltyTier.value} tier` : "Loyalty",
          value: String(loyaltyPoints.value),
          detail: loyaltyTier.value ? "Loyalty points" : "Earn points on every order",
          tone: loyaltyTier.value ? "good" : "neutral",
        },
      ];
    }

    if (role === "writer") {
      return [
        {
          label: "Current window",
          value: money(writerWs.currentWindow?.net),
          detail: `${writerWs.currentWindow?.count ?? 0} earnings events`,
          tone: "good",
        },
        {
          label: "Pending balance",
          value: money(writerWs.balance?.pending),
          detail: "Not yet matured",
          tone: "warn",
        },
        {
          label: "Orders completed",
          value: String(writerWs.summary?.completed_orders ?? 0),
          detail: "Lifetime total",
          tone: "neutral",
        },
        {
          label: "Status",
          value: writerWs.isAcceptingOrders ? "Open" : "Paused",
          detail: writerWs.isAcceptingOrders ? "Accepting new assignments" : "Paused for new work",
          tone: writerWs.isAcceptingOrders ? "good" : "warn",
        },
      ];
    }

    if (role === "editor") return editorWs.metrics;

    if (role === "support") return supportWs.metrics as MetricDefinition[];

    if (role === "superadmin") {
      return superadminWs.metrics.map((m) => ({
        label: m.label,
        value: String(m.value),
        detail: m.detail,
        tone: m.tone as MetricDefinition["tone"],
      }));
    }

    // admin
    return adminWork.metrics.map((m) => ({
      label: m.label,
      value: String(m.value),
      detail: m.detail,
      tone: m.tone as MetricDefinition["tone"],
    }));
  });

  const workItems = computed<WorkItem[]>(() => {
    if (role === "client") {
      return orders.openOrders.slice(0, 3).map((o) => ({
        title: `#${o.id} ${o.topic}`,
        meta: o.client_deadline
          ? `Due ${new Date(o.client_deadline).toLocaleDateString()}`
          : "No deadline set",
        status: o.payment_status !== "paid" ? "Awaiting payment" : o.status,
        link: `/client/orders/${o.id}`,
      }));
    }

    if (role === "writer") {
      const items = writerWs.assignments.length ? writerWs.assignments : [];
      return items.slice(0, 3).map((order) => {
        const deadline = order.client_deadline ? new Date(order.client_deadline) : null;
        const hoursLeft = deadline
          ? Math.round((deadline.getTime() - Date.now()) / 3600000)
          : null;
        const dueMeta =
          hoursLeft == null
            ? "No deadline"
            : hoursLeft < 0
              ? `${Math.abs(hoursLeft)}h overdue`
              : hoursLeft < 24
                ? `Due in ${hoursLeft}h`
                : `Due ${deadline!.toLocaleDateString()}`;
        return {
          title: order.topic ?? `Order #${order.id}`,
          meta: dueMeta,
          status: hoursLeft !== null && hoursLeft < 0 ? "Overdue" : order.status ?? "In progress",
          link: `/writer/orders/${order.id}`,
        };
      });
    }

    if (role === "editor") {
      return editorWs.activeTasks.slice(0, 3).map((task) => {
        const diffH = task.order_deadline
          ? Math.round((new Date(task.order_deadline).getTime() - Date.now()) / 3600000)
          : null;
        const dueMeta =
          diffH == null ? "No deadline" : diffH < 0 ? `${Math.abs(diffH)}h overdue` : `${diffH}h left`;
        return {
          title: task.order_topic || `Order #${task.order_id}`,
          meta: dueMeta,
          status: task.review_status ?? "pending",
          link: `/editor/qa`,
        };
      });
    }

    if (role === "support") {
      return supportWs.filteredTickets.slice(0, 3).map((ticket) => ({
        title: ticket.title,
        meta: ticket.category ?? "support",
        status: ticket.priority,
        link: `/support/tickets`,
      }));
    }

    if (role === "superadmin") {
      return superadminWs.activeTenants.slice(0, 3).map((tenant) => ({
        title: tenant.name ?? tenant.domain ?? `Tenant #${tenant.id}`,
        meta: `${tenant.domain} · ${tenant.user_count ?? 0} users`,
        status: tenant.is_active === false ? "Inactive" : "Active",
        link: `/superadmin/tenants`,
      }));
    }

    // admin
    return adminWork.filteredItems.slice(0, 3).map((item) => ({
      title: `${item.reference} ${item.title}`,
      meta: `${item.website} · ${item.client}`,
      status: item.status,
      link: `/admin/orders`,
    }));
  });

  const primaryActionTo = computed(() => {
    const routes: Record<UserRole, string> = {
      client: "/client/new-order",
      writer: "/writer/available",
      editor: "/editor/qa",
      support: "/support/tickets",
      admin: "/admin/orders",
      superadmin: "/superadmin/tenants",
    };
    return routes[role];
  });

  async function load() {
    if (role === "client") {
      await Promise.allSettled([
        orders.fetchOrders(),
        wallets.fetchWallet(),
        comms.loadInboxThreads(),
        api
          .get<{ loyalty_points?: number; tier?: string }>(
            apiPath("/loyalty-management/loyalty/summary/"),
          )
          .then(({ data }) => {
            loyaltyPoints.value = data.loyalty_points ?? 0;
            loyaltyTier.value = data.tier ?? null;
          })
          .catch(() => undefined),
      ]);
    } else if (role === "writer") {
      await Promise.allSettled([writerWs.hydrate(), writerWs.fetchAssignments()]);
    } else if (role === "editor") {
      await editorWs.hydrate();
    } else if (role === "support") {
      await supportWs.hydrate();
    } else if (role === "superadmin") {
      await superadminWs.hydrate();
    } else {
      await adminWork.refresh();
    }
  }

  return { isLoading, error, metrics, workItems, primaryActionTo, load };
}
