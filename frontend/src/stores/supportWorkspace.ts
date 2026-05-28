import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { supportApi } from "@/api/support";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import type { CreateSavedReplyPayload } from "@/api/adminSupport";
import type {
  CommunicationEscalationRecord,
  SavedReplyRecord,
  SupportAnalytics,
  SupportDeskFilter,
  SupportMetric,
  SupportOrdersDashboard,
  SupportQueueResponse,
  SupportSlaDashboard,
  SupportTicketRecord,
  SupportWorkloadResponse,
} from "@/types/support";

type ListResponse<T> = T[] | { results?: T[] };

function normalizeList<T>(data: ListResponse<T> | undefined): T[] {
  if (Array.isArray(data)) return data;
  return data?.results ?? [];
}

function numberValue(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function previewTickets(): SupportTicketRecord[] {
  const now = Date.now();
  return [
    {
      id: 501,
      title: "Client cannot open delivered files",
      description: "Client says the download link opens the dashboard but not the final files.",
      created_by_name: "Nadia Morgan",
      assigned_to_name: "You",
      status: "open",
      priority: "critical",
      category: "files",
      is_escalated: true,
      has_sla: true,
      object_id: 10001,
      created_at: new Date(now - 1000 * 60 * 50).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 12).toISOString(),
    },
    {
      id: 502,
      title: "Writer needs scope clarification",
      description: "Writer asks whether appendices count toward the page limit.",
      created_by_name: "Writer #10001",
      assigned_to: null,
      status: "in_progress",
      priority: "high",
      category: "order",
      has_sla: true,
      object_id: 10008,
      created_at: new Date(now - 1000 * 60 * 60 * 4).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 38).toISOString(),
    },
    {
      id: 503,
      title: "Payment receipt mismatch",
      description: "Client paid by wallet and card, but the receipt only shows card payment.",
      created_by_name: "Caleb R.",
      assigned_to_name: "You",
      status: "open",
      priority: "medium",
      category: "billing",
      has_sla: false,
      object_id: 10012,
      created_at: new Date(now - 1000 * 60 * 60 * 26).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 60 * 3).toISOString(),
    },
  ];
}

function previewQueue(tickets: SupportTicketRecord[]): SupportQueueResponse {
  return {
    unassigned_tickets: tickets.filter((ticket) => !ticket.assigned_to && !ticket.assigned_to_name),
    my_assigned_tickets: tickets.filter((ticket) => ticket.assigned_to || ticket.assigned_to_name),
    high_priority_tickets: tickets.filter((ticket) => ["high", "critical"].includes(ticket.priority)),
    overdue_tickets: tickets.filter((ticket) => ticket.id === 503),
    counts: {
      unassigned: 1,
      my_assigned: 2,
      high_priority: 2,
      overdue: 1,
    },
  };
}

