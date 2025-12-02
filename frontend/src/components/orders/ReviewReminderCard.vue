<template>
  <div class="review-reminder-card" v-if="reminder">
    <div class="card-header">
      <h4>Review Reminder</h4>
      <span :class="['status-badge', statusClass]">
        {{ statusText }}
      </span>
    </div>
    
    <div class="card-body">
      <p><strong>Order #{{ reminder.order_id }}</strong>: {{ reminder.order_title }}</p>
      <p v-if="reminder.writer_username">
        Writer: {{ reminder.writer_username }}
      </p>
      
      <div class="review-status">
        <div class="status-item">
          <span :class="{ completed: reminder.has_reviewed }">
            {{ reminder.has_reviewed ? '✓' : '○' }} Review Submitted
          </span>
        </div>
        <div class="status-item">
          <span :class="{ completed: reminder.has_rated }">
            {{ reminder.has_rated ? '✓' : '○' }} Rating Given
          </span>
        </div>
        <div v-if="reminder.rating" class="rating-display">
          Rating: <strong>{{ reminder.rating }}/5</strong>
        </div>
      </div>
      
      <div class="actions">
        <button 
          v-if="!reminder.has_reviewed"
          @click="markReviewed"
          class="btn-primary"
          :disabled="loading"
        >
          Mark as Reviewed
        </button>
        <div v-if="!reminder.has_rated" class="rating-input">
          <label>Rate Writer:</label>
          <select v-model="selectedRating" @change="markRated" :disabled="loading">
            <option value="">Select rating</option>
            <option v-for="i in 5" :key="i" :value="i">{{ i }} star{{ i > 1 ? 's' : '' }}</option>
          </select>
        </div>
        <router-link 
          :to="`/orders/${reminder.order_id}/review`"
          class="btn-link"
        >
          Write Review
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { reviewRemindersAPI } from '@/api'

export default {
  name: 'ReviewReminderCard',
  props: {
    reminder: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      selectedRating: null
    }
  },
  computed: {
    statusClass() {
      if (this.reminder.is_completed) return 'status-complete'
      if (this.reminder.has_reviewed || this.reminder.has_rated) return 'status-partial'
      return 'status-pending'
    },
    statusText() {
      if (this.reminder.is_completed) return 'Completed'
      if (this.reminder.has_reviewed || this.reminder.has_rated) return 'In Progress'
      return 'Pending'
    }
  },
  methods: {
    async markReviewed() {
      if (this.loading) return
      this.loading = true
      try {
        await reviewRemindersAPI.markReviewed(this.reminder.id)
        this.$emit('updated')
        this.$toast.success('Review marked as submitted')
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to update')
      } finally {
        this.loading = false
      }
    },
    async markRated() {
      if (!this.selectedRating || this.loading) return
      this.loading = true
      try {
        await reviewRemindersAPI.markRated(this.reminder.id, parseInt(this.selectedRating))
        this.$emit('updated')
        this.$toast.success('Rating submitted successfully')
        this.selectedRating = null
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to submit rating')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.review-reminder-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-partial {
  background: #d1ecf1;
  color: #0c5460;
}

.status-complete {
  background: #d4edda;
  color: #155724;
}

.review-status {
  margin: 1rem 0;
}

.status-item .completed {
  color: #28a745;
  font-weight: 500;
}

.rating-display {
  margin-top: 0.5rem;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-input select {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
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

