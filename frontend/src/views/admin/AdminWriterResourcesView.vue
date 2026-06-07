<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  BookOpen,
  CheckCircle2,
  FileText,
  Link2,
  Loader2,
  Plus,
  Search,
  Star,
  Trash2,
  UploadCloud,
  Video,
  Wrench,
} from "@lucide/vue";
import { adminWritersApi, type AdminWriterResource, type WriterResourceCategory, type WriterResourceType } from "@/api/adminWriters";
import { filesApi } from "@/api/files";

const resources = ref<AdminWriterResource[]>([]);
const categories = ref<WriterResourceCategory[]>([]);
const loading = ref(false);
const saving = ref(false);
const notice = ref("");
const error = ref("");
const search = ref("");
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const newCategoryName = ref("");

const form = reactive({
  title: "",
  description: "",
  resource_type: "document" as WriterResourceType,
  category: null as number | null,
  file_url: "",
  external_url: "",
  video_url: "",
  content: "",
  is_featured: false,
  is_active: true,
  display_order: 0,
});

const typeOptions: Array<{ value: WriterResourceType; label: string }> = [
  { value: "document", label: "PDF / Doc" },
  { value: "article", label: "Article" },
  { value: "link", label: "Link" },
  { value: "video", label: "Video" },
  { value: "tool", label: "Tool" },
];

const filteredResources = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return resources.value;
  return resources.value.filter((item) =>
    [
      item.title,
      item.description,
      item.category_name,
      item.resource_type_display,
    ].some((value) => (value ?? "").toLowerCase().includes(q)),
  );
});

const resourceStats = computed(() => ({
  total: resources.value.length,
  active: resources.value.filter((item) => item.is_active).length,
  featured: resources.value.filter((item) => item.is_featured).length,
}));

function resetForm() {
  form.title = "";
  form.description = "";
  form.resource_type = "document";
  form.category = null;
  form.file_url = "";
  form.external_url = "";
  form.video_url = "";
  form.content = "";
  form.is_featured = false;
  form.is_active = true;
  form.display_order = 0;
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = "";
}

function onFileSelected(event: Event) {
  selectedFile.value = (event.target as HTMLInputElement).files?.[0] ?? null;
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [resourceRes, categoryRes] = await Promise.all([
      adminWritersApi.resources(),
      adminWritersApi.resourceCategories(),
    ]);
    resources.value = resourceRes.data;
    categories.value = categoryRes.data;
  } catch {
    error.value = "Could not load writer resources.";
  } finally {
    loading.value = false;
  }
}

async function createCategory() {
  const name = newCategoryName.value.trim();
  if (!name) return;
  error.value = "";
  try {
    const { data } = await adminWritersApi.createResourceCategory({ name });
    categories.value = [...categories.value, data].sort((a, b) => a.display_order - b.display_order || a.name.localeCompare(b.name));
    form.category = data.id;
    newCategoryName.value = "";
  } catch {
    error.value = "Could not create category.";
  }
}

async function saveResource() {
  notice.value = "";
  error.value = "";
  saving.value = true;
  try {
    let uploadedFileId: number | null = null;
    if (selectedFile.value) {
      const { data } = await filesApi.uploadFile(selectedFile.value, "writer_guide", false);
      uploadedFileId = Number(data.file_id);
    }

    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      resource_type: form.resource_type,
      category: form.category,
      file_url: form.file_url.trim() || null,
      files_app_file_id: uploadedFileId,
      external_url: form.external_url.trim(),
      video_url: form.video_url.trim(),
      content: form.content.trim(),
      is_featured: form.is_featured,
      is_active: form.is_active,
      display_order: Number(form.display_order) || 0,
    };
    const { data } = await adminWritersApi.createResource(payload);
    resources.value = [data, ...resources.value];
    resetForm();
    notice.value = "Resource published to the writer board.";
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: Record<string, string | string[]> } })?.response?.data;
    error.value = detail ? Object.values(detail).flat().join(" ") : "Could not save resource.";
  } finally {
    saving.value = false;
  }
}

