import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminCommsApi,
  type BroadcastRecord,
  type CommunicationQueueRecord,
  type CommunicationThreadRecord,
  type CreateEmailCampaignPayload,
  type EmailCampaignRecord,
  type SendBroadcastPayload,
} from "@/api/adminComms";
import { useAuthStore } from "@/stores/auth";
import type { AdminCommsMetric } from "@/types/adminComms";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewThreads(): CommunicationThreadRecord[] {
  return [
    {
      id: 88,
      target_type: "order",
      target_id: 1042,
      kind: "client_writer",
      status: "open",
      subject: "Healthcare policy brief clarification",
      reference: "ORD-1042",
      last_message_at: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
    },
    {
      id: 91,
      target_type: "specialorder",
      target_id: 67,
      kind: "support",
      status: "escalated",
      subject: "Portal credentials need review",
      reference: "SPO-67",
      last_message_at: new Date(Date.now() - 1000 * 60 * 27).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 14).toISOString(),
    },
    {
      id: 94,
      target_type: "classorder",
      target_id: 15,
      kind: "payment",
      status: "open",
      subject: "Class milestone payment reminder",
      reference: "CLS-15",
      last_message_at: new Date(Date.now() - 1000 * 60 * 80).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    },
  ];
}

function previewBroadcasts(): BroadcastRecord[] {
  return [
    {
      id: 4,
      title: "Writer payment window",
      message: "Weekly payout review closes at 6 PM UTC.",
      event_type: "system.broadcast",
      channels: ["in_app", "email"],
      target_roles: ["writer"],
      is_active: true,
      is_blocking: false,
      require_acknowledgement: false,
      acknowledgement_count: 18,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    },
    {
      id: 5,
      title: "Portal maintenance",
      message: "Class portal access will have a short maintenance window.",
      event_type: "system.broadcast",
      channels: ["in_app"],
      target_roles: ["client", "writer"],
      is_active: true,
      is_blocking: true,
      require_acknowledgement: true,
      acknowledgement_count: 7,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    },
  ];
}

function previewCampaigns(): EmailCampaignRecord[] {
  return [
    {
      id: 21,
      title: "Returning client discount",
      subject: "A writing credit is waiting",
      status: "scheduled",
      email_type: "marketing",
      scheduled_time: new Date(Date.now() + 1000 * 60 * 60 * 7).toISOString(),
      website: "NurseMyGrade",
      created_by: "admin preview",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 18).toISOString(),
    },
    {
      id: 22,
      title: "Writer policy update",
      subject: "New class portal handling rules",
      status: "draft",
      email_type: "operational",
      website: "Platform",
      created_by: "admin preview",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    },
  ];
}

