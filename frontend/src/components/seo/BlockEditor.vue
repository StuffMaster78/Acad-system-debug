<template>
  <div class="block-editor space-y-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold">Content Blocks</h3>
      <select
        v-model="newBlockType"
        @change="addBlock"
        class="border rounded px-3 py-2 text-sm"
      >
        <option value="">Add Block...</option>
        <option value="paragraph">Paragraph</option>
        <option value="heading">Heading</option>
        <option value="image">Image</option>
        <option value="cta">Call-to-Action</option>
        <option value="list">List</option>
      </select>
    </div>

    <div class="space-y-3">
      <div
        v-for="(block, index) in modelValue"
        :key="index"
        class="border rounded-lg p-4 bg-gray-50 relative group"
      >
        <div class="flex items-start justify-between mb-2">
          <span class="text-xs font-medium text-gray-500 uppercase">{{ block.type }}</span>
          <div class="flex gap-2">
            <button
              @click="moveBlock(index, 'up')"
              :disabled="index === 0"
              class="text-gray-400 hover:text-gray-600 disabled:opacity-30"
              title="Move up"
            >
              ↑
            </button>
            <button
              @click="moveBlock(index, 'down')"
              :disabled="index === modelValue.length - 1"
              class="text-gray-400 hover:text-gray-600 disabled:opacity-30"
              title="Move down"
            >
              ↓
            </button>
            <button
              @click="removeBlock(index)"
              class="text-red-400 hover:text-red-600"
              title="Remove"
            >
              ×
            </button>
          </div>
        </div>

        <!-- Paragraph Block -->
        <div v-if="block.type === 'paragraph'" class="space-y-2">
          <textarea
            v-model="block.content"
            @input="updateBlocks"
            rows="3"
            placeholder="Enter paragraph text..."
            class="w-full border rounded px-3 py-2 text-sm"
          />
        </div>

        <!-- Heading Block -->
        <div v-else-if="block.type === 'heading'" class="space-y-2">
          <select
            v-model="block.level"
            @change="updateBlocks"
            class="w-full border rounded px-3 py-2 text-sm mb-2"
          >
            <option :value="1">H1</option>
            <option :value="2">H2</option>
            <option :value="3">H3</option>
            <option :value="4">H4</option>
          </select>
          <input
            v-model="block.content"
            @input="updateBlocks"
            type="text"
            placeholder="Enter heading text..."
            class="w-full border rounded px-3 py-2 text-sm"
          />
        </div>

        <!-- Image Block -->
        <div v-else-if="block.type === 'image'" class="space-y-2">
          <MediaPicker
            v-model="block.asset"
            :website-id="websiteId"
            :accept-types="'image/*'"
            trigger-label="Select Image"
            modal-title="Select Image"
            @selected="(asset) => handleImageSelected(index, asset)"
          />
          <div v-if="block.url || block.asset" class="mt-2">
            <img
              :src="block.url || block.asset?.url"
              alt="Block image preview"
              class="w-full max-w-md h-auto rounded border"
            />
          </div>
          <input
            v-model="block.alt"
            @input="updateBlocks"
            type="text"
            placeholder="Alt text (for accessibility)"
            class="w-full border rounded px-3 py-2 text-sm"
          />
          <input
            v-model="block.caption"
            @input="updateBlocks"
            type="text"
            placeholder="Caption (optional)"
            class="w-full border rounded px-3 py-2 text-sm"
          />
        </div>

        <!-- CTA Block -->
        <div v-else-if="block.type === 'cta'" class="space-y-2">
          <input
            v-model="block.title"
            @input="updateBlocks"
            type="text"
            placeholder="CTA Title"
            class="w-full border rounded px-3 py-2 text-sm"
          />
          <textarea
            v-model="block.description"
            @input="updateBlocks"
            rows="2"
            placeholder="CTA Description"
            class="w-full border rounded px-3 py-2 text-sm"
          />
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="block.button_text"
              @input="updateBlocks"
              type="text"
              placeholder="Button Text"
              class="w-full border rounded px-3 py-2 text-sm"
            />
            <input
              v-model="block.button_url"
              @input="updateBlocks"
              type="url"
              placeholder="Button URL"
              class="w-full border rounded px-3 py-2 text-sm"
            />
          </div>
        </div>

        <!-- List Block -->
        <div v-else-if="block.type === 'list'" class="space-y-2">
          <select
            v-model="block.style"
            @change="updateBlocks"
            class="w-full border rounded px-3 py-2 text-sm mb-2"
          >
            <option value="unordered">Unordered (Bullets)</option>
            <option value="ordered">Ordered (Numbers)</option>
          </select>
          <div class="space-y-2">
            <div
              v-for="(item, itemIndex) in block.items"
              :key="itemIndex"
              class="flex gap-2"
            >
              <input
                v-model="block.items[itemIndex]"
                @input="updateBlocks"
                type="text"
                :placeholder="`Item ${itemIndex + 1}`"
                class="flex-1 border rounded px-3 py-2 text-sm"
              />
              <button
                @click="removeListItem(index, itemIndex)"
                class="text-red-400 hover:text-red-600 px-2"
              >
                ×
              </button>
            </div>
            <button
              @click="addListItem(index)"
              class="text-sm text-blue-600 hover:underline"
            >
              + Add Item
            </button>
          </div>
        </div>
      </div>

      <div v-if="modelValue.length === 0" class="text-center py-8 text-gray-400 border-2 border-dashed rounded-lg">
        No blocks yet. Add your first block to get started.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import MediaPicker from '@/components/media/MediaPicker.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  websiteId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const newBlockType = ref('')

