export function useApi() {
  const config = useRuntimeConfig()

  return $fetch.create({
    baseURL: config.public.apiBase,
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
