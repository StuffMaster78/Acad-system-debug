import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminSupportApi,
  type CommunicationEscalationRecord,
  type CreateSavedReplyPayload,
  type SavedReplyRecord,
  type SupportQueueResponse,
  type SupportTicketRecord,
  type SupportWorkloadResponse,
} from "@/api/adminSupport";
import { useAuthStore } from "@/stores/auth";
import type { AdminSupportMetric } from "@/types/adminSupport";

type ListResponse<T> = T[] | { results: T[] };
type SupportFilter = "all" | "unassigned" | "high_priority" | "overdue" | "escalated";

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewTickets(): SupportTicketRecord[] {
  const now = Date.now();
  return [
    {
      id: 401,
      title: "Client cannot access class portal",
      description: "Credentials were updated but the client still sees the old login state.",
      created_by_name: "nadia.m",
      assigned_to_name: "Support Lead",
      website: 1,
      status: "open",
      priority: "critical",
      category: "technical",
      is_escalated: true,
      has_sla: true,
      object_id: 15,
      created_at: new Date(now - 1000 * 60 * 95).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 15).toISOString(),
    },
    {
      id: 402,
      title: "Refund explanation requested",
      description: "Client wants a clearer explanation for a partial wallet refund.",
      created_by_name: "caleb.r",
      assigned_to: null,
      website: 2,
      status: "in_progress",
      priority: "high",
      category: "billing",
      is_escalated: false,
      has_sla: true,
      object_id: 1038,
      created_at: new Date(now - 1000 * 60 * 60 * 8).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 44).toISOString(),
    },
    {
      id: 403,
      title: "Writer asks for deadline clarification",
      description: "Assigned writer needs support to confirm deliverable scope.",
      created_by_name: "amina.writer",
      assigned_to_name: "Support Desk",
      website: 1,
      status: "open",
      priority: "medium",
      category: "order",
      is_escalated: false,
      has_sla: false,
      object_id: 1042,
      created_at: new Date(now - 1000 * 60 * 60 * 29).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 60 * 5).toISOString(),
    },
  ];
}

function previewQueue(tickets: SupportTicketRecord[]): SupportQueueResponse {
  return {
    unassigned_tickets: tickets.filter((ticket) => !ticket.assigned_to && !ticket.assigned_to_name),
    my_assigned_tickets: tickets.filter((ticket) => ticket.assigned_to || ticket.assigned_to_name),
    high_priority_tickets: tickets.filter((ticket) => ["high", "critical"].includes(ticket.priority)),
    overdue_tickets: tickets.filter((ticket) => ticket.id === 403),
    counts: {
      unassigned: 1,
      my_assigned: 2,
      high_priority: 2,
      overdue: 1,
    },
  };
}

function previewEscalations(): CommunicationEscalationRecord[] {
  return [
    {
      id: 77,
      thread: 91,
      status: "open",
      reason: "Client portal access dispute needs senior review.",
      escalated_by_display: "Support Lead",
      escalated_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    },
  ];
}

function previewReplies(): SavedReplyRecord[] {
  return [
    {
      id: 11,
      title: "Refund timeline",
      body: "<p>Your refund request is in review. Wallet refunds are usually faster than provider refunds.</p>",
      category: "billing",
      is_active: true,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    },
    {
      id: 12,
      title: "Portal access reset",
      body: "<p>We have refreshed your portal access. Please try signing in again from the latest link.</p>",
      category: "technical",
      is_active: true,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 22).toISOString(),
    },
  ];
}

