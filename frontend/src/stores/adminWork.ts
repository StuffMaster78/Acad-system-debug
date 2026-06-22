import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminWorkApi,
  type ClassOrderListRecord,
  type SpecialOrderListRecord,
  type WebsiteRecord,
} from "@/api/adminWork";
import { useAuthStore } from "@/stores/auth";
import { useWebsitesStore } from "@/stores/websites";
import type {
  AdminWorkItem,
  AdminWorkKind,
  AdminWorkMetric,
  AdminWorkSummary,
  AdminWorkTone,
} from "@/types/adminWork";
import type { OrderSummary } from "@/types/orders";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function stringifyAmount(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return undefined;
  return String(value);
}

function previewWorkItems(): AdminWorkItem[] {
  const now = Date.now();
  return [
    {
      id: 1042,
      kind: "order",
      reference: "ORD-1042",
      title: "Healthcare policy brief",
      status: "in_progress",
      paymentStatus: "paid",
      website: "NurseMyGrade",
      client: "Nadia M.",
      assignedWriter: "Amina K.",
      deadline: new Date(now + 1000 * 60 * 60 * 18).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 30).toISOString(),
      amount: "186.00",
      currency: "USD",
      priority: "critical",
      subject: "Health policy",
    },
    {
      id: 1048,
      kind: "order",
      reference: "ORD-1048",
      title: "Machine learning report",
      status: "paid",
      paymentStatus: "paid",
      website: "EssayManiacs",
      client: "Caleb R.",
      assignedWriter: "Unassigned",
      deadline: new Date(now + 1000 * 60 * 60 * 44).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 4).toISOString(),
      amount: "242.00",
      currency: "USD",
      priority: "staffing",
      subject: "Computer science",
    },
    {
      id: 67,
      kind: "special_order",
      reference: "SPO-67",
      title: "Capstone data cleanup and analysis",
      status: "quoted",
      paymentStatus: "quote_pending",
      website: "GradHelp Africa",
      client: "Miriam O.",
      assignedWriter: "Jon M.",
      deadline: new Date(now + 1000 * 60 * 60 * 24 * 5).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 14).toISOString(),
      amount: "520.00",
      currency: "USD",
      priority: "high",
      subject: "Special project",
      notes: "Sensitive portal access required.",
    },
    {
      id: 73,
      kind: "special_order",
      reference: "SPO-73",
      title: "Full dissertation formatting package",
      status: "ready_for_delivery",
      paymentStatus: "funded",
      website: "NurseMyGrade",
      client: "Evan P.",
      assignedWriter: "Amina K.",
      deadline: new Date(now + 1000 * 60 * 60 * 8).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 72).toISOString(),
      amount: "740.00",
      currency: "USD",
      priority: "urgent",
      subject: "Formatting",
    },
    {
      id: 12,
      kind: "class_order",
      reference: "CLS-12",
      title: "Statistics 301 weekly class support",
      status: "active",
      paymentStatus: "partial",
      website: "GradeCrest",
      client: "Jordan L.",
      assignedWriter: "Mira Draft",
      deadline: new Date(now + 1000 * 60 * 60 * 24 * 28).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 24 * 9).toISOString(),
      amount: "1180.00",
      currency: "USD",
      subject: "Statistics",
      notes: "3 upcoming quizzes, 1 project milestone.",
    },
    {
      id: 15,
      kind: "class_order",
      reference: "CLS-15",
      title: "Business law portal management",
      status: "paused",
      paymentStatus: "overdue",
      website: "GradHelp Africa",
      client: "Patricia W.",
      assignedWriter: "Unassigned",
      deadline: new Date(now - 1000 * 60 * 60 * 6).toISOString(),
      createdAt: new Date(now - 1000 * 60 * 60 * 24 * 18).toISOString(),
      amount: "860.00",
      currency: "USD",
      subject: "Business law",
      isPaused: true,
      notes: "Paused pending milestone payment.",
    },
  ];
}

function websiteLabel(websites: WebsiteRecord[], id?: number | null) {
  if (!id) return "Platform";
  // Prefer the shared websites store which is already loaded; fall back to local list
  const shared = useWebsitesStore().nameById(id);
  if (shared !== `Site #${id}`) return shared;
  const website = websites.find((item) => item.id === id);
  return website?.name ?? website?.domain ?? website?.slug ?? `Website #${id}`;
}

function normalizeOrder(order: OrderSummary, websites: WebsiteRecord[]): AdminWorkItem {
  const raw = order as OrderSummary & {
    website?: number | null;
    website_id?: number | null;
    client_name?: string;
    client_id?: number | null;
    assigned_writer_name?: string;
    assigned_writer?: number | null;
    writer_name?: string;
    writer?: number | null;
  };

  return {
    id: order.id,
    kind: "order",
    reference: `ORD-${order.id}`,
    title: order.topic,
    status: order.status,
    paymentStatus: order.payment_status,
    website: websiteLabel(websites, raw.website ?? raw.website_id),
    client: raw.client_name ?? (raw.client_id ? `Client #${raw.client_id}` : "Client"),
    assignedWriter:
      raw.assigned_writer_name ??
      raw.writer_name ??
      (raw.assigned_writer || raw.writer ? `Writer #${raw.assigned_writer ?? raw.writer}` : "Unassigned"),
    deadline: order.writer_deadline ?? order.client_deadline ?? null,
    createdAt: order.created_at ?? null,
    amount: stringifyAmount(order.total_price),
    currency: order.currency,
    subject: order.service_family ?? order.service_code,
  };
}

