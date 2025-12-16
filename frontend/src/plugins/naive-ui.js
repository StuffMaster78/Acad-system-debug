/**
 * Naive UI Configuration
 * 
 * Configures Naive UI to work seamlessly with Tailwind CSS
 * and the existing theme system (light/dark mode)
 */

import naive from 'naive-ui'
import { create } from 'naive-ui'

// Theme configuration that syncs with Tailwind
const lightTheme = create({
  common: {
    primaryColor: '#3b82f6', // primary-500
    primaryColorHover: '#2563eb', // primary-600
    primaryColorPressed: '#1d4ed8', // primary-700
    primaryColorSuppl: '#60a5fa', // primary-400
    borderRadius: '0.5rem', // rounded-lg
    borderRadiusSmall: '0.375rem', // rounded-md
    fontSize: '14px',
    fontSizeSmall: '12px',
    fontSizeLarge: '16px',
    fontSizeHuge: '18px',
    heightSmall: '32px',
    heightMedium: '36px',
    heightLarge: '40px',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  light: {
    baseColor: '#ffffff',
    textColor1: '#111827', // gray-900
    textColor2: '#374151', // gray-700
    textColor3: '#6b7280', // gray-500
    borderColor: '#e5e7eb', // gray-200
    cardColor: '#ffffff',
    modalColor: '#ffffff',
    popoverColor: '#ffffff',
    tableColor: '#ffffff',
    tableHeaderColor: '#f9fafb', // gray-50
    hoverColor: '#f3f4f6', // gray-100
  },
})

const customDarkTheme = create({
  common: {
    primaryColor: '#60a5fa', // primary-400 (lighter for dark mode)
    primaryColorHover: '#3b82f6', // primary-500
    primaryColorPressed: '#2563eb', // primary-600
    primaryColorSuppl: '#93c5fd', // primary-300
    borderRadius: '0.5rem',
    borderRadiusSmall: '0.375rem',
    fontSize: '14px',
    fontSizeSmall: '12px',
    fontSizeLarge: '16px',
    fontSizeHuge: '18px',
    heightSmall: '32px',
    heightMedium: '36px',
    heightLarge: '40px',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  dark: {
    baseColor: '#0a0a0a',
    textColor1: '#f9fafb', // gray-50
    textColor2: '#e5e7eb', // gray-200
    textColor3: '#9ca3af', // gray-400
    borderColor: '#374151', // gray-700
    cardColor: '#1a1a1a',
    modalColor: '#1a1a1a',
    popoverColor: '#1a1a1a',
    tableColor: '#1a1a1a',
    tableHeaderColor: '#0f0f0f',
    hoverColor: '#374151', // gray-700
  },
})

/**
 * Setup Naive UI with theme support
 * @param {import('vue').App} app - Vue app instance
 */
export function setupNaiveUI(app) {
  // Global component config
  const configProviderProps = {
    theme: null, // Will be set reactively in components
    themeOverrides: {
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
    },
  }

  // Use Naive UI
  app.use(naive, configProviderProps)
  
  // Export themes for use in components
  app.config.globalProperties.$naiveThemes = {
    light: lightTheme,
    dark: customDarkTheme,
  }
}

// Export themes for direct use
export { lightTheme, customDarkTheme as darkTheme }

/**
 * Naive UI components can be imported individually for tree-shaking
 * Example: import { NButton, NInput } from 'naive-ui'
 * 
 * Or use globally (already registered via app.use(naive))
 * Components are prefixed with 'N' (e.g., NButton, NInput, NModal)
 */

