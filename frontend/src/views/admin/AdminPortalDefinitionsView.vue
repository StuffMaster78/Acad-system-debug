<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Globe, Pencil, Plus, Trash2, X } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface PortalDefinition {
  id: number;
  code: string;
  name: string;
  domain: string;
  is_active: boolean;
  created_at: string;
}

const list = ref<PortalDefinition[]>([]);
const loading = ref(false);
const notice = ref<{ type: "success" | "error"; msg: string } | null>(null);

function toast(type: "success" | "error", msg: string) {
  notice.value = { type, msg };
  setTimeout(() => { notice.value = null; }, 4000);
}

// ── Form ──────────────────────────────────────────────────────────────────────
const formOpen = ref(false);
const editingId = ref<number | null>(null);
const draft = ref({ code: "", name: "", domain: "", is_active: true });
const saving = ref(false);
const deleteTarget = ref<PortalDefinition | null>(null);

function openCreate() {
  editingId.value = null;
  draft.value = { code: "", name: "", domain: "", is_active: true };
  formOpen.value = true;
}

function openEdit(p: PortalDefinition) {
  editingId.value = p.id;
  draft.value = { code: p.code, name: p.name, domain: p.domain, is_active: p.is_active };
  formOpen.value = true;
}

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get<PortalDefinition[]>(apiPath("/accounts/portals/"));
    list.value = Array.isArray(data) ? data : (data as any).results ?? [];
  } catch {
    toast("error", "Failed to load portal definitions.");
  } finally {
    loading.value = false;
  }
}

