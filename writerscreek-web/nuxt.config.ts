export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-09',

  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        '/',
        '/about',
        '/apply',
        '/how-it-works',
        '/earnings',
        '/blog',
        '/faq',
        '/contact',
        '/login',
        '/legal/privacy',
        '/legal/terms',
        '/legal/refunds',
      ],
      failOnError: true,
    },
    devProxy: {
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: false,
      },
      '/api/v2': {
        target: 'http://localhost:8000/api/v2',
        changeOrigin: false,
      },
      '/cms-api': {
        target: 'http://localhost:8000/cms-api',
        changeOrigin: false,
      },
    },
  },

  site: {
    url: 'https://writerscreek.com',
    name: 'Writers Creek',
  },

  sitemap: {
    exclude: ['/login', '/auth/**'],
  },

  runtimeConfig: {
    public: {
      apiBase: '',
      appUrl: '',        // writer portal  — https://app.writerscreek.com
      staffUrl: '',      // staff portal   — https://admin.writerscreek.com
      siteUrl: 'https://writerscreek.com',
    },
  },

  components: [
    { path: '~/components/layout', prefix: '' },
    { path: '~/components/marketing', prefix: '' },
    { path: '~/components/ui', prefix: '' },
    { path: '~/components/privacy', prefix: '' },
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
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
        },
      ],
    },
  },
})
