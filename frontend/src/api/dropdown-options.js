import apiClient from './client'

export default {
  /**
   * Get all dropdown options
   * @param {Object} params - Query parameters
   * @param {number} params.website_id - Filter by website ID
   * @param {boolean} params.include_enums - Include enum choices (default: true)
   * @param {boolean} params.include_configs - Include order configs (default: true)
   * @param {boolean} params.include_websites - Include websites list (default: true)
   * @param {boolean} params.include_users - Include users list (default: false)
   */
  getAll: (params = {}) => apiClient.get('/dropdown-options/', { params }),

  /**
   * Get dropdown options by category
   * @param {string} category - Category name (e.g., 'paper_types', 'order_status', 'websites')
   * @param {Object} params - Query parameters
   */
  getByCategory: (category, params = {}) => 
    apiClient.get(`/dropdown-options/${category}/`, { params }),

  /**
   * Get order configuration options
   */
  getOrderConfigs: (params = {}) => 
    apiClient.get('/dropdown-options/order_configs/', { params }),

  /**
   * Get enum choices (status, payment types, etc.)
   */
  getEnums: (params = {}) => 
    apiClient.get('/dropdown-options/enums/', { params }),

  /**
   * Get paper types
   */
  getPaperTypes: (params = {}) => 
    apiClient.get('/dropdown-options/paper_types/', { params }),

  /**
   * Get subjects
   */
  getSubjects: (params = {}) => 
    apiClient.get('/dropdown-options/subjects/', { params }),

  /**
   * Get academic levels
   */
  getAcademicLevels: (params = {}) => 
    apiClient.get('/dropdown-options/academic_levels/', { params }),

  /**
   * Get formatting styles
   */
  getFormattingStyles: (params = {}) => 
    apiClient.get('/dropdown-options/formatting_styles/', { params }),

  /**
   * Get types of work
   */
  getTypesOfWork: (params = {}) => 
    apiClient.get('/dropdown-options/types_of_work/', { params }),

  /**
   * Get English types
   */
  getEnglishTypes: (params = {}) => 
    apiClient.get('/dropdown-options/english_types/', { params }),

  /**
   * Get order status options
   */
  getOrderStatus: () => 
    apiClient.get('/dropdown-options/enums/').then(res => ({
      data: res.data?.order_status || []
    })),

  /**
   * Get payment status options
   */
  getPaymentStatus: () => 
    apiClient.get('/dropdown-options/enums/').then(res => ({
      data: res.data?.payment_status || []
    })),

  /**
   * Get websites list
   */
  getWebsites: (params = {}) => 
    apiClient.get('/dropdown-options/websites/', { params }),

  /**
   * Get users list (admin only)
   */
  getUsers: (params = {}) => 
    apiClient.get('/dropdown-options/users/', { params }),
}

