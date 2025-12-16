import apiClient from './client'

export default {
  // Newsletters
  listNewsletters: (params) => apiClient.get('/blog_pages_management/newsletters/', { params }),
  getNewsletter: (id) => apiClient.get(`/blog_pages_management/newsletters/${id}/`),
  createNewsletter: (data) => apiClient.post('/blog_pages_management/newsletters/', data),
  updateNewsletter: (id, data) => apiClient.put(`/blog_pages_management/newsletters/${id}/`, data),
  patchNewsletter: (id, data) => apiClient.patch(`/blog_pages_management/newsletters/${id}/`, data),
  deleteNewsletter: (id) => apiClient.delete(`/blog_pages_management/newsletters/${id}/`),
  sendNewsletter: (id, data) => apiClient.post(`/blog_pages_management/newsletters/${id}/send/`, data),
  scheduleNewsletter: (id, data) => apiClient.post(`/blog_pages_management/newsletters/${id}/schedule/`, data),
  
  // Newsletter Subscribers
  listSubscribers: (params) => apiClient.get('/blog_pages_management/newsletter-subscribers/', { params }),
  getSubscriber: (id) => apiClient.get(`/blog_pages_management/newsletter-subscribers/${id}/`),
  createSubscriber: (data) => apiClient.post('/blog_pages_management/newsletter-subscribers/', data),
  updateSubscriber: (id, data) => apiClient.put(`/blog_pages_management/newsletter-subscribers/${id}/`, data),
  deleteSubscriber: (id) => apiClient.delete(`/blog_pages_management/newsletter-subscribers/${id}/`),
  unsubscribe: (id) => apiClient.post(`/blog_pages_management/newsletter-subscribers/${id}/unsubscribe/`),
  resubscribe: (id) => apiClient.post(`/blog_pages_management/newsletter-subscribers/${id}/resubscribe/`),
  bulkSubscribe: (data) => apiClient.post('/blog_pages_management/newsletter-subscribers/bulk_subscribe/', data),
  bulkUnsubscribe: (data) => apiClient.post('/blog_pages_management/newsletter-subscribers/bulk_unsubscribe/', data),
  exportSubscribers: (params) => apiClient.get('/blog_pages_management/newsletter-subscribers/export/', { params, responseType: 'blob' }),
  
  // Newsletter Analytics
  listAnalytics: (params) => apiClient.get('/blog_pages_management/newsletter-analytics/', { params }),
  getAnalytics: (id) => apiClient.get(`/blog_pages_management/newsletter-analytics/${id}/`),
  getNewsletterAnalytics: (newsletterId) => apiClient.get(`/blog_pages_management/newsletter-analytics/`, { params: { newsletter: newsletterId } }),
}

