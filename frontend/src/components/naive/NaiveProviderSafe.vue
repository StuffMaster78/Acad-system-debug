<template>
  <NConfigProvider v-if="ready" :theme="currentTheme" :theme-overrides="themeOverrides">
    <slot />
  </NConfigProvider>
  <div v-else>
    <slot />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { NConfigProvider } from 'naive-ui'
import { useTheme } from '@/composables/useTheme'
import { lightTheme, darkTheme } from '@/plugins/naive-ui'

const ready = ref(false)

onMounted(() => {
  try {
    ready.value = true
  } catch (error) {
    console.error('Naive UI Provider error:', error)
    ready.value = false
  }
})

// Get theme - this will initialize if needed
let isDark = computed(() => false)
try {
  const { isDark: themeIsDark } = useTheme()
  isDark = themeIsDark
} catch (error) {
  console.warn('Theme not available, using light theme:', error)
}

const currentTheme = computed(() => {
  try {
    return isDark.value ? darkTheme : lightTheme
  } catch (error) {
    return lightTheme
  }
})

const themeOverrides = {
  Button: {
    borderRadius: '0.5rem',
    fontWeightStrong: '600',
  },
  Input: {
    borderRadius: '0.5rem',
  },
  Card: {
    borderRadius: '0.75rem',
    paddingMedium: '24px',
  },
  Modal: {
    borderRadius: '0.75rem',
  },
  DataTable: {
    borderRadius: '0.5rem',
  },
  Select: {
    borderRadius: '0.5rem',
  },
  Dropdown: {
    borderRadius: '0.5rem',
  },
}
</script>

