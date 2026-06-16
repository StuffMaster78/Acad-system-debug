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
          50:  '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',  // accent sky-400
          500: '#0ea5e9',
          600: '#0284c7',  // primary CTA
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        ink:      '#0f172a',
        graphite: '#475569',
        mist:     '#f8fafc',
      },
      backgroundImage: {
        'hero-grid': `radial-gradient(rgba(56,189,248,0.07) 1.5px, transparent 1.5px)`,
      },
      backgroundSize: {
        'grid-28': '28px 28px',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config
