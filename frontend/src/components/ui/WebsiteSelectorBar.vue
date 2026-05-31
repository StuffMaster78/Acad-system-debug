<template>
  <div class="flex items-center gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5">
    <Globe class="size-4 shrink-0 text-amber-700" />
    <div class="min-w-0 flex-1">
      <span class="text-xs font-semibold text-amber-800">{{ label }}</span>
      <select
        v-if="websites.length > 1"
        :value="modelValue"
        class="ml-2 rounded border border-amber-200 bg-white px-2 py-1 text-xs font-semibold text-ink focus:outline-none focus:ring-1 focus:ring-amber-400"
        @change="$emit('update:modelValue', Number(($event.target as HTMLSelectElement).value))"
      >
        <option v-for="ws in websites" :key="ws.id" :value="ws.id">
          {{ ws.name }} ({{ ws.domain.replace(/https?:\/\//, "") }})
        </option>
      </select>
      <span v-else class="ml-2 text-xs font-bold text-ink">
        {{ currentWebsite?.name ?? "—" }}
        <span class="font-normal text-amber-700">({{ currentWebsite?.domain.replace(/https?:\/\//, "") }})</span>
      </span>
    </div>
    <span class="shrink-0 rounded-full bg-amber-200 px-2 py-0.5 text-xs font-semibold text-amber-900">
      Multi-site
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { Globe } from "@lucide/vue";
import { websitesApi, type Website } from "@/api/websites";
import { useAuthStore } from "@/stores/auth";

const props = withDefaults(
  defineProps<{ modelValue: number | null; label?: string }>(),
  { label: "Managing content for:" },
);
const emit  = defineEmits<{ "update:modelValue": [id: number | null] }>();

const auth     = useAuthStore();
const websites = ref<Website[]>([]);

const isStaff = computed(() => {
  const role = auth.role;
  return role === "superadmin" || role === "admin";
});

const currentWebsite = computed(() =>
  websites.value.find((w) => w.id === props.modelValue) ?? websites.value[0] ?? null
);

onMounted(async () => {
  if (!isStaff.value) return;
  try {
    const { data } = await websitesApi.list({ is_active: true, limit: 50 });
    websites.value = Array.isArray(data) ? data : (data as { results: Website[] }).results ?? [];
    if (websites.value.length && !props.modelValue) {
      emit("update:modelValue", websites.value[0].id);
    }
  } catch { /* non-fatal */ }
});
</script>
