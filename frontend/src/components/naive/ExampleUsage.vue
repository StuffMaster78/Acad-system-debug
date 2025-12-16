<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-bold mb-4">Naive UI Examples</h2>
    
    <!-- Buttons -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Buttons</h3>
      <div class="flex gap-3 flex-wrap">
        <NButton type="primary">Primary</NButton>
        <NButton type="success">Success</NButton>
        <NButton type="warning">Warning</NButton>
        <NButton type="error">Error</NButton>
        <NButton type="info">Info</NButton>
        <NButton type="default">Default</NButton>
        <NButton type="tertiary">Tertiary</NButton>
      </div>
    </div>

    <!-- Inputs -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Inputs</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <NInput v-model:value="inputValue" placeholder="Enter text..." clearable />
        <NInputNumber v-model:value="numberValue" placeholder="Enter number" />
        <NTextarea v-model:value="textareaValue" placeholder="Enter textarea..." />
        <NSelect v-model:value="selectValue" :options="selectOptions" placeholder="Select option" />
      </div>
    </div>

    <!-- Modal -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Modal</h3>
      <NButton @click="showModal = true">Open Modal</NButton>
      <NModal v-model:show="showModal" title="Example Modal" preset="card" style="width: 600px">
        <p>This is a Naive UI modal. It automatically syncs with your theme!</p>
        <template #footer>
          <NButton @click="showModal = false">Close</NButton>
        </template>
      </NModal>
    </div>

    <!-- Data Table -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Data Table</h3>
      <NDataTable
        :columns="tableColumns"
        :data="tableData"
        :pagination="pagination"
        striped
      />
    </div>

    <!-- Card -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Card</h3>
      <NCard title="Example Card">
        <p>This is a Naive UI card component. It works great with Tailwind!</p>
      </NCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  NButton,
  NInput,
  NInputNumber,
  NTextarea,
  NSelect,
  NModal,
  NDataTable,
  NCard,
} from 'naive-ui'

const inputValue = ref('')
const numberValue = ref(null)
const textareaValue = ref('')
const selectValue = ref(null)
const showModal = ref(false)

const selectOptions = [
  { label: 'Option 1', value: '1' },
  { label: 'Option 2', value: '2' },
  { label: 'Option 3', value: '3' },
]

const tableColumns = [
  { title: 'Name', key: 'name' },
  { title: 'Age', key: 'age' },
  { title: 'Email', key: 'email' },
]

const tableData = ref([
  { name: 'John Doe', age: 30, email: 'john@example.com' },
  { name: 'Jane Smith', age: 25, email: 'jane@example.com' },
  { name: 'Bob Johnson', age: 35, email: 'bob@example.com' },
])

const pagination = {
  pageSize: 10,
}
</script>

