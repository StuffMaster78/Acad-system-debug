import { ref } from 'vue'

/**
 * Confirmation dialog composable
 * Provides a programmatic way to show confirmation dialogs using ConfirmationDialog component
 * 
 * Usage in component:
 * ```vue
 * <template>
 *   <ConfirmationDialog
 *     v-model:show="confirmDialog.show"
 *     :title="confirmDialog.title"
 *     :message="confirmDialog.message"
 *     :variant="confirmDialog.variant"
 *     @confirm="confirmDialog.onConfirm"
 *     @cancel="confirmDialog.onCancel"
 *   />
 * </template>
 * 
 * <script setup>
 * const { showConfirm, showDestructiveConfirm } = useConfirm()
 * 
 * const handleDelete = async () => {
 *   const confirmed = await showDestructiveConfirm(
 *     'This will permanently delete the item.',
 *     'Delete Item'
 *   )
 *   if (confirmed) {
 *     // Proceed with deletion
 *   }
 * }
 * </script>
 * ```
 */
export function useConfirm() {
  const confirmState = ref({
    show: false,
    title: '',
    message: '',
    details: null,
    variant: 'default',
    confirmText: null,
    cancelText: null,
    icon: null,
    resolve: null,
    reject: null
  })

  const showConfirm = (
    message,
    title = 'Confirm Action',
    options = {}
  ) => {
    return new Promise((resolve, reject) => {
      confirmState.value = {
        show: true,
        title,
        message,
        details: options.details || null,
        variant: options.variant || 'default',
        confirmText: options.confirmText || null,
        cancelText: options.cancelText || null,
        icon: options.icon || null,
        resolve,
        reject
      }
    })
  }

  const showDestructiveConfirm = (
    message,
    title = 'Are you sure?',
    options = {}
  ) => {
    return showConfirm(
      message,
      title,
      {
        ...options,
        variant: 'danger',
        icon: options.icon || '⚠️',
        details: options.details || 'This action cannot be undone.'
      }
    )
  }

  const showWarningConfirm = (
    message,
    title = 'Warning',
    options = {}
  ) => {
    return showConfirm(
      message,
      title,
      {
        ...options,
        variant: 'warning',
        icon: options.icon || '⚠️'
      }
    )
  }

  const handleConfirm = () => {
    if (confirmState.value.resolve) {
      confirmState.value.resolve(true)
    }
    confirmState.value.show = false
  }

  const handleCancel = () => {
    if (confirmState.value.reject) {
      confirmState.value.reject(false)
    } else if (confirmState.value.resolve) {
      confirmState.value.resolve(false)
    }
    confirmState.value.show = false
  }

  return {
    confirmState,
    showConfirm,
    showDestructiveConfirm,
    showWarningConfirm,
    handleConfirm,
    handleCancel
  }
}

