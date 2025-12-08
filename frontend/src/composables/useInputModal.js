import { ref } from 'vue'

/**
 * Input modal composable
 * Provides an easy way to show input modals (replacement for prompt())
 * 
 * Usage:
 * ```vue
 * <template>
 *   <InputModal
 *     v-model:show="inputModal.show"
 *     :title="inputModal.title"
 *     :message="inputModal.message"
 *     :label="inputModal.label"
 *     :placeholder="inputModal.placeholder"
 *     :multiline="inputModal.multiline"
 *     @submit="inputModal.onSubmit"
 *     @cancel="inputModal.onCancel"
 *   />
 * </template>
 * 
 * <script setup>
 * import { useInputModal } from '@/composables/useInputModal'
 * 
 * const inputModal = useInputModal()
 * 
 * const handleAction = async () => {
 *   const reason = await inputModal.show(
 *     'Enter reason for this action',
 *     'Reason Required',
 *     { multiline: true }
 *   )
 *   if (reason) {
 *     // Proceed with reason
 *   }
 * }
 * </script>
 * ```
 */
export function useInputModal() {
  const show = ref(false)
  const title = ref('Input Required')
  const message = ref(null)
  const label = ref(null)
  const placeholder = ref('Enter value...')
  const hint = ref(null)
  const multiline = ref(false)
  const rows = ref(4)
  const required = ref(true)
  const defaultValue = ref('')
  const confirmText = ref(null)
  const cancelText = ref(null)
  
  let resolvePromise = null
  let escapeHandler = null

  const showModal = (
    messageText,
    titleText = 'Input Required',
    options = {}
  ) => {
    return new Promise((resolve) => {
      // Ensure all values are properly set
      message.value = typeof messageText === 'string' ? messageText : String(messageText || '')
      title.value = typeof titleText === 'string' ? titleText : 'Input Required'
      label.value = options.label || null
      placeholder.value = options.placeholder || 'Enter value...'
      hint.value = options.hint || null
      multiline.value = options.multiline || false
      rows.value = options.rows || 4
      required.value = options.required !== false
      // Ensure defaultValue is always a string
      defaultValue.value = typeof options.defaultValue === 'string' ? options.defaultValue : ''
      confirmText.value = options.confirmText || null
      cancelText.value = options.cancelText || null
      resolvePromise = resolve
      show.value = true
    })
  }

  const onSubmit = (value) => {
    if (resolvePromise) {
      resolvePromise(value)
      resolvePromise = null
    }
    show.value = false
  }

  const onCancel = () => {
    if (resolvePromise) {
      resolvePromise(null)
      resolvePromise = null
    }
    show.value = false
  }

  return {
    show,
    title,
    message,
    label,
    placeholder,
    hint,
    multiline,
    rows,
    required,
    defaultValue,
    confirmText,
    cancelText,
    showModal,
    onSubmit,
    onCancel
  }
}