export const useAdminCommsStore = defineStore("admin-comms", () => {
  const threads = ref<CommunicationThreadRecord[]>([]);
  const escalations = ref<CommunicationQueueRecord[]>([]);
  const moderationFlags = ref<CommunicationQueueRecord[]>([]);
  const broadcasts = ref<BroadcastRecord[]>([]);
  const campaigns = ref<EmailCampaignRecord[]>([]);
  const query = ref("");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");
  const broadcastComposer = ref({
    title: "Operations update",
    message: "<p>A new operations update has been posted by admin.</p>",
    target_roles: ["client", "writer"] as SendBroadcastPayload["target_roles"],
    channels: ["in_app"] as string[],
    priority: "normal" as SendBroadcastPayload["priority"],
    require_acknowledgement: false,
    is_blocking: false,
  });
  const campaignComposer = ref({
    title: "New campaign",
    subject: "A writing update from our team",
    body: "<h2>Hello {{ first_name }}</h2><p>We have an update for you.</p>",
    email_type: "marketing" as string,
    target_roles: ["client"] as CreateEmailCampaignPayload["target_roles"],
    website: null as number | null,
    scheduled_time: null as string | null,
  });

  const filteredThreads = computed(() => {
    const needle = query.value.trim().toLowerCase();
    if (!needle) return threads.value;
    return threads.value.filter((thread) =>
      [thread.subject, thread.reference, thread.kind, thread.status, thread.target_type]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    );
  });

  const metrics = computed<AdminCommsMetric[]>(() => {
    const activeThreads = threads.value.filter((thread) => thread.status !== "closed").length;
    const activeBroadcasts = broadcasts.value.filter((broadcast) => broadcast.is_active !== false).length;
    const activeCampaigns = campaigns.value.filter((campaign) =>
      ["draft", "scheduled", "sending"].includes(campaign.status),
    ).length;

    return [
      {
        label: "Open threads",
        value: activeThreads,
        detail: `${escalations.value.length} escalations, ${moderationFlags.value.length} moderation flags.`,
        tone: escalations.value.length || moderationFlags.value.length ? "risk" : "neutral",
      },
      {
        label: "Broadcasts",
        value: activeBroadcasts,
        detail: "Active admin notifications across roles.",
        tone: "neutral",
      },
      {
        label: "Mass emails",
        value: activeCampaigns,
        detail: "Draft, scheduled, and sending campaigns.",
        tone: activeCampaigns ? "warn" : "neutral",
      },
    ];
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        threads.value = previewThreads();
        escalations.value = [{ id: 1, thread: 91, status: "open", severity: "high" }];
        moderationFlags.value = [{ id: 2, thread: 88, status: "pending", reason: "external_link" }];
        broadcasts.value = previewBroadcasts();
        campaigns.value = previewCampaigns();
        return;
      }

      const [
        threadRes,
        escalationRes,
        moderationRes,
        broadcastRes,
        campaignRes,
      ] = await Promise.allSettled([
        adminCommsApi.threads({ page_size: 50 }),
        adminCommsApi.escalations(),
        adminCommsApi.moderationFlags(),
        adminCommsApi.broadcasts(),
        adminCommsApi.campaigns(),
      ]);

      if (threadRes.status === "fulfilled") threads.value = normalizeList(threadRes.value.data);
      if (escalationRes.status === "fulfilled") escalations.value = normalizeList(escalationRes.value.data);
      if (moderationRes.status === "fulfilled") moderationFlags.value = normalizeList(moderationRes.value.data);
      if (broadcastRes.status === "fulfilled") broadcasts.value = normalizeList(broadcastRes.value.data);
      if (campaignRes.status === "fulfilled") campaigns.value = normalizeList(campaignRes.value.data);
    } catch (caught) {
      error.value = "Unable to load admin communications queues.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function sendBroadcast() {
    const auth = useAuthStore();
    const payload: SendBroadcastPayload = {
      event_key: "system.broadcast",
      title: broadcastComposer.value.title,
      message: broadcastComposer.value.message,
      channels: broadcastComposer.value.channels,
      target_roles: broadcastComposer.value.target_roles,
      priority: broadcastComposer.value.priority,
      show_to_all: false,
      require_acknowledgement: broadcastComposer.value.require_acknowledgement,
      is_blocking: broadcastComposer.value.is_blocking,
      is_critical: broadcastComposer.value.priority === "critical",
    };

    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        broadcasts.value = [
          {
            id: Date.now(),
            title: payload.title,
            message: payload.message,
            event_type: payload.event_key,
            channels: payload.channels,
            target_roles: payload.target_roles,
            is_active: true,
            acknowledgement_count: 0,
            created_at: new Date().toISOString(),
          },
          ...broadcasts.value,
        ];
        notice.value = "Preview broadcast queued.";
        return;
      }
      await adminCommsApi.sendBroadcast(payload);
      notice.value = "Broadcast queued.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function sendCampaignNow(campaignId: number) {
    const auth = useAuthStore();
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        campaigns.value = campaigns.value.map((c) =>
          c.id === campaignId ? { ...c, status: "sending" } : c,
        );
        notice.value = "Preview: campaign marked as sending.";
        return;
      }
      await adminCommsApi.sendCampaignNow(campaignId);
      notice.value = "Campaign sending started.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function scheduleCampaign(campaignId: number, scheduledTime: string) {
    const auth = useAuthStore();
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        campaigns.value = campaigns.value.map((c) =>
          c.id === campaignId ? { ...c, status: "scheduled", scheduled_time: scheduledTime } : c,
        );
        notice.value = "Preview: campaign scheduled.";
        return;
      }
      await adminCommsApi.scheduleCampaign(campaignId, scheduledTime);
      notice.value = "Campaign scheduled.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function sendCampaignTest(campaignId: number) {
    const auth = useAuthStore();
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        notice.value = "Preview campaign test sent.";
        return;
      }
      await adminCommsApi.sendCampaignTest(campaignId);
      notice.value = "Campaign test email queued.";
    } finally {
      isMutating.value = false;
    }
  }

  async function createCampaign(sendTest = false) {
    const auth = useAuthStore();
    const payload: CreateEmailCampaignPayload = {
      title: campaignComposer.value.title,
      subject: campaignComposer.value.subject,
      body: campaignComposer.value.body,
      email_type: campaignComposer.value.email_type,
      target_roles: campaignComposer.value.target_roles,
      website: campaignComposer.value.website ?? undefined,
      scheduled_time: campaignComposer.value.scheduled_time ?? undefined,
    };

    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        const campaign: EmailCampaignRecord = {
          id: Date.now(),
          title: payload.title,
          subject: payload.subject,
          status: "draft",
          email_type: payload.email_type,
          website: "Platform",
          created_by: "admin preview",
          created_at: new Date().toISOString(),
        };
        campaigns.value = [campaign, ...campaigns.value];
        notice.value = sendTest
          ? "Preview campaign drafted and test queued."
          : "Preview campaign draft created.";
        return;
      }

      const { data } = await adminCommsApi.createCampaign(payload);
      if (sendTest) await adminCommsApi.sendCampaignTest(data.id);
      notice.value = sendTest ? "Campaign draft created and test queued." : "Campaign draft created.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  return {
    threads,
    escalations,
    moderationFlags,
    broadcasts,
    campaigns,
    query,
    isLoading,
    isMutating,
    error,
    notice,
    broadcastComposer,
    campaignComposer,
    filteredThreads,
    metrics,
    hydrate,
    sendBroadcast,
    sendCampaignNow,
    scheduleCampaign,
    sendCampaignTest,
    createCampaign,
  };
});
