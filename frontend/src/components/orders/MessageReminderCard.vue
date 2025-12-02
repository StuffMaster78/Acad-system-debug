<template>
  <div class="message-reminder-card" v-if="reminder">
    <div class="card-header">
      <h4>Message Reminder</h4>
      <span :class="['reminder-type', reminder.reminder_type]">
        {{ reminder.reminder_type_display }}
      </span>
    </div>
    
    <div class="card-body">
      <p><strong>Order #{{ reminder.order_id }}</strong>: {{ reminder.order_title }}</p>
      
      <div class="reminder-status">
        <div class="status-item">
          <span :class="{ completed: reminder.is_read }">
            {{ reminder.is_read ? '✓' : '○' }} Read
          </span>
        </div>
        <div class="status-item">
          <span :class="{ completed: reminder.is_responded }">
            {{ reminder.is_responded ? '✓' : '○' }} Responded
          </span>
        </div>
      </div>
      
      <div class="actions">
        <button 
          v-if="!reminder.is_read"
          @click="markRead"
          class="btn-primary"
          :disabled="loading"
        >
          Mark as Read
        </button>
        <button 
          v-if="!reminder.is_responded"
          @click="markResponded"
          class="btn-primary"
          :disabled="loading"
        >
          Mark as Responded
        </button>
        <router-link 
          :to="`/orders/${reminder.order_id}/messages`"
          class="btn-link"
        >
          View Messages
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { messageRemindersAPI } from '@/api'

export default {
  name: 'MessageReminderCard',
  props: {
    reminder: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false
    }
  },
  methods: {
    async markRead() {
      if (this.loading) return
      this.loading = true
      try {
        await messageRemindersAPI.markRead(this.reminder.id)
        this.$emit('updated')
        this.$toast.success('Message marked as read')
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to update')
      } finally {
        this.loading = false
      }
    },
    async markResponded() {
      if (this.loading) return
      this.loading = true
      try {
        await messageRemindersAPI.markResponded(this.reminder.id)
        this.$emit('updated')
        this.$toast.success('Message marked as responded')
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to update')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.message-reminder-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
}

.reminder-type {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.reminder-type.unread {
  background: #fff3cd;
  color: #856404;
}

.reminder-type.unresponded {
  background: #d1ecf1;
  color: #0c5460;
}

.reminder-type.urgent {
  background: #f8d7da;
  color: #721c24;
}

.reminder-status {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.status-item .completed {
  color: #28a745;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.btn-link:hover {
  background: #5a6268;
}
</style>

