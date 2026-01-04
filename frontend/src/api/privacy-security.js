/**
 * Privacy & Security Information API
 * Provides privacy policy, security practices, data rights, etc.
 */
import apiClient from './client'

export default {
  // Get privacy policy
  getPrivacyPolicy: () => 
    apiClient.get('/users/privacy-security/privacy-policy/'),
  
  // Get security practices & SOPs
  getSecurityPractices: () => 
    apiClient.get('/users/privacy-security/security-practices/'),
  
  // Get data rights information
  getDataRights: () => 
    apiClient.get('/users/privacy-security/data-rights/'),
  
  // Get cookie policy
  getCookiePolicy: () => 
    apiClient.get('/users/privacy-security/cookie-policy/'),
  
  // Get terms of service
  getTermsOfService: () => 
    apiClient.get('/users/privacy-security/terms-of-service/'),
  
  // Get all privacy & security information
  getAll: () => 
    apiClient.get('/users/privacy-security/all/'),

  // Admin: Create or update privacy policy
  createOrUpdatePrivacyPolicy: (data) =>
    apiClient.post('/admin/privacy-security/privacy-policy/', data),
  
  // Admin: Create or update security practices
  createOrUpdateSecurityPractices: (data) =>
    apiClient.post('/admin/privacy-security/security-practices/', data),
  
  // Admin: Create or update data rights
  createOrUpdateDataRights: (data) =>
    apiClient.post('/admin/privacy-security/data-rights/', data),
  
  // Admin: Create or update cookie policy
  createOrUpdateCookiePolicy: (data) =>
    apiClient.post('/admin/privacy-security/cookie-policy/', data),
  
  // Admin: Create or update terms of service
  createOrUpdateTermsOfService: (data) =>
    apiClient.post('/admin/privacy-security/terms-of-service/', data),
}

