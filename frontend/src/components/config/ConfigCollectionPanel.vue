<script setup lang="ts">
import { computed, watch } from "vue";
import { Check, Pencil, Plus, Trash2, X } from "@lucide/vue";
import type { ConfigSectionMeta } from "@/types/config";
import { useAdminConfigHubStore } from "@/stores/adminConfigHub";
import type { ConfigCollection } from "@/api/orderConfig";

const props = defineProps<{
  section: ConfigSectionMeta;
  domain: string;
}>();

const hub = useAdminConfigHubStore();

const collection = computed(() => props.section.crudCollection as ConfigCollection | undefined);
const isSubjects = computed(() => collection.value === "subjects");

const CATEGORY_OPTIONS = [
  { value: "", label: "All categories" },
  { value: "general", label: "General" },
  { value: "humanities", label: "Humanities & Arts" },
  { value: "sciences", label: "Natural Sciences" },
  { value: "health_sciences", label: "Health Sciences" },
  { value: "nursing", label: "Nursing & Healthcare" },
  { value: "computing", label: "Computing & Technology" },
  { value: "engineering", label: "Engineering" },
  { value: "business", label: "Business & Economics" },
  { value: "education", label: "Education" },
  { value: "social_sciences", label: "Social Sciences" },
  { value: "law", label: "Law & Legal Studies" },
  { value: "theology", label: "Theology & Religion" },
  { value: "mathematics", label: "Mathematics & Statistics" },
  { value: "environment", label: "Environment & Earth Sciences" },
];

const items = computed(() => {
  if (!collection.value) return [];
  return hub.collectionItems[collection.value] ?? [];
});

function load() {
  if (collection.value) hub.loadCollection(collection.value);
}

// Reload when category filter changes for subjects
watch(() => hub.categoryFilter, () => {
  if (isSubjects.value && collection.value) hub.loadCollection(collection.value);
});

load();
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 px-5 py-3">
      <h3 class="text-sm font-semibold text-ink">{{ section.label }}</h3>

      <!-- Category filter (subjects only) -->
      <select
        v-if="isSubjects"
        v-model="hub.categoryFilter"
        class="focus-ring h-8 rounded-lg border border-slate-200 bg-white px-2 text-xs text-graphite"
      >
        <option v-for="opt in CATEGORY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>

      <button
        class="ml-auto flex items-center gap-1.5 rounded-lg bg-berry px-3 py-1.5 text-xs font-medium text-white hover:bg-berry/90 transition-colors"
        @click="hub.showCreateForm = !hub.showCreateForm; hub.activeCollection = collection!"
      >
        <Plus class="size-3.5" />
        New
      </button>
    </div>

    <!-- Create form -->
    <div v-if="hub.showCreateForm && hub.activeCollection === collection" class="border-b border-slate-100 bg-berry/5 px-5 py-3">
      <div class="flex flex-wrap gap-2">
        <input
          v-model="hub.createForm.name"
          placeholder="Name *"
          class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring"
        />
        <input
          v-model="hub.createForm.code"
          placeholder="Code (optional)"
          class="w-36 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring"
        />
        <button
          class="flex items-center gap-1 rounded-lg bg-berry px-3 py-1.5 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
          :disabled="hub.isSaving"
          @click="hub.createOption()"
        ><Check class="size-4" /> Save</button>
        <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-graphite hover:text-ink" @click="hub.showCreateForm = false">
          <X class="size-4" />
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="hub.isLoadingCollection" class="py-10 text-center text-sm text-graphite animate-pulse">Loading…</div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
          <tr>
            <th class="px-5 py-2.5 text-left">Name</th>
            <th v-if="isSubjects" class="px-5 py-2.5 text-left">Category</th>
            <th class="px-5 py-2.5 text-left">Code</th>
            <th v-if="isSubjects" class="px-5 py-2.5 text-center">Technical</th>
            <th class="px-5 py-2.5 text-center">Active</th>
            <th class="px-5 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          <tr v-if="!items.length">
            <td :colspan="isSubjects ? 6 : 4" class="py-8 text-center text-graphite">No items yet.</td>
          </tr>
          <tr v-for="item in items" :key="item.id" class="group">
            <!-- Edit row -->
            <template v-if="hub.editingId === item.id">
              <td class="px-5 py-2">
                <input v-model="hub.editForm.name" class="w-full rounded border border-slate-200 px-2 py-1 text-sm focus-ring" />
              </td>
              <td v-if="isSubjects" class="px-5 py-2">
                <select
                  v-model="(hub.editForm as Record<string,unknown>).category"
                  class="focus-ring h-8 rounded-md border border-slate-200 bg-white px-2 text-xs"
                >
                  <option v-for="opt in CATEGORY_OPTIONS.slice(1)" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </td>
              <td class="px-5 py-2">
                <input v-model="hub.editForm.code" class="w-28 rounded border border-slate-200 px-2 py-1 text-sm focus-ring font-mono text-xs" />
              </td>
              <td v-if="isSubjects" class="px-5 py-2 text-center">
                <input v-model="(hub.editForm as Record<string,unknown>).is_technical" type="checkbox" class="rounded" />
              </td>
              <td class="px-5 py-2 text-center">
                <input v-model="hub.editForm.is_active" type="checkbox" class="rounded" />
              </td>
              <td class="px-5 py-2">
                <div class="flex items-center justify-end gap-1.5">
                  <button class="rounded bg-berry px-2 py-1 text-xs font-medium text-white hover:bg-berry/90 disabled:opacity-60" :disabled="hub.isSaving" @click="hub.saveEdit()">
                    <Check class="size-3 inline" /> Save
                  </button>
                  <button class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:text-ink" @click="hub.cancelEdit()">Cancel</button>
                </div>
              </td>
            </template>

            <!-- View row -->
            <template v-else>
              <td class="px-5 py-2.5 font-medium text-ink">{{ item.name }}</td>
              <td v-if="isSubjects" class="px-5 py-2.5">
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite capitalize">
                  {{ CATEGORY_OPTIONS.find(o => o.value === (item as Record<string,unknown>).category)?.label ?? 'General' }}
                </span>
              </td>
              <td class="px-5 py-2.5 font-mono text-xs text-graphite">{{ item.code ?? "—" }}</td>
              <td v-if="isSubjects" class="px-5 py-2.5 text-center">
                <span v-if="(item as Record<string,unknown>).is_technical" class="text-xs font-medium text-amber-600">Tech</span>
                <span v-else class="text-xs text-slate-300">—</span>
              </td>
              <td class="px-5 py-2.5 text-center">
                <button
                  :class="item.is_active ? 'text-emerald-600 hover:text-emerald-700' : 'text-slate-300 hover:text-slate-400'"
                  @click="hub.toggleActive(item)"
                ><Check class="size-4 mx-auto" /></button>
              </td>
              <td class="px-5 py-2.5">
                <div class="flex items-center justify-end gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button class="rounded p-1 text-graphite hover:text-ink" @click="hub.startEdit(item)"><Pencil class="size-3.5" /></button>
                  <button class="rounded p-1 text-graphite hover:text-rose-600" @click="hub.deleteOption(item)"><Trash2 class="size-3.5" /></button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Item count -->
    <div v-if="items.length" class="border-t border-slate-100 px-5 py-2 text-xs text-graphite">
      {{ items.length }} item{{ items.length !== 1 ? 's' : '' }}
      <span v-if="isSubjects && hub.categoryFilter"> in {{ CATEGORY_OPTIONS.find(o => o.value === hub.categoryFilter)?.label }}</span>
    </div>
  </div>
</template>
