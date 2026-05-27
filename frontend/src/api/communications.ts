import { api, apiPath } from "./client";

export type CommunicationThreadKind =
  | "client_support"
  | "client_writer"
  | "revision"
  | "dispute";

export interface ThreadParticipant {
  id: number;
  name: string;
  role: string;
}

export interface CommunicationThread {
  id: number;
  target_type: string;
  target_id: number;
  kind: CommunicationThreadKind | string;
  status: string;
  subject: string;
  reference: string;
  last_message_at?: string | null;
  participants?: ThreadParticipant[];
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface MessageAttachment {
  name: string;
  type: string;
  url?: string;
  dataUrl?: string;
}

export interface CommunicationMessage {
  id: number;
  thread: number;
  sender?: number | null;
  sender_display: string;
  sender_role?: string | null;
  sender_name?: string | null;
  message_type: string;
  status: string;
  body: string;
  parent?: number | null;
  is_internal: boolean;
  is_system_generated: boolean;
  is_edited: boolean;
  attachments?: MessageAttachment[];
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CommunicationThreadCreatePayload {
  target_app_label: "orders";
  target_model: "order";
  target_object_id: number;
  kind: CommunicationThreadKind;
  subject?: string;
  reference?: string;
  metadata?: Record<string, unknown>;
}

export interface CommunicationMessageCreatePayload {
  body: string;
  parent?: number | null;
  is_internal?: boolean;
  attachments?: MessageAttachment[];
  metadata?: Record<string, unknown>;
}

type ListResponse<T> = T[] | { results: T[] };

export const communicationsApi = {
  threads: (params?: Record<string, unknown>) =>
    api.get<ListResponse<CommunicationThread>>(apiPath("/communications/threads/"), { params }),
  createThread: (payload: CommunicationThreadCreatePayload) =>
    api.post<CommunicationThread>(apiPath("/communications/threads/"), payload),
  threadMessages: (threadId: number | string, params?: Record<string, unknown>) =>
    api.get<ListResponse<CommunicationMessage>>(
      apiPath(`/communications/threads/${threadId}/messages/`),
      { params },
    ),
  createThreadMessage: (
    threadId: number | string,
    payload: CommunicationMessageCreatePayload,
  ) =>
    api.post<CommunicationMessage>(
      apiPath(`/communications/threads/${threadId}/messages/`),
      payload,
    ),
  messages: (params?: Record<string, unknown>) =>
    api.get<ListResponse<CommunicationMessage>>(apiPath("/communications/messages/"), { params }),
  createMessage: (payload: Record<string, unknown>) =>
    api.post(apiPath("/communications/messages/"), payload),
  savedReplies: (params?: Record<string, unknown>) =>
    api.get(apiPath("/communications/saved-replies/"), { params }),
  escalations: (params?: Record<string, unknown>) =>
    api.get(apiPath("/communications/escalations/"), { params }),
};
