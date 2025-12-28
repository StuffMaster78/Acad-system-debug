<template>
  <form
    @submit.prevent="handleSubmit"
    class="special-day-form space-y-8"
  >
    <!-- Basic Information Section -->
    <div class="space-y-6 mb-8">
      <div class="pb-4 border-b border-gray-200 dark:border-gray-700 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Basic Information</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Enter the essential details for this special day</p>
      </div>
      
      <div class="space-y-6">
        <!-- Name (simple, always-interactable text input) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Special Day Name <span class="text-red-500">*</span>
          </label>
      <input
        v-model="formData.name"
        type="text"
            placeholder="e.g., Black Friday Sale, Thanksgiving Day, Summer Kickoff"
        required
            maxlength="120"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-colors"
          />
          <div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Give this a clear, recognizable name – customers may see it. {{ formData.name.length || 0 }}/120 characters.
          </div>
          <div v-if="errors.name" class="mt-1 text-xs text-red-600 dark:text-red-400">
            {{ errors.name }}
          </div>
        </div>

        <!-- Description (reset to simplest known-good RichTextEditor usage, with example) -->
        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <RichTextEditor
        v-model="formData.description"
            placeholder="Enter a detailed description of this special day..."
            toolbar="basic"
            height="200px"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Use rich formatting to describe what this day is about. This content is stored as HTML.
          </p>
          <details class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            <summary class="cursor-pointer hover:text-gray-700 dark:hover:text-gray-200">
              See an example description
            </summary>
            <div class="mt-1 border-l border-gray-200 dark:border-gray-700 pl-3">
              <p>
                <strong>Example:</strong>
                “Thanksgiving Day is a major US holiday celebrated on the fourth Thursday of November.
                Use this campaign to highlight limited-time discounts and warm, family‑focused messaging.”
              </p>
            </div>
          </details>
        </div>
      </div>
    </div>

    <!-- Key dates & priority (simple grid, no wrapper) -->
    <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Event Type <span class="text-red-500">*</span>
        </label>
        <select
          v-model="formData.event_type"
          required
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-800 dark:text-white"
        >
          <option value="holiday">Holiday</option>
          <option value="special_day">Special Day</option>
          <option value="anniversary">Anniversary</option>
          <option value="seasonal">Seasonal Event</option>
          <option value="cultural">Cultural Event</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Date <span class="text-red-500">*</span>
        </label>
        <input
          v-model="formData.date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-white"
        />
        <div v-if="errors.date" class="mt-1 text-xs text-red-600 dark:text-red-400">
          {{ errors.date }}
        </div>
      </div>
    </div>

    <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Priority <span class="text-red-500">*</span>
        </label>
        <select
          v-model="formData.priority"
          required
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-800 dark:text-white"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Reminder Days Before <span class="text-red-500">*</span>
        </label>
        <input
          v-model.number="formData.reminder_days_before"
          type="number"
          min="1"
          max="30"
          required
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-white"
        />
      </div>
    </div>

    <!-- Settings Section -->
    <div class="form-checkboxes grid grid-cols-1 sm:grid-cols-2 gap-3 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
      <label class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 p-2 rounded transition-colors">
        <input
          type="checkbox"
          v-model="formData.is_annual"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <span>Repeats Annually</span>
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 p-2 rounded transition-colors">
        <input
          type="checkbox"
          v-model="formData.is_international"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <span>International Event</span>
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 p-2 rounded transition-colors">
        <input
          type="checkbox"
          v-model="formData.auto_generate_discount"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <span>Auto-Generate Discount</span>
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 p-2 rounded transition-colors">
        <input
          type="checkbox"
          v-model="formData.is_active"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        <span>Active</span>
      </label>
    </div>

    <div v-if="!formData.is_international" class="form-field space-y-2">
      <label class="block text-sm font-medium text-gray-700">Countries</label>
      <div class="country-selector space-y-2">
        <select
          v-model="selectedCountry"
          @change="addCountry"
          class="country-select w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
        >
          <option value="">Select Country</option>
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="GB">United Kingdom</option>
          <option value="AU">Australia</option>
          <option value="NZ">New Zealand</option>
          <option value="IE">Ireland</option>
        </select>
        <div class="selected-countries flex flex-wrap gap-2">
          <span
            v-for="country in formData.countries"
            :key="country"
            class="country-tag inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary-50 text-primary-700 text-xs"
          >
            {{ getCountryName(country) }}
            <button
              type="button"
              @click="removeCountry(country)"
              class="remove-country text-xs text-gray-500 hover:text-red-600"
            >
              ×
            </button>
          </span>
        </div>
      </div>
    </div>

    <div v-if="formData.auto_generate_discount" class="discount-settings space-y-4 border-t border-gray-200 pt-4 mt-6">
      <h3 class="text-sm font-semibold text-gray-900">Discount Settings</h3>
      <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          name="discount_percentage"
          label="Discount Percentage *"
          :error="errors.discount_percentage"
        >
          <input
            v-model.number="formData.discount_percentage"
            type="number"
            min="0"
            max="100"
            step="0.01"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </FormField>

        <FormField
          name="discount_code_prefix"
          label="Discount Code Prefix"
          :error="errors.discount_code_prefix"
        >
          <input
            v-model="formData.discount_code_prefix"
            type="text"
            placeholder="e.g., THANKS"
            maxlength="20"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </FormField>
      </div>

      <FormField
        name="discount_valid_days"
        label="Discount Valid Days *"
        :error="errors.discount_valid_days"
      >
        <input
          v-model.number="formData.discount_valid_days"
          type="number"
          min="1"
          max="365"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </FormField>
    </div>

    <!-- Broadcast Message Section -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-8 space-y-6">
      <div class="flex items-center justify-between pb-2">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Broadcast Message</h3>
        </div>
        <label class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input
            type="checkbox"
            v-model="formData.send_broadcast_reminder"
            class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
          />
          Send Broadcast Reminder
        </label>
      </div>

      <!-- Broadcast message template (simple RichTextEditor usage with example) -->
      <div class="space-y-1">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Message Template
        </label>
        <RichTextEditor
          v-model="formData.broadcast_message_template"
          placeholder="Enter your broadcast message template. Use {name}, {date}, {code}, {discount} as variables..."
          toolbar="basic"
          height="200px"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <span class="inline-flex items-center px-2 py-1 rounded-md bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium">
            Variables: {name}, {date}, {code}, {discount}
          </span>
        </div>
        <details class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          <summary class="cursor-pointer hover:text-gray-700 dark:hover:text-gray-200">
            See an example message
          </summary>
          <div class="mt-1 border-l border-gray-200 dark:border-gray-700 pl-3 space-y-1">
            <p><strong>Example:</strong></p>
            <p>“Hi {name},</p>
            <p>
              To celebrate {date}, we’ve created an exclusive {discount}% discount just for you.
              Use code <strong>{code}</strong> at checkout before midnight to claim your offer.
            </p>
            <p>Happy {date}!<br/>The Team”</p>
          </div>
        </details>
      </div>

      <!-- Image Attachment Section (simple block, no wrapper) -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Attach Image
        </label>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Upload an image to include with the broadcast message (optional).
        </p>
        <div class="space-y-3">
          <div
            v-if="!formData.attached_image"
            @drop.prevent="handleImageDrop"
            @dragover.prevent="isDraggingImage = true"
            @dragleave.prevent="isDraggingImage = false"
            @click="triggerImageUpload"
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer"
            :class="[
              isDraggingImage ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800',
              uploadingImage ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-400'
            ]"
          >
            <input
              ref="imageInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleImageSelect"
            />
            <div v-if="!uploadingImage" class="space-y-2">
              <div class="text-4xl">🖼️</div>
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Drop an image here or click to choose a file
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                PNG, JPG, GIF up to 5MB. Ideal: a simple banner or hero image that matches your campaign.
              </div>
              <div class="text-xs text-gray-400">
                Example: “Black Friday” hero graphic with -40% overlay.
              </div>
            </div>
            <div v-else class="space-y-2">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Uploading...</div>
            </div>
          </div>
          
          <div
            v-if="formData.attached_image"
            class="relative group"
          >
            <img
              :src="formData.attached_image"
              alt="Attached image"
              class="w-full h-48 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
            />
            <button
              type="button"
              @click="removeAttachedImage"
              class="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div class="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
              Image attached to broadcast message
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="form-actions flex items-center justify-end gap-4 pt-8 mt-8 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 -mx-6 md:-mx-8 px-6 md:px-8 py-6">
      <button
        type="button"
        @click="$emit('cancel')"
        class="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all shadow-sm hover:shadow"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        Cancel
      </button>
      <button
        type="submit"
        class="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-primary-600 to-primary-700 text-white text-sm font-semibold hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        :disabled="saving"
      >
        <span v-if="saving" class="inline-flex items-center gap-2">
          <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647A5.969 5.969 0 016 12H4c0 1.657.672 3.157 1.757 4.243l1.414-1.414A3.975 3.975 0 015 12H3c0 1.306.523 2.488 1.368 3.343l1.414-1.414A1.99 1.99 0 014 12H2z"></path>
          </svg>
          Saving...
        </span>
        <span v-else class="inline-flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ editingSpecialDay ? 'Update Special Day' : 'Create Special Day' }}
        </span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import FormField from '@/components/common/FormField.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import mediaAPI from '@/api/media'
