import apiClient from './client'

const EXPRESS_CLASSES_BASE = '/class-management/express-classes'

export default {
  /**
   * List express classes with optional filters
   */
  list(params = {}) {
    return apiClient.get(EXPRESS_CLASSES_BASE, { params })
  },

  /**
   * Get a single express class by ID
   */
  get(id) {
    return apiClient.get(`${EXPRESS_CLASSES_BASE}/${id}/`)
  },

  /**
   * Create a new express class (client inquiry)
   */
  create(data) {
    return apiClient.post(EXPRESS_CLASSES_BASE, data)
  },

  /**
   * Update an express class
   */
  update(id, data) {
    return apiClient.patch(`${EXPRESS_CLASSES_BASE}/${id}/`, data)
  },

  /**
   * Admin: Review scope and set price
   */
  reviewScope(id, data) {
    return apiClient.post(`${EXPRESS_CLASSES_BASE}/${id}/review_scope/`, data)
  },

  /**
   * Admin: Assign writer to express class
   */
  assignWriter(id, data) {
    return apiClient.post(`${EXPRESS_CLASSES_BASE}/${id}/assign_writer/`, data)
  },

  /**
   * Start progress on express class
   */
  startProgress(id) {
    return apiClient.post(`${EXPRESS_CLASSES_BASE}/${id}/start_progress/`)
  },

  /**
   * Admin: Mark express class as completed
   */
  complete(id) {
    return apiClient.post(`${EXPRESS_CLASSES_BASE}/${id}/complete/`)
  },

  /**
   * Create a communication thread for express class
   */
  createThread(id, data) {
    return apiClient.post(`${EXPRESS_CLASSES_BASE}/${id}/create_thread/`, data)
  },

  /**
   * Get all communication threads for express class
   */
  getThreads(id) {
    return apiClient.get(`${EXPRESS_CLASSES_BASE}/${id}/threads/`)
  },

  /**
   * Get approval queue for express classes
   */
  getApprovalQueue(params = {}) {
    return apiClient.get(`${EXPRESS_CLASSES_BASE}/approval-queue/`, { params })
  },

  /**
   * Inquiry Files
   */
  listInquiryFiles(expressClassId, params = {}) {
    return apiClient.get('/class-management/express-class-inquiry-files/', {
      params: { express_class: expressClassId, ...params }
    })
  },
  uploadInquiryFile(data) {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key])
      }
    })
    return apiClient.post('/class-management/express-class-inquiry-files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteInquiryFile(id) {
    return apiClient.delete(`/class-management/express-class-inquiry-files/${id}/delete/`)
  },
}

