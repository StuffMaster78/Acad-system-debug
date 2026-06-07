<!--
  SavedViewPresets — drop-in filter preset manager for admin list views.

  Usage:
    <SavedViewPresets
      view-type="orders"
      :current-filters="filters"
      @load="filters = $event"
    />

  Props:
    viewType       — matches SavedView.VIEW_TYPE_CHOICES on the backend
    currentFilters — the active filter state (to save)

  Events:
    load(filters)  — emitted when user clicks a preset; parent applies the filters
-->
<template>
  <div class="flex flex-wrap items-center gap-2">
    <!-- Preset chips -->
    <div
      v-for="sv in presets"
      :key="sv.id"
      class="group flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors"
      :class="sv.is_default
        ? 'border-signal bg-signal/5 text-signal'
        : 'border-slate-200 text-graphite hover:border-slate-300 hover:bg-slate-50'"
    >
      <button
        class="inline-flex items-center gap-1.5"
        type="button"
        @click="load(sv)"
      >
        <BookmarkCheck v-if="sv.is_default" class="h-3 w-3" />
        <Bookmark v-else class="h-3 w-3 opacity-50" />
        {{ sv.name }}
      </button>
      <button
        class="ml-0.5 rounded p-0.5 opacity-0 transition-opacity hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
        title="Delete preset"
        type="button"
        @click="deletePreset(sv.id)"
      >✕</button>
    </div>

    <!-- Save current as new preset -->
    <div v-if="!saveOpen" class="flex items-center">
      <button
        class="flex items-center gap-1 rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs text-graphite hover:border-signal hover:text-signal"
        @click="saveOpen = true"
      >
        <Plus class="h-3 w-3" /> Save current
      </button>
    </div>
    <div v-else class="flex items-center gap-1.5">
      <input
        v-model="newName"
        type="text"
        placeholder="Preset name…"
        class="focus-ring h-7 w-36 rounded-md border border-slate-200 px-2 text-xs"
        @keyup.enter="save"
        @keyup.escape="saveOpen = false"
        autofocus
      />
      <label class="flex items-center gap-1 text-xs text-graphite">
        <input v-model="setDefault" type="checkbox" class="rounded" />
        Default
      </label>
      <button class="rounded bg-signal px-2 py-0.5 text-xs font-semibold text-white" :disabled="!newName.trim()" @click="save">Save</button>
      <button class="rounded border border-slate-200 px-2 py-0.5 text-xs text-graphite" @click="saveOpen = false">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Bookmark, BookmarkCheck, Plus } from "@lucide/vue";
import { savedViewsApi, type SavedView } from "@/api/savedViews";

const props = defineProps<{
  viewType: string;
  currentFilters: Record<string, unknown>;
}>();

const emit = defineEmits<{
  (e: "load", filters: Record<string, unknown>): void;
}>();

const presets = ref<SavedView[]>([]);
const saveOpen = ref(false);
const newName = ref("");
const setDefault = ref(false);

onMounted(async () => {
  try {
    const { data } = await savedViewsApi.list(props.viewType);
    presets.value = data;
  } catch { presets.value = []; }
});

function load(sv: SavedView) {
  emit("load", sv.filters);
}

async function save() {
  const name = newName.value.trim();
  if (!name) return;
  try {
    const { data } = await savedViewsApi.save({
      view_type: props.viewType,
      name,
      filters: props.currentFilters,
      is_default: setDefault.value,
    });
    const idx = presets.value.findIndex(p => p.id === data.id);
    if (idx !== -1) presets.value[idx] = data;
    else presets.value = [...presets.value, data];
    if (setDefault.value) {
      presets.value = presets.value.map(p => ({ ...p, is_default: p.id === data.id }));
    }
    saveOpen.value = false;
    newName.value = "";
    setDefault.value = false;
  } catch { /* noop */ }
}

async function deletePreset(id: number) {
  try {
    await savedViewsApi.delete(id);
    presets.value = presets.value.filter(p => p.id !== id);
  } catch { /* noop */ }
}
</script>
