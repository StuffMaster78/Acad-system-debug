<script setup lang="ts">
useSeoMeta({
  title: 'Free Title Page Generator — APA, MLA, Chicago | EssayManiacs',
  description: 'Generate a properly formatted title page for APA 7, MLA 9, or Chicago style and download it as a Word .doc file. Free, instant, no sign-up.',
})

type FormatStyle = 'apa7' | 'mla9' | 'chicago'

const formatStyle = ref<FormatStyle>('apa7')

// Get today's date formatted per style
function todayFormatted(style: FormatStyle): string {
  const d = new Date()
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December']
  if (style === 'mla9') {
    return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`
  }
  if (style === 'chicago') {
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
  }
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
}

const paperTitle = ref('')
const authorName = ref('')
const institution = ref('')
const courseName = ref('')
const instructorName = ref('')
const paperDate = ref(todayFormatted('apa7'))
const runningHead = ref('')

const charCount = computed(() => paperTitle.value.length)

// Update date format when style changes
watch(formatStyle, (s) => {
  paperDate.value = todayFormatted(s)
})

const styles = [
  { value: 'apa7' as FormatStyle,    label: 'APA 7', desc: 'Student paper format' },
  { value: 'mla9' as FormatStyle,    label: 'MLA 9', desc: 'Block header, centered title' },
  { value: 'chicago' as FormatStyle, label: 'Chicago', desc: 'Title-centered layout' },
]

// ── Word download ──────────────────────────────────────────────────────────
function generateTitlePageHTML(): string {
  const title = paperTitle.value.trim() || 'Paper Title'
  const author = authorName.value.trim() || 'Author Name'
  const course = courseName.value.trim() || 'Course Name and Number'
  const instructor = instructorName.value.trim() || 'Instructor Name'
  const inst = institution.value.trim() || 'Institution'
  const date = paperDate.value.trim()
  const rh = runningHead.value.trim().toUpperCase() || 'SHORTENED TITLE'

  if (formatStyle.value === 'apa7') {
    return `
      <div class="right" style="margin-bottom:0">Running head: ${rh}</div>
      <p style="text-align:right;margin:0">Page 1</p>
      <br><br><br><br><br>
      <div class="center">
        <p style="font-weight:bold">${title}</p>
        <p>${author}</p>
        <p>${inst}</p>
        <p>${course}</p>
        <p>${instructor}</p>
        <p>${date}</p>
      </div>`
  }
  if (formatStyle.value === 'mla9') {
    return `
      <div style="text-align:right">
        <p style="margin:0">${author}</p>
        <p style="margin:0">${instructor}</p>
        <p style="margin:0">${course}</p>
        <p style="margin:0">${date}</p>
      </div>
      <br><br>
      <div class="center">
        <p style="font-weight:bold">${title}</p>
      </div>`
  }
  // Chicago
  return `
    <br><br><br>
    <div class="center">
      <p style="font-weight:bold">${title}</p>
    </div>
    <br><br><br><br><br><br><br>
    <div class="center">
      <p>${author}</p>
      <p>${course}</p>
      <p>${inst}</p>
      <p>${date}</p>
    </div>`
}

function downloadWord() {
  const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
<head><meta charset="utf-8">
<style>
  @page { margin: 1in; size: letter; }
  body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 2; }
  .center { text-align: center; }
  .right { text-align: right; }
  p { margin: 0; }
</style></head>
<body>${generateTitlePageHTML()}</body></html>`

  const blob = new Blob(['﻿', html], { type: 'application/msword' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'title-page.doc'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-6xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Title Page Generator</span>
      </nav>
    </div>

    <div class="max-w-6xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Title Page Generator</h1>
      <p class="text-slate-500 text-sm">Generate a properly formatted title page and download it as a Word document.</p>
    </div>

    <div class="max-w-6xl mx-auto px-4 pb-16 flex flex-col lg:flex-row gap-6">
      <!-- Left: Form -->
      <div class="flex-1 space-y-6 min-w-0">

        <!-- Style selector -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Formatting Style</h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <label
              v-for="s in styles"
              :key="s.value"
              :class="[
                'flex items-start gap-3 rounded-xl border-2 p-4 cursor-pointer transition-all',
                formatStyle === s.value
                  ? 'border-brand-500 bg-brand-50'
                  : 'border-slate-200 hover:border-brand-200'
              ]"
            >
              <input type="radio" :value="s.value" v-model="formatStyle" class="mt-0.5 accent-brand-600" />
              <div>
                <div class="font-bold text-sm text-slate-800">{{ s.label }}</div>
                <div class="text-xs text-slate-500 mt-0.5">{{ s.desc }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Fields -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">

          <!-- Running head (APA only) -->
          <div v-if="formatStyle === 'apa7'">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Running Head
              <span class="text-slate-400 font-normal text-xs">(optional — abbreviated title, all caps)</span>
            </label>
            <input
              v-model="runningHead"
              type="text"
              placeholder="e.g. SOCIAL MEDIA AND MENTAL HEALTH"
              maxlength="50"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none uppercase"
            />
          </div>

          <!-- Paper title -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Paper Title <span class="text-red-400">*</span>
              <span class="text-slate-400 font-normal text-xs ml-2">{{ charCount }} characters</span>
            </label>
            <textarea
              v-model="paperTitle"
              rows="3"
              placeholder="Enter your full paper title in Title Case"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-none"
            />
          </div>

          <!-- Author -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Author Name(s) <span class="text-red-400">*</span></label>
            <input
              v-model="authorName"
              type="text"
              placeholder="First Last (or multiple names separated by commas)"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <!-- Institution (APA + Chicago) -->
          <div v-if="formatStyle !== 'mla9'">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Institution / University</label>
            <input
              v-model="institution"
              type="text"
              placeholder="e.g. University of Michigan"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <!-- Course + Instructor row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Course Name & Number</label>
              <input
                v-model="courseName"
                type="text"
                placeholder="e.g. ENG 201 — Academic Writing"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Instructor Name</label>
              <input
                v-model="instructorName"
                type="text"
                placeholder="e.g. Dr. Jane Smith"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
          </div>

          <!-- Date -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Date</label>
            <input
              v-model="paperDate"
              type="text"
              :placeholder="formatStyle === 'mla9' ? 'DD Month YYYY' : 'Month DD, YYYY'"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <button
            type="button"
            @click="downloadWord"
            class="w-full sm:w-auto rounded-xl bg-brand-600 px-7 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
            Download as Word (.doc)
          </button>
        </div>
      </div>

      <!-- Right: Live preview -->
      <div class="lg:w-96 xl:w-[440px] flex-shrink-0">
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 sticky top-24">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Live Preview</h2>

          <!-- Paper preview -->
          <div class="border border-slate-200 rounded-xl bg-white shadow-inner overflow-hidden">
            <!-- APA 7 preview -->
            <div v-if="formatStyle === 'apa7'" class="p-6 font-serif text-xs leading-relaxed min-h-64">
              <div class="flex justify-between items-start text-xs text-slate-600 mb-8">
                <span class="uppercase">Running head: {{ runningHead.trim().toUpperCase() || 'SHORTENED TITLE' }}</span>
                <span>1</span>
              </div>
              <div class="text-center mt-10">
                <p class="font-bold text-slate-800 mb-1">{{ paperTitle.trim() || 'Full Paper Title in Title Case' }}</p>
                <p class="text-slate-600">{{ authorName.trim() || 'Author Name(s)' }}</p>
                <p class="text-slate-600">{{ institution.trim() || 'Department/Institution' }}</p>
                <p class="text-slate-600">{{ courseName.trim() || 'Course Name and Number' }}</p>
                <p class="text-slate-600">{{ instructorName.trim() || 'Instructor Name' }}</p>
                <p class="text-slate-600">{{ paperDate }}</p>
              </div>
            </div>

            <!-- MLA 9 preview -->
            <div v-else-if="formatStyle === 'mla9'" class="p-6 font-serif text-xs leading-relaxed min-h-64">
              <div class="text-right text-slate-600 mb-8">
                <p>{{ authorName.trim() || 'Author Name' }}</p>
                <p>{{ instructorName.trim() || 'Instructor Name' }}</p>
                <p>{{ courseName.trim() || 'Course Name' }}</p>
                <p>{{ paperDate }}</p>
              </div>
              <div class="text-center mt-6">
                <p class="font-bold text-slate-800">{{ paperTitle.trim() || 'Title of the Paper' }}</p>
              </div>
            </div>

            <!-- Chicago preview -->
            <div v-else class="p-6 font-serif text-xs leading-relaxed min-h-64">
              <div class="text-center mt-8">
                <p class="font-bold text-slate-800 mb-12">{{ paperTitle.trim() || 'Title of the Paper' }}</p>
              </div>
              <div class="text-center mt-8">
                <p class="text-slate-600">{{ authorName.trim() || 'Author Name' }}</p>
                <p class="text-slate-600">{{ courseName.trim() || 'Course Name and Number' }}</p>
                <p class="text-slate-600">{{ institution.trim() || 'Institution' }}</p>
                <p class="text-slate-600">{{ paperDate }}</p>
              </div>
            </div>
          </div>

          <p class="text-xs text-slate-400 mt-3 text-center">Preview is approximated — downloaded file uses proper margins and double spacing.</p>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="max-w-4xl mx-auto px-4 pb-16">
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full paper written for you? Expert writers, original content, from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
