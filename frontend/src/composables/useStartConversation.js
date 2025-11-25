/**
 * Composable for starting conversations/threads
 * Provides a unified, simplified way to start conversations for orders
 */
import { ref } from 'vue'
import communicationsAPI from '@/api/communications'
import { useAuthStore } from '@/stores/auth'

export function useStartConversation() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Start a conversation thread for an order.
   * Automatically determines participants based on the order.
   * 
   * @param {number|string} orderId - The order ID
   * @returns {Promise<Object>} The created thread object
   */
  const startConversation = async (orderId) => {
    if (!orderId) {
      throw new Error('Order ID is required')
    }

    const authStore = useAuthStore()
    if (!authStore.token) {
      throw new Error('Authentication required. Please log in.')
    }

    loading.value = true
    error.value = null

    try {
      const response = await communicationsAPI.startThreadForOrder(orderId)
      
      // Handle response format (could be { thread: {...} } or direct thread object)
      const thread = response.data?.thread || response.data
      
      if (!thread) {
        throw new Error('Thread was not returned from the server')
      }

      return thread
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to start conversation'
      error.value = errorMessage
      console.error('Failed to start conversation:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Check if a conversation already exists for an order.
   * 
   * @param {number|string} orderId - The order ID
   * @returns {Promise<Object|null>} The existing thread or null
   */
  const getExistingThread = async (orderId) => {
    try {
      const response = await communicationsAPI.listThreads({ order: orderId })
      const threads = response.data?.results || response.data || []
      return threads.length > 0 ? threads[0] : null
    } catch (err) {
      console.error('Failed to check for existing thread:', err)
      return null
    }
  }

  /**
   * Start a conversation or get existing one.
   * 
   * @param {number|string} orderId - The order ID
   * @returns {Promise<Object>} The thread object (existing or newly created)
   */
  const startOrGetConversation = async (orderId) => {
    // First check if thread already exists
    const existingThread = await getExistingThread(orderId)
    if (existingThread) {
      return existingThread
    }

    // If no existing thread, create a new one
    return await startConversation(orderId)
  }

  return {
    loading,
    error,
    startConversation,
    getExistingThread,
    startOrGetConversation
  }
}

