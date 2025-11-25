import apiClient from './client'

export default {
  // Blog Posts
  listBlogs: (params) => apiClient.get('/blog_pages_management/blogs/', { params }),
  getBlog: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/`),
  createBlog: (data) => apiClient.post('/blog_pages_management/blogs/', data),
  updateBlog: (id, data) => apiClient.put(`/blog_pages_management/blogs/${id}/`, data),
  patchBlog: (id, data) => apiClient.patch(`/blog_pages_management/blogs/${id}/`, data),
  deleteBlog: (id) => apiClient.delete(`/blog_pages_management/blogs/${id}/`),
  getAvailableWebsites: () => apiClient.get('/blog_pages_management/blogs/available_websites/'),
  getAvailableAuthors: (websiteId) => apiClient.get('/blog_pages_management/blogs/available_authors/', { 
    params: websiteId ? { website_id: websiteId } : {} 
  }),
  
  // Blog Actions
  publishBlog: (id) => apiClient.post(`/blog_pages_management/blogs/${id}/publish/`),
  unpublishBlog: (id) => apiClient.post(`/blog_pages_management/blogs/${id}/unpublish/`),
  createRevision: (id, changeSummary) => apiClient.post(`/blog_pages_management/blogs/${id}/create_revision/`, { change_summary: changeSummary }),
  restoreBlog: (id) => apiClient.post(`/blog_pages_management/blogs/${id}/restore/`),
  permanentlyDeleteBlog: (id) => apiClient.post(`/blog_pages_management/blogs/${id}/delete/`),
  
  // SEO & Metadata
  getSEO: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/schema/`),
  getOGTags: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/og_tags/`),
  getTwitterTags: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/twitter_tags/`),
  getSEOMetadata: (id) => apiClient.get(`/blog_pages_management/seo-metadata/${id}/`),
  updateSEOMetadata: (id, data) => apiClient.put(`/blog_pages_management/seo-metadata/${id}/`, data),
  
  // Categories
  listCategories: (params) => apiClient.get('/blog_pages_management/categories/', { params }),
  getCategory: (id) => apiClient.get(`/blog_pages_management/categories/${id}/`),
  createCategory: (data) => apiClient.post('/blog_pages_management/categories/', data),
  updateCategory: (id, data) => apiClient.put(`/blog_pages_management/categories/${id}/`, data),
  deleteCategory: (id) => apiClient.delete(`/blog_pages_management/categories/${id}/`),
  
  // Tags
  listTags: (params) => apiClient.get('/blog_pages_management/tags/', { params }),
  getTag: (id) => apiClient.get(`/blog_pages_management/tags/${id}/`),
  createTag: (data) => apiClient.post('/blog_pages_management/tags/', data),
  updateTag: (id, data) => apiClient.put(`/blog_pages_management/tags/${id}/`, data),
  deleteTag: (id) => apiClient.delete(`/blog_pages_management/tags/${id}/`),
  
  // Authors
  listAuthors: (params) => apiClient.get('/blog_pages_management/authors/', { params }),
  getAuthor: (id) => apiClient.get(`/blog_pages_management/authors/${id}/`),
  createAuthor: (data) => apiClient.post('/blog_pages_management/authors/', data),
  updateAuthor: (id, data) => apiClient.put(`/blog_pages_management/authors/${id}/`, data),
  deleteAuthor: (id) => apiClient.delete(`/blog_pages_management/authors/${id}/`),
  
  // Media
  listMedia: (params) => apiClient.get('/blog_pages_management/blog-media/', { params }),
  uploadMedia: (formData) => apiClient.post('/blog_pages_management/blog-media/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteMedia: (id) => apiClient.delete(`/blog_pages_management/blog-media/${id}/`),
  
  // CTAs
  listCTAs: (params) => apiClient.get('/blog_pages_management/cta-blocks/', { params }),
  getCTA: (id) => apiClient.get(`/blog_pages_management/cta-blocks/${id}/`),
  createCTA: (data) => apiClient.post('/blog_pages_management/cta-blocks/', data),
  updateCTA: (id, data) => apiClient.put(`/blog_pages_management/cta-blocks/${id}/`, data),
  deleteCTA: (id) => apiClient.delete(`/blog_pages_management/cta-blocks/${id}/`),
  
  // FAQs
  listFAQs: (params) => apiClient.get('/blog_pages_management/faq-schemas/', { params }),
  getFAQ: (id) => apiClient.get(`/blog_pages_management/faq-schemas/${id}/`),
  createFAQ: (data) => apiClient.post('/blog_pages_management/faq-schemas/', data),
  updateFAQ: (id, data) => apiClient.put(`/blog_pages_management/faq-schemas/${id}/`, data),
  deleteFAQ: (id) => apiClient.delete(`/blog_pages_management/faq-schemas/${id}/`),
  
  // Revisions
  listRevisions: (params) => apiClient.get('/blog_pages_management/blog-revisions/', { params }),
  getRevision: (id) => apiClient.get(`/blog_pages_management/blog-revisions/${id}/`),
  restoreRevision: (id) => apiClient.post(`/blog_pages_management/blog-revisions/${id}/restore/`),
  
  // Analytics
  getBlogAnalytics: (id) => apiClient.get(`/blog_pages_management/blog-analytics/${id}/`),
  getContentMetrics: (params) => apiClient.get('/blog_pages_management/content-metrics/', { params }),
  
  // Internal Linking & Recommendations
  suggestInternalLinks: (data) => apiClient.post('/blog_pages_management/blogs/suggest-internal-links/', data),
  getRelatedContent: (id, params) => apiClient.get(`/blog_pages_management/blogs/${id}/related_content/`, { params }),
}

