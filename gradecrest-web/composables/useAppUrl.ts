export function useAppUrl() {
  const config = useRuntimeConfig()
  const base = config.public.appUrl || 'https://app.gradecrest.com'
  return {
    login:    `${base}/auth/login`,
    register: `${base}/auth/register`,
    order:    `${base}/client/new-order`,
    account:  `${base}/client`,
  }
}
