import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.ts',
    './app.vue',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans:  ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui'],
        serif: ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        brand: {
          50:  '#eef4ff',
          100: '#dde9ff',
          200: '#bbd3ff',
          300: '#93b8ff',
          500: '#2563c8',
          600: '#1d4fa8',
          700: '#163e88',
          800: '#112f6a',
          900: '#0d2455',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config
