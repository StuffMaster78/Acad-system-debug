import { api, apiPath, ordersApiPath } from "./client";

export type FilePurpose =
  | "order_instruction"
  | "order_reference"
  | "order_draft"
  | "order_final"
  | "order_revision"
  | "style_reference"
  | "extra_service_file"
  | "message_attachment";

export type FileVisibility =
  | "order_participants"
  | "client_writer_staff"
  | "client_and_staff"
  | "owner_only"
  | "staff_only"
  | "private";

export interface ManagedFile {
  id?: number;
  uuid?: string;
  original_filename?: string;
  file_size_bytes?: number;
  mime_type?: string;
  file_extension?: string;
  file_kind?: string;
  scan_status?: string;
  lifecycle_status?: string;
  is_public?: boolean;
  created_at?: string;
}

export interface ExternalFileLink {
  id: number;
  title?: string;
  url: string;
  provider?: string;
  review_status?: string;
  is_active?: boolean;
  created_at?: string;
}

export type DeliveryStatus =
  | "pending"
  | "submitted"
  | "locked"
  | "approved"
  | "rejected";

export interface FileAttachment {
  id: number;
  purpose: string;
  visibility: string;
  is_primary: boolean;
  is_active?: boolean;
  is_submitted?: boolean;
  delivery_status?: DeliveryStatus;
  submitted_at?: string | null;
  first_downloaded_at?: string | null;
  display_name?: string;
  managed_file?: ManagedFile | null;
  external_link?: ExternalFileLink | null;
  metadata?: Record<string, unknown>;
  attached_at: string;
}

export interface FileDownloadResponse {
  url: string;
}

export interface DeliveryGuardError {
  blocked_reason:
    | "balance_due"
    | "scan_pending"
    | "scan_failed"
    | "not_submitted"
    | "approval_pending"
    | "rejected"
    | "guard_error";
  amount_due?: string | null;
}

export interface FileDeletionRequest {
  id: number;
  managed_file?: number | null;
  attachment?: number | null;
  requested_by?: number | null;
  reason: string;
  scope: string;
  status: string;
  admin_comment?: string;
  created_at: string;
  updated_at?: string;
}

export interface FilePolicy {
  id: number;
  name: string;
  purpose: string;
  allowed_mime_types: string[];
  allowed_extensions: string[];
  max_file_size_bytes: number;
  allow_external_links: boolean;
  external_links_require_review?: boolean;
  require_scan_before_download: boolean;
  require_review_before_download?: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminActionResponse {
  id: number;
  status?: string;
  lifecycle_status?: string;
  scan_status?: string;
}

const PURPOSE_ENDPOINT: Record<string, string> = {
  order_instruction: "instructions",
  order_reference: "references",
  style_reference: "style-references",
  order_draft: "drafts",
  order_final: "final",
  order_revision: "revisions",
  extra_service_file: "extra-services",
};

function orderFilePath(orderId: number | string, sub = "") {
  return ordersApiPath(`/orders/${orderId}/files/${sub}`);
}

export const filesApi = {
  // Order-scoped file endpoints
  orderFiles: (orderId: number | string) =>
    api.get<FileAttachment[]>(orderFilePath(orderId)),

  uploadToOrder: (
    orderId: number | string,
    purpose: FilePurpose,
    file: File,
    extra?: Record<string, string>,
  ) => {
    const sub = PURPOSE_ENDPOINT[purpose] ?? "references";
    const formData = new FormData();
    formData.append("file", file);
    if (extra) {
      for (const [k, v] of Object.entries(extra)) formData.append(k, v);
    }
    return api.post<FileAttachment>(orderFilePath(orderId, `${sub}/`), formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  orderFileDownload: (orderId: number | string, attachmentId: number | string) =>
    api.get<FileDownloadResponse>(orderFilePath(orderId, `${attachmentId}/download/`)),

  submitFinalFile: (orderId: number | string, attachmentId: number | string, payload?: { on_behalf_of?: number; reason?: string }) =>
    api.post<FileAttachment>(orderFilePath(orderId, `${attachmentId}/submit-final/`), payload ?? {}),

  requestOrderFileDeletion: (
    orderId: number | string,
    attachmentId: number | string,
    reason: string,
    scope = "detach_only",
  ) =>
    api.post(orderFilePath(orderId, `${attachmentId}/request-deletion/`), { reason, scope }),

  // Admin-only generic file management
  adminFiles: (params?: Record<string, unknown>) =>
    api.get<ManagedFile[]>(apiPath("/files/admin/files/"), { params }),

  adminDeletionRequests: (params?: Record<string, unknown>) =>
    api.get<{ results: FileDeletionRequest[] }>(
      apiPath("/files/admin/deletion-requests/"),
      { params },
    ),

  approveDeletionRequest: (requestId: number | string, admin_comment = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/deletion-requests/${requestId}/approve/`),
      { admin_comment },
    ),

  rejectDeletionRequest: (requestId: number | string, admin_comment: string) =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/deletion-requests/${requestId}/reject/`),
      { admin_comment },
    ),

  completeDeletionRequest: (requestId: number | string, admin_comment = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/deletion-requests/${requestId}/complete/`),
      { admin_comment },
    ),

  policies: () =>
    api.get<FilePolicy[]>(apiPath("/files/admin/policies/")),

  releaseQuarantine: (fileId: number | string, summary = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/files/${fileId}/release-quarantine/`),
      { summary },
    ),

  externalLinks: (params?: Record<string, unknown>) =>
    api.get<ExternalFileLink[]>(apiPath("/files/admin/external-links/"), { params }),

  approveExternalLink: (linkId: number | string) =>
    api.post<AdminActionResponse>(apiPath(`/files/admin/external-links/${linkId}/approve/`), {}),

  rejectExternalLink: (linkId: number | string, reason = "") =>
    api.post<AdminActionResponse>(apiPath(`/files/admin/external-links/${linkId}/reject/`), { reason }),

  // Generic single-file upload — used for vetting essay submissions
  uploadFile: (file: File, purpose: string, isPublic = false) => {
    const form = new FormData();
    form.append("file", file);
    form.append("purpose", purpose);
    form.append("is_public", String(isPublic));
    // Do NOT set Content-Type header manually — axios handles multipart boundary
    return api.post<{ file_id: string }>(apiPath("/files/upload/"), form);
  },
};
