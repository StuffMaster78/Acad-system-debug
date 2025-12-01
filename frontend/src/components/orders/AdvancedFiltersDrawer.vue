<template>
  <transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex"
      @keydown.esc.prevent="close"
    >
      <div class="flex-1 bg-black/30" @click="close"></div>
      <div class="w-full max-w-xl bg-white dark:bg-gray-900 shadow-2xl p-6 overflow-y-auto">
        <div class="flex items-start justify-between mb-6">
          <div>
            <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">Advanced Filters</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">Fine-tune your query with more conditions.</p>
          </div>
          <button
            class="text-gray-400 hover:text-gray-600"
            @click="close"
            aria-label="Close advanced filters"
          >
            ✕
          </button>
        </div>

        <form class="space-y-8" @submit.prevent="apply">
          <section class="space-y-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">
              Date Ranges
            </h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Created From</label>
                <input type="date" v-model="localFilters.created_from" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Created To</label>
                <input type="date" v-model="localFilters.created_to" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deadline From</label>
                <input type="date" v-model="localFilters.deadline_from" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deadline To</label>
                <input type="date" v-model="localFilters.deadline_to" class="form-input w-full" />
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">
              Amount & Scope
            </h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Price Min</label>
                <input type="number" step="0.01" min="0" v-model="localFilters.price_min" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Price Max</label>
                <input type="number" step="0.01" min="0" v-model="localFilters.price_max" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pages Min</label>
                <input type="number" min="0" v-model="localFilters.pages_min" class="form-input w-full" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pages Max</label>
                <input type="number" min="0" v-model="localFilters.pages_max" class="form-input w-full" />
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">
              Order Attributes
            </h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject</label>
                <select v-model="localFilters.subject_id" class="form-select w-full">
                  <option value="">Any subject</option>
                  <option v-for="subject in subjectOptions" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Paper Type</label>
                <select v-model="localFilters.paper_type_id" class="form-select w-full">
                  <option value="">Any paper type</option>
                  <option v-for="paper in paperTypes" :key="paper.id" :value="paper.id">
                    {{ paper.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Academic Level</label>
                <select v-model="localFilters.academic_level_id" class="form-select w-full">
                  <option value="">Any level</option>
                  <option v-for="level in academicLevels" :key="level.id" :value="level.id">
                    {{ level.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type of Work</label>
                <select v-model="localFilters.type_of_work_id" class="form-select w-full">
                  <option value="">Any type</option>
                  <option v-for="type in typesOfWork" :key="type.id" :value="type.id">
                    {{ type.name }}
                  </option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Flags</label>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="flag in flagOptions"
                  :key="flag.value"
                  class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm cursor-pointer"
                  :class="localFilters.flags.includes(flag.value) ? 'bg-primary-50 border-primary-400 text-primary-800' : 'border-gray-200 text-gray-600'"
                >
                  <input
                    type="checkbox"
                    :value="flag.value"
                    v-model="localFilters.flags"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {{ flag.label }}
                </label>
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">
              Participants
            </h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Writer</label>
                <input
                  type="text"
                  v-model="localFilters.writer_query"
                  placeholder="Name, email, or ID"
                  class="form-input w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Client</label>
                <input
                  type="text"
                  v-model="localFilters.client_query"
                  placeholder="Name, email, or ID"
                  class="form-input w-full"
                />
              </div>
            </div>
            <div class="flex items-center gap-4">
              <label class="inline-flex items-center gap-2">
                <input type="checkbox" v-model="localFilters.include_archived" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span class="text-sm text-gray-700 dark:text-gray-300">Include archived</span>
              </label>
              <label class="inline-flex items-center gap-2">
                <input type="checkbox" v-model="localFilters.only_archived" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span class="text-sm text-gray-700 dark:text-gray-300">Only archived</span>
              </label>
            </div>
          </section>

          <div class="flex items-center justify-between pt-4 border-t">
            <button
              type="button"
              class="text-sm text-gray-500 hover:text-gray-700"
              @click="reset"
            >
              Reset all
            </button>
            <div class="flex items-center gap-3">
              <button
                type="button"
                class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                @click="close"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, watch, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    required: true
  },
  flagOptions: {
    type: Array,
    default: () => []
  },
  subjectOptions: {
    type: Array,
    default: () => []
  },
  paperTypes: {
    type: Array,
    default: () => []
  },
  academicLevels: {
    type: Array,
    default: () => []
  },
  typesOfWork: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'apply', 'reset'])

const cloneFilters = (value) => JSON.parse(JSON.stringify(value || {}))

const localFilters = ref(cloneFilters(props.filters))

watch(
  () => props.filters,
  (next) => {
    localFilters.value = cloneFilters(next)
  },
  { deep: true }
)

const close = () => emit('update:modelValue', false)

const apply = () => {
  emit('apply', cloneFilters(localFilters.value))
}

const reset = () => emit('reset')
</script>

<style scoped>
@reference "tailwindcss";

.form-input,
.form-select {
  @apply border border-gray-300 rounded-lg px-3 py-2 focus:outline-none;
}

.form-input:focus,
.form-select:focus {
  /* Use CSS custom properties for primary colors since @reference doesn't include theme */
  box-shadow: 0 0 0 2px var(--color-primary-500);
  border-color: var(--color-primary-500);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

