import { ref } from "vue";
import { defineStore } from "pinia";
import type { ModalConfig, Toast, ToastType } from "@/types/ui";

export const useUiStore = defineStore("ui", () => {
  const sidebarOpen = ref(false);
  const sidebarCollapsed = ref(
    typeof window !== "undefined" && localStorage.getItem("sidebar-collapsed") === "true",
  );
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

  function toggleSidebarCollapse() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
    localStorage.setItem("sidebar-collapsed", String(sidebarCollapsed.value));
  }

  return {
    sidebarOpen,
    sidebarCollapsed,
    toasts,
    activeModal,
    globalLoading,
    toast,
    dismissToast,
    openModal,
    closeModal,
    toggleSidebar,
    closeSidebar,
    toggleSidebarCollapse,
  };
});
