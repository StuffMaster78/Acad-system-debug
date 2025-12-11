import apiClient from './client'

export default {
  // Blog Posts
  listBlogs: (params) => apiClient.get('/blog_pages_management/blogs/', { params }),
  getBlog: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/`),
  createBlog: (data) => apiClient.post('/blog_pages_management/blogs/', data),
  updateBlog: (id, data) => apiClient.put(`/blog_pages_management/blogs/${id}/`, data),
  patchBlog: (id, data) => apiClient.patch(`/blog_pages_management/blogs/${id}/`, data),
  deleteBlog: (id) => apiClient.delete(`/blog_pages_management/blogs/${id}/`),
  previewBlog: (id) => apiClient.get(`/blog_pages_management/blogs/${id}/preview/`),
  previewBlogBySlug: (slug, params = {}) => apiClient.get(`/blog_pages_management/internal-preview/blog-by-slug/${slug}/`, { params }),
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
  getBlogCTAs: (blogId) => apiClient.get(`/blog_pages_management/blog-posts/${blogId}/ctas/`),
  // Note: track_click is on CTABlockViewSet but needs placement_id in body
  // For now, we'll track via contentTracker which sends to analytics API
  trackCTAClick: (placementId) => {
    // This endpoint expects a CTA block ID, not placement ID
    // We'll handle tracking via the contentTracker instead
    return Promise.resolve({ success: true })
  },
  
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
  getWebsiteMetricsLatest: (params) => apiClient.get('/blog_pages_management/website-metrics/latest/', { params }),
  getWebsiteMetricsByCategory: (params) => apiClient.get('/blog_pages_management/website-metrics/by_category/', { params }),
  getWebsiteMetricsByTag: (params) => apiClient.get('/blog_pages_management/website-metrics/by_tag/', { params }),
  getContentAuditOverview: (params) => apiClient.get('/blog_pages_management/content-audit/audit_overview/', { params }),
  
  // Publishing Targets & Reminders
  getPublishingTargets: (params) => apiClient.get('/blog_pages_management/publishing-targets/', { params }),
  getPublishingTarget: (id) => apiClient.get(`/blog_pages_management/publishing-targets/${id}/`),
  createPublishingTarget: (data) => apiClient.post('/blog_pages_management/publishing-targets/', data),
  updatePublishingTarget: (id, data) => apiClient.put(`/blog_pages_management/publishing-targets/${id}/`, data),
  getOrCreatePublishingTarget: (params) => apiClient.get('/blog_pages_management/publishing-targets/get_or_create/', { params }),
  getMonthlyStats: (params) => apiClient.get('/blog_pages_management/publishing-targets/monthly_stats/', { params }),
  
  // Content Freshness Reminders
  getContentFreshnessReminders: (params) => apiClient.get('/blog_pages_management/content-freshness-reminders/', { params }),
  getStaleContent: (params) => apiClient.get('/blog_pages_management/content-freshness-reminders/stale_content/', { params }),
  acknowledgeFreshnessReminder: (id) => apiClient.post(`/blog_pages_management/content-freshness-reminders/${id}/acknowledge/`),
  refreshFreshnessReminders: (data) => apiClient.post('/blog_pages_management/content-freshness-reminders/refresh_reminders/', data),
  
  // Content Calendar
  getContentCalendar: (params) => apiClient.get('/blog_pages_management/content-calendar/calendar_data/', { params }),
  getMonthlySummary: (params) => apiClient.get('/blog_pages_management/content-calendar/monthly_summary/', { params }),
  bulkRescheduleContent: (data) => apiClient.post('/blog_pages_management/content-calendar/bulk_reschedule/', data),
  exportCalendarICal: (params) => apiClient.get('/blog_pages_management/content-calendar/export_ical/', { params, responseType: 'blob' }),
  
  // Category Publishing Targets
  getCategoryPublishingTargets: (params) => apiClient.get('/blog_pages_management/category-publishing-targets/', { params }),
  createCategoryPublishingTarget: (data) => apiClient.post('/blog_pages_management/category-publishing-targets/', data),
  updateCategoryPublishingTarget: (id, data) => apiClient.put(`/blog_pages_management/category-publishing-targets/${id}/`, data),
  getCategoryTargetsByWebsite: (params) => apiClient.get('/blog_pages_management/category-publishing-targets/by_website/', { params }),
  deleteCategoryPublishingTarget: (id) => apiClient.delete(`/blog_pages_management/category-publishing-targets/${id}/`),
  
  // Publishing Target Threshold
  updatePublishingTargetThreshold: (id, data) => apiClient.patch(`/blog_pages_management/publishing-targets/${id}/update_threshold/`, data),
  
  // Historical Trends
  getPublishingHistory: (params) => apiClient.get('/blog_pages_management/publishing-targets/historical_trends/', { params }),
  
  // Editor Tooling
  healthCheck: (data) => apiClient.post('/blog_pages_management/editor-tooling/health_check/', data),
  getQuickTemplates: (params) => apiClient.get('/blog_pages_management/editor-tooling/quick_templates/', { params }),
  getQuickSnippets: (params) => apiClient.get('/blog_pages_management/editor-tooling/quick_snippets/', { params }),
  getQuickBlocks: (params) => apiClient.get('/blog_pages_management/editor-tooling/quick_blocks/', { params }),
  insertSnippet: (data) => apiClient.post('/blog_pages_management/editor-tooling/insert_snippet/', data),
  insertBlock: (data) => apiClient.post('/blog_pages_management/editor-tooling/insert_block/', data),
  instantiateTemplate: (id, data) => apiClient.post(`/blog_pages_management/content-templates/${id}/instantiate/`, data),
  
  // Content Templates
  listContentTemplates: (params) => apiClient.get('/blog_pages_management/content-templates/', { params }),
  getContentTemplate: (id) => apiClient.get(`/blog_pages_management/content-templates/${id}/`),
  createContentTemplate: (data) => apiClient.post('/blog_pages_management/content-templates/', data),
  updateContentTemplate: (id, data) => apiClient.put(`/blog_pages_management/content-templates/${id}/`, data),
  deleteContentTemplate: (id) => apiClient.delete(`/blog_pages_management/content-templates/${id}/`),
  applyTemplate: (id, data) => apiClient.post(`/blog_pages_management/content-templates/${id}/apply/`, data),
  
  // Content Snippets
  listContentSnippets: (params) => apiClient.get('/blog_pages_management/content-snippets/', { params }),
  getContentSnippet: (id) => apiClient.get(`/blog_pages_management/content-snippets/${id}/`),
  createContentSnippet: (data) => apiClient.post('/blog_pages_management/content-snippets/', data),
  updateContentSnippet: (id, data) => apiClient.put(`/blog_pages_management/content-snippets/${id}/`, data),
  deleteContentSnippet: (id) => apiClient.delete(`/blog_pages_management/content-snippets/${id}/`),
  renderSnippet: (id, data) => apiClient.post(`/blog_pages_management/content-snippets/${id}/render/`, data),
  
  // Editor Tracking & Analytics
  startEditorSession: (data) => apiClient.post('/blog_pages_management/editor-sessions/start/', data),
  endEditorSession: (id) => apiClient.post(`/blog_pages_management/editor-sessions/${id}/end/`),
  trackEditorAction: (id, data) => apiClient.post(`/blog_pages_management/editor-sessions/${id}/track_action/`, data),
  listEditorSessions: (params) => apiClient.get('/blog_pages_management/editor-sessions/', { params }),
  getMyProductivityMetrics: (params) => apiClient.get('/blog_pages_management/editor-productivity/my_metrics/', { params }),
  calculateProductivityMetrics: (data) => apiClient.post('/blog_pages_management/editor-productivity/calculate/', data),
  
  // Editorial Workflow Filters
  getMyDrafts: (params) => apiClient.get('/blog_pages_management/blogs/', { params: { ...params, my_drafts: true } }),
  getNeedsReview: (params) => apiClient.get('/blog_pages_management/blogs/', { params: { ...params, needs_review: true } }),
  getScheduled: (params) => apiClient.get('/blog_pages_management/blogs/', { params: { ...params, scheduled: true } }),
  getStalePublished: (params) => apiClient.get('/blog_pages_management/blogs/', { params: { ...params, stale_published: true } }),
  
  // Revision Diff
  getRevisionDiff: (id, params) => apiClient.get(`/blog_pages_management/blogs/${id}/revision_diff/`, { params }),
  
  // Internal Linking & Recommendations
  suggestInternalLinks: (data) => apiClient.post('/blog_pages_management/blogs/suggest-internal-links/', data),
  getRelatedContent: (id, params) => apiClient.get(`/blog_pages_management/blogs/${id}/related_content/`, { params }),
}

