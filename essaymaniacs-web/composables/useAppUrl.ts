export function useAppUrl() {
  const config = useRuntimeConfig()
  const base = config.public.appUrl || 'https://app.essaymaniacs.com'

  return {
    login:    `${base}/login`,
    register: `${base}/register`,
    apply:    `${base}/apply`,
    dashboard: base,
  }
}
