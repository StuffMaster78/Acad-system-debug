<template>
  <div class="special-day-detail">
    <div class="detail-header">
      <div>
        <h2>{{ specialDay.name }}</h2>
        <p class="description">{{ specialDay.description || 'No description' }}</p>
      </div>
      <div class="badges">
        <span :class="['badge', `badge-${specialDay.priority}`]">
          {{ specialDay.priority }}
        </span>
        <span v-if="specialDay.is_international" class="badge badge-info">
          International
        </span>
        <span v-else class="badge badge-secondary">
          Country-Specific
        </span>
        <span v-if="specialDay.is_annual" class="badge badge-success">
          Annual
        </span>
      </div>
    </div>

    <div class="detail-info">
      <div class="info-grid">
        <div class="info-item">
          <label>Event Type:</label>
          <span>{{ formatEventType(specialDay.event_type) }}</span>
        </div>
        <div class="info-item">
          <label>Date:</label>
          <span>{{ formatDate(specialDay.event_date_this_year) }}</span>
        </div>
        <div class="info-item">
          <label>Days Until:</label>
          <span :class="{ 'upcoming': specialDay.days_until <= 7 }">
            {{ specialDay.days_until }} days
          </span>
        </div>
        <div class="info-item">
          <label>Reminder Days Before:</label>
          <span>{{ specialDay.reminder_days_before }} days</span>
        </div>
        <div v-if="specialDay.countries_display?.length" class="info-item">
          <label>Countries:</label>
          <span>{{ specialDay.countries_display.join(', ') }}</span>
        </div>
        <div class="info-item">
          <label>Status:</label>
          <span :class="specialDay.is_active ? 'text-success' : 'text-danger'">
            {{ specialDay.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <h3>Reminder Settings</h3>
      <div class="settings-grid">
        <div class="setting-item">
          <label>Send Broadcast Reminder:</label>
          <span :class="specialDay.send_broadcast_reminder ? 'text-success' : 'text-muted'">
            {{ specialDay.send_broadcast_reminder ? 'Yes' : 'No' }}
          </span>
        </div>
        <div class="setting-item">
          <label>Auto-Generate Discount:</label>
          <span :class="specialDay.auto_generate_discount ? 'text-success' : 'text-muted'">
            {{ specialDay.auto_generate_discount ? 'Yes' : 'No' }}
          </span>
        </div>
        <div v-if="specialDay.auto_generate_discount" class="setting-item">
          <label>Discount Percentage:</label>
          <span>{{ specialDay.discount_percentage }}%</span>
        </div>
        <div v-if="specialDay.auto_generate_discount" class="setting-item">
          <label>Discount Code Prefix:</label>
          <span>{{ specialDay.discount_code_prefix || 'Auto-generated' }}</span>
        </div>
        <div v-if="specialDay.auto_generate_discount" class="setting-item">
          <label>Discount Valid Days:</label>
          <span>{{ specialDay.discount_valid_days }} days</span>
        </div>
      </div>
    </div>

    <div v-if="specialDay.broadcast_message_template" class="template-section">
      <h3>Broadcast Message Template</h3>
      <div class="template-preview">
        {{ specialDay.broadcast_message_template }}
      </div>
    </div>

    <div class="actions">
      <button @click="$emit('edit')" class="btn btn-primary">
        <i class="fas fa-edit"></i> Edit
      </button>
      <button 
        @click="handleGenerateDiscount"
        class="btn btn-success"
        :disabled="generating"
      >
        <i class="fas fa-tag"></i> Generate Discount
      </button>
      <button @click="$emit('close')" class="btn btn-secondary">
        Close
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { holidaysAPI } from '@/api'

const props = defineProps({
  specialDay: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'generate-discount', 'close'])

const { showToast } = useToast()
const generating = ref(false)

const formatEventType = (type) => {
  const types = {
    'holiday': 'Holiday',
    'special_day': 'Special Day',
    'anniversary': 'Anniversary',
    'seasonal': 'Seasonal Event',
    'cultural': 'Cultural Event'
  }
  return types[type] || type
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleGenerateDiscount = async () => {
  generating.value = true
  try {
    const year = new Date().getFullYear()
    await holidaysAPI.specialDays.generateDiscount(props.specialDay.id, { year })
    showToast('Discount generated successfully', 'success')
    emit('generate-discount', props.specialDay.id, year)
  } catch (error) {
    showToast('Failed to generate discount', 'error')
    console.error(error)
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.special-day-detail {
  padding: 1rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.detail-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.description {
  color: #6b7280;
  margin: 0;
}

.badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-low { background: #d1d5db; color: #374151; }
.badge-medium { background: #fbbf24; color: #92400e; }
.badge-high { background: #f59e0b; color: #78350f; }
.badge-critical { background: #ef4444; color: #ffffff; }
.badge-info { background: #3b82f6; color: #ffffff; }
.badge-secondary { background: #6b7280; color: #ffffff; }
.badge-success { background: #10b981; color: #ffffff; }

.detail-info {
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #6b7280;
}

.info-item span {
  font-size: 1rem;
  color: #111827;
}

.info-item span.upcoming {
  color: #ef4444;
  font-weight: 600;
}

.settings-section,
.template-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.settings-section h3,
.template-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-item label {
  font-weight: 500;
  color: #6b7280;
}

.template-preview {
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  white-space: pre-wrap;
  color: #374151;
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }
.text-muted { color: #6b7280; }
</style>


