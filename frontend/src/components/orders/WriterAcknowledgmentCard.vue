<template>
  <div class="writer-acknowledgment-card" v-if="acknowledgment">
    <div class="card-header">
      <h3>Order Assignment</h3>
      <span :class="['status-badge', statusClass]">
        {{ statusText }}
      </span>
    </div>
    
    <div class="card-body">
      <div class="order-info">
        <p><strong>Order #{{ acknowledgment.order_id }}</strong></p>
        <p>{{ acknowledgment.order_title }}</p>
      </div>
      
      <div class="engagement-checklist">
        <h4>Engagement Checklist</h4>
        <div class="checklist-item" :class="{ completed: acknowledgment.acknowledged_at }">
          <input 
            type="checkbox" 
            :checked="acknowledgment.acknowledged_at" 
            @change="handleAcknowledge"
            :disabled="acknowledgment.acknowledged_at || loading"
          />
          <label>Acknowledge assignment</label>
        </div>
        
        <div class="checklist-item" :class="{ completed: acknowledgment.has_sent_message }">
          <input 
            type="checkbox" 
            :checked="acknowledgment.has_sent_message" 
            disabled
          />
          <label>Send message to client</label>
          <button 
            v-if="!acknowledgment.has_sent_message && acknowledgment.acknowledged_at"
            @click="markMessageSent"
            class="btn-small"
            :disabled="loading"
          >
            Mark as Sent
          </button>
        </div>
        
        <div class="checklist-item" :class="{ completed: acknowledgment.has_downloaded_files }">
          <input 
            type="checkbox" 
            :checked="acknowledgment.has_downloaded_files" 
            disabled
          />
          <label>Download order files</label>
          <button 
            v-if="!acknowledgment.has_downloaded_files && acknowledgment.acknowledged_at"
            @click="markFileDownloaded"
            class="btn-small"
            :disabled="loading"
          >
            Mark as Downloaded
          </button>
        </div>
      </div>
      
      <div v-if="acknowledgment.notes" class="notes">
        <h4>Notes</h4>
        <p>{{ acknowledgment.notes }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { writerAcknowledgmentAPI } from '@/api'

export default {
  name: 'WriterAcknowledgmentCard',
  props: {
    acknowledgment: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false
    }
  },
  computed: {
    statusClass() {
      if (this.acknowledgment.is_fully_engaged) return 'status-complete'
      if (this.acknowledgment.acknowledged_at) return 'status-partial'
      return 'status-pending'
    },
    statusText() {
      if (this.acknowledgment.is_fully_engaged) return 'Fully Engaged'
      if (this.acknowledgment.acknowledged_at) return 'Partially Engaged'
      return 'Pending Acknowledgment'
    }
  },
  methods: {
    async handleAcknowledge() {
      if (this.loading) return
      this.loading = true
      try {
        await writerAcknowledgmentAPI.acknowledge(this.acknowledgment.order_id)
        this.$emit('updated')
        this.$toast.success('Assignment acknowledged successfully')
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to acknowledge assignment')
      } finally {
        this.loading = false
      }
    },
    async markMessageSent() {
      if (this.loading) return
      this.loading = true
      try {
        await writerAcknowledgmentAPI.markMessageSent(this.acknowledgment.id)
        this.$emit('updated')
        this.$toast.success('Message marked as sent')
      } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to update')
      } finally {
        this.loading = false
      }
    },
    async markFileDownloaded() {
      if (this.loading) return
      this.loading = true
      try {
        await writerAcknowledgmentAPI.markFileDownloaded(this.acknowledgment.id)
        this.$emit('updated')
        this.$toast.success('Files marked as downloaded')
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
.writer-acknowledgment-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
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

.engagement-checklist {
  margin-top: 1rem;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.checklist-item.completed label {
  text-decoration: line-through;
  color: #6c757d;
}

.btn-small {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small:hover:not(:disabled) {
  background: #0056b3;
}

.btn-small:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

