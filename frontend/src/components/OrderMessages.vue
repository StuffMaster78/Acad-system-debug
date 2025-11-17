<template>
  <div class="order-messages">
    <div class="messages-header">
      <h2>Order Messages</h2>
      <button 
        v-if="threads.length === 0 && !loading" 
        @click="handleStartConversation" 
        :disabled="creatingThread" 
        class="btn btn-primary"
      >
        <span v-if="creatingThread">Creating...</span>
        <span v-else>Start Conversation</span>
      </button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="error = null" class="btn-close">×</button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">Loading messages...</div>

    <!-- Threads list -->
    <div v-else-if="threads.length > 0" class="threads-list">
      <div 
        v-for="thread in threads" 
        :key="thread.id" 
        class="thread-item"
        :class="{ active: activeThreadId === thread.id }"
        @click="selectThread(thread.id)"
      >
        <div class="thread-header">
          <h3>Thread #{{ thread.id }}</h3>
          <span v-if="thread.unread_count > 0" class="unread-badge">
            {{ thread.unread_count }} unread
          </span>
        </div>
        <div v-if="thread.last_message" class="thread-preview">
          {{ thread.last_message.message?.substring(0, 50) }}...
        </div>
      </div>
    </div>

    <!-- No threads message -->
    <div v-else class="empty-state">
      <p>No conversation started yet.</p>
      <button @click="handleStartConversation" :disabled="creatingThread" class="btn btn-primary">
        Start Conversation
      </button>
    </div>

    <!-- Messages view -->
    <div v-if="activeThreadId" class="messages-view">
      <div class="messages-header">
        <h3>Messages</h3>
        <button @click="activeThreadId = null" class="btn btn-secondary">Close</button>
      </div>
      
      <div v-if="loadingMessages" class="loading">Loading messages...</div>
      <div v-else class="messages-list">
        <div 
          v-for="message in messages" 
          :key="message.id" 
          class="message-item"
          :class="{ 'is-sender': message.is_sender }"
        >
          <div class="message-header">
            <strong>{{ message.sender?.username || 'System' }}</strong>
            <span class="message-time">{{ formatDate(message.sent_at) }}</span>
          </div>
          <div class="message-content">{{ message.message }}</div>
        </div>
      </div>

      <!-- Send message form -->
      <div class="message-form">
        <textarea 
          v-model="newMessage" 
          placeholder="Type your message..."
          rows="3"
          @keydown.ctrl.enter="sendMessage"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="!newMessage.trim() || sendingMessage"
          class="btn btn-primary"
        >
          <span v-if="sendingMessage">Sending...</span>
          <span v-else>Send</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useOrderMessages } from '@/composables/useOrderMessages'

export default {
  name: 'OrderMessages',
  props: {
    orderId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      creatingThread,
      loadThreads,
      loadMessages,
      createThread,
      sendThreadMessage
    } = useOrderMessages(props.orderId)
    
    const activeThreadId = ref(null)
    const newMessage = ref('')
    const sendingMessage = ref(false)
    const loadingMessages = ref(false)
    
    const handleStartConversation = async () => {
      try {
        const thread = await createThread()
        if (thread) {
          // Automatically open the new thread
          activeThreadId.value = thread.id
          await loadMessages(thread.id)
        }
      } catch (err) {
        console.error('Failed to start conversation:', err)
        // Error is already set in the composable
      }
    }
    
    const selectThread = async (threadId) => {
      activeThreadId.value = threadId
      loadingMessages.value = true
      try {
        await loadMessages(threadId)
      } finally {
        loadingMessages.value = false
      }
    }
    
    const sendMessage = async () => {
      if (!newMessage.value.trim() || !activeThreadId.value) {
        return
      }
      
      sendingMessage.value = true
      try {
        await sendThreadMessage(activeThreadId.value, newMessage.value.trim())
        newMessage.value = ''
      } catch (err) {
        console.error('Failed to send message:', err)
      } finally {
        sendingMessage.value = false
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    return {
      threads,
      messages,
      unreadCount,
      loading,
      error,
      creatingThread,
      activeThreadId,
      newMessage,
      sendingMessage,
      loadingMessages,
      handleStartConversation,
      selectThread,
      sendMessage,
      formatDate
    }
  }
}
</script>

<style scoped>
.order-messages {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #dc2626;
  padding: 0;
  width: 24px;
  height: 24px;
}

.threads-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.thread-item {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.thread-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.thread-item.active {
  border-color: #667eea;
  background: #f5f3ff;
}

.thread-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.thread-header h3 {
  margin: 0;
  font-size: 16px;
}

.unread-badge {
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.thread-preview {
  color: #6b7280;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
}

.messages-view {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.messages-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.message-item {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.message-item.is-sender {
  background: #eff6ff;
  margin-left: 20%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.message-time {
  color: #6b7280;
  font-size: 12px;
}

.message-content {
  color: #1f2937;
  line-height: 1.5;
}

.message-form {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-form textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 60px;
}

.message-form textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}
</style>

