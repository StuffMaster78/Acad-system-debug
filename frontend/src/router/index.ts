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
        path: "new-order",
        name: "client-new-order",
        component: () => import("@/views/client/NewOrderView.vue"),
      },
      {
        path: "messages",
        name: "client-messages",
        component: () => import("@/views/client/ClientMessagesView.vue"),
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
        path: "communications",
        name: "admin-communications",
        component: () => import("@/views/admin/AdminCommsView.vue"),
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
        component: () => import("@/views/writer/WriterWorkspaceView.vue"),
      },
      {
        path: "assignments",
        name: "writer-assignments",
        component: () => import("@/views/writer/WriterWorkspaceView.vue"),
      },
      {
        path: "earnings",
        name: "writer-earnings",
        component: () => import("@/views/writer/WriterWorkspaceView.vue"),
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
