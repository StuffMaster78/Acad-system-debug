export function useAppUrl() {
  const config = useRuntimeConfig()
  const base = config.public.appUrl || 'https://app.writerscreek.com'
  return {
    login:     `${base}/auth/login`,
    register:  `${base}/auth/register`,
    dashboard: `${base}/writer`,
    apply:     '/apply',
  }
}
