import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  filesApi,
  type ExternalFileLink,
  type FileDeletionRequest,
  type FilePolicy,
  type ManagedFile,
} from "@/api/files";
import { useAuthStore } from "@/stores/auth";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewManagedFiles(): ManagedFile[] {
  return [
    {
      id: 101,
      name: "order-1-reference-brief.pdf",
      size: 384_000,
      type: "application/pdf",
      status: "active",
      original_filename: "order-1-reference-brief.pdf",
      file_size_bytes: 384_000,
      mime_type: "application/pdf",
      file_kind: "order_attachment",
      lifecycle_status: "active",
      scan_status: "clean",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: 102,
      name: "writer-final-draft.docx",
      size: 146_000,
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      status: "active",
      original_filename: "writer-final-draft.docx",
      file_size_bytes: 146_000,
      mime_type: "application/docx",
      file_kind: "writer_deliverable",
      lifecycle_status: "active",
      scan_status: "clean",
      created_at: new Date(Date.now() - 1000 * 60 * 50).toISOString(),
    },
    {
      id: 103,
      name: "suspicious-upload.zip",
      size: 4_200_000,
      type: "application/zip",
      status: "quarantined",
      original_filename: "suspicious-upload.zip",
      file_size_bytes: 4_200_000,
      mime_type: "application/zip",
      file_kind: "archive",
      lifecycle_status: "quarantined",
      scan_status: "flagged",
      created_at: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
    },
  ];
}

export const useAdminFilesStore = defineStore("adminFiles", () => {
  const files = ref<ManagedFile[]>([]);
  const deletionRequests = ref<FileDeletionRequest[]>([]);
  const externalLinks = ref<ExternalFileLink[]>([]);
  const policies = ref<FilePolicy[]>([]);
  const query = ref("");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const activeFiles = computed(() =>
    files.value.filter((file) => (file.lifecycle_status ?? file.status) === "active"),
  );
  const quarantinedFiles = computed(() =>
    files.value.filter((file) => (file.lifecycle_status ?? file.status) === "quarantined"),
  );
  const pendingDeletionRequests = computed(() =>
    deletionRequests.value.filter((request) => request.status === "pending"),
  );

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        files.value = previewManagedFiles();
        deletionRequests.value = [
          {
            id: 501,
            managed_file: 101,
            attachment: 9001,
            requested_by: 0,
            reason: "Client uploaded the wrong reference file.",
            scope: "detach_only",
            status: "pending",
            created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          },
        ];
        externalLinks.value = [
          {
            id: 601,
            url: "https://drive.example.com/reference-folder",
            status: "pending_review",
            provider: "google_drive",
            created_at: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
          },
        ];
        policies.value = [
          {
            id: 701,
            name: "Order participant files",
            purpose: "order_reference",
            allowed_mime_types: ["application/pdf", "application/docx"],
            allowed_extensions: [".pdf", ".docx"],
            max_file_size_bytes: 10_000_000,
            allow_external_links: true,
            external_links_require_review: true,
            require_scan_before_download: true,
            require_review_before_download: false,
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ];
        return;
      }

      const [filesRes, deletionRes, linksRes, policiesRes] = await Promise.allSettled([
        filesApi.adminFiles(query.value ? { q: query.value } : undefined),
        filesApi.adminDeletionRequests(),
        filesApi.externalLinks(),
        filesApi.policies(),
      ]);

      if (filesRes.status === "fulfilled") files.value = filesRes.value.data;
      if (deletionRes.status === "fulfilled") deletionRequests.value = normalizeList(deletionRes.value.data);
      if (linksRes.status === "fulfilled") externalLinks.value = linksRes.value.data;
      if (policiesRes.status === "fulfilled") policies.value = normalizeList(policiesRes.value.data);

      if ([filesRes, deletionRes, linksRes, policiesRes].some((result) => result.status === "rejected")) {
        error.value = "Some file operations data is unavailable.";
      }
    } finally {
      isLoading.value = false;
    }
  }

  async function reviewDeletionRequest(requestId: number, action: "approve" | "reject" | "complete") {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      const nextStatus =
        action === "approve" ? "approved" : action === "reject" ? "rejected" : "completed";
      if (auth.isPreviewSession) {
        deletionRequests.value = deletionRequests.value.map((request) =>
          request.id === requestId ? { ...request, status: nextStatus } : request,
        );
        notice.value = `Preview deletion request ${nextStatus}.`;
        return;
      }

      if (action === "approve") await filesApi.approveDeletionRequest(requestId);
      if (action === "reject") await filesApi.rejectDeletionRequest(requestId, "Rejected from admin file console.");
      if (action === "complete") await filesApi.completeDeletionRequest(requestId);
      notice.value = `Deletion request ${nextStatus}.`;
      await hydrate();
    } catch (caught) {
      error.value = "Unable to update deletion request.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function releaseQuarantine(fileId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        files.value = files.value.map((file) =>
          file.id === fileId
            ? { ...file, status: "active", lifecycle_status: "active", scan_status: "clean" }
            : file,
        );
        notice.value = "Preview file released from quarantine.";
        return;
      }

      await filesApi.releaseQuarantine(fileId, "Released from admin file console.");
      notice.value = "File released from quarantine.";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to release file from quarantine.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function reviewExternalLink(linkId: number, action: "approve" | "reject") {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      const nextStatus = action === "approve" ? "approved" : "rejected";
      if (auth.isPreviewSession) {
        externalLinks.value = externalLinks.value.map((link) =>
          link.id === linkId ? { ...link, status: nextStatus } : link,
        );
        notice.value = `Preview external link ${nextStatus}.`;
        return;
      }

      if (action === "approve") await filesApi.approveExternalLink(linkId);
      else await filesApi.rejectExternalLink(linkId, "Rejected from admin file console.");
      notice.value = `External link ${nextStatus}.`;
      await hydrate();
    } catch (caught) {
      error.value = "Unable to review external link.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    files,
    deletionRequests,
    externalLinks,
    policies,
    query,
    isLoading,
    isMutating,
    error,
    notice,
    activeFiles,
    quarantinedFiles,
    pendingDeletionRequests,
    hydrate,
    reviewDeletionRequest,
    releaseQuarantine,
    reviewExternalLink,
  };
});
