export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase
  return $fetch.create({
    baseURL,
    credentials: 'include',
    onRequest({ options }) {
      const csrf = useCookie('csrftoken')
      if (csrf.value) {
        options.headers = { ...options.headers, 'X-CSRFToken': csrf.value }
      }
    },
  })
}
