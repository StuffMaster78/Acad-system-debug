import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  communicationsApi,
  type CommunicationMessage,
  type CommunicationThread,
  type CommunicationThreadKind,
} from "@/api/communications";
import { useAuthStore } from "@/stores/auth";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

export const useCommunicationsStore = defineStore("communications", () => {
  const orderThreads = ref<CommunicationThread[]>([]);
  const inboxThreads = ref<CommunicationThread[]>([]);
  const activeThread = ref<CommunicationThread | null>(null);
  const messages = ref<CommunicationMessage[]>([]);
  const isLoading = ref(false);
  const isSending = ref(false);
  const error = ref("");
  const notice = ref("");

  const hasThread = computed(() => Boolean(activeThread.value));

  function previewThreads(): CommunicationThread[] {
    const now = Date.now();
    return [
      {
        id: 1,
        target_type: "order",
        target_id: 1,
        kind: "client_support",
        status: "open",
        subject: "Literature review on ethical AI in academic writing",
        reference: "1",
        last_message_at: new Date(now - 1000 * 60 * 12).toISOString(),
        metadata: { source: "preview", unread_count: 1 },
        created_at: new Date(now - 1000 * 60 * 60).toISOString(),
        updated_at: new Date(now - 1000 * 60 * 12).toISOString(),
      },
      {
        id: 2,
        target_type: "order",
        target_id: 2,
        kind: "client_writer",
        status: "open",
        subject: "Business report on subscription retention",
        reference: "2",
        last_message_at: new Date(now - 1000 * 60 * 45).toISOString(),
        metadata: { source: "preview", unread_count: 0 },
        created_at: new Date(now - 1000 * 60 * 60 * 3).toISOString(),
        updated_at: new Date(now - 1000 * 60 * 45).toISOString(),
      },
      {
        id: 3,
        target_type: "order",
        target_id: 3,
        kind: "revision",
        status: "open",
        subject: "Reflective essay on clinical leadership",
        reference: "3",
        last_message_at: new Date(now - 1000 * 60 * 60 * 5).toISOString(),
        metadata: { source: "preview", unread_count: 2 },
        created_at: new Date(now - 1000 * 60 * 60 * 20).toISOString(),
        updated_at: new Date(now - 1000 * 60 * 60 * 5).toISOString(),
      },
    ];
  }

  function previewMessages(thread: CommunicationThread): CommunicationMessage[] {
    const now = Date.now();
    return [
      {
        id: thread.id * 10 + 1,
        thread: thread.id,
        sender: 0,
        sender_display: "Client preview",
        message_type: "user",
        status: "active",
        body: "Please keep the requirements easy to audit and flag anything that needs my input.",
        parent: null,
        is_internal: false,
        is_system_generated: false,
        is_edited: false,
        metadata: { source: "preview" },
        created_at: new Date(now - 1000 * 60 * 30).toISOString(),
        updated_at: new Date(now - 1000 * 60 * 30).toISOString(),
      },
      {
        id: thread.id * 10 + 2,
        thread: thread.id,
        sender: 108,
        sender_display:
          thread.kind === "client_support" ? "Support desk" : "Assigned writer",
        message_type: "user",
        status: "active",
        body:
          thread.kind === "revision"
            ? "I have the revision notes and will align the new version with the requested scope."
            : "Understood. I will keep the thread updated as the order moves.",
        parent: null,
        is_internal: false,
        is_system_generated: false,
        is_edited: false,
        metadata: { source: "preview" },
        created_at: new Date(now - 1000 * 60 * 12).toISOString(),
        updated_at: new Date(now - 1000 * 60 * 12).toISOString(),
      },
    ];
  }

  async function loadInboxThreads() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        inboxThreads.value = previewThreads();
        activeThread.value = activeThread.value ?? inboxThreads.value[0] ?? null;
        messages.value = activeThread.value ? previewMessages(activeThread.value) : [];
        return;
      }

      const { data } = await communicationsApi.threads();
      inboxThreads.value = normalizeList(data);
      activeThread.value = activeThread.value ?? inboxThreads.value[0] ?? null;
      if (activeThread.value) await loadMessages(activeThread.value.id);
    } catch (caught) {
      error.value = "Unable to load messages.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function selectThread(thread: CommunicationThread) {
    const auth = useAuthStore();
    activeThread.value = thread;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        messages.value = previewMessages(thread);
        return;
      }
      await loadMessages(thread.id);
    } catch (caught) {
      error.value = "Unable to load this thread.";
      throw caught;
    }
  }

  async function loadOrderThread(orderId: number | string) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        const thread: CommunicationThread = {
          id: Number(orderId),
          target_type: "order",
          target_id: Number(orderId),
          kind: "client_support",
          status: "open",
          subject: `Order #${orderId}`,
          reference: String(orderId),
          last_message_at: new Date().toISOString(),
          metadata: { source: "preview" },
          created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          updated_at: new Date().toISOString(),
        };
        orderThreads.value = [thread];
        activeThread.value = thread;
        messages.value = [
          {
            id: 1,
            thread: thread.id,
            sender: 0,
            sender_display: "Client preview",
            message_type: "user",
            status: "active",
            body: "Please keep the methodology section concise and make the source quality easy to verify.",
            parent: null,
            is_internal: false,
            is_system_generated: false,
            is_edited: false,
            metadata: { source: "preview" },
            created_at: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
            updated_at: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
          },
          {
            id: 2,
            thread: thread.id,
            sender: 108,
            sender_display: "Assigned writer",
            message_type: "user",
            status: "active",
            body: "Got it. I will keep that section tight and cite only peer-reviewed sources.",
            parent: null,
            is_internal: false,
            is_system_generated: false,
            is_edited: false,
            metadata: { source: "preview" },
            created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
            updated_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
          },
        ];
        return;
      }
      const { data } = await communicationsApi.threads();
      const allThreads = normalizeList(data);
      orderThreads.value = allThreads.filter(
        (thread) =>
          thread.target_type === "order" &&
          String(thread.target_id) === String(orderId),
      );
      activeThread.value =
        orderThreads.value.find((thread) => thread.kind === "client_support") ??
        orderThreads.value[0] ??
        null;

      if (activeThread.value) {
        await loadMessages(activeThread.value.id);
      } else {
        messages.value = [];
      }
    } catch (caught) {
      error.value = "Unable to load order messages.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function createOrderThread(input: {
    orderId: number | string;
    kind?: CommunicationThreadKind;
    subject?: string;
  }) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        const thread: CommunicationThread = {
          id: Number(input.orderId),
          target_type: "order",
          target_id: Number(input.orderId),
          kind: input.kind ?? "client_support",
          status: "open",
          subject: input.subject ?? `Order #${input.orderId}`,
          reference: String(input.orderId),
          last_message_at: null,
          metadata: { source: "preview" },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        activeThread.value = thread;
        orderThreads.value = [thread, ...orderThreads.value];
        messages.value = [];
        notice.value = "Preview message thread created.";
        return thread;
      }
      const { data } = await communicationsApi.createThread({
        target_app_label: "orders",
        target_model: "order",
        target_object_id: Number(input.orderId),
        kind: input.kind ?? "client_support",
        subject: input.subject ?? `Order #${input.orderId}`,
        metadata: {
          source: "client_order_workbench",
        },
      });
      activeThread.value = data;
      orderThreads.value = [data, ...orderThreads.value];
      inboxThreads.value = [data, ...inboxThreads.value];
      messages.value = [];
      notice.value = "Order message thread created.";
      return data;
    } catch (caught) {
      error.value = "Unable to create an order message thread.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMessages(threadId: number | string) {
    const { data } = await communicationsApi.threadMessages(threadId);
    messages.value = normalizeList(data);
  }

  async function sendMessage(
    body: string,
    opts?: { isInternal?: boolean; recipientRole?: string; attachments?: Array<{ name: string; type: string; dataUrl: string }> },
  ) {
    const auth = useAuthStore();
    if (!activeThread.value) return null;
    isSending.value = true;
    error.value = "";
    notice.value = "";

    const isInternal = opts?.isInternal ?? false;
    const recipientRole = opts?.recipientRole;
    const attachments = opts?.attachments;

    try {
      if (auth.isPreviewSession) {
        const message: CommunicationMessage = {
          id: Date.now(),
          thread: activeThread.value.id,
          sender: 0,
          sender_display: "You (preview)",
          message_type: "user",
          status: "active",
          body,
          parent: null,
          is_internal: isInternal,
          is_system_generated: false,
          is_edited: false,
          attachments: attachments?.map((a) => ({ name: a.name, type: a.type, dataUrl: a.dataUrl })),
          metadata: { source: "preview", recipient_role: recipientRole },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        messages.value = [...messages.value, message];
        notice.value = "Preview message sent.";
        return message;
      }
      const { data } = await communicationsApi.createThreadMessage(
        activeThread.value.id,
        {
          body,
          is_internal: isInternal,
          ...(attachments?.length ? { attachments } : {}),
          metadata: {
            source: "message_thread",
            ...(recipientRole ? { recipient_role: recipientRole } : {}),
          },
        },
      );
      messages.value = [...messages.value, data];
      notice.value = "Message sent.";
      return data;
    } catch (caught) {
      error.value = "Unable to send that message.";
      throw caught;
    } finally {
      isSending.value = false;
    }
  }

  return {
    orderThreads,
    inboxThreads,
    activeThread,
    messages,
    isLoading,
    isSending,
    error,
    notice,
    hasThread,
    loadInboxThreads,
    selectThread,
    loadOrderThread,
    createOrderThread,
    loadMessages,
    sendMessage,
  };
});
