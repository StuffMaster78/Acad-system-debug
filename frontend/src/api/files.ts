import { api, apiPath } from "./client";

export type FilePurpose =
  | "order_instruction"
  | "order_reference"
  | "order_deliverable"
  | "style_reference"
  | "order_revision"
  | "message_attachment";

export type FileVisibility =
  | "order_participants"
  | "client_writer_staff"
  | "client_and_staff"
  | "owner_only";

export interface FileUploadResponse {
  file_id: number;
}

export interface ManagedFile {
  id?: number;
  name?: string;
  size?: number;
  type?: string;
  status?: string;
  uuid?: string;
  original_filename?: string;
  file_size_bytes?: number;
  mime_type?: string;
  file_extension?: string;
  file_kind?: string;
  scan_status?: string;
  lifecycle_status?: string;
  public_url?: string | null;
  download_url?: string | null;
  created_at?: string;
}

export interface FileAttachment {
  id: number;
  purpose: string;
  visibility: string;
  is_primary: boolean;
  managed_file?: ManagedFile | null;
  attached_at: string;
}

export interface FileAttachPayload {
  file_id: number;
  object_id: number | string;
  content_type: "order";
  purpose: FilePurpose;
  visibility: FileVisibility;
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

export interface ExternalFileLink {
  id: number;
  url: string;
  status: string;
  provider?: string;
  created_at: string;
}

export interface FilePolicy {
  id: number;
  name: string;
  purpose: string;
  allowed_mime_types: string[];
  allowed_extensions: string[];
  max_file_size_bytes: number;
  allow_external_links: boolean;
  external_links_require_review: boolean;
  require_scan_before_download: boolean;
  require_review_before_download: boolean;
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

type ListResponse<T> = T[] | { results: T[] };

export const filesApi = {
  upload: (formData: FormData) =>
    api.post<FileUploadResponse>(apiPath("/files/upload/"), formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  attach: (payload: FileAttachPayload) =>
    api.post<FileAttachment>(apiPath("/files/attach/"), payload),
  orderAttachments: (orderId: number | string, params?: Record<string, unknown>) =>
    api.get<FileAttachment[] | { results: FileAttachment[] }>(
      apiPath("/files/attachments/"),
      { params: { content_type: "order", object_id: orderId, ...params } },
    ),
  downloadUrl: (attachmentId: number | string) =>
    apiPath(`/files/download/${attachmentId}/`),
  adminFiles: (params?: Record<string, unknown>) =>
    api.get<ManagedFile[]>(apiPath("/files/admin/files/"), { params }),
  adminDeletionRequests: (params?: Record<string, unknown>) =>
    api.get<ListResponse<FileDeletionRequest>>(
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
  externalLinks: (params?: Record<string, unknown>) =>
    api.get<ExternalFileLink[]>(apiPath("/files/admin/external-links/"), { params }),
  approveExternalLink: (linkId: number | string, review_note = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/external-links/${linkId}/approve/`),
      { review_note },
    ),
  rejectExternalLink: (linkId: number | string, review_note = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/external-links/${linkId}/reject/`),
      { review_note },
    ),
  policies: () =>
    api.get<ListResponse<FilePolicy>>(apiPath("/files/admin/policies/")),
  releaseQuarantine: (fileId: number | string, summary = "") =>
    api.post<AdminActionResponse>(
      apiPath(`/files/admin/files/${fileId}/release-quarantine/`),
      { summary },
    ),
};
