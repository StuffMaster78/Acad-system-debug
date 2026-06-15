<script setup lang="ts">
const popup = useExitPopup()
const cfg = computed(() => popup.config.value)

onMounted(() => {
  popup.init()
})
</script>

<template>
  <Teleport to="body">
    <div v-if="popup.open.value && cfg" class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/55 px-4">
      <div class="relative w-full max-w-md rounded-lg bg-white p-6 shadow-2xl">
        <button class="absolute right-3 top-3 rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" type="button" aria-label="Close" @click="popup.dismiss()">x</button>
        <img v-if="cfg.image_url" :src="cfg.image_url" alt="" class="mb-4 h-32 w-full rounded-md object-cover">
        <p class="text-xl font-bold text-slate-950">{{ cfg.title }}</p>
        <p class="mt-2 text-sm leading-6 text-slate-600">{{ cfg.body }}</p>
        <div class="mt-5 flex flex-col gap-2 sm:flex-row sm:justify-end">
          <button v-if="cfg.secondary_cta_label" class="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" type="button" @click="popup.dismiss()">{{ cfg.secondary_cta_label }}</button>
          <NuxtLink class="rounded-md bg-slate-950 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-slate-800" :to="cfg.primary_cta_url || '/quote'" @click="popup.dismiss()">{{ cfg.primary_cta_label || 'Continue' }}</NuxtLink>
        </div>
      </div>
    </div>
  </Teleport>
</template>