async function toggleResource(resource: AdminWriterResource, field: "is_active" | "is_featured") {
  const next = !resource[field];
  try {
    const { data } = await adminWritersApi.updateResource(resource.id, { [field]: next });
    resources.value = resources.value.map((item) => item.id === data.id ? data : item);
  } catch {
    error.value = "Could not update resource.";
  }
}

async function retireResource(resource: AdminWriterResource) {
  if (!confirm(`Retire "${resource.title}" from the writer board?`)) return;
  try {
    await adminWritersApi.deleteResource(resource.id);
    resources.value = resources.value.map((item) =>
      item.id === resource.id ? { ...item, is_active: false } : item,
    );
  } catch {
    error.value = "Could not retire resource.";
  }
}

function typeIcon(type: WriterResourceType) {
  return type === "document" ? FileText
    : type === "link" ? Link2
      : type === "video" ? Video
        : type === "tool" ? Wrench
          : BookOpen;
}

onMounted(load);
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer enablement</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Writer resources</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Publish internal articles, PDFs, links, videos, and tools for writers from one managed board.
        </p>
      </div>
      <div class="grid grid-cols-3 gap-2 text-center">
        <div class="rounded-lg border border-slate-200 bg-white px-4 py-3">
          <p class="text-xl font-semibold text-ink">{{ resourceStats.total }}</p>
          <p class="text-xs text-graphite">Total</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white px-4 py-3">
          <p class="text-xl font-semibold text-ink">{{ resourceStats.active }}</p>
          <p class="text-xs text-graphite">Active</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white px-4 py-3">
          <p class="text-xl font-semibold text-ink">{{ resourceStats.featured }}</p>
          <p class="text-xs text-graphite">Featured</p>
        </div>
      </div>
    </section>

    <p v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
      {{ notice }}
    </p>
    <p v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800">
      {{ error }}
    </p>

    <div class="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
      <section class="rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
          <Plus class="h-4 w-4 text-signal" />
          <h2 class="text-sm font-semibold text-ink">Create resource</h2>
        </div>
        <form class="space-y-4 p-5" @submit.prevent="saveResource">
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Title</span>
            <input v-model.trim="form.title" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" required />
          </label>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Type</span>
            <select v-model="form.resource_type" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
              <option v-for="type in typeOptions" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
          </label>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Category</span>
            <select v-model="form.category" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
              <option :value="null">Uncategorized</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
            </select>
          </label>

          <div class="flex gap-2">
            <input v-model.trim="newCategoryName" class="focus-ring h-10 min-w-0 flex-1 rounded-md border border-slate-200 px-3 text-sm" placeholder="New category" />
            <button class="focus-ring rounded-md border border-slate-200 px-3 text-sm font-semibold text-ink hover:bg-slate-50" type="button" @click="createCategory">
              Add
            </button>
          </div>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Short description</span>
            <textarea v-model.trim="form.description" class="focus-ring mt-1.5 w-full resize-none rounded-md border border-slate-200 px-3 py-2 text-sm" rows="2" />
          </label>

          <div v-if="form.resource_type === 'document' || form.resource_type === 'tool'" class="space-y-3 rounded-lg border border-slate-100 bg-slate-50 p-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Upload file</span>
              <input ref="fileInput" class="mt-1.5 block w-full text-sm text-graphite file:mr-3 file:rounded-md file:border-0 file:bg-ink file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white" type="file" accept=".pdf,.doc,.docx,.txt,.rtf,.ppt,.pptx" @change="onFileSelected" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Or file URL</span>
              <input v-model.trim="form.file_url" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm" type="url" placeholder="https://..." />
            </label>
          </div>

          <label v-if="form.resource_type === 'link' || form.resource_type === 'tool'" class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">External URL</span>
            <input v-model.trim="form.external_url" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="url" placeholder="https://..." />
          </label>

          <label v-if="form.resource_type === 'video'" class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Video URL</span>
            <input v-model.trim="form.video_url" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="url" placeholder="https://..." />
          </label>

          <label v-if="form.resource_type === 'article'" class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Article body</span>
            <textarea v-model.trim="form.content" class="focus-ring mt-1.5 w-full resize-y rounded-md border border-slate-200 px-3 py-2 text-sm" rows="8" placeholder="Write the internal guide here..." />
          </label>

          <div class="grid gap-3 sm:grid-cols-2">
            <label class="flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm text-graphite">
              <input v-model="form.is_featured" type="checkbox" />
              Featured
            </label>
            <label class="flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm text-graphite">
              <input v-model="form.is_active" type="checkbox" />
              Active
            </label>
          </div>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Display order</span>
            <input v-model.number="form.display_order" class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" type="number" min="0" />
          </label>

          <button class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60" type="submit" :disabled="saving || !form.title.trim()">
            <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
            <UploadCloud v-else class="h-4 w-4" />
            Publish resource
          </button>
        </form>
      </section>

      <section class="min-w-0 rounded-lg border border-slate-200 bg-white">
        <div class="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 md:flex-row md:items-center md:justify-between">
          <h2 class="text-sm font-semibold text-ink">Resource inventory</h2>
          <label class="relative block md:w-72">
            <Search class="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input v-model.trim="search" class="focus-ring h-9 w-full rounded-md border border-slate-200 pl-9 pr-3 text-sm" placeholder="Search resources" />
          </label>
        </div>

        <div v-if="loading" class="flex items-center justify-center gap-2 py-16 text-sm text-graphite">
          <Loader2 class="h-4 w-4 animate-spin" />
          Loading resources...
        </div>
        <div v-else-if="!filteredResources.length" class="py-16 text-center">
          <FileText class="mx-auto h-9 w-9 text-slate-300" />
          <p class="mt-3 text-sm font-semibold text-ink">No resources found</p>
          <p class="mt-1 text-sm text-graphite">Create one on the left to populate the writer board.</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-[900px] w-full text-sm">
            <thead class="bg-slate-50 text-left text-xs uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-5 py-3 font-semibold">Resource</th>
                <th class="px-5 py-3 font-semibold">Category</th>
                <th class="px-5 py-3 font-semibold">Signals</th>
                <th class="px-5 py-3 font-semibold">Engagement</th>
                <th class="px-5 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="resource in filteredResources" :key="resource.id">
                <td class="px-5 py-4">
                  <div class="flex items-start gap-3">
                    <component :is="typeIcon(resource.resource_type)" class="mt-0.5 h-4 w-4 shrink-0 text-signal" />
                    <div class="min-w-0">
                      <p class="truncate font-semibold text-ink">{{ resource.title }}</p>
                      <p class="mt-1 line-clamp-2 text-xs leading-5 text-graphite">{{ resource.description || resource.resource_type_display }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-4 text-graphite">{{ resource.category_name || "Uncategorized" }}</td>
                <td class="px-5 py-4">
                  <div class="flex flex-wrap gap-1.5">
                    <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="resource.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'">
                      {{ resource.is_active ? "Active" : "Retired" }}
                    </span>
                    <span v-if="resource.is_featured" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
                      <Star class="h-3 w-3" /> Featured
                    </span>
                  </div>
                </td>
                <td class="px-5 py-4 text-xs text-graphite">
                  <div>{{ resource.view_count }} views</div>
                  <div>{{ resource.download_count }} downloads</div>
                </td>
                <td class="px-5 py-4">
                  <div class="flex justify-end gap-2">
                    <button class="focus-ring rounded-md border border-slate-200 p-2 text-slate-600 hover:bg-slate-50" type="button" title="Toggle featured" @click="toggleResource(resource, 'is_featured')">
                      <Star class="h-4 w-4" />
                    </button>
                    <button class="focus-ring rounded-md border border-slate-200 p-2 text-slate-600 hover:bg-slate-50" type="button" title="Toggle active" @click="toggleResource(resource, 'is_active')">
                      <CheckCircle2 class="h-4 w-4" />
                    </button>
                    <button class="focus-ring rounded-md border border-rose-200 p-2 text-rose-600 hover:bg-rose-50" type="button" title="Retire resource" @click="retireResource(resource)">
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>
