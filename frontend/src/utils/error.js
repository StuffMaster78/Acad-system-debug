export function normalizeApiError(error) {
  // Network-level
  if (!error.response) {
    return {
      status: 0,
      message: `Network error: unable to reach API (${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'})`,
      code: 'NETWORK_ERROR',
    }
  }

  const status = error.response.status
  const data = error.response.data || {}

  const message = data.error || data.detail || data.message || (Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : null) || `Request failed with status ${status}`

  return {
    status,
    message,
    code: data.code || null,
    raw: data,
  }
}

export function isAuthError(error) {
  const status = error?.response?.status
  return status === 401 || status === 403
}

