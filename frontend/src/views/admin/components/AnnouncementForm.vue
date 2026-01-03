<template>
  <div class="space-y-6">
    <!-- Basic Information -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold mb-4">Basic Information</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Title <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.title"
            type="text"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
            placeholder="Enter announcement title"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Category
          </label>
          <select
            v-model="formData.category"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
          >
            <option value="general">General</option>
            <option value="news">News</option>
            <option value="update">System Update</option>
            <option value="maintenance">Maintenance</option>
            <option value="promotion">Promotion</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Message <span class="text-red-500">*</span>
          </label>
          <RichTextEditor
            v-model="formData.message"
            :height="'300px'"
            placeholder="Enter announcement message..."
            toolbar="full"
          />
        </div>
      </div>
    </div>

    <!-- Targeting & Delivery -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold mb-4">Targeting & Delivery</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Target Roles
          </label>
          <div class="flex flex-wrap gap-3">
            <label v-for="role in availableRoles" :key="role" class="flex items-center gap-2">
              <input
                type="checkbox"
                :value="role"
                v-model="formData.target_roles"
                class="rounded"
              />
              <span class="text-sm">{{ role.charAt(0).toUpperCase() + role.slice(1) }}</span>
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-2">Leave empty to target all users</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Delivery Channels
          </label>
          <div class="flex flex-wrap gap-3">
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                value="in_app"
                v-model="formData.channels"
                class="rounded"
              />
              <span class="text-sm">In-App Notification</span>
            </label>
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                value="email"
                v-model="formData.channels"
                class="rounded"
              />
              <span class="text-sm">Email</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Options -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold mb-4">Additional Options</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Featured Image
          </label>
          <input
            type="file"
            accept="image/*"
            @change="handleImageUpload"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
          />
          <img
            v-if="formData.featured_image_url"
            :src="formData.featured_image_url"
            alt="Featured image preview"
            class="mt-2 w-32 h-32 object-cover rounded"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Read More URL
          </label>
          <input
            v-model="formData.read_more_url"
            type="url"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
            placeholder="https://example.com/read-more"
          />
        </div>

        <div class="flex flex-wrap gap-4">
          <label class="flex items-center gap-2">
            <input
              type="checkbox"
              v-model="formData.pinned"
              class="rounded"
            />
            <span class="text-sm">Pin this announcement</span>
          </label>

          <label class="flex items-center gap-2">
            <input
              type="checkbox"
              v-model="formData.require_acknowledgement"
              class="rounded"
            />
            <span class="text-sm">Require acknowledgement</span>
          </label>

          <label class="flex items-center gap-2">
            <input
              type="checkbox"
              v-model="formData.is_active"
              class="rounded"
            />
            <span class="text-sm">Active</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Scheduling -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold mb-4">Scheduling</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Schedule For (Optional)
          </label>
          <input
            v-model="formData.scheduled_for"
            type="datetime-local"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
          />
          <p class="text-xs text-gray-500 mt-2">Leave empty to send immediately</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Expires At (Optional)
          </label>
          <input
            v-model="formData.expires_at"
            type="datetime-local"
            class="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
          />
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <button
        @click="$emit('cancel')"
        class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
      >
        Cancel
      </button>
      <button
        @click="handleSubmit"
        :disabled="!isValid || saving"
        class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : (isEdit ? 'Update' : 'Create') }} Announcement
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import mediaAPI from '@/api/media'

const props = defineProps({
  announcement: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const isEdit = computed(() => !!props.announcement)
const saving = ref(false)

const availableRoles = ['client', 'writer', 'editor', 'admin', 'support']

const formData = ref({
  title: '',
  message: '',
  category: 'general',
  target_roles: [],
  channels: ['in_app', 'email'],
  pinned: false,
  require_acknowledgement: false,
  is_active: true,
  featured_image: null,
  featured_image_url: null,
  read_more_url: '',
  scheduled_for: '',
  expires_at: ''
})

const isValid = computed(() => {
  return formData.value.title.trim() && formData.value.message.trim()
})

// Load existing data if editing
watch(() => props.announcement, (newVal) => {
  if (newVal) {
    formData.value = {
      title: newVal.title || '',
      message: newVal.message || '',
      category: newVal.category || 'general',
      target_roles: newVal.target_roles || [],
      channels: newVal.channels || ['in_app', 'email'],
      pinned: newVal.is_pinned || false,
      require_acknowledgement: newVal.require_acknowledgement || false,
      is_active: newVal.is_active !== undefined ? newVal.is_active : true,
      featured_image: null,
      featured_image_url: newVal.featured_image_url || null,
      read_more_url: newVal.read_more_url || '',
      scheduled_for: newVal.scheduled_for || '',
      expires_at: newVal.expires_at || ''
    }
  }
}, { immediate: true })

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    saving.value = true
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    uploadFormData.append('category', 'announcement')

    const response = await mediaAPI.create(uploadFormData)
    formData.value.featured_image_url = response.data.url || response.data.file
    formData.value.featured_image = response.data.id
  } catch (e) {
    console.error('Error uploading image:', e)
    alert('Failed to upload image: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const handleSubmit = () => {
  if (!isValid.value) return

  const data = {
    ...formData.value,
    scheduled_for: formData.value.scheduled_for ? new Date(formData.value.scheduled_for).toISOString() : null,
    expires_at: formData.value.expires_at ? new Date(formData.value.expires_at).toISOString() : null
  }

  emit('submit', data)
}
</script>

