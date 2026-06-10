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
        sans: ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        // Primary — deep navy (hero, dark sections)
        navy: {
          950: '#020617',
          900: '#0c1629',
          800: '#111f3a',
          700: '#1a2f52',
          600: '#1e3a6e',
        },
        // Accent — indigo (CTAs, highlights)
        gc: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        // Surface neutrals
        ink:      '#0f172a',
        graphite: '#475569',
        mist:     '#f8fafc',
      },
      boxShadow: {
        card: '0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04)',
        lift: '0 4px 16px rgba(15,23,42,0.10), 0 2px 4px rgba(15,23,42,0.06)',
        glow: '0 0 0 3px rgba(99,102,241,0.25)',
      },
      backgroundImage: {
        'hero-grid': `
          linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
        `,
      },
      backgroundSize: {
        'grid-40': '40px 40px',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config
