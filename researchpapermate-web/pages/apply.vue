<script setup lang="ts">
const app = useAppUrl()

const perks = [
  { icon: 'dollar-sign', color: 'bg-green-100 text-green-600', title: 'Competitive pay',  desc: 'Earn up to $50 per page based on your level and performance.' },
  { icon: 'clock',       color: 'bg-amber-100 text-amber-600', title: 'Flexible hours',   desc: 'Work when you want. Accept only the orders that suit you.' },
  { icon: 'trending-up', color: 'bg-brand-100 text-brand-600', title: 'Grow your rating', desc: 'Build your reputation and unlock higher-paying order tiers.' },
]

useSeoMeta({
  title: 'Apply as a Writer',
  description: 'Join our team of expert academic writers. Apply online — flexible work, competitive pay.',
})
</script>

<template>
  <div class="section max-w-3xl text-center">
    <h1 class="section-heading">Write with Us</h1>
    <p class="section-sub">
      Join hundreds of expert writers earning competitive pay on their own schedule.
    </p>

    <div class="mt-12 grid gap-6 text-left sm:grid-cols-3">
      <div v-for="perk in perks" :key="perk.title" class="card text-center">
        <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl" :class="perk.color.split(' ')[0]">
          <Icon :name="perk.icon" class="h-6 w-6" :class="perk.color.split(' ')[1]" />
        </div>
        <h3 class="font-semibold text-slate-900">{{ perk.title }}</h3>
        <p class="mt-2 text-sm text-slate-500">{{ perk.desc }}</p>
      </div>
    </div>

    <a :href="app.apply" class="btn-primary mt-12 px-10 py-4 text-base">
      Start your application
    </a>
  </div>
</template>
