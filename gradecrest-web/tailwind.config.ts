import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

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
        // Deep forest green — hero and dark sections
        forest: {
          950: '#052e16',
          900: '#0a2e1a',
          800: '#14532d',
          700: '#166534',
          600: '#15803d',
        },
        // Primary green — CTAs, highlights, links (replaces indigo gc-*)
        gc: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        // Gold — headline accents, trust badges, stars
        gold: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        // brand alias — lets shared components work without per-site forks
        brand: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        // Warm cream — light section backgrounds (replaces cold mist)
        cream: {
          50:  '#fffef7',
          100: '#fefce8',
          200: '#fef9c3',
        },
        // Amber — deeper gold tones for gradients and hover states
        amber: {
          50:  '#fffbeb',
          100: '#fef3c7',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
        },
        // Emerald — bridge tint used sparingly for icons and tags
        emerald: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
        },
        // Surface neutrals
        ink:      '#0f172a',
        graphite: '#475569',
        mist:     '#fafaf7',
      },
      boxShadow: {
        card: '0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04)',
        lift: '0 4px 16px rgba(15,23,42,0.10), 0 2px 4px rgba(15,23,42,0.06)',
        glow: '0 0 0 3px rgba(22,163,74,0.25)',
      },
      backgroundImage: {
        // Gold dot grid — used in dark hero sections
        'hero-grid': `radial-gradient(rgba(251,191,36,0.08) 1.5px, transparent 1.5px)`,
      },
      backgroundSize: {
        'grid-40': '28px 28px',
      },
    },
  },
  plugins: [typography],
} satisfies Config
