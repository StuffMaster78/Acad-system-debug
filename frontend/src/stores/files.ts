import { ref } from "vue";
import { defineStore } from "pinia";
import {
  filesApi,
  type FileAttachment,
  type FilePurpose,
  type FileVisibility,
} from "@/api/files";
import { useAuthStore } from "@/stores/auth";

export interface QueuedFile {
  id: string;
  file: File;
  purpose: FilePurpose;
  visibility: FileVisibility;
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
      const { data } = await filesApi.orderAttachments(orderId);
      attachments.value = Array.isArray(data) ? data : data.results;
    } catch {
      // non-fatal — attachments panel still shows queued uploads
    } finally {
      isLoadingAttachments.value = false;
    }
  }

  function addToQueue(
    files: FileList | File[],
    defaults: { purpose: FilePurpose; visibility: FileVisibility },
  ) {
    const incoming = Array.from(files);
    for (const file of incoming) {
      uploadQueue.value.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        purpose: defaults.purpose,
        visibility: defaults.visibility,
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

  async function uploadQueue_(orderId: number | string) {
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
            visibility: item.visibility,
            is_primary: false,
            managed_file: {
              uuid: crypto.randomUUID(),
              original_filename: item.file.name,
              file_size_bytes: item.file.size,
              mime_type: item.file.type || "application/octet-stream",
              file_kind: "order_attachment",
              scan_status: "not_scanned",
              lifecycle_status: "active",
              public_url: null,
              download_url: null,
              created_at: new Date().toISOString(),
            },
            attached_at: new Date().toISOString(),
          };
          attachments.value = [attachment, ...attachments.value];
          uploadQueue.value[idx] = { ...uploadQueue.value[idx], status: "done" };
          successCount++;
          continue;
        }

        const formData = new FormData();
        formData.append("file", item.file);
        formData.append("purpose", item.purpose);
        formData.append("file_kind", "order_attachment");
        formData.append("is_public", "false");

        const upload = await filesApi.upload(formData);
        const attach = await filesApi.attach({
          file_id: upload.data.file_id,
          object_id: orderId,
          content_type: "order",
          purpose: item.purpose,
          visibility: item.visibility,
        });

        attachments.value = [attach.data, ...attachments.value];
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
      notice.value = `${successCount} file${successCount !== 1 ? "s" : ""} attached successfully.`;
    } else if (successCount > 0) {
      notice.value = `${successCount} of ${pending.length} files attached. Some failed.`;
    } else {
      error.value = "All uploads failed. Check the files and try again.";
    }
  }

  async function uploadAndAttachToOrder(input: {
    orderId: number | string;
    file: File;
    purpose: FilePurpose;
    visibility: FileVisibility;
  }) {
    addToQueue([input.file], { purpose: input.purpose, visibility: input.visibility });
    await uploadQueue_(input.orderId);
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
    uploadFiles: uploadQueue_,
    uploadAndAttachToOrder,
    clearMessages,
  };
});
