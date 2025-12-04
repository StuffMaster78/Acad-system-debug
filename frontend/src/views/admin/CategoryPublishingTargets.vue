<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Category Publishing Targets</h1>
        <p class="mt-2 text-gray-600">Set monthly publishing targets per category</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedWebsiteId"
          @change="loadTargets"
          class="border rounded px-3 py-2"
        >
          <option value="">Select Website</option>
          <option v-for="website in websites" :key="website.id" :value="website.id">
            {{ website.name }}
          </option>
        </select>
        <button
          v-if="selectedWebsiteId"
          @click="showCreateModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Add Category Target
        </button>
      </div>
    </div>

    <!-- Category Targets List -->
    <div v-if="selectedWebsiteId && !loading" class="card">
      <div v-if="categoryTargets.length" class="space-y-4">
        <div
          v-for="target in categoryTargets"
          :key="target.id"
          class="border rounded-lg p-4"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="font-semibold text-lg">{{ target.category_name }}</h3>
              <div class="mt-2">
                <div class="flex items-center gap-4 mb-2">
                  <div>
                    <span class="text-sm text-gray-600">Monthly Target:</span>
                    <span class="ml-2 font-semibold">{{ target.monthly_target }} posts</span>
                  </div>
                  <div v-if="target.current_month_stats">
                    <span class="text-sm text-gray-600">This Month:</span>
                    <span class="ml-2 font-semibold">{{ target.current_month_stats.published }} / {{ target.current_month_stats.target }}</span>
                  </div>
                </div>
                <div v-if="target.current_month_stats" class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all"
                    :class="target.current_month_stats.percentage >= 100 ? 'bg-green-500' : target.current_month_stats.percentage >= 50 ? 'bg-blue-500' : 'bg-yellow-500'"
                    :style="{ width: `${Math.min(target.current_month_stats.percentage, 100)}%` }"
                  ></div>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="editTarget(target)"
                class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
              >
                Edit
              </button>
              <button
                @click="deleteTarget(target.id)"
                class="px-3 py-1 text-sm bg-red-100 text-red-800 rounded hover:bg-red-200"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-12 text-gray-500">
        No category targets set. Create one to get started.
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingTarget" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingTarget ? 'Edit Category Target' : 'Create Category Target' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>

          <form @submit.prevent="saveTarget" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Category *</label>
              <select
                v-model="targetForm.category_id"
                required
                class="w-full border rounded px-3 py-2"
              >
                <option value="">Select Category</option>
                <option
                  v-for="cat in availableCategories"
                  :key="cat.id"
                  :value="cat.id"
                >
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Monthly Target *</label>
              <input
                v-model.number="targetForm.monthly_target"
                type="number"
                min="1"
                required
                class="w-full border rounded px-3 py-2"
              />
              <p class="text-xs text-gray-500 mt-1">Number of posts to publish in this category per month</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="targetForm.is_active"
                type="checkbox"
                class="mr-2"
              />
              <label class="text-sm">Active</label>
            </div>

            <div class="flex justify-end gap-2 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                {{ editingTarget ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'

const websites = ref([])
const selectedWebsiteId = ref('')
const categoryTargets = ref([])
const availableCategories = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const editingTarget = ref(null)

const targetForm = ref({
  website_id: null,
  category_id: null,
  monthly_target: 1,
  is_active: true
})

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({})
    websites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadTargets = async () => {
  if (!selectedWebsiteId.value) {
    categoryTargets.value = []
    return
  }

  loading.value = true
  try {
    const res = await blogPagesAPI.getCategoryTargetsByWebsite({
      website_id: selectedWebsiteId.value
    })
    categoryTargets.value = res.data || []
  } catch (e) {
    console.error('Failed to load category targets:', e)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  if (!selectedWebsiteId.value) return

  try {
    const res = await blogPagesAPI.listCategories({
      website: selectedWebsiteId.value
    })
    availableCategories.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

const editTarget = (target) => {
  editingTarget.value = target
  targetForm.value = {
    website_id: target.website,
    category_id: target.category,
    monthly_target: target.monthly_target,
    is_active: target.is_active
  }
  showCreateModal.value = true
}

const saveTarget = async () => {
  try {
    targetForm.value.website_id = selectedWebsiteId.value

    if (editingTarget.value) {
      await blogPagesAPI.updateCategoryPublishingTarget(editingTarget.value.id, targetForm.value)
    } else {
      await blogPagesAPI.createCategoryPublishingTarget(targetForm.value)
    }

    closeModal()
    await loadTargets()
  } catch (e) {
    console.error('Failed to save target:', e)
    alert('Failed to save category target. Please try again.')
  }
}

const deleteTarget = async (id) => {
  if (!confirm('Delete this category target?')) return

  try {
    await blogPagesAPI.deleteCategoryPublishingTarget(id)
    await loadTargets()
  } catch (e) {
    console.error('Failed to delete target:', e)
    alert('Failed to delete category target. Please try again.')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingTarget.value = null
  targetForm.value = {
    website_id: null,
    category_id: null,
    monthly_target: 1,
    is_active: true
  }
}

watch(selectedWebsiteId, () => {
  if (selectedWebsiteId.value) {
    loadTargets()
    loadCategories()
  }
})

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}
</style>

