<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Blog Dark Mode Images</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage dark mode images for blog posts</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Add Dark Mode Image
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Images</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ images.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Unique Blogs</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ uniqueBlogs.length }}</p>
      </div>
    </div>

    <!-- Images Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="image in images"
        :key="image.id"
        class="card p-4"
      >
        <div class="mb-3">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Blog #{{ image.blog || image.blog_id || 'N/A' }}</p>
          <img
            v-if="image.dark_mode_image"
            :src="image.dark_mode_image"
            alt="Dark mode image"
            class="w-full h-48 object-cover rounded-lg mb-3"
          />
          <div v-else class="w-full h-48 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center mb-3">
            <span class="text-gray-500 dark:text-gray-400">No image</span>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="editImage(image)"
            class="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Edit
          </button>
          <button
            @click="deleteImage(image)"
            class="px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
      <div v-if="images.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No dark mode images found. Add your first image to get started.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingImage ? 'Edit Dark Mode Image' : 'Add Dark Mode Image'"
      size="md"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Blog ID *</label>
          <input
            v-model.number="form.blog"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Blog post ID"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dark Mode Image *</label>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileChange"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Upload an image optimized for dark mode display</p>
          <div v-if="previewUrl" class="mt-2">
            <img :src="previewUrl" alt="Preview" class="max-w-full h-32 object-contain rounded-lg border" />
          </div>
        </div>
        <div v-if="formError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ formError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveImage"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingImage ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import blogPagesAPI from '@/api/blog-pages'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const images = ref([])
const showModal = ref(false)
const editingImage = ref(null)
const formError = ref('')
const fileInput = ref(null)
const previewUrl = ref(null)
const selectedFile = ref(null)

const form = ref({
  blog: null,
})

const uniqueBlogs = computed(() => {
  return [...new Set(images.value.map(img => img.blog || img.blog_id).filter(Boolean))]
})

const loadImages = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listDarkModeImages()
    images.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load dark mode images')
    console.error('Error loading images:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingImage.value = null
  form.value = {
    blog: null,
  }
  selectedFile.value = null
  previewUrl.value = null
  formError.value = ''
  showModal.value = true
}

const editImage = (image) => {
  editingImage.value = image
  form.value = {
    blog: image.blog || image.blog_id || null,
  }
  previewUrl.value = image.dark_mode_image || null
  selectedFile.value = null
  formError.value = ''
  showModal.value = true
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const closeModal = () => {
  showModal.value = false
  editingImage.value = null
  selectedFile.value = null
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = null
  formError.value = ''
}

const saveImage = async () => {
  saving.value = true
  formError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('blog', form.value.blog)
    if (selectedFile.value) {
      formData.append('dark_mode_image', selectedFile.value)
    }
    
    if (editingImage.value) {
      await blogPagesAPI.updateDarkModeImage(editingImage.value.id, formData)
      showSuccess('Dark mode image updated successfully')
    } else {
      if (!selectedFile.value) {
        formError.value = 'Please select an image file'
        saving.value = false
        return
      }
      await blogPagesAPI.createDarkModeImage(formData)
      showSuccess('Dark mode image added successfully')
    }
    
    closeModal()
    loadImages()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save dark mode image'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteImage = (image) => {
  confirm.showDestructive(
    'Delete Dark Mode Image',
    'Are you sure you want to delete this dark mode image?',
    'This action cannot be undone.',
    async () => {
      try {
        await blogPagesAPI.deleteDarkModeImage(image.id)
        showSuccess('Dark mode image deleted successfully')
        loadImages()
      } catch (error) {
        showError('Failed to delete dark mode image')
      }
    }
  )
}

onMounted(() => {
  loadImages()
})
</script>

