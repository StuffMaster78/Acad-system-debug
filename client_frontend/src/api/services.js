import apiClient from './client'

export default {
  // Website info (public)
  getWebsite: (domain) => apiClient.get(`/websites/websites/`, { 
    params: { domain } 
  }),
  
  // Pricing calculator
  calculatePrice: (data) => apiClient.post('/pricing-configs/pricing-configs/calculate_price/', data),
  
  // Get pricing configs (public)
  getPricingConfigs: () => apiClient.get('/pricing-configs/pricing-configs/'),
  
  // Order quote (public)
  getQuote: (data) => apiClient.post('/orders/orders/quote/', data),
  
  // Create order (requires auth or guest)
  createOrder: (data) => apiClient.post('/orders/orders/create/', data),
  
  // Service pages
  getServicePages: (params) => apiClient.get('/service-pages/service-pages/', { params }),
  getServicePage: (slug) => apiClient.get(`/service-pages/service-pages/${slug}/`),
  
  // Blog posts
  getBlogPosts: (params) => apiClient.get('/blog_pages_management/blog-posts/', { params }),
  getBlogPost: (slug) => apiClient.get(`/blog_pages_management/blog-posts/${slug}/`),
  
  // SEO pages
  getSeoPage: (slug) => apiClient.get(`/seo-pages/seo-pages/${slug}/`),
}

