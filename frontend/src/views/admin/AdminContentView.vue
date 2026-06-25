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
                  <template v-if="!doc.is_active">
                    <template v-if="deletingDocId === doc.id">
                      <button class="rounded-md border border-rose-200 bg-rose-50 px-2 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100" @click="deleteDoc(doc.id)">Delete</button>
                      <button class="rounded-md border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50" @click="deletingDocId = null">Cancel</button>
                    </template>
                    <button v-else class="rounded p-1 text-slate-400 hover:text-rose-500" @click="deletingDocId = doc.id"><Trash2 class="size-3.5" /></button>
                  </template>
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
                <template v-if="deletingCategoryId === cat.id">
                  <button class="rounded border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-semibold text-rose-700 hover:bg-rose-100" @click.stop="deleteCategory(cat.id)">Delete</button>
                  <button class="rounded border border-slate-200 px-2 py-0.5 text-xs text-graphite hover:bg-slate-50" @click.stop="deletingCategoryId = null">Cancel</button>
                </template>
                <button v-else class="rounded p-1 text-slate-400 hover:text-rose-500" @click.stop="deletingCategoryId = cat.id"><Trash2 class="size-3.5" /></button>
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
                <template v-if="deletingArticleId === art.id">
                  <button class="rounded border border-rose-200 bg-rose-50 px-2 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100" @click="deleteArticle(art.id)">Delete</button>
                  <button class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50" @click="deletingArticleId = null">Cancel</button>
                </template>
                <button v-else class="rounded p-1.5 text-slate-400 hover:text-rose-500" @click="deletingArticleId = art.id"><Trash2 class="size-3.5" /></button>
              </div>
            </div>
            <div v-if="!articles.length" class="py-12 text-center text-sm text-graphite">
              {{ selectedCategory ? 'No articles in this category yet.' : 'Select a category or create the first article.' }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Static pages ──────────────────────────────────────────────────────── -->
    <template v-else-if="tab === 'pages'">
      <div class="space-y-4">

        <!-- List -->
        <div v-if="!editingPage" class="space-y-3">
          <div class="flex items-center justify-between">
            <p class="text-sm text-graphite">
              Pages are published at <code class="rounded bg-slate-100 px-1 text-xs">/lp/&lt;slug&gt;</code> on the public site.
            </p>
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-berry px-3 py-2 text-xs font-semibold text-white hover:bg-rose-700"
              @click="newPage"
            >
              + New page
            </button>
          </div>

          <div v-if="isLoadingPages" class="space-y-2 animate-pulse">
            <div v-for="n in 4" :key="n" class="h-14 rounded-xl bg-slate-100" />
          </div>

          <div v-else-if="!pages.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-16 text-center">
            <FileText class="mx-auto mb-3 size-8 text-slate-300" />
            <p class="text-sm font-medium text-graphite">No static pages yet.</p>
            <p class="mt-1 text-xs text-slate-400">Create your first page — About Us, Contact, FAQ, or any custom content.</p>
            <button class="mt-4 text-xs font-semibold text-berry hover:underline" @click="newPage">Create first page</button>
          </div>

          <div v-else class="rounded-xl border border-slate-200 bg-white divide-y divide-slate-100">
            <div v-for="page in pages" :key="page.id" class="flex items-center gap-4 px-5 py-4">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-semibold text-ink truncate">{{ page.title }}</p>
                  <span
                    class="rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="page.is_published ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
                  >{{ page.is_published ? 'Live' : 'Draft' }}</span>
                </div>
                <div class="mt-0.5 flex flex-wrap items-center gap-3 text-xs text-graphite">
                  <span class="font-mono">/lp/{{ page.slug }}</span>
                  <a
                    v-if="page.is_published"
                    :href="`/lp/${page.slug}`"
                    target="_blank"
                    rel="noreferrer"
                    class="flex items-center gap-1 text-blue-600 hover:underline"
                  >
                    <ExternalLink class="size-3" /> View live
                  </a>
                </div>
                <p v-if="page.meta_description" class="mt-1 text-xs text-slate-400 line-clamp-1">{{ page.meta_description }}</p>
              </div>

              <div class="flex shrink-0 items-center gap-2">
                <button
                  class="rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-colors"
                  :class="page.is_published
                    ? 'border-amber-200 text-amber-700 hover:bg-amber-50'
                    : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'"
                  @click="togglePublish(page)"
                >{{ page.is_published ? 'Unpublish' : 'Publish' }}</button>
                <button
                  class="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50"
                  @click="editPage(page)"
                >Edit</button>
                <template v-if="deletingPageId === page.id">
                  <button class="rounded border border-rose-200 bg-rose-50 px-2 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100" @click="deletePage(page)">Delete</button>
                  <button class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-50" @click="deletingPageId = null">Cancel</button>
                </template>
                <button v-else class="rounded p-1.5 text-slate-400 hover:text-rose-500" @click="deletingPageId = page.id"><Trash2 class="size-3.5" /></button>
              </div>
            </div>
          </div>
        </div>

        <!-- Editor -->
        <div v-else class="rounded-xl border border-slate-200 bg-white">
          <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <p class="font-semibold text-ink">{{ editingPage.id ? 'Edit page' : 'New page' }}</p>
            <button class="text-graphite hover:text-ink" @click="editingPage = null">
              <X class="size-4" />
            </button>
          </div>

          <div class="space-y-5 p-5">
            <!-- Identity -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block sm:col-span-2">
                <span class="text-xs font-semibold text-graphite">Page title</span>
                <input
                  v-model="editingPage.title"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  placeholder="About Us"
                />
              </label>
              <label class="block">
                <span class="text-xs font-semibold text-graphite">URL slug</span>
                <div class="mt-1 flex items-center">
                  <span class="rounded-l-md border border-r-0 border-slate-200 bg-slate-50 px-2.5 py-2 text-xs text-graphite">/lp/</span>
                  <input
                    v-model="editingPage.slug"
                    class="focus-ring min-w-0 flex-1 rounded-r-md border border-slate-200 px-3 py-2 text-sm"
                    placeholder="about-us"
                  />
                </div>
              </label>
              <label class="block">
                <span class="text-xs font-semibold text-graphite">SEO title <span class="font-normal text-slate-400">(optional — defaults to page title)</span></span>
                <input
                  v-model="editingPage.meta_title"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  placeholder="About WritingSystem | Expert Academic Writers"
                />
              </label>
              <label class="block sm:col-span-2">
                <span class="text-xs font-semibold text-graphite">Meta description <span class="font-normal text-slate-400">(155 chars max)</span></span>
                <textarea
                  v-model="editingPage.meta_description"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  rows="2"
                  maxlength="160"
                  placeholder="A brief description shown in search results…"
                />
              </label>
            </div>

            <!-- Scheduling -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold text-graphite">Schedule publish <span class="font-normal text-slate-400">(optional)</span></span>
                <input
                  v-model="editingPage.publish_date"
                  type="datetime-local"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  :min="new Date().toISOString().slice(0, 16)"
                />
              </label>
            </div>

            <!-- Body -->
            <div>
              <p class="mb-2 text-xs font-semibold text-graphite">Page content</p>
              <RichTextEditor
                v-model="editingPage.body_html"
                placeholder="Write your page content here. Use headings, paragraphs, lists, and links."
                min-height="400px"
              />
            </div>

            <p v-if="pageSaveError" class="text-xs text-berry">{{ pageSaveError }}</p>

            <div class="flex flex-wrap gap-2 border-t border-slate-100 pt-4">
              <button
                class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-4 py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50 disabled:opacity-60"
                :disabled="isSavingPage"
                @click="savePage(false)"
              >
                <Loader2 v-if="isSavingPage" class="size-4 animate-spin" />
                Save as draft
              </button>
              <button
                class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                :disabled="isSavingPage"
                @click="savePage(true)"
              >
                Publish now
              </button>
              <button
                class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm text-graphite hover:bg-slate-50"
                @click="editingPage = null"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>

      </div>
    </template>

    <!-- ── Citation Density ──────────────────────────────────────────────────── -->
    <template v-else-if="tab === 'citations'">
      <div class="space-y-5">

        <!-- Header + refresh -->
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p class="text-sm text-graphite max-w-2xl">
              Blog posts that reference academic sources rank better in AI answer engines (Perplexity, ChatGPT).
              Posts with <strong class="text-ink">citation_mode ≠ "none"</strong> but zero citations are the priority.
            </p>
          </div>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite hover:bg-slate-50"
            @click="loadCitationDensity"
          >
            <RefreshCw class="size-4" :class="citationLoading ? 'animate-spin' : ''" />
            Refresh
          </button>
        </div>

        <!-- Loading -->
        <div v-if="citationLoading && !citationData" class="flex justify-center py-12">
          <Loader2 class="size-7 text-slate-300 animate-spin" />
        </div>

        <template v-else-if="citationData">
          <!-- Summary cards -->
          <div class="grid gap-3 sm:grid-cols-4">
            <div class="rounded-xl border border-slate-200 bg-white p-4 text-center">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total posts</p>
              <p class="mt-1 text-2xl font-bold text-ink">{{ citationData.summary.total_posts }}</p>
            </div>
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">With citations</p>
              <p class="mt-1 text-2xl font-bold text-emerald-700">{{ citationData.summary.posts_with_citations }}</p>
            </div>
            <div
              class="rounded-xl border p-4 text-center"
              :class="citationData.summary.posts_needing_citations > 0
                ? 'border-amber-200 bg-amber-50'
                : 'border-slate-200 bg-white'"
            >
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Need citations</p>
              <p
                class="mt-1 text-2xl font-bold"
                :class="citationData.summary.posts_needing_citations > 0 ? 'text-amber-700' : 'text-slate-400'"
              >
                {{ citationData.summary.posts_needing_citations }}
              </p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4 text-center">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Coverage</p>
              <p
                class="mt-1 text-2xl font-bold"
                :class="citationData.summary.coverage_pct >= 80 ? 'text-emerald-600' : citationData.summary.coverage_pct >= 50 ? 'text-amber-600' : 'text-rose-600'"
              >
                {{ citationData.summary.coverage_pct }}%
              </p>
            </div>
          </div>

          <!-- Coverage bar -->
          <div class="rounded-xl border border-slate-200 bg-white px-5 py-4">
            <div class="flex items-center justify-between mb-2 text-xs text-graphite">
              <span>Citation coverage</span>
              <span class="font-semibold">{{ citationData.summary.posts_with_citations }} / {{ citationData.summary.total_posts }} posts</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                class="h-full rounded-full transition-all"
                :class="citationData.summary.coverage_pct >= 80 ? 'bg-emerald-500' : citationData.summary.coverage_pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'"
                :style="{ width: `${citationData.summary.coverage_pct}%` }"
              />
            </div>
            <p class="mt-2 text-xs text-graphite">
              Target: <strong class="text-ink">80%+</strong> coverage for strong GEO signals.
              <span v-if="citationData.summary.coverage_pct < 80" class="text-amber-700 ml-1">
                {{ citationData.summary.posts_needing_citations }} posts need attention.
              </span>
            </p>
          </div>

          <!-- Filter chips -->
          <div class="flex gap-2">
            <button
              v-for="f in [{ key: 'all', label: 'All posts' }, { key: 'needs', label: '⚠ Need citations' }, { key: 'has', label: '✓ Have citations' }]"
              :key="f.key"
              class="px-3 py-1.5 text-xs font-medium rounded-full border transition-colors"
              :class="citationFilter === f.key
                ? 'bg-ink text-white border-ink'
                : 'bg-white text-graphite border-slate-200 hover:border-slate-400'"
              @click="citationFilter = f.key as typeof citationFilter"
            >
              {{ f.label }}
              <span class="ml-1 opacity-60">
                ({{
                  f.key === 'all'   ? citationData.posts.length :
                  f.key === 'needs' ? citationData.posts.filter(p => p.needs_citations).length :
                  citationData.posts.filter(p => p.citation_count > 0).length
                }})
              </span>
            </button>
          </div>

          <!-- Posts table -->
          <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
            <div v-if="!filteredPosts.length" class="flex flex-col items-center py-12 text-graphite">
              <BookOpen class="size-10 mb-3 text-slate-300" />
              <p class="text-sm">No posts match this filter.</p>
            </div>
            <table v-else class="min-w-full text-sm">
              <thead class="bg-slate-50 text-xs text-graphite uppercase tracking-wide border-b border-slate-100">
                <tr>
                  <th class="px-4 py-3 text-left font-medium">Post title</th>
                  <th class="px-4 py-3 text-left font-medium">Citation mode</th>
                  <th class="px-4 py-3 text-center font-medium">Citations</th>
                  <th class="px-4 py-3 text-left font-medium">Status</th>
                  <th class="px-4 py-3 text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr
                  v-for="post in filteredPosts"
                  :key="post.id"
                  class="hover:bg-slate-50 transition-colors"
                  :class="post.needs_citations ? 'bg-amber-50/30' : ''"
                >
                  <td class="px-4 py-3">
                    <p class="font-medium text-ink truncate max-w-[280px]">{{ post.title }}</p>
                    <p class="text-xs text-graphite mt-0.5">{{ post.slug }}</p>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                      :class="post.citation_mode === 'none'
                        ? 'bg-slate-100 text-graphite'
                        : 'bg-blue-50 text-blue-700'"
                    >
                      {{ post.citation_mode === 'none' ? 'No citations' : post.citation_mode.replace(/_/g, ' ') }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span
                      class="inline-flex items-center justify-center size-7 rounded-full text-xs font-bold"
                      :class="post.citation_count === 0
                        ? post.needs_citations ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-graphite'
                        : 'bg-emerald-100 text-emerald-800'"
                    >
                      {{ post.citation_count }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-1.5 text-xs">
                      <AlertTriangle v-if="post.needs_citations" class="size-3.5 text-amber-500 shrink-0" />
                      <CheckCircle2 v-else-if="post.citation_count > 0" class="size-3.5 text-emerald-500 shrink-0" />
                      <span :class="post.needs_citations ? 'text-amber-700' : post.citation_count > 0 ? 'text-emerald-700' : 'text-graphite'">
                        {{ post.needs_citations ? 'Needs citations' : post.citation_count > 0 ? 'Good' : 'Mode: none' }}
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <a
                      :href="post.wagtail_edit_url"
                      target="_blank"
                      rel="noopener"
                      class="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-ink hover:border-signal hover:text-signal transition-colors"
                    >
                      Add citations
                      <ExternalLink class="size-3" />
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- How-to callout -->
          <div class="rounded-xl border border-blue-100 bg-blue-50 px-5 py-4">
            <p class="text-sm font-semibold text-blue-900">How to improve citation coverage</p>
            <ol class="mt-2 space-y-1 text-xs text-blue-800 list-decimal list-inside">
              <li>Click <strong>Add citations</strong> to open the post in Wagtail.</li>
              <li>Set <strong>Citation mode</strong> to APA 7, MLA 9, or Chicago.</li>
              <li>Add references via the <strong>References library</strong> — DOI or URL lookup auto-fills metadata.</li>
              <li>Re-publish the post. Citations appear at the bottom and generate JSON-LD.</li>
            </ol>
          </div>
        </template>
      </div>
    </template>

    <!-- ── Blog & Authors ────────────────────────────────────────────────────── -->
    <template v-else-if="tab === 'blog'">
      <div class="space-y-5">
        <p class="text-sm text-graphite">
          Blog posts, categories, tags, and author profiles are managed in Wagtail CMS.
          Use the links below to jump directly to each section.
        </p>

        <!-- Wagtail quick-links -->
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <a
            v-for="link in blogLinks"
            :key="link.href"
            :href="link.href"
            target="_blank"
            rel="noopener"
            class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 transition-colors hover:border-signal hover:bg-slate-50 group"
          >
            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-lg group-hover:bg-signal/10">
              {{ link.emoji }}
            </span>
            <div class="min-w-0">
              <p class="font-semibold text-ink group-hover:text-signal">{{ link.label }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ link.detail }}</p>
            </div>
            <ExternalLink class="ml-auto h-3.5 w-3.5 shrink-0 text-slate-400 group-hover:text-signal" />
          </a>
        </div>

        <!-- CMS admin home link -->
        <div class="rounded-xl border border-slate-200 bg-slate-50 px-5 py-4 flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-semibold text-ink">Wagtail admin</p>
            <p class="text-xs text-graphite mt-0.5">Full CMS — create, edit, and publish all page types.</p>
          </div>
          <a
            href="/cms-admin/"
            target="_blank"
            rel="noopener"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800"
          >
            Open CMS
            <ExternalLink class="h-3 w-3" />
          </a>
        </div>
      </div>
    </template>

    <!-- ── Exit popup ─────────────────────────────────────────────────────────── -->
    <template v-else-if="tab === 'popup'">
      <div v-if="!popupCfg" class="flex items-center gap-2 py-8 text-sm text-graphite">
        <Loader2 class="h-4 w-4 animate-spin" /> Loading…
      </div>

      <form v-else class="space-y-6 max-w-2xl" @submit.prevent="savePopupConfig">

        <!-- Enable toggle -->
        <div class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5">
          <div>
            <p class="font-semibold text-ink">Enable exit popup</p>
            <p class="mt-0.5 text-xs text-graphite">Show the popup when a visitor moves their cursor toward leaving.</p>
          </div>
          <button
            type="button"
            class="relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border-2 border-transparent transition-colors focus:outline-none"
            :class="popupCfg.is_enabled ? 'bg-signal' : 'bg-slate-200'"
            @click="popupCfg.is_enabled = !popupCfg.is_enabled"
            :aria-checked="popupCfg.is_enabled"
            role="switch"
          >
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
              :class="popupCfg.is_enabled ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <!-- Content -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 space-y-4">
          <p class="text-sm font-semibold text-ink border-b border-slate-100 pb-3">Content</p>

          <div>
            <label class="mb-1 block text-xs font-medium text-graphite">Headline</label>
            <input
              v-model="popupCfg.title"
              type="text"
              maxlength="140"
              placeholder="Wait — before you go!"
              class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-graphite">Body text</label>
            <textarea
              v-model="popupCfg.body"
              rows="3"
              placeholder="Describe the offer or reason to stay…"
              class="focus-ring w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-graphite">Image URL <span class="font-normal text-slate-400">(optional — leave blank for text-only)</span></label>
            <input
              v-model="popupCfg.image_url"
              type="url"
              placeholder="https://…"
              class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300"
            />
            <div v-if="popupCfg.image_url" class="mt-2 overflow-hidden rounded-lg border border-slate-100">
              <img :src="popupCfg.image_url" alt="Preview" class="h-32 w-full object-cover" />
            </div>
          </div>
        </div>

        <!-- CTAs -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 space-y-4">
          <p class="text-sm font-semibold text-ink border-b border-slate-100 pb-3">Call to action</p>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1 block text-xs font-medium text-graphite">Primary button label</label>
              <input v-model="popupCfg.primary_cta_label" type="text" maxlength="80" placeholder="Place my order"
                class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300" />
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-graphite">Primary button URL</label>
              <input v-model="popupCfg.primary_cta_url" type="text" placeholder="/order"
                class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300" />
            </div>
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-graphite">Dismiss label <span class="font-normal text-slate-400">(optional)</span></label>
            <input v-model="popupCfg.secondary_cta_label" type="text" maxlength="80" placeholder="Maybe later"
              class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink placeholder:text-slate-300" />
          </div>
        </div>

        <!-- Trigger -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 space-y-4">
          <p class="text-sm font-semibold text-ink border-b border-slate-100 pb-3">Trigger</p>

          <div class="flex gap-3">
            <label
              v-for="opt in TRIGGER_OPTS"
              :key="opt.value"
              class="flex flex-1 cursor-pointer flex-col items-center gap-1 rounded-xl border p-3 text-center text-xs font-medium transition-colors"
              :class="popupCfg.trigger === opt.value
                ? 'border-signal bg-signal/5 text-signal'
                : 'border-slate-200 text-graphite hover:border-slate-300'"
            >
              <input type="radio" :value="opt.value" v-model="popupCfg.trigger" class="sr-only" />
              <span class="text-xl">{{ opt.icon }}</span>
              {{ opt.label }}
            </label>
          </div>

          <div v-if="popupCfg.trigger === 'delay'">
            <label class="mb-1 block text-xs font-medium text-graphite">Delay (seconds)</label>
            <input v-model.number="popupCfg.delay_seconds" type="number" min="1" max="120"
              class="focus-ring w-32 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink" />
          </div>

          <div v-if="popupCfg.trigger === 'scroll_depth'">
            <label class="mb-1 block text-xs font-medium text-graphite">Scroll depth (%)</label>
            <input v-model.number="popupCfg.scroll_depth_percent" type="number" min="10" max="100"
              class="focus-ring w-32 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink" />
          </div>
        </div>

        <!-- Frequency -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 space-y-4">
          <p class="text-sm font-semibold text-ink border-b border-slate-100 pb-3">Frequency</p>
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-1 block text-xs font-medium text-graphite">Cooldown after dismiss (hours)</label>
              <input v-model.number="popupCfg.cooldown_hours" type="number" min="0"
                class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink" />
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-graphite">Max shows per session</label>
              <input v-model.number="popupCfg.max_shows_per_session" type="number" min="1"
                class="focus-ring w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink" />
            </div>
          </div>
        </div>

        <!-- Save -->
        <div class="flex items-center gap-3">
          <button
            type="submit"
            :disabled="popupSaving"
            class="focus-ring inline-flex items-center gap-2 rounded-lg bg-signal px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            <Loader2 v-if="popupSaving" class="h-3.5 w-3.5 animate-spin" />
            {{ popupSaving ? 'Saving…' : 'Save popup' }}
          </button>
          <p v-if="popupSuccess" class="flex items-center gap-1.5 text-sm text-emerald-600">
            <CheckCircle2 class="h-4 w-4" /> Saved
          </p>
          <p v-if="popupError" class="text-sm text-red-600">{{ popupError }}</p>
        </div>

      </form>
    </template>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { AlertTriangle, BookOpen, CheckCircle2, ExternalLink, FileText, Loader2, Pencil, RefreshCw, Trash2, X } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import RichTextEditor from "@/components/ui/RichTextEditor.vue";
import WebsiteSelectorBar from "@/components/ui/WebsiteSelectorBar.vue";
import { useAuthStore } from "@/stores/auth";
import { adminPublishingApi, type SeoPageRecord } from "@/api/adminPublishing";
import {
  legalApi,
  ALL_DOC_TYPES, DOC_TYPE_LABELS,
  type DocType, type HelpArticle, type HelpCategory, type LegalDocument,
} from "@/api/legal";

const TABS = [
  { key: "legal"     as const, label: "Legal documents" },
  { key: "help"      as const, label: "Help center" },
  { key: "pages"     as const, label: "Static pages" },
  { key: "blog"      as const, label: "Blog & authors" },
  { key: "citations" as const, label: "Citation density" },
  { key: "popup"     as const, label: "Exit popup" },
];
const tab = ref<"legal" | "help" | "pages" | "blog" | "citations" | "popup">("legal");
const auth = useAuthStore();
const isSuperAdmin = (auth.user as Record<string, unknown>)?.role === "superadmin"
  || !!(auth.user as Record<string, unknown>)?.is_superuser;
const websiteId = ref<number | null>(null);

const blogLinks = [
  { emoji: "✍️", label: "Blog posts", href: "/cms-admin/pages/", detail: "Create and publish blog articles." },
  { emoji: "🏷️", label: "Categories", href: "/cms-admin/snippets/cms_core/blogcategory/", detail: "Manage blog category names and slugs." },
  { emoji: "🔖", label: "Tags", href: "/cms-admin/snippets/cms_core/blogtag/", detail: "Manage tags used across posts." },
  { emoji: "👤", label: "Authors", href: "/cms-admin/snippets/cms_authors/cmsauthor/", detail: "Writer bios, credentials, and profiles." },
  { emoji: "📄", label: "Service pages", href: "/cms-admin/pages/", detail: "Landing pages for individual services." },
  { emoji: "🖼️", label: "Media library", href: "/cms-admin/images/", detail: "Upload and manage images for CMS content." },
];

// Build website_id param for API calls (superadmin only)
function wsParam() {
  return websiteId.value ? { website_id: websiteId.value } : {};
}

// ── Legal documents ──────────────────────────────────────────────────────────
const selectedDocType = ref<DocType>("terms_of_service");
const docVersions = ref<LegalDocument[]>([]);
const activeVersions = ref<Record<string, string>>({});
const editingDoc = ref<(Partial<LegalDocument> & { content: string }) | null>(null);
const isSavingDoc = ref(false);
const docSaveError = ref("");
const activating = ref<number | null>(null);

async function loadDocVersions() {
  try {
    const { data } = await legalApi.admin.listDocuments({ doc_type: selectedDocType.value, ...wsParam() });
    docVersions.value = data;
  } catch { docVersions.value = []; }
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
  } catch { /* non-fatal */ } finally {
    activating.value = null;
  }
}

const deletingDocId = ref<number | null>(null);

async function deleteDoc(id: number) {
  await legalApi.admin.deleteDocument(id);
  deletingDocId.value = null;
  await loadDocVersions();
}

// ── Help center ──────────────────────────────────────────────────────────────
const categories = ref<HelpCategory[]>([]);
const selectedCategory = ref<HelpCategory | null>(null);
const editingCategory = ref<Partial<HelpCategory> | null>(null);
const articles = ref<HelpArticle[]>([]);
const editingArticle = ref<(Partial<HelpArticle> & { content: string }) | null>(null);
const isSavingArticle = ref(false);
const articleSaveError = ref("");

async function loadCategories() {
  try {
    const { data } = await legalApi.admin.listCategories();
    categories.value = data;
  } catch { categories.value = []; }
}

async function loadArticles() {
  try {
    const params = selectedCategory.value ? { category: selectedCategory.value.id } : undefined;
    const { data } = await legalApi.admin.listArticles({ ...params, ...wsParam() });
    articles.value = data;
  } catch { articles.value = []; }
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

const deletingCategoryId = ref<number | null>(null);

async function deleteCategory(id: number) {
  await legalApi.admin.deleteCategory(id);
  deletingCategoryId.value = null;
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

const deletingArticleId = ref<number | null>(null);

async function deleteArticle(id: number) {
  await legalApi.admin.deleteArticle(id);
  deletingArticleId.value = null;
  await loadArticles();
  await loadCategories();
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

// ── Static pages ─────────────────────────────────────────────────────────────
const pages = ref<SeoPageRecord[]>([]);
const isLoadingPages = ref(false);
const editingPage = ref<(Partial<SeoPageRecord> & { body_html: string }) | null>(null);
const isSavingPage = ref(false);
const pageSaveError = ref("");

// Extract HTML body from the first paragraph block
function extractBody(page: SeoPageRecord): string {
  const para = (page.blocks ?? []).find((b) => (b as Record<string,unknown>).type === "paragraph");
  return para ? String((para as Record<string,unknown>).value ?? "") : "";
}

// Pack HTML back into a paragraph block
function packBody(html: string): Record<string, unknown>[] {
  return html.trim() ? [{ type: "paragraph", value: html }] : [];
}

async function loadPages() {
  isLoadingPages.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (websiteId.value) params.website_id = websiteId.value;
    const { data } = await adminPublishingApi.seoPages(params);
    pages.value = Array.isArray(data) ? data : (data as { results: SeoPageRecord[] }).results ?? [];
  } catch { pages.value = []; }
  finally { isLoadingPages.value = false; }
}

function newPage() {
  editingPage.value = {
    title: "",
    slug: "",
    meta_title: "",
    meta_description: "",
    is_published: false,
    blocks: [],
    body_html: "",
    publish_date: null,
  };
}

function editPage(page: SeoPageRecord) {
  editingPage.value = { ...page, body_html: extractBody(page) };
}

async function savePage(publish: boolean) {
  if (!editingPage.value) return;
  isSavingPage.value = true;
  pageSaveError.value = "";
  try {
    const payload = {
      title: editingPage.value.title ?? "",
      slug: editingPage.value.slug ?? "",
      meta_title: editingPage.value.meta_title ?? editingPage.value.title ?? "",
      meta_description: editingPage.value.meta_description ?? "",
      blocks: packBody(editingPage.value.body_html ?? ""),
      is_published: publish,
      publish_date: publish ? (editingPage.value.publish_date ?? null) : null,
      website: websiteId.value ?? pages.value[0]?.website ?? null,
    };
    if (editingPage.value.id) {
      await adminPublishingApi.updateSeoPage(editingPage.value.id, payload);
    } else {
      await adminPublishingApi.createSeoPage(payload as Parameters<typeof adminPublishingApi.createSeoPage>[0]);
    }
    editingPage.value = null;
    await loadPages();
  } catch {
    pageSaveError.value = "Save failed. Check the slug is unique and all fields are filled.";
  } finally {
    isSavingPage.value = false;
  }
}

async function togglePublish(page: SeoPageRecord) {
  await adminPublishingApi.updateSeoPage(page.id, { is_published: !page.is_published });
  await loadPages();
}

const deletingPageId = ref<number | null>(null);

async function deletePage(page: SeoPageRecord) {
  await adminPublishingApi.updateSeoPage(page.id, { is_published: false });
  deletingPageId.value = null;
  await loadPages();
}

onMounted(async () => {
  await Promise.all([
    loadDocVersions(),
    loadActiveVersions(),
    loadCategories(),
    loadArticles(),
    loadPages(),
  ]);
});

// ── Citation density ──────────────────────────────────────────────────────────

interface CitationPost {
  id: number;
  title: string;
  slug: string;
  url_path: string;
  citation_mode: string;
  citation_count: number;
  needs_citations: boolean;
  first_published_at: string | null;
  last_published_at: string | null;
  wagtail_edit_url: string;
}

interface CitationDensityResponse {
  summary: {
    total_posts: number;
    posts_with_citations: number;
    posts_needing_citations: number;
    coverage_pct: number;
  };
  posts: CitationPost[];
}

const citationData    = ref<CitationDensityResponse | null>(null);
const citationLoading = ref(false);
const citationFilter  = ref<"all" | "needs" | "has">("all");

const filteredPosts = computed(() => {
  const posts = citationData.value?.posts ?? [];
  if (citationFilter.value === "needs") return posts.filter(p => p.needs_citations);
  if (citationFilter.value === "has")   return posts.filter(p => p.citation_count > 0);
  return posts;
});

async function loadCitationDensity() {
  citationLoading.value = true;
  try {
    const { data } = await api.get<CitationDensityResponse>(
      apiPath("/cms-api/references/citation-density/density/")
    );
    citationData.value = data;
  } catch { /* non-fatal */ }
  finally { citationLoading.value = false; }
}

// Load on tab switch
watch(tab, (t) => {
  if (t === "citations" && !citationData.value) loadCitationDensity();
  if (t === "popup") loadPopupConfig();
});

// ── Exit popup ───────────────────────────────────────────────────────────────
interface PopupCfg {
  is_enabled: boolean;
  trigger: "exit_intent" | "delay" | "scroll_depth";
  title: string;
  body: string;
  image_url: string;
  primary_cta_label: string;
  primary_cta_url: string;
  secondary_cta_label: string;
  delay_seconds: number;
  scroll_depth_percent: number;
  cooldown_hours: number;
  max_shows_per_session: number;
}

const TRIGGER_OPTS = [
  { value: "exit_intent" as const, icon: "🖱️", label: "Exit intent" },
  { value: "delay"       as const, icon: "⏱️", label: "Time delay" },
  { value: "scroll_depth" as const, icon: "📜", label: "Scroll depth" },
];

const popupCfg     = ref<PopupCfg | null>(null);
const popupSaving  = ref(false);
const popupSuccess = ref(false);
const popupError   = ref("");

async function loadPopupConfig() {
  popupCfg.value = null;
  try {
    const { data } = await api.get<PopupCfg>(
      apiPath("/privacy/admin/exit-popup/"),
      { params: wsParam() },
    );
    popupCfg.value = data;
  } catch { popupError.value = "Could not load popup config."; }
}

async function savePopupConfig() {
  if (!popupCfg.value) return;
  popupSaving.value = true;
  popupSuccess.value = false;
  popupError.value = "";
  try {
    const { data } = await api.patch<PopupCfg>(
      apiPath("/privacy/admin/exit-popup/"),
      { ...popupCfg.value, ...wsParam() },
    );
    popupCfg.value = data;
    popupSuccess.value = true;
    setTimeout(() => { popupSuccess.value = false; }, 3000);
  } catch {
    popupError.value = "Save failed. Please try again.";
  } finally {
    popupSaving.value = false;
  }
}
</script>
