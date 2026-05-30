<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Content Management</h1>
        <p class="mt-0.5 text-sm text-graphite">Legal documents, user guides, and help articles.</p>
      </div>
    </div>

    <!-- Website selector (superadmin only) -->
    <WebsiteSelectorBar
      v-if="isSuperAdmin"
      v-model="websiteId"
      class="mb-4"
      @update:modelValue="() => { loadDocVersions(); loadActiveVersions(); loadCategories(); loadArticles(); }"
    />

    <!-- Tabs -->
    <div class="border-b border-slate-200">
      <nav class="flex gap-1">
        <button
          v-for="t in TABS"
          :key="t.key"
          class="rounded-t-lg border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="tab === t.key
            ? 'border-berry text-berry'
            : 'border-transparent text-graphite hover:text-ink'"
          @click="tab = t.key"
        >
          {{ t.label }}
        </button>
      </nav>
    </div>

    <!-- ── Legal Documents ─────────────────────────────────────────────────── -->
    <template v-if="tab === 'legal'">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- Left: document type selector + version list -->
        <div class="rounded-lg border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-3">
            <p class="text-sm font-semibold text-ink">Document type</p>
          </div>
          <div class="divide-y divide-slate-100">
            <button
              v-for="dt in ALL_DOC_TYPES"
              :key="dt"
              class="flex w-full items-center justify-between px-4 py-3 text-left text-sm transition-colors hover:bg-slate-50"
              :class="selectedDocType === dt ? 'bg-berry/5 font-semibold text-berry' : 'text-graphite'"
              @click="selectDocType(dt)"
            >
              <span>{{ DOC_TYPE_LABELS[dt] }}</span>
              <span
                v-if="activeVersions[dt]"
                class="rounded-full bg-emerald-100 px-1.5 py-0.5 text-xs font-semibold text-emerald-700"
              >
                v{{ activeVersions[dt] }}
              </span>
            </button>
          </div>
          <div class="border-t border-slate-200 p-3">
            <button
              class="focus-ring w-full rounded-md bg-berry px-3 py-2 text-sm font-semibold text-white hover:bg-rose-700"
              @click="newDocument"
            >
              + New version
            </button>
          </div>
        </div>

        <!-- Right: editor / version history -->
        <div class="lg:col-span-2 space-y-4">

          <!-- Version history -->
          <div v-if="docVersions.length && !editingDoc" class="rounded-lg border border-slate-200 bg-white">
            <div class="border-b border-slate-200 px-4 py-3 flex items-center justify-between">
              <p class="text-sm font-semibold text-ink">{{ DOC_TYPE_LABELS[selectedDocType] }}</p>
            </div>
            <div class="divide-y divide-slate-100">
              <div v-for="doc in docVersions" :key="doc.id" class="flex items-center justify-between px-4 py-3">
                <div>
                  <p class="text-sm font-medium text-ink">v{{ doc.version }}</p>
                  <p class="text-xs text-graphite">Effective {{ fmtDate(doc.effective_date) }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    v-if="doc.is_active"
                    class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700"
                  >Active</span>
                  <button
                    v-if="!doc.is_active"
                    class="rounded border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                    :disabled="activating === doc.id"
                    @click="activateDoc(doc.id)"
                  >
                    <Loader2 v-if="activating === doc.id" class="inline size-3 animate-spin" />
                    <span v-else>Activate</span>
                  </button>
                  <button
                    class="rounded border border-slate-200 px-2.5 py-1 text-xs text-graphite hover:bg-slate-50"
                    @click="editDocument(doc)"
                  >
                    Edit
                  </button>
                  <button
                    v-if="!doc.is_active"
                    class="rounded p-1 text-slate-400 hover:text-rose-500"
                    @click="deleteDoc(doc.id)"
                  >
                    <Trash2 class="size-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Document editor -->
          <div v-if="editingDoc" class="rounded-lg border border-slate-200 bg-white">
            <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <p class="text-sm font-semibold text-ink">
                {{ editingDoc.id ? 'Edit document' : 'New document' }}
              </p>
              <button class="text-graphite hover:text-ink" @click="editingDoc = null">
                <X class="size-4" />
              </button>
            </div>
            <div class="space-y-4 p-4">
              <div class="grid grid-cols-2 gap-4">
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Title</span>
                  <input v-model="editingDoc.title" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
                </label>
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Version</span>
                  <input v-model="editingDoc.version" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="1.0" />
                </label>
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Effective date</span>
                  <input v-model="editingDoc.effective_date" type="date" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
                </label>
                <label class="flex items-center gap-2 pt-5">
                  <input v-model="editingDoc.requires_re_acceptance" type="checkbox" class="rounded border-slate-300" />
                  <span class="text-xs text-graphite">Require users to re-accept</span>
                </label>
              </div>

              <div>
                <p class="mb-2 text-xs font-medium text-graphite">Content</p>
                <RichTextEditor
                  v-model="editingDoc.content"
                  placeholder="Write the full document content here…"
                  min-height="400px"
                />
              </div>

              <p v-if="docSaveError" class="text-xs text-berry">{{ docSaveError }}</p>

              <div class="flex gap-2 pt-2">
                <button
                  class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="isSavingDoc"
                  @click="saveDocument(false)"
                >
                  <Loader2 v-if="isSavingDoc" class="size-4 animate-spin" />
                  Save draft
                </button>
                <button
                  class="focus-ring inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="isSavingDoc"
                  @click="saveDocument(true)"
                >
                  Save &amp; Activate
                </button>
                <button
                  class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50"
                  @click="editingDoc = null"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="!docVersions.length && !editingDoc" class="rounded-xl border border-dashed border-slate-200 bg-white py-16 text-center">
            <FileText class="mx-auto mb-3 size-8 text-slate-300" />
            <p class="text-sm text-graphite">No versions yet for {{ DOC_TYPE_LABELS[selectedDocType] }}.</p>
            <button class="mt-4 text-sm font-semibold text-berry hover:underline" @click="newDocument">Create first version</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Help Center ─────────────────────────────────────────────────────── -->
    <template v-else-if="tab === 'help'">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- Left: categories -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-wider text-graphite">Categories</p>
            <button class="text-xs font-semibold text-berry hover:underline" @click="newCategory">+ Add</button>
          </div>

          <!-- Category editor -->
          <div v-if="editingCategory" class="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
            <input v-model="editingCategory.title" class="focus-ring w-full rounded border border-slate-200 px-3 py-2 text-sm" placeholder="Category title" />
            <input v-model="editingCategory.slug" class="focus-ring w-full rounded border border-slate-200 px-3 py-2 text-sm" placeholder="slug" />
            <input v-model="editingCategory.icon" class="focus-ring w-full rounded border border-slate-200 px-3 py-2 text-sm" placeholder="book-open (Lucide icon name)" />
            <select v-model="editingCategory.audience" class="focus-ring w-full rounded border border-slate-200 px-3 py-2 text-sm">
              <option value="all">All users</option>
              <option value="client">Clients</option>
              <option value="writer">Writers</option>
              <option value="staff">Staff</option>
            </select>
            <div class="flex gap-2">
              <button class="flex-1 rounded bg-ink px-3 py-1.5 text-xs font-semibold text-white" @click="saveCategory">Save</button>
              <button class="rounded border border-slate-200 px-3 py-1.5 text-xs text-graphite" @click="editingCategory = null">Cancel</button>
            </div>
          </div>

          <div class="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
            <div
              v-for="cat in categories"
              :key="cat.id"
              class="flex cursor-pointer items-center justify-between px-4 py-3 hover:bg-slate-50"
              :class="selectedCategory?.id === cat.id ? 'bg-berry/5' : ''"
              @click="selectCategory(cat)"
            >
              <div>
                <p class="text-sm font-medium text-ink">{{ cat.title }}</p>
                <p class="text-xs text-graphite">{{ cat.article_count }} articles · {{ cat.audience }}</p>
              </div>
              <div class="flex gap-1">
                <button class="rounded p-1 text-slate-400 hover:text-ink" @click.stop="editCategory(cat)"><Pencil class="size-3.5" /></button>
                <button class="rounded p-1 text-slate-400 hover:text-rose-500" @click.stop="deleteCategory(cat.id)"><Trash2 class="size-3.5" /></button>
              </div>
            </div>
            <div v-if="!categories.length" class="px-4 py-8 text-center text-sm text-graphite">
              No categories yet.
            </div>
          </div>
        </div>

        <!-- Right: articles -->
        <div class="lg:col-span-2 space-y-4">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-wider text-graphite">
              Articles{{ selectedCategory ? ` in "${selectedCategory.title}"` : '' }}
            </p>
            <button class="text-xs font-semibold text-berry hover:underline" @click="newArticle">+ New article</button>
          </div>

          <!-- Article editor -->
          <div v-if="editingArticle" class="rounded-lg border border-slate-200 bg-white">
            <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <p class="text-sm font-semibold text-ink">{{ editingArticle.id ? 'Edit article' : 'New article' }}</p>
              <button class="text-graphite hover:text-ink" @click="editingArticle = null"><X class="size-4" /></button>
            </div>
            <div class="space-y-4 p-4">
              <div class="grid grid-cols-2 gap-4">
                <label class="block col-span-2">
                  <span class="text-xs font-medium text-graphite">Title</span>
                  <input v-model="editingArticle.title" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
                </label>
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Slug</span>
                  <input v-model="editingArticle.slug" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
                </label>
                <label class="block">
                  <span class="text-xs font-medium text-graphite">Audience</span>
                  <select v-model="editingArticle.audience" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm">
                    <option value="all">All users</option>
                    <option value="client">Clients</option>
                    <option value="writer">Writers</option>
                    <option value="staff">Staff</option>
                  </select>
                </label>
                <label class="block col-span-2">
                  <span class="text-xs font-medium text-graphite">Summary (one line)</span>
                  <input v-model="editingArticle.summary" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" placeholder="Shown in category listings" />
                </label>
              </div>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 text-xs text-graphite">
                  <input v-model="editingArticle.is_published" type="checkbox" class="rounded border-slate-300" />
                  Published
                </label>
                <label class="flex items-center gap-2 text-xs text-graphite">
                  <input v-model="editingArticle.is_featured" type="checkbox" class="rounded border-slate-300" />
                  Featured on help center home
                </label>
              </div>
              <div>
                <p class="mb-2 text-xs font-medium text-graphite">Content</p>
                <RichTextEditor
                  v-model="editingArticle.content"
                  placeholder="Write the article content here. Use headings, lists, and links."
                  min-height="350px"
                />
              </div>
              <p v-if="articleSaveError" class="text-xs text-berry">{{ articleSaveError }}</p>
              <div class="flex gap-2 pt-2">
                <button
                  class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="isSavingArticle"
                  @click="saveArticle"
                >
                  <Loader2 v-if="isSavingArticle" class="size-4 animate-spin" />
                  Save
                </button>
                <button class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50" @click="editingArticle = null">Cancel</button>
              </div>
            </div>
          </div>

          <!-- Article list -->
          <div v-else class="rounded-lg border border-slate-200 bg-white divide-y divide-slate-100">
            <div v-for="art in articles" :key="art.id" class="flex items-start justify-between px-4 py-3">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <p class="truncate text-sm font-medium text-ink">{{ art.title }}</p>
                  <span v-if="art.is_published" class="shrink-0 rounded-full bg-emerald-100 px-1.5 py-0.5 text-xs font-semibold text-emerald-700">Live</span>
                  <span v-else class="shrink-0 rounded-full bg-amber-100 px-1.5 py-0.5 text-xs font-semibold text-amber-700">Draft</span>
                  <span v-if="art.is_featured" class="shrink-0 rounded-full bg-blue-100 px-1.5 py-0.5 text-xs font-semibold text-blue-700">Featured</span>
                </div>
                <p class="mt-0.5 truncate text-xs text-graphite">{{ art.summary }}</p>
              </div>
              <div class="ml-4 flex shrink-0 gap-1">
                <button class="rounded p-1.5 text-slate-400 hover:text-ink" @click="editArticle(art)"><Pencil class="size-3.5" /></button>
                <button class="rounded p-1.5 text-slate-400 hover:text-rose-500" @click="deleteArticle(art.id)"><Trash2 class="size-3.5" /></button>
              </div>
            </div>
            <div v-if="!articles.length" class="py-12 text-center text-sm text-graphite">
              {{ selectedCategory ? 'No articles in this category yet.' : 'Select a category or create the first article.' }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { FileText, Loader2, Pencil, Trash2, X } from "@lucide/vue";
import RichTextEditor from "@/components/ui/RichTextEditor.vue";
import WebsiteSelectorBar from "@/components/ui/WebsiteSelectorBar.vue";
import { useAuthStore } from "@/stores/auth";
import {
  legalApi,
  ALL_DOC_TYPES, DOC_TYPE_LABELS,
  type DocType, type HelpArticle, type HelpCategory, type LegalDocument,
} from "@/api/legal";

const TABS = [
  { key: "legal" as const, label: "Legal documents" },
  { key: "help"  as const, label: "Help center" },
];
const tab = ref<"legal" | "help">("legal");
const auth = useAuthStore();
const isSuperAdmin = (auth.user as Record<string, unknown>)?.role === "superadmin"
  || !!(auth.user as Record<string, unknown>)?.is_superuser;
const websiteId = ref<number | null>(null);

// Build website_id param for API calls (superadmin only)
function wsParam() {
  return websiteId.value ? { website_id: websiteId.value } : {};
}

// ── Legal documents ──────────────────────────────────────────────────────────
const selectedDocType = ref<DocType>("terms_of_service");
const docVersions = ref<LegalDocument[]>([]);
const activeVersions = ref<Record<string, string>>({});
const editingDoc = ref<Partial<LegalDocument> | null>(null);
const isSavingDoc = ref(false);
const docSaveError = ref("");
const activating = ref<number | null>(null);

async function loadDocVersions() {
  const { data } = await legalApi.admin.listDocuments({ doc_type: selectedDocType.value, ...wsParam() });
  docVersions.value = data;
}

async function loadActiveVersions() {
  try {
    const { data } = await legalApi.admin.listDocuments({ ...wsParam() });
    const active: Record<string, string> = {};
    data.filter((d) => d.is_active).forEach((d) => { active[d.doc_type] = d.version; });
    activeVersions.value = active;
  } catch { /* non-fatal */ }
}

function selectDocType(dt: DocType) {
  selectedDocType.value = dt;
  editingDoc.value = null;
  loadDocVersions();
}

function newDocument() {
  editingDoc.value = {
    doc_type: selectedDocType.value,
    title: DOC_TYPE_LABELS[selectedDocType.value],
    version: "1.0",
    effective_date: new Date().toISOString().split("T")[0],
    content: "",
    requires_re_acceptance: false,
    is_active: false,
  };
}

function editDocument(doc: LegalDocument) {
  editingDoc.value = { ...doc };
}

async function saveDocument(activate: boolean) {
  if (!editingDoc.value) return;
  isSavingDoc.value = true;
  docSaveError.value = "";
  try {
    const payload = { ...editingDoc.value, is_active: activate };
    if (editingDoc.value.id) {
      await legalApi.admin.updateDocument(editingDoc.value.id, { ...payload, ...wsParam() });
      if (activate) await legalApi.admin.activateDocument(editingDoc.value.id);
    } else {
      const { data } = await legalApi.admin.createDocument({ ...payload, ...wsParam() });
      if (activate) await legalApi.admin.activateDocument(data.id);
    }
    editingDoc.value = null;
    await loadDocVersions();
    await loadActiveVersions();
  } catch {
    docSaveError.value = "Save failed. Check all fields and try again.";
  } finally {
    isSavingDoc.value = false;
  }
}

async function activateDoc(id: number) {
  activating.value = id;
  try {
    await legalApi.admin.activateDocument(id);
    await loadDocVersions();
    await loadActiveVersions();
  } finally {
    activating.value = null;
  }
}

async function deleteDoc(id: number) {
  if (!confirm("Delete this version?")) return;
  await legalApi.admin.deleteDocument(id);
  await loadDocVersions();
}

// ── Help center ──────────────────────────────────────────────────────────────
const categories = ref<HelpCategory[]>([]);
const selectedCategory = ref<HelpCategory | null>(null);
const editingCategory = ref<Partial<HelpCategory> | null>(null);
const articles = ref<HelpArticle[]>([]);
const editingArticle = ref<Partial<HelpArticle> | null>(null);
const isSavingArticle = ref(false);
const articleSaveError = ref("");

async function loadCategories() {
  const { data } = await legalApi.admin.listCategories();
  categories.value = data;
}

async function loadArticles() {
  const params = selectedCategory.value ? { category: selectedCategory.value.id } : undefined;
  const { data } = await legalApi.admin.listArticles({ ...params, ...wsParam() });
  articles.value = data;
}

function selectCategory(cat: HelpCategory) {
  selectedCategory.value = cat;
  editingArticle.value = null;
  loadArticles();
}

function newCategory() {
  editingCategory.value = { title: "", slug: "", description: "", icon: "help-circle", audience: "all", is_active: true };
}

function editCategory(cat: HelpCategory) {
  editingCategory.value = { ...cat };
}

async function saveCategory() {
  if (!editingCategory.value) return;
  try {
    if (editingCategory.value.id) {
      await legalApi.admin.updateCategory(editingCategory.value.id, editingCategory.value);
    } else {
      await legalApi.admin.createCategory({ ...editingCategory.value, ...wsParam() });
    }
    editingCategory.value = null;
    await loadCategories();
  } catch { /* show inline error if needed */ }
}

async function deleteCategory(id: number) {
  if (!confirm("Delete this category? Articles will be uncategorized.")) return;
  await legalApi.admin.deleteCategory(id);
  if (selectedCategory.value?.id === id) selectedCategory.value = null;
  await loadCategories();
  await loadArticles();
}

function newArticle() {
  editingArticle.value = {
    title: "", slug: "", summary: "", content: "",
    audience: "all", is_published: false, is_featured: false,
    category: selectedCategory.value?.id,
  };
}

function editArticle(art: HelpArticle) {
  editingArticle.value = { ...art };
}

async function saveArticle() {
  if (!editingArticle.value) return;
  isSavingArticle.value = true;
  articleSaveError.value = "";
  try {
    if (editingArticle.value.id) {
      await legalApi.admin.updateArticle(editingArticle.value.id, editingArticle.value);
    } else {
      await legalApi.admin.createArticle({ ...editingArticle.value, ...wsParam() });
    }
    editingArticle.value = null;
    await loadArticles();
    await loadCategories();
  } catch {
    articleSaveError.value = "Save failed. Check all fields and try again.";
  } finally {
    isSavingArticle.value = false;
  }
}

async function deleteArticle(id: number) {
  if (!confirm("Delete this article?")) return;
  await legalApi.admin.deleteArticle(id);
  await loadArticles();
  await loadCategories();
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

onMounted(async () => {
  await Promise.all([
    loadDocVersions(),
    loadActiveVersions(),
    loadCategories(),
    loadArticles(),
  ]);
});
</script>