function normalizeSpecialOrder(order: SpecialOrderListRecord): AdminWorkItem {
  return {
    id: order.id,
    kind: "special_order",
    reference: `SPO-${order.id}`,
    title: order.title,
    status: order.status,
    paymentStatus: order.pricing_mode,
    website: order.origin || "Platform",
    client: order.client_name || (order.client ? `Client #${order.client}` : "Client"),
    assignedWriter: order.writer_name || (order.writer ? `Writer #${order.writer}` : "Unassigned"),
    deadline: null,
    createdAt: order.created_at ?? null,
    amount: stringifyAmount(order.budget),
    currency: order.currency,
    priority: order.priority,
    subject: order.predefined_config_name || "Special order",
  };
}

function normalizeClassOrder(order: ClassOrderListRecord): AdminWorkItem {
  return {
    id: order.id,
    kind: "class_order",
    reference: `CLS-${order.id}`,
    title: order.title,
    status: order.status,
    paymentStatus: order.payment_status,
    website: "Class portal",
    client: order.client_name || (order.client ? `Client #${order.client}` : "Client"),
    assignedWriter:
      order.assigned_writer_name ||
      (order.assigned_writer ? `Writer #${order.assigned_writer}` : "Unassigned"),
    deadline: null,
    createdAt: order.created_at ?? null,
    amount: stringifyAmount(order.final_amount),
    currency: order.currency,
    subject: order.class_subject || order.class_name || order.academic_level,
    notes: order.pause_reason,
    isPaused: order.is_work_paused,
  };
}

function isUnassigned(item: AdminWorkItem) {
  return item.assignedWriter.toLowerCase() === "unassigned";
}

function isAtRisk(item: AdminWorkItem) {
  const status = item.status.toLowerCase();
  const payment = item.paymentStatus?.toLowerCase() ?? "";
  const priority = item.priority?.toLowerCase() ?? "";
  const deadline = item.deadline ? new Date(item.deadline).getTime() : Number.POSITIVE_INFINITY;
  const dueSoon = deadline < Date.now() + 1000 * 60 * 60 * 24;

  return (
    item.isPaused ||
    dueSoon ||
    status.includes("late") ||
    status.includes("hold") ||
    status.includes("paused") ||
    payment.includes("overdue") ||
    priority.includes("critical") ||
    priority.includes("urgent")
  );
}

export function workKindLabel(kind: AdminWorkKind) {
  if (kind === "special_order") return "Special";
  if (kind === "class_order") return "Class";
  return "Order";
}

export function workTone(item: AdminWorkItem): AdminWorkTone {
  if (isAtRisk(item)) return "danger";
  if (isUnassigned(item)) return "warning";
  if (item.status.toLowerCase().includes("complete")) return "success";
  return "neutral";
}

export const useAdminWorkStore = defineStore("admin-work", () => {
  const items = ref<AdminWorkItem[]>([]);
  const activeKind = ref<AdminWorkKind | "all">("all");
  const query = ref("");
  const isLoading = ref(false);
  const error = ref("");

  const filteredItems = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return items.value.filter((item) => {
      const kindMatches = activeKind.value === "all" || item.kind === activeKind.value;
      const textMatches =
        !needle ||
        [
          item.reference,
          item.title,
          item.website,
          item.client,
          item.assignedWriter,
          item.status,
          item.subject,
        ]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(needle));
      return kindMatches && textMatches;
    });
  });

  const summary = computed<AdminWorkSummary>(() => ({
    total: items.value.length,
    normalOrders: items.value.filter((item) => item.kind === "order").length,
    specialOrders: items.value.filter((item) => item.kind === "special_order").length,
    classOrders: items.value.filter((item) => item.kind === "class_order").length,
    unassigned: items.value.filter(isUnassigned).length,
    atRisk: items.value.filter(isAtRisk).length,
  }));

  const metrics = computed<AdminWorkMetric[]>(() => [
    {
      label: "Active work",
      value: summary.value.total,
      detail: "Normal, special, and class work in one command view.",
      tone: "neutral",
    },
    {
      label: "Special orders",
      value: summary.value.specialOrders,
      detail: "Quoted, fixed, sensitive, and high-touch work.",
      tone: "good",
    },
    {
      label: "Class work",
      value: summary.value.classOrders,
      detail: "Long-running class portals and coursework bundles.",
      tone: "neutral",
    },
    {
      label: "Needs attention",
      value: summary.value.atRisk + summary.value.unassigned,
      detail: `${summary.value.unassigned} unassigned, ${summary.value.atRisk} at risk.`,
      tone: summary.value.atRisk || summary.value.unassigned ? "risk" : "good",
    },
  ]);

  async function refresh() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        items.value = previewWorkItems();
        return;
      }

      const [ordersRes, specialRes, classRes, websitesRes] = await Promise.allSettled([
        adminWorkApi.orders({ page_size: 50 }),
        adminWorkApi.specialOrders({ page_size: 50 }),
        adminWorkApi.classOrders({ page_size: 50 }),
        adminWorkApi.websites(),
      ]);

      const websites =
        websitesRes.status === "fulfilled" ? normalizeList(websitesRes.value.data) : [];
      const nextItems: AdminWorkItem[] = [];

      if (ordersRes.status === "fulfilled") {
        nextItems.push(...normalizeList(ordersRes.value.data).map((order) => normalizeOrder(order, websites)));
      }
      if (specialRes.status === "fulfilled") {
        nextItems.push(...normalizeList(specialRes.value.data).map(normalizeSpecialOrder));
      }
      if (classRes.status === "fulfilled") {
        nextItems.push(...normalizeList(classRes.value.data).map(normalizeClassOrder));
      }

      items.value = nextItems;
      if (!nextItems.length) {
        error.value = "No work records came back from the backend yet.";
      }
    } catch (caught) {
      error.value = "Unable to load the admin work command view.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    items,
    activeKind,
    query,
    isLoading,
    error,
    filteredItems,
    summary,
    metrics,
    refresh,
  };
});
