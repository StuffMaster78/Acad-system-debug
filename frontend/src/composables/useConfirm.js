import { ref } from 'vue'

/**
 * Composable for showing confirmation dialogs
 * Returns a function that shows a confirmation dialog and returns a promise
 */
export function useConfirm() {
  const showDialog = ref(false)
  const dialogConfig = ref({
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
    details: null,
    icon: null,
    variant: 'default', // 'default', 'danger', 'warning'
    confirmText: 'Confirm',
    cancelText: 'Cancel',
  })
  const resolveRef = ref(null)

  const confirm = (config = {}) => {
    return new Promise((resolve) => {
      dialogConfig.value = {
        title: config.title || 'Confirm Action',
        message: config.message || 'Are you sure you want to proceed?',
        details: config.details || null,
        icon: config.icon || null,
        variant: config.variant || 'default',
        confirmText: config.confirmText || 'Confirm',
        cancelText: config.cancelText || 'Cancel',
      }
      resolveRef.value = resolve
      showDialog.value = true
    })
  }

  const handleConfirm = () => {
    if (resolveRef.value) {
      resolveRef.value(true)
      resolveRef.value = null
    }
    showDialog.value = false
  }

  const handleCancel = () => {
    if (resolveRef.value) {
      resolveRef.value(false)
      resolveRef.value = null
    }
    showDialog.value = false
  }

  return {
    showDialog,
    dialogConfig,
    confirm,
    handleConfirm,
    handleCancel,
  }
}
