import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { roleHome } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import type { UserRole } from "@/types/roles";

const ROLE_SURFACE: Record<UserRole, string> = {
  client: "client",
  writer: "writer",
  editor: "staff",
  support: "staff",
  admin: "staff",
  superadmin: "staff",
};

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
      path: "announcements",
      name: `${role}-announcements`,
      component: () => import("@/views/shared/AnnouncementsView.vue"),
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
      {
        path: "billing",
        name: "client-billing",
        component: () => import("@/views/client/ClientBillingView.vue"),
      },
      {
        path: "loyalty",
        name: "client-loyalty",
        component: () => import("@/views/client/ClientLoyaltyView.vue"),
      },
      {
        path: "charts",
        name: "client-charts",
        component: () => import("@/views/client/ClientChartsView.vue"),
      },
      {
        path: "classes",
        name: "client-classes",
        component: () => import("@/views/client/ClientClassesView.vue"),
      },
      {
        path: "classes/new",
        name: "client-class-new",
        component: () => import("@/views/client/NewClassView.vue"),
      },
      {
        path: "classes/:id",
        name: "client-class-detail",
        component: () => import("@/views/client/ClientClassDetailView.vue"),
      },
      {
        path: "special-orders",
        name: "client-special-orders",
        component: () => import("@/views/client/ClientSpecialOrdersView.vue"),
      },
      {
        path: "special-orders/new",
        name: "client-special-order-new",
        component: () => import("@/views/client/NewSpecialOrderView.vue"),
      },
      {
        path: "special-orders/express",
        name: "client-special-order-express",
        component: () => import("@/views/client/NewExpressSpecialOrderView.vue"),
      },
      {
        path: "special-orders/:id",
        name: "client-special-order-detail",
        component: () => import("@/views/client/ClientSpecialOrderDetailView.vue"),
      },
      {
        path: "disputes",
        name: "client-disputes",
        component: () => import("@/views/client/ClientDisputesView.vue"),
      },
      {
        path: "referrals",
        name: "client-referrals",
        component: () => import("@/views/client/ClientReferralsView.vue"),
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
        path: "orders/:id",
        name: "admin-order-detail",
        component: () => import("@/views/admin/AdminOrderDetailView.vue"),
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
        path: "clients/:id",
        name: "admin-client-profile",
        component: () => import("@/views/admin/AdminClientProfileView.vue"),
      },
      {
        path: "editors",
        name: "admin-editors",
        component: () => import("@/views/admin/AdminAccessView.vue"),
        meta: { roleFilter: "editor" },
      },
      {
        path: "support-staff",
        name: "admin-support-staff",
        component: () => import("@/views/admin/AdminAccessView.vue"),
        meta: { roleFilter: "support" },
      },
      {
        path: "payments",
        name: "admin-payments",
        component: () => import("@/views/admin/AdminPaymentsView.vue"),
      },
      {
        path: "refunds",
        name: "admin-refunds",
        component: () => import("@/views/admin/AdminRefundsView.vue"),
      },
      {
        path: "wallets",
        name: "admin-wallets",
        component: () => import("@/views/admin/AdminWalletsView.vue"),
      },
      {
        path: "ledger",
        name: "admin-ledger",
        component: () => import("@/views/admin/AdminLedgerView.vue"),
      },
      {
        path: "access",
        name: "admin-access",
        component: () => import("@/views/admin/AdminAccessView.vue"),
      },
      {
        path: "users/:id",
        name: "admin-user-profile",
        component: () => import("@/views/admin/AdminUserProfileView.vue"),
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
        path: "loyalty",
        name: "admin-loyalty",
        component: () => import("@/views/admin/AdminLoyaltyView.vue"),
      },
      {
        path: "holidays",
        name: "admin-holidays",
        component: () => import("@/views/admin/AdminHolidaysView.vue"),
      },
      {
        path: "publishing",
        name: "admin-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "content",
        name: "admin-content",
        component: () => import("@/views/admin/AdminContentView.vue"),
      },
      {
        path: "content-graph",
        name: "admin-content-graph",
        component: () => import("@/views/admin/AdminContentGraphView.vue"),
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
        path: "charts",
        name: "admin-charts",
        component: () => import("@/views/admin/AdminChartsView.vue"),
      },
      {
        path: "support",
        name: "admin-support",
        component: () => import("@/views/admin/AdminSupportView.vue"),
      },
      {
        path: "website",
        name: "admin-website",
        component: () => import("@/views/admin/AdminWebsiteView.vue"),
      },
      {
        path: "compensation",
        name: "admin-compensation",
        component: () => import("@/views/admin/AdminCompensationView.vue"),
      },
      {
        path: "email",
        name: "admin-email",
        component: () => import("@/views/admin/AdminEmailDeliveryView.vue"),
      },
      {
        path: "rewards",
        name: "admin-rewards",
        component: () => import("@/views/admin/AdminRewardsView.vue"),
      },
      {
        path: "reputation",
        name: "admin-reputation",
        component: () => import("@/views/admin/AdminReputationView.vue"),
      },
      {
        path: "financials",
        name: "admin-financials",
        component: () => import("@/views/admin/AdminFinancialCenterView.vue"),
      },
      {
        path: "financial-events",
        name: "admin-financial-events",
        component: () => import("@/views/admin/AdminFinancialEventsView.vue"),
      },
      {
        path: "discounts",
        name: "admin-discounts",
        component: () => import("@/views/admin/AdminDiscountsView.vue"),
      },
      {
        path: "config",
        name: "admin-config",
        component: () => import("@/views/admin/AdminConfigHubView.vue"),
      },
      {
        path: "bids",
        name: "admin-bids",
        component: () => import("@/views/admin/AdminBidsView.vue"),
      },
      {
        path: "classes",
        name: "admin-classes",
        component: () => import("@/views/admin/AdminClassesView.vue"),
      },
      {
        path: "classes/:id",
        name: "admin-class-detail",
        component: () => import("@/views/admin/AdminClassDetailView.vue"),
      },
      {
        path: "special-orders",
        name: "admin-special-orders",
        component: () => import("@/views/admin/AdminSpecialOrdersView.vue"),
      },
      {
        path: "special-orders/:id",
        name: "admin-special-order-detail",
        component: () => import("@/views/admin/AdminSpecialOrderDetailView.vue"),
      },
      {
        path: "disputes",
        name: "admin-disputes",
        component: () => import("@/views/admin/AdminDisputesView.vue"),
      },
      {
        path: "reviews",
        name: "admin-reviews",
        component: () => import("@/views/admin/AdminReviewsView.vue"),
      },
      {
        path: "writers/:id",
        name: "admin-writer-profile",
        component: () => import("@/views/admin/AdminWriterProfileView.vue"),
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
        path: "calendar",
        name: "writer-calendar",
        component: () => import("@/views/writer/WriterCalendarView.vue"),
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
        path: "charts",
        name: "writer-charts",
        component: () => import("@/views/writer/WriterChartsView.vue"),
      },
      {
        path: "bids",
        name: "writer-bids",
        component: () => import("@/views/writer/WriterBidsView.vue"),
      },
      {
        path: "fines",
        name: "writer-fines",
        component: () => import("@/views/writer/WriterFinesView.vue"),
      },
      {
        path: "messages",
        name: "writer-messages",
        component: () => import("@/views/writer/WriterMessagesView.vue"),
      },
      {
        path: "classes",
        name: "writer-classes",
        component: () => import("@/views/writer/WriterClassesView.vue"),
      },
      {
        path: "classes/:id",
        name: "writer-class-detail",
        component: () => import("@/views/writer/WriterClassDetailView.vue"),
      },
      {
        path: "special-orders",
        name: "writer-special-orders",
        component: () => import("@/views/writer/WriterSpecialOrdersView.vue"),
      },
      {
        path: "special-orders/:id",
        name: "writer-special-order-detail",
        component: () => import("@/views/writer/WriterSpecialOrderDetailView.vue"),
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
        path: "orders/:id",
        name: "editor-order-detail",
        component: () => import("@/views/editor/EditorOrderDetailView.vue"),
      },
      {
        path: "writers/:id",
        name: "editor-writer-profile",
        component: () => import("@/views/admin/AdminWriterProfileView.vue"),
      },
      {
        path: "publishing",
        name: "editor-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "content",
        name: "editor-content",
        component: () => import("@/views/admin/AdminContentView.vue"),
      },
      {
        path: "content-graph",
        name: "editor-content-graph",
        component: () => import("@/views/admin/AdminContentGraphView.vue"),
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
        path: "charts",
        name: "editor-charts",
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
        path: "orders/:id",
        name: "support-order-detail",
        component: () => import("@/views/support/SupportOrderDetailView.vue"),
      },
      {
        path: "classes",
        name: "support-classes",
        component: () => import("@/views/admin/AdminClassesView.vue"),
      },
      {
        path: "classes/:id",
        name: "support-class-detail",
        component: () => import("@/views/admin/AdminClassDetailView.vue"),
      },
      {
        path: "special-orders",
        name: "support-special-orders",
        component: () => import("@/views/admin/AdminSpecialOrdersView.vue"),
      },
      {
        path: "special-orders/:id",
        name: "support-special-order-detail",
        component: () => import("@/views/admin/AdminSpecialOrderDetailView.vue"),
      },
      {
        path: "writers/:id",
        name: "support-writer-profile",
        component: () => import("@/views/admin/AdminWriterProfileView.vue"),
      },
      {
        path: "publishing",
        name: "support-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "content",
        name: "support-content",
        component: () => import("@/views/admin/AdminContentView.vue"),
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
      {
        path: "charts",
        name: "support-charts",
        component: () => import("@/views/support/SupportChartsView.vue"),
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
        path: "audit",
        name: "superadmin-audit",
        component: () => import("@/views/superadmin/SuperadminAuditView.vue"),
      },
      {
        path: "tenants",
        name: "superadmin-tenants",
        component: () => import("@/views/superadmin/SuperadminTenantsView.vue"),
      },
      {
        path: "tenants/:id",
        name: "superadmin-tenant-detail",
        component: () => import("@/views/superadmin/SuperadminTenantDetailView.vue"),
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
        path: "orders/:id",
        name: "superadmin-order-detail",
        component: () => import("@/views/admin/AdminOrderDetailView.vue"),
      },
      {
        path: "classes",
        name: "superadmin-classes",
        component: () => import("@/views/admin/AdminClassesView.vue"),
      },
      {
        path: "classes/:id",
        name: "superadmin-class-detail",
        component: () => import("@/views/admin/AdminClassDetailView.vue"),
      },
      {
        path: "special-orders",
        name: "superadmin-special-orders",
        component: () => import("@/views/admin/AdminSpecialOrdersView.vue"),
      },
      {
        path: "special-orders/:id",
        name: "superadmin-special-order-detail",
        component: () => import("@/views/admin/AdminSpecialOrderDetailView.vue"),
      },
      {
        path: "writers",
        name: "superadmin-writers",
        component: () => import("@/views/admin/AdminWritersView.vue"),
      },
      {
        path: "writers/:id",
        name: "superadmin-writer-profile",
        component: () => import("@/views/admin/AdminWriterProfileView.vue"),
      },
      {
        path: "clients",
        name: "superadmin-clients",
        component: () => import("@/views/admin/AdminClientsView.vue"),
      },
      {
        path: "clients/:id",
        name: "superadmin-client-profile",
        component: () => import("@/views/admin/AdminClientProfileView.vue"),
      },
      {
        path: "editors",
        name: "superadmin-editors",
        component: () => import("@/views/admin/AdminAccessView.vue"),
        meta: { roleFilter: "editor" },
      },
      {
        path: "support-staff",
        name: "superadmin-support-staff",
        component: () => import("@/views/admin/AdminAccessView.vue"),
        meta: { roleFilter: "support" },
      },
      {
        path: "payments",
        name: "superadmin-payments",
        component: () => import("@/views/superadmin/SuperadminFinanceView.vue"),
      },
      {
        path: "refunds",
        name: "superadmin-refunds",
        component: () => import("@/views/admin/AdminRefundsView.vue"),
      },
      {
        path: "wallets",
        name: "superadmin-wallets",
        component: () => import("@/views/admin/AdminWalletsView.vue"),
      },
      {
        path: "ledger",
        name: "superadmin-ledger",
        component: () => import("@/views/admin/AdminLedgerView.vue"),
      },
      {
        path: "access",
        name: "superadmin-access",
        component: () => import("@/views/admin/AdminAccessView.vue"),
      },
      {
        path: "users/:id",
        name: "superadmin-user-profile",
        component: () => import("@/views/admin/AdminUserProfileView.vue"),
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
        path: "loyalty",
        name: "superadmin-loyalty",
        component: () => import("@/views/admin/AdminLoyaltyView.vue"),
      },
      {
        path: "holidays",
        name: "superadmin-holidays",
        component: () => import("@/views/admin/AdminHolidaysView.vue"),
      },
      {
        path: "publishing",
        name: "superadmin-publishing",
        component: () => import("@/views/admin/AdminPublishingView.vue"),
      },
      {
        path: "content",
        name: "superadmin-content",
        component: () => import("@/views/admin/AdminContentView.vue"),
      },
      {
        path: "content-graph",
        name: "superadmin-content-graph",
        component: () => import("@/views/admin/AdminContentGraphView.vue"),
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
        path: "charts",
        name: "superadmin-charts",
        component: () => import("@/views/admin/AdminChartsView.vue"),
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
        path: "website",
        name: "superadmin-website",
        component: () => import("@/views/admin/AdminWebsiteView.vue"),
      },
      {
        path: "compensation",
        name: "superadmin-compensation",
        component: () => import("@/views/admin/AdminCompensationView.vue"),
      },
      {
        path: "email",
        name: "superadmin-email",
        component: () => import("@/views/admin/AdminEmailDeliveryView.vue"),
      },
      {
        path: "rewards",
        name: "superadmin-rewards",
        component: () => import("@/views/admin/AdminRewardsView.vue"),
      },
      {
        path: "reputation",
        name: "superadmin-reputation",
        component: () => import("@/views/admin/AdminReputationView.vue"),
      },
      {
        path: "financials",
        name: "superadmin-financials",
        component: () => import("@/views/admin/AdminFinancialCenterView.vue"),
      },
      {
        path: "financial-events",
        name: "superadmin-financial-events",
        component: () => import("@/views/admin/AdminFinancialEventsView.vue"),
      },
      {
        path: "discounts",
        name: "superadmin-discounts",
        component: () => import("@/views/admin/AdminDiscountsView.vue"),
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
    meta: { roles: [role], surface: ROLE_SURFACE[role] },
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
          meta: { surface: "client" },
          component: () => import("@/views/public/ServicesView.vue"),
        },
        {
          path: "services/:slug",
          name: "service-page",
          meta: { surface: "client" },
          component: () => import("@/views/public/ServicePageView.vue"),
        },
        {
          path: "blog",
          name: "blog",
          meta: { surface: "client" },
          component: () => import("@/views/public/BlogIndexView.vue"),
        },
        {
          path: "blog/:slug",
          name: "blog-post",
          meta: { surface: "client" },
          component: () => import("@/views/public/BlogPostView.vue"),
        },
        {
          path: "lp/:slug",
          name: "landing-page",
          meta: { surface: "client" },
          component: () => import("@/views/public/LandingPageView.vue"),
        },
        {
          path: "authors",
          name: "authors",
          meta: { surface: "client" },
          component: () => import("@/views/public/AuthorsView.vue"),
        },
        {
          path: "authors/:slug",
          name: "author",
          meta: { surface: "client" },
          component: () => import("@/views/public/AuthorView.vue"),
        },
        {
          path: "resources",
          name: "resources",
          meta: { surface: "client" },
          component: () => import("@/views/public/ResourcesView.vue"),
        },
        {
          path: "resources/:slug",
          name: "resource",
          meta: { surface: "client" },
          component: () => import("@/views/public/ResourceView.vue"),
        },
        {
          path: "help",
          name: "help-center",
          meta: { surface: "client" },
          component: () => import("@/views/public/HelpCenterView.vue"),
        },
        {
          path: "help/articles/:slug",
          name: "help-article",
          meta: { surface: "client" },
          component: () => import("@/views/public/HelpArticleView.vue"),
        },
        {
          path: "help/category/:slug",
          name: "help-category",
          meta: { surface: "client" },
          component: () => import("@/views/public/HelpCenterView.vue"),
        },
        {
          path: "legal/:docType",
          name: "legal-document",
          component: () => import("@/views/public/LegalView.vue"),
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
    {
      path: "/auth/magic-link",
      name: "magic-link",
      component: () => import("@/views/auth/MagicLinkView.vue"),
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
  const portalCtx = usePortalContextStore();

  const routeSurface = to.meta.surface as string | undefined;
  const hostIsRegistered = portalCtx.portal !== null || portalCtx.website !== null;
  const isLocalhost = typeof window !== "undefined" && window.location.hostname === "localhost";

  // Surface guard: on a registered domain (non-localhost), block routes whose
  // surface doesn't match the resolved portal surface.
  if (routeSurface && hostIsRegistered && !isLocalhost && routeSurface !== portalCtx.surface) {
    return portalCtx.homeRoute;
  }

  // Role–surface guard: authenticated user on a registered domain must belong
  // to an allowed role for this surface. Prevents e.g. a client account
  // reaching /writer/... even if the URL is manually typed.
  if (
    auth.isAuthenticated &&
    auth.role &&
    hostIsRegistered &&
    !isLocalhost &&
    portalCtx.allowedRoles.length > 0 &&
    !portalCtx.allowedRoles.includes(auth.role)
  ) {
    return { name: "unauthorized" };
  }

  // Auth guard: unauthenticated access to protected routes.
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