export const useSupportWorkspaceStore = defineStore("support-workspace", () => {
  const tickets = ref<SupportTicketRecord[]>([]);
  const queue = ref<SupportQueueResponse>({});
  const workload = ref<SupportWorkloadResponse>({});
  const orders = ref<SupportOrdersDashboard>({});
  const sla = ref<SupportSlaDashboard>({});
  const analytics = ref<SupportAnalytics>({});
  const escalations = ref<CommunicationEscalationRecord[]>([]);
  const savedReplies = ref<SavedReplyRecord[]>([]);
  const query = ref("");
  const filter = ref<SupportDeskFilter>("all");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");
  const replyComposer = ref<CreateSavedReplyPayload>({
    title: "Scope clarification",
    category: "order",
    body: "<p>Thanks for checking. We are confirming the scope with the operations team and will update this thread shortly.</p>",
  });

  const rescueCount = computed(() =>
    numberValue(orders.value.summary?.total_requiring_attention) +
    numberValue(sla.value.active_status?.breached) +
    escalations.value.filter((item) => item.status !== "resolved").length,
  );

  const metrics = computed<SupportMetric[]>(() => {
    const openTickets = tickets.value.filter((ticket) => ticket.status !== "closed").length;
    const highPriority = queue.value.counts?.high_priority ?? tickets.value.filter((ticket) => ["high", "critical"].includes(ticket.priority)).length;
    const overdue = queue.value.counts?.overdue ?? 0;
    const responseHours = workload.value.average_response_time_hours;

    return [
      {
        label: "Open queue",
        value: String(openTickets),
        detail: `${queue.value.counts?.my_assigned ?? 0} assigned to you, ${queue.value.counts?.unassigned ?? 0} unassigned.`,
        tone: openTickets ? "warn" : "good",
      },
      {
        label: "High priority",
        value: String(highPriority),
        detail: "Critical and high-priority support work.",
        tone: highPriority ? "risk" : "neutral",
      },
      {
        label: "SLA pressure",
        value: String(overdue + numberValue(sla.value.active_status?.breached)),
        detail: `${Math.round(numberValue(workload.value.sla_compliance_rate_percent))}% SLA compliance.`,
        tone: overdue ? "risk" : "good",
      },
      {
        label: "Response time",
        value: responseHours == null ? "-" : `${Number(responseHours).toFixed(1)}h`,
        detail: `${workload.value.tickets_resolved_today ?? 0} tickets resolved today.`,
        tone: numberValue(responseHours) > 4 ? "warn" : "good",
      },
    ];
  });

  const filteredTickets = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return tickets.value.filter((ticket) => {
      const mine = Boolean(ticket.assigned_to || ticket.assigned_to_name);
      const filterMatches =
        filter.value === "all" ||
        (filter.value === "mine" && mine) ||
        (filter.value === "unassigned" && !mine) ||
        (filter.value === "high_priority" && ["high", "critical"].includes(ticket.priority)) ||
        (filter.value === "overdue" && queue.value.overdue_tickets?.some((item) => item.id === ticket.id)) ||
        (filter.value === "escalated" && ticket.is_escalated);
      const textMatches =
        !needle ||
        [
          ticket.title,
          ticket.description,
          ticket.created_by_name,
          ticket.assigned_to_name,
          ticket.status,
          ticket.priority,
          ticket.category,
          ticket.object_id,
        ]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(needle));
      return filterMatches && textMatches;
    });
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        tickets.value = previewTickets();
        queue.value = previewQueue(tickets.value);
        workload.value = {
          current_ticket_load: 7,
          average_response_time_hours: 1.2,
          resolution_rate_percent: 86,
          tickets_resolved_today: 5,
          tickets_resolved_this_week: 28,
          tickets_resolved_this_month: 104,
          sla_compliance_rate_percent: 92,
          workload_tracker: {
            tickets_handled: 246,
            disputes_handled: 19,
            orders_managed: 83,
            last_activity: new Date().toISOString(),
          },
        };
        orders.value = {
          disputed_orders: { count: 3, orders: [{ id: 10015, topic: "Disputed literature review", status: "disputed" }] },
          payment_issue_orders: { count: 2, orders: [{ id: 10012, topic: "Payment receipt mismatch", payment_status: "pending" }] },
          pending_refunds: { count: 1, refunds: [{ id: 81, order_id: 10009, amount: "45.00", reason: "Partial refund request" }] },
          orders_with_tickets: { count: 8, orders: [{ id: 10001, topic: "Nursing leadership reflection" }] },
          summary: { total_requiring_attention: 6 },
        };
        sla.value = {
          active_status: { on_track: 8, warning: 3, breached: 1, total_active: 12 },
          upcoming_deadlines: [{ id: 9, order_id: 10001, time_remaining_display: "2h 15m", status: "warning" }],
          recent_breaches: [{ id: 11, order_id: 10012, breach_duration_display: "1h 10m", status: "breached" }],
        };
        analytics.value = {
          performance: { satisfaction_score: 94, reopened_ticket_rate: 6, first_contact_resolution_rate: 71 },
          trends: [{ week: "2026-05-18", resolved: 28, escalated: 4 }],
          sla: { compliance_rate: 92, breached_count: 1 },
        };
        escalations.value = [
          {
            id: 91,
            thread: 701,
            status: "open",
            reason: "Client cannot access delivery and the order is near dispute.",
            escalated_by_display: "Support Preview",
            escalated_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
          },
        ];
        savedReplies.value = [
          {
            id: 31,
            title: "File access reset",
            body: "<p>We refreshed the delivery access for your order. Please retry the file link from your dashboard.</p>",
            category: "files",
            is_active: true,
            created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
          },
          {
            id: 32,
            title: "Scope confirmation",
            body: "<p>We are checking this scope question with operations and will keep the writer and client aligned.</p>",
            category: "order",
            is_active: true,
            created_at: new Date(Date.now() - 1000 * 60 * 160).toISOString(),
          },
        ];
        return;
      }

      const [
        ticketsRes,
        queueRes,
        workloadRes,
        ordersRes,
        slaRes,
        performanceRes,
        trendsRes,
        escalationRes,
        repliesRes,
      ] = await Promise.allSettled([
        supportApi.tickets({ page_size: 75, ordering: "-created_at" }),
        supportApi.queue(),
        supportApi.workload(),
        supportApi.orders(),
        supportApi.slaDashboard(),
        supportApi.performance(),
        supportApi.trends(),
        supportApi.escalations(),
        supportApi.savedReplies(),
      ]);

      if (ticketsRes.status === "fulfilled") tickets.value = normalizeList(ticketsRes.value.data);
      if (queueRes.status === "fulfilled") queue.value = queueRes.value.data;
      if (workloadRes.status === "fulfilled") workload.value = workloadRes.value.data;
      if (ordersRes.status === "fulfilled") orders.value = ordersRes.value.data;
      if (slaRes.status === "fulfilled") sla.value = slaRes.value.data;
      if (performanceRes.status === "fulfilled") analytics.value.performance = performanceRes.value.data;
      if (trendsRes.status === "fulfilled") analytics.value.trends = trendsRes.value.data.trends ?? [];
      if (escalationRes.status === "fulfilled") escalations.value = normalizeList(escalationRes.value.data);
      if (repliesRes.status === "fulfilled") savedReplies.value = normalizeList(repliesRes.value.data);

      const failed = [
        ticketsRes,
        queueRes,
        workloadRes,
        ordersRes,
        slaRes,
        performanceRes,
        trendsRes,
        escalationRes,
        repliesRes,
      ].some((result) => result.status === "rejected");
      if (failed) error.value = "Some support workspace data is unavailable from the backend.";
    } finally {
      isLoading.value = false;
    }
  }

  async function closeTicket(ticketId: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        tickets.value = tickets.value.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, status: "closed", updated_at: new Date().toISOString() } : ticket,
        );
        notice.value = "Preview ticket closed.";
        ui.toast("Ticket closed.", "success");
        return;
      }
      await supportApi.closeTicket(ticketId, "Closed from support workspace.");
      notice.value = "Ticket closed.";
      ui.toast("Ticket closed.", "success");
      await hydrate();
    } catch (caught) {
      error.value = "Unable to close that ticket.";
      ui.toast("Unable to close that ticket.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function escalateTicket(ticketId: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        tickets.value = tickets.value.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, is_escalated: true, priority: "critical" } : ticket,
        );
        notice.value = "Preview ticket escalated.";
        ui.toast("Ticket escalated.", "warn");
        return;
      }
      await supportApi.escalateTicket(ticketId);
      notice.value = "Ticket escalated.";
      ui.toast("Ticket escalated.", "warn");
      await hydrate();
    } catch (caught) {
      error.value = "Unable to escalate that ticket.";
      ui.toast("Unable to escalate that ticket.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function reopenTicket(ticketId: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        tickets.value = tickets.value.map((t) =>
          t.id === ticketId ? { ...t, status: "open" } : t,
        );
        notice.value = "Preview ticket reopened.";
        ui.toast("Ticket reopened.", "success");
        return;
      }
      await supportApi.reopenTicket(ticketId);
      notice.value = "Ticket reopened.";
      ui.toast("Ticket reopened.", "success");
      await hydrate();
    } catch (caught) {
      error.value = "Unable to reopen that ticket.";
      ui.toast("Unable to reopen that ticket.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function resolveEscalation(escalationId: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        escalations.value = escalations.value.map((escalation) =>
          escalation.id === escalationId
            ? { ...escalation, status: "resolved", resolved_at: new Date().toISOString(), resolution_note: "Resolved in preview." }
            : escalation,
        );
        notice.value = "Preview escalation resolved.";
        ui.toast("Escalation resolved.", "success");
        return;
      }
      await supportApi.resolveEscalation(escalationId, "Resolved from support workspace.");
      notice.value = "Escalation resolved.";
      ui.toast("Escalation resolved.", "success");
      await hydrate();
    } catch (caught) {
      error.value = "Unable to resolve that escalation.";
      ui.toast("Unable to resolve that escalation.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createSavedReply() {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        savedReplies.value = [
          {
            id: Date.now(),
            title: replyComposer.value.title,
            body: replyComposer.value.body,
            category: replyComposer.value.category,
            is_active: true,
            created_at: new Date().toISOString(),
          },
          ...savedReplies.value,
        ];
        notice.value = "Preview saved reply created.";
        ui.toast("Saved reply created.", "success");
        return;
      }
      const { data } = await supportApi.createSavedReply(replyComposer.value);
      savedReplies.value = [data, ...savedReplies.value];
      notice.value = "Saved reply created.";
      ui.toast("Saved reply created.", "success");
    } catch (caught) {
      error.value = "Unable to create that saved reply.";
      ui.toast("Unable to create that saved reply.", "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function toggleReplyActive(id: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    const reply = savedReplies.value.find((r) => r.id === id);
    if (!reply) return;
    const newActive = !reply.is_active;
    savedReplies.value = savedReplies.value.map((r) =>
      r.id === id ? { ...r, is_active: newActive } : r,
    );
    if (auth.isPreviewSession) {
      ui.toast(newActive ? "Reply activated." : "Reply deactivated.", "success");
      return;
    }
    try {
      const { data } = await supportApi.patchSavedReply(id, { is_active: newActive });
      savedReplies.value = savedReplies.value.map((r) => (r.id === id ? data : r));
      ui.toast(newActive ? "Reply activated." : "Reply deactivated.", "success");
    } catch {
      savedReplies.value = savedReplies.value.map((r) =>
        r.id === id ? { ...r, is_active: !newActive } : r,
      );
      ui.toast("Unable to update reply.", "error");
    }
  }

  async function deleteReply(id: number) {
    const auth = useAuthStore();
    const ui = useUiStore();
    savedReplies.value = savedReplies.value.filter((r) => r.id !== id);
    if (auth.isPreviewSession) {
      ui.toast("Saved reply deleted.", "success");
      return;
    }
    try {
      await supportApi.deleteSavedReply(id);
      ui.toast("Saved reply deleted.", "success");
    } catch {
      ui.toast("Unable to delete reply.", "error");
      if (!savedReplies.value.find((r) => r.id === id)) {
        await supportApi.savedReplies().then(({ data }) => {
          savedReplies.value = Array.isArray(data) ? data : (data as { results: typeof savedReplies.value }).results ?? [];
        }).catch(() => undefined);
      }
    }
  }

  return {
    tickets,
    queue,
    workload,
    orders,
    sla,
    analytics,
    escalations,
    savedReplies,
    query,
    filter,
    replyComposer,
    isLoading,
    isMutating,
    error,
    notice,
    rescueCount,
    metrics,
    filteredTickets,
    hydrate,
    closeTicket,
    reopenTicket,
    escalateTicket,
    resolveEscalation,
    createSavedReply,
    toggleReplyActive,
    deleteReply,
  };
});