const updateBlocks = () => {
  emit('update:modelValue', [...props.modelValue])
}

const addBlock = () => {
  if (!newBlockType.value) return

  const newBlock = { type: newBlockType.value }

  switch (newBlockType.value) {
    case 'paragraph':
      newBlock.content = ''
      break
    case 'heading':
      newBlock.level = 2
      newBlock.content = ''
      break
    case 'image':
      newBlock.url = ''
      newBlock.alt = ''
      newBlock.caption = ''
      newBlock.asset = null
      break
    case 'cta':
      newBlock.title = ''
      newBlock.description = ''
      newBlock.button_text = ''
      newBlock.button_url = ''
      break
    case 'list':
      newBlock.style = 'unordered'
      newBlock.items = ['']
      break
  }

  emit('update:modelValue', [...props.modelValue, newBlock])
  newBlockType.value = ''
}

const removeBlock = (index) => {
  const blocks = [...props.modelValue]
  blocks.splice(index, 1)
  emit('update:modelValue', blocks)
}

const moveBlock = (index, direction) => {
  const blocks = [...props.modelValue]
  const newIndex = direction === 'up' ? index - 1 : index + 1
  if (newIndex >= 0 && newIndex < blocks.length) {
    [blocks[index], blocks[newIndex]] = [blocks[newIndex], blocks[index]]
    emit('update:modelValue', blocks)
  }
}

const handleImageSelected = (index, asset) => {
  const blocks = [...props.modelValue]
  blocks[index].asset = asset
  blocks[index].url = asset?.url || ''
  emit('update:modelValue', blocks)
}

const addListItem = (blockIndex) => {
  const blocks = [...props.modelValue]
  if (!blocks[blockIndex].items) {
    blocks[blockIndex].items = []
  }
  blocks[blockIndex].items.push('')
  emit('update:modelValue', blocks)
}

const removeListItem = (blockIndex, itemIndex) => {
  const blocks = [...props.modelValue]
  blocks[blockIndex].items.splice(itemIndex, 1)
  emit('update:modelValue', blocks)
}
</script>

<style scoped>
.block-editor {
  /* Additional styles if needed */
}
</style>

