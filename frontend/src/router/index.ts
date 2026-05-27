import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { roleHome } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const DashboardLayout = () => import("@/layouts/DashboardLayout.vue");
const PublicLayout = () => import("@/layouts/PublicLayout.vue");
const RoleDashboard = () => import("@/views/dashboard/RoleDashboard.vue");

function roleRoute(role: UserRole): RouteRecordRaw {
  const roleChildren: RouteRecordRaw[] = [
    {
      path: "",
      name: `${role}-dashboard`,
      component: RoleDashboard,
      props: { role },
    },
    {
      path: "activity",
      name: `${role}-activity`,
      component: () => import("@/views/shared/ActivityView.vue"),
      props: { role },
    },
    {
      path: "notifications",
      name: `${role}-notifications`,
      component: () => import("@/views/shared/NotificationsView.vue"),
      props: { role },
    },
    {
      path: "account",
      name: `${role}-account`,
      component: () => import("@/views/shared/AccountView.vue"),
      props: { role },
    },
    {
      path: ":section",
      name: `${role}-section`,
      component: RoleDashboard,
      props: { role },
    },
  ];

  if (role === "client") {
    roleChildren.splice(
      1,
      0,
      {
        path: "orders",
        name: "client-orders",
        component: () => import("@/views/client/ClientOrdersView.vue"),
      },
      {
        path: "orders/:id",
        name: "client-order-detail",
        component: () => import("@/views/client/ClientOrderDetailView.vue"),
      },
      {
        path: "support",
        name: "client-support",
        component: () => import("@/views/client/ClientSupportView.vue"),
      },
      {
        path: "new-order",
        name: "client-new-order",
        component: () => import("@/views/client/NewOrderView.vue"),
      },
      {
        path: "messages",
        name: "client-messages",
        component: () => import("@/views/client/ClientMessagesView.vue"),
      },
      {
        path: "wallet",
        name: "client-wallet",
        component: () => import("@/views/client/ClientWalletView.vue"),
      },
    );
  }

  if (role === "admin") {
    roleChildren.splice(
      1,
      0,
      {
        path: "orders",
        name: "admin-orders",
        component: () => import("@/views/admin/AdminOrdersView.vue"),
      },
      {
        path: "ops",
        name: "admin-ops",
        component: () => import("@/views/admin/AdminOpsView.vue"),
      },
      {
        path: "files",
        name: "admin-files",
        component: () => import("@/views/admin/AdminFilesView.vue"),
      },
      {
        path: "writers",
        name: "admin-writers",
        component: () => import("@/views/admin/AdminWritersView.vue"),
      },
      {
        path: "clients",
        name: "admin-clients",
        component: () => import("@/views/admin/AdminClientsView.vue"),
      },
      {
        path: "payments",
        name: "admin-payments",
        component: () => import("@/views/admin/AdminPaymentsView.vue"),
      },
      {
        path: "wallets",
        name: "admin-wallets",
        component: () => import("@/views/admin/AdminWalletsView.vue"),
      },
      {
        path: "access",
        name: "admin-access",
        component: () => import("@/views/admin/AdminAccessView.vue"),
      },
      {
        path: "communications",
        name: "admin-communications",
        component: () => import("@/views/admin/AdminCommsView.vue"),
      },
      {
        path: "growth",
        name: "admin-growth",
        component: () => import("@/views/admin/AdminGrowthView.vue"),
      },
      {
        path: "publishing",
        name: "admin-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "settings",
        name: "admin-settings",
        component: () => import("@/views/admin/AdminSettingsView.vue"),
      },
      {
        path: "analytics",
        name: "admin-analytics",
        component: () => import("@/views/admin/AdminAnalyticsView.vue"),
      },
      {
        path: "support",
        name: "admin-support",
        component: () => import("@/views/admin/AdminSupportView.vue"),
      },
      {
        path: "config",
        name: "admin-config",
        component: () => import("@/views/admin/AdminConfigHubView.vue"),
      },
    );
  }

  if (role === "writer") {
    roleChildren[0] = {
      path: "",
      name: "writer-dashboard",
      component: () => import("@/views/writer/WriterWorkspaceView.vue"),
    };

    roleChildren.splice(
      1,
      0,
      {
        path: "available",
        name: "writer-available",
        component: () => import("@/views/writer/WriterAvailableView.vue"),
      },
      {
        path: "assignments",
        name: "writer-assignments",
        component: () => import("@/views/writer/WriterAssignmentsView.vue"),
      },
      {
        path: "orders/:id",
        name: "writer-order-detail",
        component: () => import("@/views/writer/WriterOrderDetailView.vue"),
      },
      {
        path: "earnings",
        name: "writer-earnings",
        component: () => import("@/views/writer/WriterEarningsView.vue"),
      },
      {
        path: "messages",
        name: "writer-messages",
        component: () => import("@/views/writer/WriterMessagesView.vue"),
      },
    );
  }

  if (role === "editor") {
    roleChildren[0] = {
      path: "",
      name: "editor-dashboard",
      component: () => import("@/views/editor/EditorWorkspaceView.vue"),
    };

    roleChildren.splice(
      1,
      0,
      {
        path: "qa",
        name: "editor-qa",
        component: () => import("@/views/editor/EditorQAView.vue"),
      },
      {
        path: "publishing",
        name: "editor-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "workload",
        name: "editor-workload",
        component: () => import("@/views/editor/EditorWorkloadView.vue"),
      },
      {
        path: "analytics",
        name: "editor-analytics",
        component: () => import("@/views/editor/EditorAnalyticsView.vue"),
      },
      {
        path: "messages",
        name: "editor-messages",
        component: () => import("@/views/editor/EditorMessagesView.vue"),
      },
      {
        path: "config",
        name: "editor-config",
        component: () => import("@/views/admin/AdminConfigHubView.vue"),
      },
    );
  }

  if (role === "support") {
    roleChildren[0] = {
      path: "",
      name: "support-dashboard",
      component: () => import("@/views/support/SupportWorkspaceView.vue"),
    };

    roleChildren.splice(
      1,
      0,
      {
        path: "tickets",
        name: "support-tickets",
        component: () => import("@/views/support/SupportTicketsView.vue"),
      },
      {
        path: "tickets/:id",
        name: "support-ticket-detail",
        component: () => import("@/views/support/SupportTicketDetailView.vue"),
      },
      {
        path: "orders",
        name: "support-orders",
        component: () => import("@/views/support/SupportOrdersView.vue"),
      },
      {
        path: "publishing",
        name: "support-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "escalations",
        name: "support-escalations",
        component: () => import("@/views/support/SupportEscalationsView.vue"),
      },
      {
        path: "replies",
        name: "support-replies",
        component: () => import("@/views/support/SupportRepliesView.vue"),
      },
      {
        path: "messages",
        name: "support-messages",
        component: () => import("@/views/support/SupportMessagesView.vue"),
      },
      {
        path: "config",
        name: "support-config",
        component: () => import("@/views/admin/AdminConfigHubView.vue"),
      },
    );
  }

  if (role === "superadmin") {
    roleChildren[0] = {
      path: "",
      name: "superadmin-dashboard",
      component: () => import("@/views/superadmin/SuperadminCommandView.vue"),
    };

    roleChildren.splice(
      1,
      0,
      {
        path: "tenants",
        name: "superadmin-tenants",
        component: () => import("@/views/superadmin/SuperadminCommandView.vue"),
      },
      {
        path: "ops",
        name: "superadmin-ops",
        component: () => import("@/views/admin/AdminOpsView.vue"),
      },
      {
        path: "orders",
        name: "superadmin-orders",
        component: () => import("@/views/admin/AdminOrdersView.vue"),
      },
      {
        path: "writers",
        name: "superadmin-writers",
        component: () => import("@/views/admin/AdminWritersView.vue"),
      },
      {
        path: "clients",
        name: "superadmin-clients",
        component: () => import("@/views/admin/AdminClientsView.vue"),
      },
      {
        path: "payments",
        name: "superadmin-payments",
        component: () => import("@/views/superadmin/SuperadminFinanceView.vue"),
      },
      {
        path: "wallets",
        name: "superadmin-wallets",
        component: () => import("@/views/admin/AdminWalletsView.vue"),
      },
      {
        path: "access",
        name: "superadmin-access",
        component: () => import("@/views/admin/AdminAccessView.vue"),
      },
      {
        path: "communications",
        name: "superadmin-communications",
        component: () => import("@/views/admin/AdminCommsView.vue"),
      },
      {
        path: "growth",
        name: "superadmin-growth",
        component: () => import("@/views/admin/AdminGrowthView.vue"),
      },
      {
        path: "publishing",
        name: "superadmin-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "files",
        name: "superadmin-files",
        component: () => import("@/views/admin/AdminFilesView.vue"),
      },
      {
        path: "analytics",
        name: "superadmin-analytics",
        component: () => import("@/views/admin/AdminAnalyticsView.vue"),
      },
      {
        path: "operations",
        name: "superadmin-operations",
        component: () => import("@/views/superadmin/SuperadminCommandView.vue"),
      },
      {
        path: "finance",
        name: "superadmin-finance",
        component: () => import("@/views/superadmin/SuperadminFinanceView.vue"),
      },
      {
        path: "settings",
        name: "superadmin-settings",
        component: () => import("@/views/admin/AdminSettingsView.vue"),
      },
      {
        path: "support",
        name: "superadmin-support",
        component: () => import("@/views/admin/AdminSupportView.vue"),
      },
      {
        path: "config",
        name: "superadmin-config",
        component: () => import("@/views/admin/AdminConfigHubView.vue"),
      },
    );
  }

  return {
    path: `/${role}`,
    component: DashboardLayout,
    props: { role },
    meta: { roles: [role] },
    children: roleChildren,
  };
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: PublicLayout,
      children: [
        { path: "", name: "home", component: () => import("@/views/public/HomeView.vue") },
        {
          path: "services",
          name: "services",
          component: () => import("@/views/public/ServicesView.vue"),
        },
      ],
    },
    {
      path: "/auth/login",
      name: "login",
      component: () => import("@/views/auth/LoginView.vue"),
    },
    {
      path: "/auth/forgot-password",
      name: "forgot-password",
      component: () => import("@/views/auth/ForgotPasswordView.vue"),
    },
    {
      path: "/auth/reset-password",
      name: "reset-password",
      component: () => import("@/views/auth/ResetPasswordView.vue"),
    },
    roleRoute("client"),
    roleRoute("writer"),
    roleRoute("editor"),
    roleRoute("support"),
    roleRoute("admin"),
    roleRoute("superadmin"),
    {
      path: "/unauthorized",
      name: "unauthorized",
      component: () => import("@/views/public/HomeView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/public/NotFoundView.vue"),
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  const roles = to.meta.roles as UserRole[] | undefined;

  if (roles?.length && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  if (roles?.length && (!auth.role || !roles.includes(auth.role))) {
    if (auth.role) return roleHome[auth.role];
    return { name: "unauthorized" };
  }

  return true;
});
