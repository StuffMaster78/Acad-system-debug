import { ref } from "vue";
import { defineStore } from "pinia";
import {
  filesApi,
  type FileAttachment,
  type FilePurpose,
  type FileVisibility,
} from "@/api/files";
import { useAuthStore } from "@/stores/auth";

export const useFilesStore = defineStore("files", () => {
  const attachments = ref<FileAttachment[]>([]);
  const isUploading = ref(false);
  const error = ref("");
  const notice = ref("");

  async function uploadAndAttachToOrder(input: {
    orderId: number | string;
    file: File;
    purpose: FilePurpose;
    visibility: FileVisibility;
  }) {
    const auth = useAuthStore();
    isUploading.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        const attachment: FileAttachment = {
          id: Date.now(),
          purpose: input.purpose,
          visibility: input.visibility,
          is_primary: false,
          managed_file: {
            uuid: crypto.randomUUID(),
            original_filename: input.file.name,
            file_size_bytes: input.file.size,
            mime_type: input.file.type || "application/octet-stream",
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
        notice.value = "Preview file attached to this order.";
        return attachment;
      }

      const formData = new FormData();
      formData.append("file", input.file);
      formData.append("purpose", input.purpose);
      formData.append("file_kind", "order_attachment");
      formData.append("is_public", "false");

      const upload = await filesApi.upload(formData);
      const attach = await filesApi.attach({
        file_id: upload.data.file_id,
        object_id: input.orderId,
        content_type: "order",
        purpose: input.purpose,
        visibility: input.visibility,
      });

      attachments.value = [attach.data, ...attachments.value];
      notice.value = "File attached to this order.";
      return attach.data;
    } catch (caught) {
      error.value = "Unable to upload and attach that file.";
      throw caught;
    } finally {
      isUploading.value = false;
    }
  }

  function clearMessages() {
    error.value = "";
    notice.value = "";
  }

  return {
    attachments,
    isUploading,
    error,
    notice,
    uploadAndAttachToOrder,
    clearMessages,
  };
});
