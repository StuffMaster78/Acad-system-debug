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
        serif: ['DM Serif Display', 'Georgia', 'ui-serif'],
      },
      colors: {
        // Deep claret / burgundy — primary brand colour
        claret: {
          50:  '#fdf2f6',
          100: '#fce4ee',
          200: '#f9c8dc',
          300: '#f49dbe',
          400: '#ec638e',
          500: '#de3766',
          600: '#c41f50',
          700: '#9e1540',
          800: '#7B2241',
          900: '#5C1A38',
          950: '#3D1025',
        },
        // Aged amber / copper — accent, CTAs, stars
        amber: {
          50:  '#fefbf0',
          100: '#fdf3d0',
          200: '#fae59f',
          300: '#f6cf5a',
          400: '#f2b828',
          500: '#e09f10',
          600: '#C8792A',
          700: '#a35f1f',
          800: '#854c1c',
          900: '#6d3f1c',
        },
        // Warm parchment backgrounds
        parchment: {
          50:  '#FDFAF4',
          100: '#FBF6EF',
          200: '#F5EDE1',
          300: '#EDE0CE',
          400: '#DFD0B8',
        },
        // Ink — near-black with warm undertone
        ink: {
          DEFAULT: '#1A1017',
          secondary: '#4A3840',
          muted: '#8A7075',
        },
        // Alias 'brand' so shared components (nav, forms) work without forking
        brand: {
          50:  '#fdf2f6',
          100: '#fce4ee',
          200: '#f9c8dc',
          300: '#f49dbe',
          400: '#ec638e',
          500: '#c41f50',
          600: '#9e1540',
          700: '#7B2241',
          800: '#5C1A38',
          900: '#3D1025',
        },
      },
      backgroundImage: {
        'claret-grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config
