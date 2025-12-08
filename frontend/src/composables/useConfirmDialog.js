import { ref } from 'vue'

/**
 * Confirmation dialog composable
 * Provides an easy way to show confirmation dialogs
 * 
 * Usage:
 * ```vue
 * <template>
 *   <ConfirmationDialog
 *     v-model:show="confirm.show"
 *     :title="confirm.title"
 *     :message="confirm.message"
 *     :variant="confirm.variant"
 *     @confirm="confirm.onConfirm"
 *     @cancel="confirm.onCancel"
 *   />
 * </template>
 * 
 * <script setup>
 * import { useConfirmDialog } from '@/composables/useConfirmDialog'
 * 
 * const confirm = useConfirmDialog()
 * 
 * const handleDelete = async () => {
 *   const result = await confirm.show(
 *     'This will permanently delete the item.',
 *     'Delete Item',
 *     { variant: 'danger' }
 *   )
 *   if (result) {
 *     // Proceed with deletion
 *   }
 * }
 * </script>
 * ```
 */
export function useConfirmDialog() {
  const show = ref(false)
  const title = ref('Confirm Action')
  const message = ref('Are you sure you want to proceed?')
  const details = ref(null)
  const variant = ref('default') // 'default', 'danger', 'warning'
  const confirmText = ref(null)
  const cancelText = ref(null)
  const icon = ref(null)
  
  let resolvePromise = null

  const showDialog = (
    messageText,
    titleText = 'Confirm Action',
    options = {}
  ) => {
    return new Promise((resolve) => {
      message.value = messageText
      title.value = titleText
      details.value = options.details || null
      variant.value = options.variant || 'default'
      confirmText.value = options.confirmText || null
      cancelText.value = options.cancelText || null
      icon.value = options.icon || null
      resolvePromise = resolve
      show.value = true
    })
  }

  const showDestructive = (
    messageText,
    titleText = 'Are you sure?',
    options = {}
  ) => {
    return showDialog(
      messageText,
      titleText,
      {
        ...options,
        variant: 'danger',
        icon: options.icon || '⚠️',
        details: options.details || 'This action cannot be undone.'
      }
    )
  }

  const showWarning = (
    messageText,
    titleText = 'Warning',
    options = {}
  ) => {
    return showDialog(
      messageText,
      titleText,
      {
        ...options,
        variant: 'warning',
        icon: options.icon || '⚠️'
      }
    )
  }

  const onConfirm = () => {
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
    show.value = false
  }

  const onCancel = () => {
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
    show.value = false
  }

  return {
    show,
    title,
    message,
    details,
    variant,
    confirmText,
    cancelText,
    icon,
    showDialog,
    showDestructive,
    showWarning,
    onConfirm,
    onCancel
  }
}

