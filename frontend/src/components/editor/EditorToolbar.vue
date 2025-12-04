<template>
  <div class="editor-toolbar bg-gray-50 border-b border-gray-200 p-2 flex items-center gap-2 flex-wrap">
    <!-- Templates Button -->
    <div class="relative">
      <button
        @click="showTemplates = !showTemplates"
        class="px-3 py-1.5 text-sm bg-white border rounded hover:bg-gray-50 flex items-center gap-1"
        :class="{ 'bg-blue-50 border-blue-300': showTemplates }"
      >
        📄 Templates
      </button>
      <div
        v-if="showTemplates"
        class="absolute top-full left-0 mt-1 bg-white border rounded shadow-lg z-50 w-64 max-h-96 overflow-y-auto"
      >
        <div class="p-2 border-b">
          <input
            v-model="templateSearch"
            type="text"
            placeholder="Search templates..."
            class="w-full px-2 py-1 text-sm border rounded"
            @input="searchTemplates"
          />
        </div>
        <div v-if="loadingTemplates" class="p-4 text-center text-sm text-gray-500">
          Loading...
        </div>
        <div v-else-if="templates.length" class="divide-y">
          <button
            v-for="template in templates"
            :key="template.id"
            @click="insertTemplate(template)"
            class="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
          >
            <div class="font-medium">{{ template.name }}</div>
            <div class="text-xs text-gray-500">{{ template.template_type }}</div>
          </button>
        </div>
        <div v-else class="p-4 text-center text-sm text-gray-500">
          No templates found
        </div>
      </div>
    </div>

    <!-- Snippets Button -->
    <div class="relative">
      <button
        @click="showSnippets = !showSnippets"
        class="px-3 py-1.5 text-sm bg-white border rounded hover:bg-gray-50 flex items-center gap-1"
        :class="{ 'bg-blue-50 border-blue-300': showSnippets }"
      >
        ✂️ Snippets
      </button>
      <div
        v-if="showSnippets"
        class="absolute top-full left-0 mt-1 bg-white border rounded shadow-lg z-50 w-64 max-h-96 overflow-y-auto"
      >
        <div class="p-2 border-b">
          <input
            v-model="snippetSearch"
            type="text"
            placeholder="Search snippets..."
            class="w-full px-2 py-1 text-sm border rounded"
            @input="searchSnippets"
          />
        </div>
        <div v-if="loadingSnippets" class="p-4 text-center text-sm text-gray-500">
          Loading...
        </div>
        <div v-else-if="snippets.length" class="divide-y">
          <button
            v-for="snippet in snippets"
            :key="snippet.id"
            @click="insertSnippet(snippet)"
            class="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
          >
            <div class="font-medium">{{ snippet.name }}</div>
            <div class="text-xs text-gray-500">{{ snippet.snippet_type }}</div>
          </button>
        </div>
        <div v-else class="p-4 text-center text-sm text-gray-500">
          No snippets found
        </div>
      </div>
    </div>

    <!-- Content Blocks Button -->
    <div class="relative">
      <button
        @click="showBlocks = !showBlocks"
        class="px-3 py-1.5 text-sm bg-white border rounded hover:bg-gray-50 flex items-center gap-1"
        :class="{ 'bg-blue-50 border-blue-300': showBlocks }"
      >
        🧩 Blocks
      </button>
      <div
        v-if="showBlocks"
        class="absolute top-full left-0 mt-1 bg-white border rounded shadow-lg z-50 w-64 max-h-96 overflow-y-auto"
      >
        <div class="p-2 border-b">
          <select
            v-model="blockTypeFilter"
            @change="loadBlocks"
            class="w-full px-2 py-1 text-sm border rounded"
          >
            <option value="">All Types</option>
            <option value="table">Table</option>
            <option value="info_box">Info Box</option>
            <option value="warning_box">Warning Box</option>
            <option value="tip_box">Tip Box</option>
            <option value="quote">Quote</option>
            <option value="statistics">Statistics</option>
          </select>
        </div>
        <div v-if="loadingBlocks" class="p-4 text-center text-sm text-gray-500">
          Loading...
        </div>
        <div v-else-if="blocks.length" class="divide-y">
          <button
            v-for="block in blocks"
            :key="block.id"
            @click="insertBlock(block)"
            class="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
          >
            <div class="font-medium">{{ block.name }}</div>
            <div class="text-xs text-gray-500">{{ block.block_type }}</div>
          </button>
        </div>
        <div v-else class="p-4 text-center text-sm text-gray-500">
          No blocks found
        </div>
      </div>
    </div>

    <!-- Health Check Button -->
    <button
      @click="runHealthCheck"
      class="px-3 py-1.5 text-sm bg-white border rounded hover:bg-gray-50 flex items-center gap-1"
      :class="healthCheckClass"
      :disabled="checkingHealth"
    >
      <span v-if="checkingHealth">⏳</span>
      <span v-else>✅</span>
      Health Check
    </button>

    <!-- Divider -->
    <div class="h-6 w-px bg-gray-300"></div>

    <!-- Keyboard Shortcuts Help -->
    <button
      @click="showShortcuts = !showShortcuts"
      class="px-3 py-1.5 text-sm bg-white border rounded hover:bg-gray-50"
      title="Keyboard Shortcuts"
    >
      ⌨️
    </button>
  </div>

  <!-- Health Check Results Modal -->
  <div
    v-if="healthResults"
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    @click="healthResults = null"
  >
    <div
      class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      @click.stop
    >
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Content Health Check</h2>
          <button
            @click="healthResults = null"
            class="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <!-- Overall Score -->
        <div class="mb-6 p-4 rounded-lg" :class="getScoreClass(healthResults.overall_score)">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">Overall Score</div>
              <div class="text-3xl font-bold">{{ healthResults.overall_score }}/100</div>
            </div>
            <div class="text-4xl">
              {{ healthResults.overall_score >= 80 ? '✅' : healthResults.overall_score >= 60 ? '⚠️' : '❌' }}
            </div>
          </div>
        </div>

        <!-- Individual Checks -->
        <div class="space-y-4">
          <div
            v-for="(check, name) in healthResults.checks"
            :key="name"
            class="border rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold capitalize">{{ name.replace('_', ' ') }}</h3>
              <span class="text-sm font-medium" :class="getScoreTextClass(check.score)">
                {{ check.score }}/100
              </span>
            </div>
            <div v-if="check.suggestions && check.suggestions.length" class="mt-2">
              <div
                v-for="(suggestion, idx) in check.suggestions"
                :key="idx"
                class="text-sm text-gray-600 mb-1"
              >
                • {{ suggestion }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Keyboard Shortcuts Modal -->
  <div
    v-if="showShortcuts"
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    @click="showShortcuts = false"
  >
    <div
      class="bg-white rounded-lg max-w-md w-full"
      @click.stop
    >
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Keyboard Shortcuts</h2>
          <button
            @click="showShortcuts = false"
            class="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span><kbd>Ctrl</kbd> + <kbd>S</kbd></span>
            <span>Save</span>
          </div>
          <div class="flex justify-between">
            <span><kbd>Ctrl</kbd> + <kbd>B</kbd></span>
            <span>Bold</span>
          </div>
          <div class="flex justify-between">
            <span><kbd>Ctrl</kbd> + <kbd>I</kbd></span>
            <span>Italic</span>
          </div>
          <div class="flex justify-between">
            <span><kbd>Ctrl</kbd> + <kbd>K</kbd></span>
            <span>Insert Link</span>
          </div>
          <div class="flex justify-between">
            <span><kbd>Ctrl</kbd> + <kbd>H</kbd></span>
            <span>Health Check</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import blogPagesAPI from '@/api/blog-pages'

const props = defineProps({
  websiteId: {
    type: [String, Number],
    required: true
  },
  contentType: {
    type: String,
    default: 'blog_post' // or 'service_page'
  },
  editorInstance: {
    type: Object,
    default: null
  },
  currentContent: {
    type: String,
    default: ''
  },
  metaTitle: {
    type: String,
    default: ''
  },
  metaDescription: {
    type: String,
    default: ''
  },
  slug: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['content-inserted', 'template-applied', 'health-check'])

const showTemplates = ref(false)
const showSnippets = ref(false)
const showBlocks = ref(false)
const showShortcuts = ref(false)
const templates = ref([])
const snippets = ref([])
const blocks = ref([])
const loadingTemplates = ref(false)
const loadingSnippets = ref(false)
const loadingBlocks = ref(false)
const templateSearch = ref('')
const snippetSearch = ref('')
const blockTypeFilter = ref('')
const healthResults = ref(null)
const checkingHealth = ref(false)

const healthCheckClass = computed(() => {
  if (checkingHealth.value) return 'opacity-50 cursor-wait'
  if (healthResults.value) {
    const score = healthResults.value.overall_score
    if (score >= 80) return 'bg-green-50 border-green-300'
    if (score >= 60) return 'bg-yellow-50 border-yellow-300'
    return 'bg-red-50 border-red-300'
  }
  return ''
})

const loadTemplates = async () => {
  if (!props.websiteId) return
  
  loadingTemplates.value = true
  try {
    const res = await blogPagesAPI.getQuickTemplates({
      website_id: props.websiteId,
      template_type: props.contentType
    })
    templates.value = res.data || []
  } catch (e) {
    console.error('Failed to load templates:', e)
  } finally {
    loadingTemplates.value = false
  }
}

const searchTemplates = async () => {
  // Implement search if needed
  await loadTemplates()
}

const loadSnippets = async () => {
  if (!props.websiteId) return
  
  loadingSnippets.value = true
  try {
    const res = await blogPagesAPI.getQuickSnippets({
      website_id: props.websiteId,
      search: snippetSearch.value
    })
    snippets.value = res.data || []
  } catch (e) {
    console.error('Failed to load snippets:', e)
  } finally {
    loadingSnippets.value = false
  }
}

const searchSnippets = async () => {
  await loadSnippets()
}

const loadBlocks = async () => {
  if (!props.websiteId) return
  
  loadingBlocks.value = true
  try {
    const res = await blogPagesAPI.getQuickBlocks({
      website_id: props.websiteId,
      block_type: blockTypeFilter.value || undefined
    })
    blocks.value = res.data || []
  } catch (e) {
    console.error('Failed to load blocks:', e)
  } finally {
    loadingBlocks.value = false
  }
}

const insertTemplate = async (template) => {
  try {
    // Apply template to create new content
    const res = await blogPagesAPI.instantiateTemplate(template.id, {
      target: props.contentType,
      website_id: props.websiteId
    })
    
    // Track template usage
    emit('template-used', { template_id: template.id, template_name: template.name })
    emit('template-applied', res.data)
    showTemplates.value = false
  } catch (e) {
    console.error('Failed to apply template:', e)
    alert('Failed to apply template. Please try again.')
  }
}

const insertSnippet = async (snippet) => {
  try {
    const quill = props.editorInstance
    if (!quill) {
      alert('Editor instance not available')
      return
    }
    
    const range = quill.getSelection(true)
    const cursorPos = range ? range.index : quill.getLength()
    
    const res = await blogPagesAPI.insertSnippet({
      snippet_id: snippet.id,
      current_content: props.currentContent,
      cursor_position: cursorPos,
      format: 'html'
    })
    
    // Insert into editor
    quill.root.innerHTML = res.data.content
    quill.setSelection(res.data.new_cursor_position, 0)
    
    emit('content-inserted', {
      type: 'snippet',
      snippet: res.data.snippet
    })
    emit('snippet-used', { snippet_id: snippet.id, snippet_name: snippet.name })
    showSnippets.value = false
  } catch (e) {
    console.error('Failed to insert snippet:', e)
    alert('Failed to insert snippet. Please try again.')
  }
}

const insertBlock = async (block) => {
  try {
    const quill = props.editorInstance
    if (!quill) {
      alert('Editor instance not available')
      return
    }
    
    const range = quill.getSelection(true)
    const cursorPos = range ? range.index : quill.getLength()
    
    const res = await blogPagesAPI.insertBlock({
      block_id: block.id,
      current_content: props.currentContent,
      cursor_position: cursorPos
    })
    
    // Insert into editor
    quill.root.innerHTML = res.data.content
    quill.setSelection(res.data.new_cursor_position, 0)
    
    emit('content-inserted', {
      type: 'block',
      block: res.data.block
    })
    emit('block-used', { block_id: block.id, block_name: block.name })
    showBlocks.value = false
  } catch (e) {
    console.error('Failed to insert block:', e)
    alert('Failed to insert block. Please try again.')
  }
}

const runHealthCheck = async () => {
  checkingHealth.value = true
  try {
    const res = await blogPagesAPI.healthCheck({
      title: props.metaTitle || '',
      meta_title: props.metaTitle || '',
      meta_description: props.metaDescription || '',
      content: props.currentContent || '',
      slug: props.slug || '',
      min_words: 300
    })
    
    healthResults.value = res.data
    emit('health-check', res.data)
    emit('health-check-run', { score: res.data.overall_score })
  } catch (e) {
    console.error('Failed to run health check:', e)
    alert('Failed to run health check. Please try again.')
  } finally {
    checkingHealth.value = false
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'bg-green-50 border-green-200'
  if (score >= 60) return 'bg-yellow-50 border-yellow-200'
  return 'bg-red-50 border-red-200'
}

const getScoreTextClass = (score) => {
  if (score >= 80) return 'text-green-700'
  if (score >= 60) return 'text-yellow-700'
  return 'text-red-700'
}

// Close dropdowns when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.editor-toolbar')) {
    showTemplates.value = false
    showSnippets.value = false
    showBlocks.value = false
  }
}

watch(() => props.websiteId, () => {
  if (props.websiteId) {
    loadTemplates()
    loadSnippets()
    loadBlocks()
  }
})

watch(showTemplates, (val) => {
  if (val) loadTemplates()
})

watch(showSnippets, (val) => {
  if (val) loadSnippets()
})

watch(showBlocks, (val) => {
  if (val) loadBlocks()
})

onMounted(() => {
  if (props.websiteId) {
    loadTemplates()
    loadSnippets()
    loadBlocks()
  }
  document.addEventListener('click', handleClickOutside)
})

// Cleanup
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
kbd {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  font-family: monospace;
}
</style>

