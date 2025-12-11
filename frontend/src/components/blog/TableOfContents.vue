<template>
  <div v-if="toc && toc.length > 0" class="table-of-contents">
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-8">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <h2 class="text-lg font-bold text-blue-900 dark:text-blue-100">Table of Contents</h2>
      </div>
      
      <nav class="space-y-1">
        <a
          v-for="(item, index) in toc"
          :key="index"
          :href="`#${item.id}`"
          @click.prevent="scrollToHeading(item.id)"
          :class="[
            'block py-2 px-3 rounded-lg transition-all duration-200 hover:bg-blue-100 dark:hover:bg-blue-900/40',
            getHeadingClass(item.level),
            activeHeading === item.id ? 'bg-blue-200 dark:bg-blue-800 font-semibold text-blue-900 dark:text-blue-100' : 'text-blue-700 dark:text-blue-300'
          ]"
        >
          <span class="flex items-center">
            <span class="flex-1">{{ item.text }}</span>
            <svg v-if="activeHeading === item.id" class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </span>
        </a>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  toc: {
    type: Array,
    default: () => []
  }
})

const activeHeading = ref(null)

const getHeadingClass = (level) => {
  const classes = {
    'h2': 'text-base font-semibold',
    'h3': 'text-sm font-medium ml-4',
    'h4': 'text-sm ml-8',
    'h5': 'text-xs ml-12',
    'h6': 'text-xs ml-16'
  }
  return classes[level] || 'text-sm'
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const offset = 100 // Offset for fixed headers
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - offset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })

    // Update URL without triggering scroll
    history.pushState(null, null, `#${id}`)
    
    // Update active heading
    activeHeading.value = id
  }
}

const updateActiveHeading = () => {
  const headings = props.toc.map(item => ({
    id: item.id,
    element: document.getElementById(item.id)
  })).filter(h => h.element)

  if (headings.length === 0) return

  const scrollPosition = window.scrollY + 150 // Offset for fixed headers

  // Find the current active heading based on scroll position
  let current = null
  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i]
    if (heading.element && heading.element.offsetTop <= scrollPosition) {
      current = heading.id
      break
    }
  }

  activeHeading.value = current || headings[0]?.id
}

const handleScroll = () => {
  updateActiveHeading()
}

const handleHashChange = () => {
  const hash = window.location.hash.slice(1)
  if (hash && props.toc.some(item => item.id === hash)) {
    activeHeading.value = hash
    // Small delay to ensure content is rendered
    setTimeout(() => {
      scrollToHeading(hash)
    }, 100)
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('hashchange', handleHashChange)
  
  // Check for initial hash
  handleHashChange()
  
  // Initial active heading update
  updateActiveHeading()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('hashchange', handleHashChange)
})
</script>

<style scoped>
.table-of-contents a {
  text-decoration: none;
}

.table-of-contents a:hover {
  transform: translateX(2px);
}
</style>

