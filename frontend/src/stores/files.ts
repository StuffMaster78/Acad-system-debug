import { ref } from "vue";
import { defineStore } from "pinia";
import { filesApi, type FileAttachment, type FilePurpose } from "@/api/files";
import { useAuthStore } from "@/stores/auth";

export interface QueuedFile {
  id: string;
  file: File;
  purpose: FilePurpose;
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
}

export const useFilesStore = defineStore("files", () => {
  const attachments = ref<FileAttachment[]>([]);
  const uploadQueue = ref<QueuedFile[]>([]);
  const isUploading = ref(false);
  const isLoadingAttachments = ref(false);
  const error = ref("");
  const notice = ref("");

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
  ) {
    addToQueue([file], purpose);
    await uploadFiles(orderId);
  }

  async function downloadFile(orderId: number | string, attachmentId: number | string) {
    try {
      const { data } = await filesApi.orderFileDownload(orderId, attachmentId);
      if (data.url) window.open(data.url, "_blank", "noopener,noreferrer");
    } catch {
      error.value = "Could not generate download link.";
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
  }

  return {
    attachments,
    uploadQueue,
    isUploading,
    isLoadingAttachments,
    error,
    notice,
    fetchOrderAttachments,
    addToQueue,
    removeFromQueue,
    clearQueue,
    uploadFiles,
    uploadSingleFile,
    downloadFile,
    requestFileDeletion,
    clearMessages,
  };
});