export const useAdminSupportStore = defineStore("admin-support", () => {
  const tickets = ref<SupportTicketRecord[]>([]);
  const queue = ref<SupportQueueResponse>({});
  const workload = ref<SupportWorkloadResponse>({});
  const escalations = ref<CommunicationEscalationRecord[]>([]);
  const savedReplies = ref<SavedReplyRecord[]>([]);
  const query = ref("");
  const filter = ref<SupportFilter>("all");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");
  const replyComposer = ref<CreateSavedReplyPayload>({
    title: "New saved reply",
    category: "general",
    body: "<p>Thanks for reaching out. We are checking this and will update you shortly.</p>",
  });

  const metrics = computed<AdminSupportMetric[]>(() => {
    const openTickets = tickets.value.filter((ticket) => ticket.status !== "closed").length;
    const highPriority = queue.value.counts?.high_priority ?? tickets.value.filter((ticket) => ["high", "critical"].includes(ticket.priority)).length;
    const overdue = queue.value.counts?.overdue ?? 0;
    const unresolvedEscalations = escalations.value.filter((item) => item.status !== "resolved").length;

    return [
      {
        label: "Open tickets",
        value: openTickets,
        detail: `${queue.value.counts?.unassigned ?? 0} unassigned in the queue.`,
        tone: openTickets ? "warn" : "good",
      },
      {
        label: "High priority",
        value: highPriority,
        detail: "Critical and high-priority tickets needing fast handling.",
        tone: highPriority ? "risk" : "neutral",
      },
      {
        label: "SLA pressure",
        value: overdue,
        detail: `${Math.round(workload.value.sla_compliance_rate_percent ?? 0)}% support SLA compliance.`,
        tone: overdue ? "risk" : "good",
      },
      {
        label: "Escalations",
        value: unresolvedEscalations,
        detail: "Open communication escalations requiring admin attention.",
        tone: unresolvedEscalations ? "warn" : "neutral",
      },
    ];
  });

  const filteredTickets = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return tickets.value.filter((ticket) => {
      const filterMatches =
        filter.value === "all" ||
        (filter.value === "unassigned" && !ticket.assigned_to && !ticket.assigned_to_name) ||
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
          current_ticket_load: 8,
          average_response_time_hours: 1.4,
          resolution_rate_percent: 83,
          tickets_resolved_today: 6,
          tickets_resolved_this_week: 31,
          tickets_resolved_this_month: 118,
          sla_compliance_rate_percent: 91,
        };
        escalations.value = previewEscalations();
        savedReplies.value = previewReplies();
        return;
      }

      const [ticketsRes, queueRes, workloadRes, escalationRes, repliesRes] = await Promise.allSettled([
        adminSupportApi.tickets({ page_size: 75, ordering: "-created_at" }),
        adminSupportApi.queue(),
        adminSupportApi.workload(),
        adminSupportApi.escalations(),
        adminSupportApi.savedReplies(),
      ]);

      if (ticketsRes.status === "fulfilled") tickets.value = normalizeList(ticketsRes.value.data);
      if (queueRes.status === "fulfilled") queue.value = queueRes.value.data;
      if (workloadRes.status === "fulfilled") workload.value = workloadRes.value.data;
      if (escalationRes.status === "fulfilled") escalations.value = normalizeList(escalationRes.value.data);
      if (repliesRes.status === "fulfilled") savedReplies.value = normalizeList(repliesRes.value.data);
    } catch (caught) {
      error.value = "Unable to load admin support operations.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function closeTicket(ticketId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        tickets.value = tickets.value.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, status: "closed", updated_at: new Date().toISOString() } : ticket,
        );
        notice.value = "Preview ticket closed.";
        return;
      }
      await adminSupportApi.closeTicket(ticketId, "Closed from admin support.");
      notice.value = "Ticket closed.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function escalateTicket(ticketId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        tickets.value = tickets.value.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, is_escalated: true, priority: "critical" } : ticket,
        );
        notice.value = "Preview ticket escalated.";
        return;
      }
      await adminSupportApi.escalateTicket(ticketId);
      notice.value = "Ticket escalated.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function resolveEscalation(escalationId: number) {
    const auth = useAuthStore();
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
        return;
      }
      await adminSupportApi.resolveEscalation(escalationId, "Resolved from admin support.");
      notice.value = "Escalation resolved.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function createSavedReply() {
    const auth = useAuthStore();
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
        return;
      }
      const { data } = await adminSupportApi.createSavedReply(replyComposer.value);
      savedReplies.value = [data, ...savedReplies.value];
      notice.value = "Saved reply created.";
    } finally {
      isMutating.value = false;
    }
  }

  return {
    tickets,
    queue,
    workload,
    escalations,
    savedReplies,
    replyComposer,
    query,
    filter,
    isLoading,
    isMutating,
    error,
    notice,
    metrics,
    filteredTickets,
    hydrate,
    closeTicket,
    escalateTicket,
    resolveEscalation,
    createSavedReply,
  };
});
