<template>
  <div class="rich-text-editor">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div :id="editorId" class="rich-text-editor-container"></div>
    
    <div v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</div>
    <div v-if="helpText" class="mt-2 text-sm text-gray-500">{{ helpText }}</div>
    <div v-if="showCharCount && maxLength" class="mt-2 text-sm text-gray-500 text-right">
      {{ currentLength }}/{{ maxLength }} characters
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import { stripHtml } from '@/utils/htmlUtils'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Start typing...'
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },
  maxLength: {
    type: Number,
    default: null
  },
  showCharCount: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  toolbar: {
    type: [String, Array],
    default: 'full' // 'full', 'basic', 'minimal', or custom array
  },
  height: {
    type: String,
    default: '200px'
  },
  imageUploadHandler: {
    type: Function,
    default: null // Custom image upload handler
  },
  allowImages: {
    type: Boolean,
    default: true
  },
  stripHtml: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const editorId = ref(`quill-editor-${Math.random().toString(36).substr(2, 9)}`)
const quillInstance = ref(null)
const currentLength = ref(0)

const getToolbarConfig = () => {
  const imageButton = props.allowImages ? ['image'] : []
  
  if (props.toolbar === 'full') {
    return [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'script': 'sub' }, { 'script': 'super' }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      [{ 'direction': 'rtl' }],
      [{ 'align': [] }],
      ['link', ...imageButton, 'video'],
      ['blockquote', 'code-block'],
      ['clean']
    ]
  } else if (props.toolbar === 'basic') {
    return [
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      ['link', ...imageButton],
      ['clean']
    ]
  } else if (props.toolbar === 'minimal') {
    return [
      ['bold', 'italic'],
      ['link', ...imageButton]
    ]
  } else {
    return props.toolbar
  }
}

const handleImageUpload = async (file) => {
  // If custom handler provided, use it
  if (props.imageUploadHandler) {
    try {
      const imageUrl = await props.imageUploadHandler(file)
      return imageUrl
    } catch (error) {
      console.error('Image upload failed:', error)
      return null
    }
  }
  
  // Default: Convert to base64 data URL
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      resolve(e.target.result)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const initializeEditor = () => {
  const container = document.getElementById(editorId.value)
  if (!container) return

  const toolbarConfig = getToolbarConfig()
  
  quillInstance.value = new Quill(container, {
    theme: 'snow',
    placeholder: props.placeholder,
    readOnly: props.disabled,
    modules: {
      toolbar: {
        container: toolbarConfig,
        handlers: props.allowImages ? {
          image: function() {
            const input = document.createElement('input')
            input.setAttribute('type', 'file')
            input.setAttribute('accept', 'image/*')
            input.click()
            
            input.onchange = async () => {
              const file = input.files?.[0]
              if (!file) return
              
              // Check file size (max 5MB)
              if (file.size > 5 * 1024 * 1024) {
                alert('Image size must be less than 5MB')
                return
              }
              
              // Get current selection
              const range = quillInstance.value.getSelection(true)
              
              // Show loading indicator
              quillInstance.value.insertText(range.index, 'Uploading image...', 'user')
              quillInstance.value.setSelection(range.index + 20, 0)
              
              try {
                const imageUrl = await handleImageUpload(file)
                if (imageUrl) {
                  // Remove loading text
                  quillInstance.value.deleteText(range.index, 20)
                  // Insert image
                  quillInstance.value.insertEmbed(range.index, 'image', imageUrl)
                  // Move cursor after image
                  quillInstance.value.setSelection(range.index + 1, 0)
                } else {
                  // Remove loading text on error
                  quillInstance.value.deleteText(range.index, 20)
                  alert('Failed to upload image')
                }
              } catch (error) {
                quillInstance.value.deleteText(range.index, 20)
                alert('Error uploading image: ' + error.message)
              }
            }
          }
        } : {}
      }
    }
  })

  // Set initial content
  if (props.modelValue) {
    quillInstance.value.root.innerHTML = props.modelValue
  }

  // Update character count
  updateCharCount()

  // Listen for text changes
  quillInstance.value.on('text-change', () => {
    const html = quillInstance.value.root.innerHTML
    const text = quillInstance.value.getText()
    
    // Check max length
    if (props.maxLength && text.length > props.maxLength) {
      // Truncate if needed
      const delta = quillInstance.value.getContents()
      const length = quillInstance.value.getLength()
      quillInstance.value.deleteText(props.maxLength, length - props.maxLength)
      return
    }
    
    updateCharCount()
    
    // Strip HTML if requested (for fields that should be plain text)
    const output = props.stripHtml ? stripHtml(html) : html
    emit('update:modelValue', output)
  })

  // Listen for selection changes (for formatting)
  quillInstance.value.on('selection-change', (range) => {
    if (range) {
      // Selection active
    }
  })
}

const updateCharCount = () => {
  if (quillInstance.value) {
    currentLength.value = quillInstance.value.getText().length
  }
}

const updateContent = (newValue) => {
  if (quillInstance.value && newValue !== quillInstance.value.root.innerHTML) {
    quillInstance.value.root.innerHTML = newValue || ''
    updateCharCount()
  }
}

const setDisabled = (disabled) => {
  if (quillInstance.value) {
    quillInstance.value.enable(!disabled)
  }
}

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
  updateContent(newValue)
})

// Watch for disabled prop changes
watch(() => props.disabled, (newValue) => {
  setDisabled(newValue)
})

onMounted(() => {
  initializeEditor()
})

onBeforeUnmount(() => {
  if (quillInstance.value) {
    quillInstance.value = null
  }
})

// Expose methods for parent component
defineExpose({
  getContent: () => quillInstance.value?.root.innerHTML || '',
  getText: () => quillInstance.value?.getText() || '',
  getQuillInstance: () => quillInstance.value,
  setContent: (content) => {
    if (quillInstance.value) {
      quillInstance.value.root.innerHTML = content || ''
      updateCharCount()
      emit('update:modelValue', content)
    }
  },
  clear: () => {
    if (quillInstance.value) {
      quillInstance.value.setText('')
      updateCharCount()
      emit('update:modelValue', '')
    }
  },
  focus: () => {
    if (quillInstance.value) {
      quillInstance.value.focus()
    }
  }
})
</script>

<style scoped>
.rich-text-editor {
  width: 100%;
}

.rich-text-editor-container {
  min-height: v-bind(height);
}

/* Override Quill styles to match our design */
:deep(.ql-container) {
  font-family: inherit;
  font-size: 14px;
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
  border: 1px solid #d1d5db;
  border-top: none;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
}

:deep(.ql-editor) {
  min-height: v-bind(height);
  padding: 12px 15px;
}

:deep(.ql-editor.ql-blank::before) {
  font-style: normal;
  color: #9ca3af;
}

:deep(.ql-editor:focus) {
  outline: none;
}

/* Focus state */
:deep(.ql-container.ql-snow:focus-within) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Disabled state */
:deep(.ql-disabled) {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

:deep(.ql-disabled .ql-editor) {
  cursor: not-allowed;
}
</style>

