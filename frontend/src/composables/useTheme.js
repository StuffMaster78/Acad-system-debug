import { ref, computed, onMounted } from 'vue'

const theme = ref('system') // 'light' | 'dark' | 'system'
const initialized = ref(false)

const prefersDark = () =>
  typeof window !== 'undefined' &&
  window.matchMedia &&
  window.matchMedia('(prefers-color-scheme: dark)').matches

const applyTheme = (value) => {
  if (typeof document === 'undefined') return
  const root = document.documentElement

  const effectiveDark =
    value === 'dark' || (value === 'system' && prefersDark())

  if (effectiveDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

export const initTheme = () => {
  if (initialized.value) return
  initialized.value = true

  try {
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      theme.value = stored
    } else {
      theme.value = 'system'
    }
  } catch {
    theme.value = 'system'
  }

  applyTheme(theme.value)

  if (typeof window !== 'undefined' && window.matchMedia) {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', () => {
      if (theme.value === 'system') {
        applyTheme(theme.value)
      }
    })
  }
}

export function useTheme() {
  if (!initialized.value) {
    initTheme()
  }

  const setTheme = (value) => {
    if (!['light', 'dark', 'system'].includes(value)) return
    theme.value = value
    try {
      localStorage.setItem('theme', value)
    } catch {
      // ignore
    }
    applyTheme(value)
  }

  const isDark = computed(() => {
    if (theme.value === 'dark') return true
    if (theme.value === 'light') return false
    return prefersDark()
  })

  const toggleTheme = () => {
    setTheme(isDark.value ? 'light' : 'dark')
  }

  onMounted(() => {
    if (!initialized.value) {
      initTheme()
    }
  })

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
  }
}


