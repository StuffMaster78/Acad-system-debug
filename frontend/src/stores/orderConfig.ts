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
  });
  const isLoading = ref(false);
  const error = ref("");

  const hasLiveOptions = computed(() =>
    Object.values(collections.value).some((items) => items.length > 0),
  );

  async function fetchAll() {
    isLoading.value = true;
    error.value = "";
    try {
      const [
        academicLevels,
        paperTypes,
        formattingStyles,
        subjects,
        typesOfWork,
        englishTypes,
      ] = await Promise.all([
        orderConfigApi.academicLevels(),
        orderConfigApi.paperTypes(),
        orderConfigApi.formattingStyles(),
        orderConfigApi.subjects(),
        orderConfigApi.typesOfWork(),
        orderConfigApi.englishTypes(),
      ]);

      collections.value = {
        academicLevels,
        paperTypes,
        formattingStyles,
        subjects,
        typesOfWork,
        englishTypes,
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
