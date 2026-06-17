import type { InjectionKey, Ref } from "vue";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import type { UserRole } from "@/types/roles";

export interface OrderDetailContext {
  orderId: Ref<string>;
  order: Ref<OrderSummary | null>;
  lifecycle: Ref<OrderLifecycle | null>;
  role: UserRole;
}

export const ORDER_DETAIL_KEY: InjectionKey<OrderDetailContext> = Symbol("order-detail");

// Which tabs each role may access
export const ROLE_TABS: Record<UserRole, string[]> = {
  client: ["details", "files", "messages", "payments", "revisions", "adjustments", "timeline"],
  writer: ["details", "files", "messages", "revisions", "adjustments", "timeline"],
  support: ["details", "files", "messages", "payments", "revisions", "adjustments", "timeline"],
  editor: ["details", "files", "messages", "quality", "timeline"],
  admin: ["details", "files", "messages", "payments", "staffing", "revisions", "adjustments", "quality", "timeline", "audit"],
  superadmin: ["details", "files", "messages", "payments", "staffing", "revisions", "adjustments", "quality", "timeline", "audit"],
};

export const TAB_LABELS: Record<string, string> = {
  details: "Details",
  files: "Files",
  messages: "Messages",
  payments: "Payments",
  staffing: "Staffing",
  revisions: "Revisions",
  adjustments: "Scope Changes",
  quality: "Quality",
  timeline: "Timeline",
  audit: "Audit",
};

// Masked identity helpers — display only.
// Server-side enforcement: OrderListSerializer.to_representation() strips
// client_username from writer responses and writer_username from client responses.
export function maskedClient(order: OrderSummary): string {
  if (order.client_registration_id) return `Client #${order.client_registration_id}`;
  if (order.client) return `Client #C${String(order.client).padStart(4, "0")}`;
  return "Client (guest)";
}

export function maskedWriter(writerId: number | null | undefined): string {
  if (writerId) return `Writer #W${String(writerId).padStart(4, "0")}`;
  return "Unassigned";
}

export function backRoute(role: UserRole): string {
  const map: Record<UserRole, string> = {
    client: "/client/orders",
    writer: "/writer/assignments",
    support: "/support/orders",
    editor: "/editor/qa",
    admin: "/admin/orders",
    superadmin: "/superadmin/orders",
  };
  return map[role] ?? "/";
}

export function dateLabel(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", {
    month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  }).format(new Date(value));
}

export function deadlineCountdown(value: string | null | undefined): string {
  if (!value) return "";
  const h = (new Date(value).getTime() - Date.now()) / 3_600_000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

export function isStaff(role: UserRole): boolean {
  return role === "admin" || role === "superadmin" || role === "support" || role === "editor";
}
