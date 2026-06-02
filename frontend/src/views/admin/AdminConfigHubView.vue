<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import ConfigTopBar from "@/components/config/ConfigTopBar.vue";
import ConfigSidebar from "@/components/config/ConfigSidebar.vue";
import ConfigSectionCard from "@/components/config/ConfigSectionCard.vue";
import ConfigCollectionPanel from "@/components/config/ConfigCollectionPanel.vue";
import ConfigAuditDrawer from "@/components/config/ConfigAuditDrawer.vue";
import RuntimeConfigPanel from "@/components/config/RuntimeConfigPanel.vue";
import { useAdminMasterConfigStore } from "@/stores/adminMasterConfig";
import { useAdminConfigHubStore } from "@/stores/adminConfigHub";
import { useRuntimeConfigStore } from "@/stores/runtimeConfig";
import { getDomain } from "@/config/configDefinitions";

const config = useAdminMasterConfigStore();
const hub = useAdminConfigHubStore();
const runtime = useRuntimeConfigStore();

onMounted(() => {
  config.loadConfigValues();
  runtime.load();
});

// Active domain sections to render
const activeDomainMeta = computed(() => getDomain(config.activeDomain));
const activeSections = computed(() => activeDomainMeta.value?.sections ?? []);

// When navigating, scroll to the active section
watch(
  () => [config.activeDomain, config.activeSection],
  () => {
    const el = document.getElementById(`section-${config.activeSection}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  },
);
</script>

<template>
  <div class="flex h-full flex-col overflow-hidden bg-slate-50">

    <!-- Top bar -->
    <div class="relative shrink-0">
      <ConfigTopBar />
    </div>

    <!-- Body -->
    <div class="flex min-h-0 flex-1 overflow-hidden">

      <!-- Left sidebar -->
      <ConfigSidebar />

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto">

        <!-- Search results mode -->
        <div v-if="config.isSearching" class="p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-ink">
              Search results
              <span class="ml-2 text-sm font-normal text-graphite">({{ config.searchResults.length }} settings)</span>
            </h2>
          </div>

          <div v-if="!config.searchResults.length" class="rounded-lg border border-slate-200 bg-white p-12 text-center text-graphite">
            No settings match "{{ config.searchQuery }}"
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="result in config.searchResults"
              :key="result.key"
              class="rounded-lg border border-slate-200 bg-white px-5 py-3"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-sm font-medium text-ink">{{ result.label }}</p>
                  <p class="text-xs text-graphite">{{ result.description }}</p>
                  <p class="mt-1 text-[11px] text-slate-400">
                    {{ result.domain.replace(/-/g, " ") }} → {{ result.section.replace(/-/g, " ") }}
                  </p>
                </div>
                <button
                  class="shrink-0 rounded-lg border border-slate-200 px-2.5 py-1 text-xs text-graphite hover:bg-slate-50 hover:text-ink transition-colors"
                  @click="config.navigate(result.domain, result.section); config.searchQuery = ''"
                >
                  Go to section →
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Runtime Controls — live backend registry -->
        <div v-else-if="config.activeDomain === 'system'" class="p-6">
          <RuntimeConfigPanel />
        </div>

        <!-- Normal domain view -->
        <div v-else class="p-6 space-y-4">

          <!-- Domain header -->
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-ink">{{ activeDomainMeta?.label }}</h2>
              <p class="text-sm text-graphite">
                {{ activeSections.length }} section{{ activeSections.length !== 1 ? "s" : "" }}
                <span v-if="config.selectedWebsite" class="ml-1 font-medium text-berry">
                  · {{ config.selectedWebsite }} overrides
                </span>
              </p>
            </div>
          </div>

          <!-- Sections -->
          <template v-for="section in activeSections" :key="section.key">
            <div :id="`section-${section.key}`">
              <!-- CRUD sections (academic levels, paper types, etc.) -->
              <ConfigCollectionPanel
                v-if="section.isCrud && section.crudCollection"
                :section="section"
                :domain="config.activeDomain"
              />

              <!-- Discount codes CRUD (special handling) -->
              <div
                v-else-if="section.isCrud && section.key === 'discount-codes'"
                class="overflow-hidden rounded-lg border border-slate-200 bg-white"
              >
                <div class="border-b border-slate-100 px-5 py-3">
                  <h3 class="text-sm font-semibold text-ink">Discount Codes</h3>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
                      <tr>
                        <th class="px-5 py-2.5 text-left">Code</th>
                        <th class="px-5 py-2.5 text-left">Type</th>
                        <th class="px-5 py-2.5 text-right">Value</th>
                        <th class="px-5 py-2.5 text-right">Uses</th>
                        <th class="px-5 py-2.5 text-left">Expires</th>
                        <th class="px-5 py-2.5 text-center">Active</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-50">
                      <tr v-if="!hub.discountCodes.length">
                        <td colspan="6" class="py-8 text-center text-graphite">No discount codes yet.</td>
                      </tr>
                      <tr v-for="code in hub.discountCodes" :key="code.id" class="hover:bg-slate-50">
                        <td class="px-5 py-2.5 font-mono font-semibold text-ink">{{ code.code }}</td>
                        <td class="px-5 py-2.5 capitalize text-graphite">{{ code.discount_type }}</td>
                        <td class="px-5 py-2.5 text-right text-ink">
                          {{ code.discount_type === "percentage" ? `${code.value}%` : `$${code.value}` }}
                        </td>
                        <td class="px-5 py-2.5 text-right text-graphite">
                          {{ code.uses_count }}{{ code.max_uses ? ` / ${code.max_uses}` : "" }}
                        </td>
                        <td class="px-5 py-2.5 text-graphite">{{ code.expires_at ?? "Never" }}</td>
                        <td class="px-5 py-2.5 text-center">
                          <span
                            class="rounded-full px-2 py-0.5 text-xs font-semibold"
                            :class="code.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-graphite'"
                          >{{ code.is_active ? "Active" : "Off" }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Blog categories CRUD -->
              <div
                v-else-if="section.isCrud && section.key === 'blog-categories'"
                class="overflow-hidden rounded-lg border border-slate-200 bg-white"
              >
                <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
                  <h3 class="text-sm font-semibold text-ink">Blog & Page Categories</h3>
                </div>
                <div class="p-4">
                  <div class="mb-3 flex gap-2">
                    <input
                      v-model="hub.newCategoryName"
                      placeholder="New category name…"
                      class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring"
                      @keyup.enter="hub.createBlogCategory()"
                    />
                    <button
                      class="flex items-center gap-1.5 rounded-lg bg-berry px-3 py-1.5 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
                      :disabled="hub.isSaving || !hub.newCategoryName.trim()"
                      @click="hub.createBlogCategory()"
                    >Add</button>
                  </div>
                  <div class="overflow-hidden rounded-lg border border-slate-100">
                    <table class="w-full text-sm">
                      <thead class="bg-slate-50 text-xs text-graphite">
                        <tr>
                          <th class="px-4 py-2 text-left font-semibold">Name</th>
                          <th class="px-4 py-2 text-left font-semibold">Slug</th>
                          <th class="px-4 py-2 text-right font-semibold">Posts</th>
                          <th class="px-4 py-2 text-center font-semibold">Active</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-50">
                        <tr v-if="!hub.blogCategories.length">
                          <td colspan="4" class="py-6 text-center text-graphite">No categories yet.</td>
                        </tr>
                        <tr v-for="cat in hub.blogCategories" :key="cat.id">
                          <td class="px-4 py-2.5 font-medium text-ink">{{ cat.name }}</td>
                          <td class="px-4 py-2.5 font-mono text-xs text-graphite">{{ cat.slug }}</td>
                          <td class="px-4 py-2.5 text-right text-graphite">{{ cat.post_count }}</td>
                          <td class="px-4 py-2.5 text-center">
                            <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="cat.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-graphite'">
                              {{ cat.is_active ? "Active" : "Off" }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <!-- API keys CRUD -->
              <div
                v-else-if="section.isCrud && section.key === 'api-keys'"
                class="overflow-hidden rounded-lg border border-slate-200 bg-white"
              >
                <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
                  <h3 class="text-sm font-semibold text-ink">API Keys</h3>
                  <span class="rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-[10px] text-graphite">Superadmin</span>
                </div>
                <table class="w-full text-sm">
                  <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
                    <tr>
                      <th class="px-5 py-2.5 text-left">Name</th>
                      <th class="px-5 py-2.5 text-left">Prefix</th>
                      <th class="px-5 py-2.5 text-left">Last used</th>
                      <th class="px-5 py-2.5 text-center">Active</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-50">
                    <tr v-if="!hub.apiKeys.length">
                      <td colspan="4" class="py-8 text-center text-graphite">No API keys yet.</td>
                    </tr>
                    <tr v-for="key in hub.apiKeys" :key="key.id" class="hover:bg-slate-50">
                      <td class="px-5 py-2.5 font-medium text-ink">{{ key.name }}</td>
                      <td class="px-5 py-2.5 font-mono text-xs text-graphite">{{ key.prefix }}…</td>
                      <td class="px-5 py-2.5 text-graphite text-xs">{{ key.last_used_at ?? "Never" }}</td>
                      <td class="px-5 py-2.5 text-center">
                        <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="key.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-graphite'">
                          {{ key.is_active ? "Active" : "Off" }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Settings-based section -->
              <ConfigSectionCard
                v-else
                :domain="config.activeDomain"
                :section="section"
              />
            </div>
          </template>

        </div>
      </main>

      <!-- Right audit drawer -->
      <ConfigAuditDrawer v-if="config.auditSection" />
    </div>
  </div>
</template>
