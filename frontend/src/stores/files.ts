import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { filesApi, type DeliveryGuardError, type FileAttachment, type FilePurpose } from "@/api/files";
import { useAuthStore } from "@/stores/auth";

export interface QueuedFile {
  id: string;
  file: File;
  name: string;
  purpose: FilePurpose;
  status: "pending" | "uploading" | "done" | "error";
  progress?: number;
  error?: string;
}

export const useFilesStore = defineStore("files", () => {
  const attachments = ref<FileAttachment[]>([]);
  const uploadQueue = ref<QueuedFile[]>([]);
  const isUploading = ref(false);
  const isLoadingAttachments = ref(false);
  const error = ref("");
  const notice = ref("");
  const deliveryBlocked = ref<DeliveryGuardError | null>(null);
  const newFileCount = computed(
    () => attachments.value.filter((attachment) => attachment.is_new_for_user).length,
  );

  async function fetchOrderAttachments(orderId: number | string) {
    isLoadingAttachments.value = true;
    try {
      const { data } = await filesApi.orderFiles(orderId);
      attachments.value = Array.isArray(data) ? data : (data as { results: FileAttachment[] }).results ?? [];
    } catch {
      // non-fatal
    } finally {
      isLoadingAttachments.value = false;
    }
  }

  function addToQueue(files: FileList | File[], purpose: FilePurpose) {
    for (const file of Array.from(files)) {
      uploadQueue.value.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        name: file.name,
        purpose,
        status: "pending",
      });
    }
  }

  function removeFromQueue(id: string) {
    uploadQueue.value = uploadQueue.value.filter((item) => item.id !== id);
  }

  function clearQueue() {
    uploadQueue.value = uploadQueue.value.filter((item) => item.status !== "done");
  }

  async function uploadFiles(orderId: number | string) {
    const auth = useAuthStore();
    const pending = uploadQueue.value.filter((item) => item.status === "pending");
    if (!pending.length) return;

    isUploading.value = true;
    error.value = "";
    notice.value = "";
    let successCount = 0;

    for (const item of pending) {
      const idx = uploadQueue.value.findIndex((q) => q.id === item.id);
      if (idx === -1) continue;
      uploadQueue.value[idx] = { ...uploadQueue.value[idx], status: "uploading" };

      try {
        if (auth.isPreviewSession) {
          const attachment: FileAttachment = {
            id: Date.now(),
            purpose: item.purpose,
            visibility: "order_participants",
            is_primary: false,
            is_active: true,
            display_name: item.file.name,
            managed_file: {
              uuid: crypto.randomUUID(),
              original_filename: item.file.name,
              file_size_bytes: item.file.size,
              mime_type: item.file.type || "application/octet-stream",
              file_kind: "order_attachment",
              scan_status: "not_scanned",
              lifecycle_status: "active",
              is_public: false,
              created_at: new Date().toISOString(),
            },
            attached_at: new Date().toISOString(),
          };
          attachments.value = [attachment, ...attachments.value];
          uploadQueue.value[idx] = { ...uploadQueue.value[idx], status: "done" };
          successCount++;
          continue;
        }

        const { data: attachment } = await filesApi.uploadToOrder(
          orderId,
          item.purpose,
          item.file,
        );
        attachments.value = [attachment, ...attachments.value];
        uploadQueue.value[idx] = { ...uploadQueue.value[idx], status: "done" };
        successCount++;
      } catch {
        uploadQueue.value[idx] = {
          ...uploadQueue.value[idx],
          status: "error",
          error: "Upload failed — check file type and size.",
        };
      }
    }

    isUploading.value = false;

    if (successCount === pending.length) {
      notice.value = `${successCount} file${successCount !== 1 ? "s" : ""} uploaded successfully.`;
    } else if (successCount > 0) {
      notice.value = `${successCount} of ${pending.length} uploaded. Some failed.`;
    } else {
      error.value = "All uploads failed. Check the files and try again.";
    }
  }

  async function uploadSingleFile(
    orderId: number | string,
    file: File,
    purpose: FilePurpose,
    extra?: Record<string, string>,
  ) {
    const auth = useAuthStore();
    isUploading.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        addToQueue([file], purpose);
        await uploadFiles(orderId);
        return;
      }
      const { data } = await filesApi.uploadToOrder(orderId, purpose, file, extra);
      attachments.value = [data, ...attachments.value];
      notice.value = "File uploaded successfully.";
    } catch {
      error.value = "Upload failed — check file type and size.";
    } finally {
      isUploading.value = false;
    }
  }

  async function submitExternalLink(
    orderId: number | string,
    payload: { url: string; title?: string; purpose: FilePurpose },
  ) {
    const auth = useAuthStore();
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const attachment: FileAttachment = {
          id: Date.now(),
          purpose: payload.purpose,
          visibility: payload.purpose === "writer_guide" ? "writer_and_staff" : "order_participants",
          is_primary: false,
          is_active: true,
          display_name: payload.title || payload.url,
          external_link: {
            id: Date.now(),
            title: payload.title || payload.url,
            url: payload.url,
            review_status: "approved",
            is_active: true,
            created_at: new Date().toISOString(),
          },
          attached_at: new Date().toISOString(),
        };
        attachments.value = [attachment, ...attachments.value];
        notice.value = "Link added.";
        return;
      }
      const { data } = await filesApi.submitExternalOrderLink(orderId, payload);
      attachments.value = [data, ...attachments.value];
      notice.value = "Link added.";
    } catch {
      error.value = "Could not add the link.";
    }
  }

  async function downloadFile(orderId: number | string, attachmentId: number | string) {
    deliveryBlocked.value = null;
    try {
      const { data } = await filesApi.orderFileDownload(orderId, attachmentId);
      if (data.url) {
        const idx = attachments.value.findIndex(
          (attachment) => attachment.id === Number(attachmentId),
        );
        if (idx !== -1) {
          attachments.value[idx] = {
            ...attachments.value[idx],
            is_new_for_user: false,
          };
        }
        window.open(data.url, "_blank", "noopener,noreferrer");
      }
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      const responseData = (err as { response?: { data?: unknown } })?.response?.data as DeliveryGuardError | undefined;
      if (status === 402 || status === 423) {
        deliveryBlocked.value = responseData ?? { blocked_reason: "guard_error" };
      } else {
        error.value = "Could not generate download link.";
      }
    }
  }

  async function submitFinalFile(orderId: number | string, attachmentId: number | string) {
    try {
      const { data } = await filesApi.submitFinalFile(orderId, attachmentId);
      const idx = attachments.value.findIndex((a) => a.id === attachmentId);
      if (idx !== -1) attachments.value[idx] = { ...attachments.value[idx], ...data };
      notice.value = "File submitted for delivery. The client will be notified.";
      return true;
    } catch {
      error.value = "Could not submit file for delivery.";
      return false;
    }
  }

  async function requestFileDeletion(
    orderId: number | string,
    attachmentId: number | string,
    reason: string,
  ) {
    try {
      await filesApi.requestOrderFileDeletion(orderId, attachmentId, reason);
      attachments.value = attachments.value.filter((a) => a.id !== attachmentId);
      notice.value = "Deletion request submitted.";
    } catch {
      error.value = "Could not submit deletion request.";
    }
  }

  function clearMessages() {
    error.value = "";
    notice.value = "";
    deliveryBlocked.value = null;
  }

  return {
    attachments,
    uploadQueue,
    isUploading,
    isLoadingAttachments,
    error,
    notice,
    deliveryBlocked,
    newFileCount,
    fetchOrderAttachments,
    addToQueue,
    removeFromQueue,
    clearQueue,
    uploadFiles,
    uploadSingleFile,
    submitExternalLink,
    downloadFile,
    submitFinalFile,
    requestFileDeletion,
    clearMessages,
  };
});
