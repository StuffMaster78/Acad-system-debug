import {
  BarChart3,
  BriefcaseBusiness,
  ClipboardList,
  CreditCard,
  FileText,
  FolderOpen,
  Gauge,
  Headphones,
  Home,
  Inbox,
  LifeBuoy,
  Megaphone,
  MessageSquare,
  Newspaper,
  Settings,
  ShieldCheck,
  Users,
  Wallet,
} from "@lucide/vue";
import type { Component } from "vue";
import type { UserRole } from "@/types/roles";

export interface NavItem {
  label: string;
  to: string;
  icon: Component;
}

export const roleHome: Record<UserRole, string> = {
  superadmin: "/superadmin",
  admin: "/admin",
  writer: "/writer",
  client: "/client",
  editor: "/editor",
  support: "/support",
};

export const navigationByRole: Record<UserRole, NavItem[]> = {
  superadmin: [
    { label: "Command", to: "/superadmin", icon: ShieldCheck },
    { label: "Tenants", to: "/superadmin/tenants", icon: BriefcaseBusiness },
    { label: "Operations", to: "/superadmin/operations", icon: Gauge },
    { label: "Finance", to: "/superadmin/finance", icon: CreditCard },
    { label: "Settings", to: "/superadmin/settings", icon: Settings },
  ],
  admin: [
    { label: "Operations", to: "/admin", icon: Gauge },
    { label: "Orders", to: "/admin/orders", icon: ClipboardList },
    { label: "Writers", to: "/admin/writers", icon: Users },
    { label: "Clients", to: "/admin/clients", icon: Users },
    { label: "Payments", to: "/admin/payments", icon: CreditCard },
    { label: "Comms", to: "/admin/communications", icon: Megaphone },
    { label: "Publishing", to: "/admin/publishing", icon: Newspaper },
    { label: "Files", to: "/admin/files", icon: FolderOpen },
    { label: "Analytics", to: "/admin/analytics", icon: BarChart3 },
    { label: "Settings", to: "/admin/settings", icon: Settings },
    { label: "Support", to: "/admin/support", icon: LifeBuoy },
  ],
  writer: [
    { label: "Workspace", to: "/writer", icon: Home },
    { label: "Available", to: "/writer/available", icon: Inbox },
    { label: "Assignments", to: "/writer/assignments", icon: ClipboardList },
    { label: "Earnings", to: "/writer/earnings", icon: Wallet },
    { label: "Messages", to: "/writer/messages", icon: MessageSquare },
  ],
  client: [
    { label: "Home", to: "/client", icon: Home },
    { label: "Orders", to: "/client/orders", icon: ClipboardList },
    { label: "New Order", to: "/client/new-order", icon: FileText },
    { label: "Wallet", to: "/client/wallet", icon: Wallet },
    { label: "Messages", to: "/client/messages", icon: MessageSquare },
  ],
  editor: [
    { label: "Desk", to: "/editor", icon: Home },
    { label: "QA Queue", to: "/editor/qa", icon: ClipboardList },
    { label: "Workload", to: "/editor/workload", icon: Gauge },
    { label: "Analytics", to: "/editor/analytics", icon: BarChart3 },
  ],
  support: [
    { label: "Queue", to: "/support", icon: Headphones },
    { label: "Tickets", to: "/support/tickets", icon: LifeBuoy },
    { label: "Orders", to: "/support/orders", icon: ClipboardList },
    { label: "Escalations", to: "/support/escalations", icon: ShieldCheck },
    { label: "Saved Replies", to: "/support/replies", icon: MessageSquare },
  ],
};
