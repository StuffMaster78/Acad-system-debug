export function useApi() {
  const config = useRuntimeConfig()

  return $fetch.create({
    baseURL: config.public.apiBase,
    credentials: 'include',
    onRequest({ options }) {
      const csrf = useCookie('csrftoken')
      if (csrf.value) {
        options.headers = {
          ...options.headers,
          'X-CSRFToken': csrf.value,
        }
      }
    },
  })
}
