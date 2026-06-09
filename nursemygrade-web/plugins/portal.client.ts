export default defineNuxtPlugin(async () => {
  const store = usePortalStore()
  await store.fetch()
})
