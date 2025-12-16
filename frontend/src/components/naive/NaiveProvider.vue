<template>
  <NConfigProvider :theme="currentTheme" :theme-overrides="themeOverrides">
    <slot />
  </NConfigProvider>
</template>

<script setup>
import { computed } from 'vue'
import { NConfigProvider } from 'naive-ui'
import { useTheme } from '@/composables/useTheme'
import { lightTheme, darkTheme } from '@/plugins/naive-ui'

// Get theme - this will initialize if needed
const { isDark } = useTheme()

const currentTheme = computed(() => {
  return isDark.value ? darkTheme : lightTheme
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

