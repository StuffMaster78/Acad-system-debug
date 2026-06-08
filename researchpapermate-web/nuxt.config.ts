export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],

  // SSG: pnpm build → .output/public/ → serve with nginx
  nitro: {
    prerender: {
      crawlLinks: true,
      routes: ['/', '/services', '/pricing', '/blog', '/contact', '/apply', '/login', '/register', '/auth/magic-link'],
      failOnError: false,
    },
    // Dev: proxy /api/v1/* to Django so the Host header is localhost:3000
    // (matches the Website/PortalDefinition records seeded for local dev).
    // Production: nginx handles this — API calls go to api.researchpapermate.com.
    devProxy: {
      // Nitro strips the matched prefix, then appends remainder to target.
      // /api/v1/portal-context/ → strips /api/v1 → appends /portal-context/ → http://localhost:8000/api/v1/portal-context/
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: false, // keeps Host: localhost:3000 so Django resolves the right tenant
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: '',   // override with NUXT_PUBLIC_API_BASE in .env
      appUrl: '',    // override with NUXT_PUBLIC_APP_URL in .env
      siteUrl: 'https://researchpapermate.com',
    },
  },

  components: [
    { path: '~/components/layout', prefix: '' },
    { path: '~/components/marketing', prefix: '' },
    { path: '~/components', prefix: '' },
  ],

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:wght@700&display=swap',
        },
      ],
    },
  },
})
