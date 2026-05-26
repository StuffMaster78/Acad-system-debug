import { ref } from "vue";
import { defineStore } from "pinia";
import type { ModalConfig, Toast, ToastType } from "@/types/ui";

export const useUiStore = defineStore("ui", () => {
  const sidebarOpen = ref(false);
  const toasts = ref<Toast[]>([]);
  const activeModal = ref<ModalConfig | null>(null);
  const globalLoading = ref(false);

  function toast(message: string, type: ToastType = "info") {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    toasts.value = [...toasts.value, { id, message, type }];
    window.setTimeout(() => dismissToast(id), 4000);
  }

  function dismissToast(id: number) {
    toasts.value = toasts.value.filter((item) => item.id !== id);
  }

  function openModal(name: string, payload?: Record<string, unknown>) {
    activeModal.value = { name, payload };
  }

  function closeModal() {
    activeModal.value = null;
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value;
  }

  function closeSidebar() {
    sidebarOpen.value = false;
  }

  return {
    sidebarOpen,
    toasts,
    activeModal,
    globalLoading,
    toast,
    dismissToast,
    openModal,
    closeModal,
    toggleSidebar,
    closeSidebar,
  };
});
