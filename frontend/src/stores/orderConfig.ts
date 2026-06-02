import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { orderConfigApi } from "@/api/orderConfig";
import type { OrderConfigCollections } from "@/types/config";

export const useOrderConfigStore = defineStore("order-config", () => {
  const collections = ref<OrderConfigCollections>({
    academicLevels: [],
    paperTypes: [],
    formattingStyles: [],
    subjects: [],
    typesOfWork: [],
    englishTypes: [],
    writerLevels: [],
  });
  const isLoading = ref(false);
  const error = ref("");

  const hasLiveOptions = computed(() =>
    Object.values(collections.value).some((items) => items.length > 0),
  );

  async function fetchAll(websiteId?: number | null) {
    isLoading.value = true;
    error.value = "";
    try {
      // Only pass website_id when explicitly provided (admin cross-site switching).
      // For regular users the backend middleware scopes configs from the Host header.
      const params = websiteId != null ? { website_id: websiteId } : undefined;

      const [
        academicLevels,
        paperTypes,
        formattingStyles,
        subjects,
        typesOfWork,
        englishTypes,
        writerLevelsRes,
      ] = await Promise.all([
        orderConfigApi.academicLevels(params),
        orderConfigApi.paperTypes(params),
        orderConfigApi.formattingStyles(params),
        orderConfigApi.subjects(params),
        orderConfigApi.typesOfWork(params),
        orderConfigApi.englishTypes(params),
        orderConfigApi.writerLevels(params).catch(() => []),
      ]);

      collections.value = {
        academicLevels,
        paperTypes,
        formattingStyles,
        subjects,
        typesOfWork,
        englishTypes,
        writerLevels: writerLevelsRes,
      };
    } catch (caught) {
      error.value = "Order options couldn't be loaded from the server. Check your connection and try again.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    collections,
    isLoading,
    error,
    hasLiveOptions,
    fetchAll,
  };
});
