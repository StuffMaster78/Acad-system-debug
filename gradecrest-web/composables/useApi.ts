export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase
  return $fetch.create({
    baseURL,
    credentials: 'include',
    onRequest({ options }) {
      const csrf = useCookie('csrftoken')
      if (csrf.value) {
        const headers = new Headers(options.headers)
        headers.set('X-CSRFToken', csrf.value)
        options.headers = headers
      }
    },
  })
}