async function save() {
  saving.value = true;
  try {
    if (editingId.value) {
      await api.patch(apiPath(`/accounts/portals/${editingId.value}/`), draft.value);
      toast("success", "Portal definition updated.");
    } else {
      await api.post(apiPath("/accounts/portals/"), draft.value);
      toast("success", "Portal definition created.");
    }
    formOpen.value = false;
    await load();
  } catch {
    toast("error", "Failed to save portal definition.");
  } finally {
    saving.value = false;
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return;
  try {
    await api.delete(apiPath(`/accounts/portals/${deleteTarget.value.id}/`));
    toast("success", "Deleted.");
    deleteTarget.value = null;
    await load();
  } catch {
    toast("error", "Failed to delete.");
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-gray-900">Portal Definitions</h1>
        <p class="mt-0.5 text-sm text-gray-500">
          Map domains to surfaces (client / writer / staff). Each record tells the
          backend which login surface a domain resolves to.
        </p>
      </div>
      <button
        class="inline-flex h-9 items-center gap-2 rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white hover:bg-indigo-700"
        @click="openCreate"
      >
        <Plus class="h-4 w-4" />
        New definition
      </button>
    </div>

    <!-- Toast -->
    <div
      v-if="notice"
      :class="notice.type === 'success' ? 'bg-green-50 text-green-800 border-green-200' : 'bg-red-50 text-red-800 border-red-200'"
      class="rounded-lg border px-4 py-3 text-sm font-medium"
    >
      {{ notice.msg }}
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div v-if="loading" class="px-6 py-12 text-center text-sm text-gray-500">Loading…</div>
      <div v-else-if="!list.length" class="px-6 py-12 text-center">
        <Globe class="mx-auto h-8 w-8 text-gray-300" />
        <p class="mt-3 text-sm font-medium text-gray-700">No portal definitions yet</p>
        <p class="mt-1 text-xs text-gray-500">Create one to map a domain to a surface.</p>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200 text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Code</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Name</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Domain</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Surface</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Status</th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in list" :key="p.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-xs text-gray-700">{{ p.code }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ p.name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.domain }}</td>
            <td class="px-4 py-3">
              <span
                :class="{
                  'bg-blue-50 text-blue-700 border-blue-200': p.code.includes('client'),
                  'bg-violet-50 text-violet-700 border-violet-200': p.code.includes('writer'),
                  'bg-amber-50 text-amber-700 border-amber-200': p.code.includes('admin') || p.code.includes('staff'),
                }"
                class="inline-block rounded-full border px-2 py-0.5 text-xs font-medium"
              >
                {{
                  p.code.includes("admin") || p.code.includes("staff") ? "staff"
                  : p.code.includes("writer") ? "writer"
                  : "client"
                }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                :class="p.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'"
                class="rounded-full px-2 py-0.5 text-xs font-medium"
              >
                {{ p.is_active ? "Active" : "Inactive" }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-2">
                <button
                  class="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"
                  title="Edit"
                  @click="openEdit(p)"
                >
                  <Pencil class="h-4 w-4" />
                </button>
                <button
                  class="rounded p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                  title="Delete"
                  @click="deleteTarget = p"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Surface reference -->
    <div class="rounded-xl border border-gray-200 bg-white p-5">
      <h2 class="text-sm font-semibold text-gray-900">Surface mapping reference</h2>
      <p class="mt-1 text-xs text-gray-500">
        The backend derives the surface from the portal <code class="rounded bg-gray-100 px-1">code</code> field.
        Use these exact codes to get the expected surface.
      </p>
      <div class="mt-3 grid grid-cols-3 gap-3 text-xs">
        <div class="rounded-lg border border-amber-200 bg-amber-50 p-3">
          <p class="font-semibold text-amber-800">Staff surface</p>
          <p class="mt-1 font-mono text-amber-700">code: internal_admin</p>
          <p class="mt-1 text-amber-600">Allows: superadmin, admin, editor, support</p>
        </div>
        <div class="rounded-lg border border-violet-200 bg-violet-50 p-3">
          <p class="font-semibold text-violet-800">Writer surface</p>
          <p class="mt-1 font-mono text-violet-700">code: writer_portal</p>
          <p class="mt-1 text-violet-600">Allows: writer</p>
        </div>
        <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
          <p class="font-semibold text-blue-800">Client surface</p>
          <p class="mt-1 font-mono text-blue-700">code: client_portal</p>
          <p class="mt-1 text-blue-600">Allows: client</p>
        </div>
      </div>
    </div>

    <!-- Create / Edit modal -->
    <div
      v-if="formOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      @click.self="formOpen = false"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div class="flex items-center justify-between">
          <h2 class="text-base font-semibold text-gray-900">
            {{ editingId ? "Edit portal definition" : "New portal definition" }}
          </h2>
          <button class="text-gray-400 hover:text-gray-600" @click="formOpen = false">
            <X class="h-5 w-5" />
          </button>
        </div>
        <div class="mt-5 space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-700">Code <span class="text-red-500">*</span></label>
            <input
              v-model="draft.code"
              placeholder="e.g. internal_admin"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
            <p class="mt-1 text-xs text-gray-400">Use one of: internal_admin, writer_portal, client_portal</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-700">Name <span class="text-red-500">*</span></label>
            <input
              v-model="draft.name"
              placeholder="e.g. Staff Admin Portal"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-700">Domain <span class="text-red-500">*</span></label>
            <input
              v-model="draft.domain"
              placeholder="e.g. admin.example.com"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>
          <label class="flex items-center gap-2 text-sm text-gray-700">
            <input v-model="draft.is_active" type="checkbox" class="rounded border-gray-300" />
            Active
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button
            class="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="formOpen = false"
          >
            Cancel
          </button>
          <button
            :disabled="saving || !draft.code || !draft.name || !draft.domain"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            @click="save"
          >
            {{ saving ? "Saving…" : editingId ? "Save changes" : "Create" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    >
      <div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h2 class="text-base font-semibold text-gray-900">Delete portal definition?</h2>
        <p class="mt-2 text-sm text-gray-600">
          <strong>{{ deleteTarget.name }}</strong> ({{ deleteTarget.domain }}) will be removed.
          Requests from that domain will fall back to the client surface.
        </p>
        <div class="mt-5 flex justify-end gap-3">
          <button
            class="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="deleteTarget = null"
          >Cancel</button>
          <button
            class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
            @click="confirmDelete"
          >Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>
