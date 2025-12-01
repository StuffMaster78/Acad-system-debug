/**
 * Account Management API
 * Unified API for account operations: password, 2FA, profile updates, security
 */
import apiClient from './client'

export default {
  // Password Management
  changePassword: (currentPassword, newPassword) => 
    apiClient.post('/users/account/change-password/', {
      current_password: currentPassword,
      new_password: newPassword
    }),
  
  requestPasswordReset: (email) => 
    apiClient.post('/users/account/request-password-reset/', { email }),
  
  completePasswordReset: (token, otpCode, newPassword) => 
    apiClient.post('/users/account/complete-password-reset/', {
      token,
      otp_code: otpCode,
      new_password: newPassword
    }),
  
  // 2FA/MFA Management
  get2FAStatus: () => 
    apiClient.get('/users/account/2fa/status/'),
  
  setup2FA: () => 
    apiClient.post('/users/account/2fa/setup/'),
  
  verifyAndEnable2FA: (totpCode) => 
    apiClient.post('/users/account/2fa/verify-and-enable/', { totp_code: totpCode }),
  
  disable2FA: (password, backupCode = null) => 
    apiClient.post('/users/account/2fa/disable/', {
      password,
      backup_code: backupCode
    }),
  
  regenerateBackupCodes: (password) => 
    apiClient.post('/users/account/2fa/regenerate-backup-codes/', { password }),
  
  // Profile Update Requests
  requestProfileUpdate: (data) => 
    apiClient.post('/users/account/request-profile-update/', data),
  
  getProfileUpdateRequests: () => 
    apiClient.get('/users/account/profile-update-requests/'),
  
  // Account Deletion
  requestAccountDeletion: (reason) => 
    apiClient.post('/users/account/request-deletion/', { reason }),
  
  getDeletionStatus: () => 
    apiClient.get('/users/account/deletion-status/'),
  
  // Security Settings
  getSecuritySettings: () => 
    apiClient.get('/users/account/security-settings/'),
  
  // Admin: Manage user accounts (for admin/superadmin)
  adminResetUserPassword: (userId) => 
    apiClient.post(`/admin-management/user-management/${userId}/reset_password/`),
  
  adminGetUserSecuritySettings: (userId) => 
    apiClient.get(`/users/users/${userId}/security-settings/`),
}

