import { useToast } from './useToast'

/**
 * Confirmation dialog composable
 * Provides a better alternative to browser confirm() dialogs
 */
export function useConfirm() {
  const { warning } = useToast()

  const confirm = (message, title = 'Confirm Action') => {
    return new Promise((resolve) => {
      // For now, use browser confirm but show a warning toast
      // In the future, this could be replaced with a custom modal
      const result = window.confirm(`${title}\n\n${message}`)
      resolve(result)
    })
  }

  const confirmDestructive = (message, title = 'Are you sure?') => {
    return new Promise((resolve) => {
      const result = window.confirm(`⚠️ ${title}\n\n${message}\n\nThis action cannot be undone.`)
      resolve(result)
    })
  }

  return {
    confirm,
    confirmDestructive,
  }
}

