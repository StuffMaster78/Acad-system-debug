export function useAppUrl() {
  const config = useRuntimeConfig()
  const base = config.public.appUrl || 'https://app.essaymaniacs.com'

  return {
    login:     `${base}/auth/login`,
    register:  `${base}/auth/register`,
    apply:     `${base}/apply`,
    dashboard: base,
    order:     `${base}/client/new-order`,
  }
}
