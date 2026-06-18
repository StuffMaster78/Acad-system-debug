export default defineNuxtPlugin(() => {
  const store = usePortalStore()
  onNuxtReady(() => void store.fetch())
})
