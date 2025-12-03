<template>
  <form
    @submit.prevent="handleSubmit"
    class="special-day-form space-y-6"
  >
    <FormField
      label="Name *"
      :error="errors.name"
    >
      <input
        v-model="formData.name"
        type="text"
        placeholder="e.g., Thanksgiving Day"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
    </FormField>

    <FormField
      label="Description"
      :error="errors.description"
    >
      <textarea
        v-model="formData.description"
        rows="3"
        placeholder="Description of the special day"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
    </FormField>

    <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Event Type *"
        :error="errors.event_type"
      >
        <select
          v-model="formData.event_type"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
        >
          <option value="holiday">Holiday</option>
          <option value="special_day">Special Day</option>
          <option value="anniversary">Anniversary</option>
          <option value="seasonal">Seasonal Event</option>
          <option value="cultural">Cultural Event</option>
        </select>
      </FormField>

      <FormField
        label="Date *"
        :error="errors.date"
      >
        <input
          v-model="formData.date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </FormField>
    </div>

    <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField label="Priority *">
        <select
          v-model="formData.priority"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </FormField>

      <FormField label="Reminder Days Before *">
        <input
          v-model.number="formData.reminder_days_before"
          type="number"
          min="1"
          max="30"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </FormField>
    </div>

    <div class="form-checkboxes grid grid-cols-1 sm:grid-cols-2 gap-3 bg-gray-50 border border-gray-200 rounded-lg p-4">
      <label class="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          v-model="formData.is_annual"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        Repeats Annually
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          v-model="formData.is_international"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        International Event
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          v-model="formData.send_broadcast_reminder"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        Send Broadcast Reminder
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          v-model="formData.auto_generate_discount"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        Auto-Generate Discount
      </label>
      <label class="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          v-model="formData.is_active"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
        Active
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

    <div v-if="formData.auto_generate_discount" class="discount-settings space-y-4 border-t border-gray-200 pt-4">
      <h3 class="text-sm font-semibold text-gray-900">Discount Settings</h3>
      <div class="form-row grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
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

    <FormField
      label="Broadcast Message Template"
      :error="errors.broadcast_message_template"
    >
      <textarea
        v-model="formData.broadcast_message_template"
        rows="4"
        placeholder="Template for broadcast message. Use {name}, {date}, {code}, {discount} as variables."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
      <small class="text-xs text-gray-500">Variables: {name}, {date}, {code}, {discount}</small>
    </FormField>

    <div class="form-actions flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
      <button
        type="button"
        @click="$emit('cancel')"
        class="btn btn-secondary px-4 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50"
      >
        Cancel
      </button>
      <button
        type="submit"
        class="btn btn-primary px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="saving"
      >
        {{ saving ? 'Saving...' : 'Save' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import FormField from '@/components/common/FormField.vue'

const props = defineProps({
  specialDay: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const saving = ref(false)
const selectedCountry = ref('')
const errors = ref({})

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
    is_active: props.specialDay.is_active ?? true
  })
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
  padding: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0;
}

.form-checkboxes label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.discount-settings h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
</style>


