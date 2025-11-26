<template>
  <div class="internal-linking-widget bg-white border border-gray-200 rounded-lg shadow-sm p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
        <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        Internal Linking Suggestions
      </h3>
      <button
        @click="toggleAutoLink"
        :class="[
          'text-xs px-2 py-1 rounded transition-colors',
          autoLinkEnabled
            ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        ]"
        :title="autoLinkEnabled ? 'Auto-linking enabled' : 'Auto-linking disabled'"
      >
        {{ autoLinkEnabled ? 'Auto ✓' : 'Auto' }}
      </button>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="suggestions.length === 0" class="text-sm text-gray-500 py-4 text-center">
      <p>Start typing to see link suggestions</p>
      <p class="text-xs mt-1">Or select text to get suggestions</p>
    </div>

    <div v-else class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        :data-suggestion-id="suggestion.id"
        class="suggestion-item p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer group"
        @click="insertLink(suggestion)"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-sm font-medium text-gray-900 truncate">{{ suggestion.title }}</span>
              <span
                :class="[
                  'text-xs px-1.5 py-0.5 rounded',
                  suggestion.type === 'blog' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
                ]"
              >
                {{ suggestion.type === 'blog' ? 'Blog' : 'Page' }}
              </span>
            </div>
            <p v-if="suggestion.excerpt" class="text-xs text-gray-600 line-clamp-2 mb-1">
              {{ suggestion.excerpt }}
            </p>
            <div class="flex items-center gap-3 text-xs text-gray-500">
              <span v-if="suggestion.category">{{ suggestion.category }}</span>
              <span v-if="suggestion.score" class="flex items-center gap-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {{ Math.round(suggestion.score * 100) }}% match
              </span>
            </div>
          </div>
          <button
            @click.stop="insertLink(suggestion)"
            class="opacity-0 group-hover:opacity-100 transition-opacity text-blue-600 hover:text-blue-700 p-1"
            title="Insert link"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="selectedText" class="mt-4 pt-4 border-t border-gray-200">
      <p class="text-xs text-gray-600 mb-2">Selected text:</p>
      <p class="text-sm font-medium text-gray-900 bg-gray-50 p-2 rounded">{{ selectedText }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { debounce } from '@/utils/debounce'
import blogPagesAPI from '@/api/blog-pages'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  websiteId: {
    type: Number,
    required: true
  },
  currentPostId: {
    type: Number,
    default: null
  },
  contentType: {
    type: String,
    default: 'blog' // 'blog' or 'seo_page'
  },
  editorInstance: {
    type: Object,
    default: null // Quill editor instance
  }
})

const emit = defineEmits(['link-inserted'])

const suggestions = ref([])
const loading = ref(false)
const selectedText = ref('')
const autoLinkEnabled = ref(false)

let debouncedFetch = null

const fetchSuggestions = async (text) => {
  if (!text || text.length < 10) {
    suggestions.value = []
    return
  }

  loading.value = true
  try {
    const response = await blogPagesAPI.suggestInternalLinks({
      content: text,
      website_id: props.websiteId,
      current_post_id: props.currentPostId,
      limit: 10,
      content_type: props.contentType
    })
    suggestions.value = response.data.suggestions || []
  } catch (error) {
    console.error('Failed to fetch link suggestions:', error)
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

const insertLink = (suggestion) => {
  const text = selectedText.value || suggestion.title
  const url = suggestion.url

  if (props.editorInstance) {
    // Quill editor
    const range = props.editorInstance.getSelection(true)
    if (range) {
      props.editorInstance.formatText(range.index, range.length, 'link', url)
      if (!selectedText.value) {
        // Replace selected text with link text
        props.editorInstance.deleteText(range.index, range.length)
        props.editorInstance.insertText(range.index, text, 'link', url)
      }
    } else {
      // Insert at cursor
      const index = props.editorInstance.getSelection()?.index || 0
      props.editorInstance.insertText(index, text, 'link', url)
    }
  } else {
    // Fallback: emit event for parent to handle
    emit('link-inserted', {
      text,
      url,
      suggestion
    })
  }

  // Clear selection
  selectedText.value = ''
  
  // Show success feedback
  const item = document.querySelector(`[data-suggestion-id="${suggestion.id}"]`)
  if (item) {
    item.classList.add('bg-green-50', 'border-green-300')
    setTimeout(() => {
      item.classList.remove('bg-green-50', 'border-green-300')
    }, 1000)
  }
}

const toggleAutoLink = () => {
  autoLinkEnabled.value = !autoLinkEnabled.value
  if (autoLinkEnabled.value) {
    // Auto-link on text selection
    watch(() => props.content, (newContent) => {
      if (newContent && newContent.length > 20) {
        debouncedFetch(newContent)
      }
    }, { immediate: true })
  }
}

const handleTextSelection = () => {
  if (props.editorInstance) {
    const range = props.editorInstance.getSelection()
    if (range && range.length > 0) {
      const text = props.editorInstance.getText(range.index, range.length)
      selectedText.value = text
      if (text.length > 10) {
        debouncedFetch(text)
      }
    } else {
      selectedText.value = ''
    }
  }
}

onMounted(() => {
  // Debounce suggestion fetching
  debouncedFetch = debounce(fetchSuggestions, 500)

  // Watch content changes
  watch(() => props.content, (newContent) => {
    if (newContent && newContent.length > 20 && !selectedText.value) {
      debouncedFetch(newContent)
    }
  })

  // Listen for text selection in editor
  if (props.editorInstance) {
    props.editorInstance.on('selection-change', handleTextSelection)
  }
})

onBeforeUnmount(() => {
  if (props.editorInstance) {
    props.editorInstance.off('selection-change', handleTextSelection)
  }
})
</script>

<style scoped>
.suggestion-item {
  transition: all 0.2s ease;
}

.suggestion-item:hover {
  transform: translateX(2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