import { useAuthStore } from '@/stores/auth'

// Debug: Log when component mounts
onMounted(() => {
  console.log('SpecialDayForm component mounted with RichTextEditor support')
  console.log('formData exists:', !!formData)
  console.log('formData.name:', formData.name)
  console.log('errors exists:', !!errors.value)
  console.log('Form should render now')
})

const props = defineProps({
  specialDay: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const editingSpecialDay = computed(() => !!props.specialDay)

const authStore = useAuthStore()
const saving = ref(false)
const selectedCountry = ref('')
const errors = ref({})
const imageInput = ref(null)
const isDraggingImage = ref(false)
const uploadingImage = ref(false)

const formData = reactive({
  name: '',
  description: '',
  event_type: 'holiday',
  date: '',
  is_annual: true,
  is_international: false,
  countries: [],
  priority: 'medium',
  reminder_days_before: 7,
  send_broadcast_reminder: true,
  auto_generate_discount: false,
  discount_percentage: 10.00,
  discount_code_prefix: '',
  discount_valid_days: 1,
  broadcast_message_template: '',
  attached_image: null,
  attached_image_url: null,
  is_active: true
})

// Initialize form if editing
if (props.specialDay) {
  Object.assign(formData, {
    name: props.specialDay.name || '',
    description: props.specialDay.description || '',
    event_type: props.specialDay.event_type || 'holiday',
    date: props.specialDay.date || props.specialDay.event_date_this_year || '',
    is_annual: props.specialDay.is_annual ?? true,
    is_international: props.specialDay.is_international ?? false,
    countries: props.specialDay.countries_display || [],
    priority: props.specialDay.priority || 'medium',
    reminder_days_before: props.specialDay.reminder_days_before || 7,
    send_broadcast_reminder: props.specialDay.send_broadcast_reminder ?? true,
    auto_generate_discount: props.specialDay.auto_generate_discount ?? false,
    discount_percentage: props.specialDay.discount_percentage || 10.00,
    discount_code_prefix: props.specialDay.discount_code_prefix || '',
    discount_valid_days: props.specialDay.discount_valid_days || 1,
    broadcast_message_template: props.specialDay.broadcast_message_template || '',
    attached_image: props.specialDay.attached_image || null,
    attached_image_url: props.specialDay.attached_image_url || null,
    is_active: props.specialDay.is_active ?? true
  })
}

// Image upload handler for rich text editor
const handleImageUpload = async (file) => {
  try {
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    uploadFormData.append('type', 'image')
    if (authStore.user?.website) {
      uploadFormData.append('website', authStore.user.website)
    }
    
    const response = await mediaAPI.create(uploadFormData)
    return response.data.url || response.data.file
  } catch (error) {
    console.error('Image upload failed:', error)
    throw new Error('Failed to upload image: ' + (error.response?.data?.detail || error.message))
  }
}

// Handle image attachment for broadcast message
const triggerImageUpload = () => {
  if (imageInput.value && !uploadingImage.value) {
    imageInput.value.click()
  }
}

const handleImageSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  if (file.size > 5 * 1024 * 1024) {
    alert('Image size must be less than 5MB')
    return
  }
  
  try {
    uploadingImage.value = true
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    uploadFormData.append('type', 'image')
    if (authStore.user?.website) {
      uploadFormData.append('website', authStore.user.website)
    }
    
    const response = await mediaAPI.create(uploadFormData)
    formData.attached_image = response.data.url || response.data.file
    formData.attached_image_url = response.data.url || response.data.file
  } catch (error) {
    console.error('Image upload failed:', error)
    alert('Failed to upload image: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploadingImage.value = false
    if (imageInput.value) {
      imageInput.value.value = ''
    }
  }
}

const handleImageDrop = async (event) => {
  isDraggingImage.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file || !file.type.startsWith('image/')) return
  
  if (file.size > 5 * 1024 * 1024) {
    alert('Image size must be less than 5MB')
    return
  }
  
  try {
    uploadingImage.value = true
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    uploadFormData.append('type', 'image')
    if (authStore.user?.website) {
      uploadFormData.append('website', authStore.user.website)
    }
    
    const response = await mediaAPI.create(uploadFormData)
    formData.attached_image = response.data.url || response.data.file
    formData.attached_image_url = response.data.url || response.data.file
  } catch (error) {
    console.error('Image upload failed:', error)
    alert('Failed to upload image: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploadingImage.value = false
  }
}

const removeAttachedImage = () => {
  formData.attached_image = null
  formData.attached_image_url = null
}

const getCountryName = (code) => {
  const names = {
    'US': 'United States',
    'CA': 'Canada',
    'GB': 'United Kingdom',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'IE': 'Ireland'
  }
  return names[code] || code
}

const addCountry = () => {
  if (selectedCountry.value && !formData.countries.includes(selectedCountry.value)) {
    formData.countries.push(selectedCountry.value)
    selectedCountry.value = ''
  }
}

const removeCountry = (country) => {
  formData.countries = formData.countries.filter(c => c !== country)
}

const handleSubmit = () => {
  errors.value = {}
  
  // Validation
  if (!formData.name.trim()) {
    errors.value.name = 'Name is required'
    return
  }
  
  if (!formData.date) {
    errors.value.date = 'Date is required'
    return
  }
  
  if (formData.auto_generate_discount && !formData.discount_percentage) {
    errors.value.discount_percentage = 'Discount percentage is required when auto-generating'
    return
  }
  
  saving.value = true
  emit('save', { ...formData })
  saving.value = false
}
</script>

<style scoped>
.special-day-form {
  padding: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.form-checkboxes label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.country-selector {
  margin-top: 0.5rem;
}

.country-select {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}

.selected-countries {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.country-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.remove-country {
  background: none;
  border: none;
  cursor: pointer;
  color: #ef4444;
  font-size: 1.25rem;
  line-height: 1;
  padding: 0;
  margin-left: 0.25rem;
}

.discount-settings {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.discount-settings h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .discount-settings {
    background: rgba(31, 41, 55, 0.5);
    border-color: #374151;
  }
  
  .discount-settings h3 {
    color: #f9fafb;
  }
}
</style>


