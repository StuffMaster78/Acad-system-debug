Network error: unable to reach API (http://localhost:8000/api/v1)<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">New Ticket</h1>
    <div v-if="message" class="mb-4 p-3 rounded bg-green-50 text-green-700">{{ message }}</div>
    <div v-if="error" class="mb-4 p-3 rounded bg-red-50 text-red-700">{{ error }}</div>
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Subject *</label>
        <input v-model="form.subject" type="text" required class="w-full border rounded px-3 py-2" />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Order ID (optional)</label>
          <input v-model.number="form.order_id" type="number" min="1" class="w-full border rounded px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Category</label>
          <select v-model="form.category" class="w-full border rounded px-3 py-2">
            <option value="">Select…</option>
            <option value="general">General</option>
            <option value="billing">Billing</option>
            <option value="order_issue">Order Issue</option>
            <option value="technical">Technical</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Priority</label>
          <select v-model="form.priority" class="w-full border rounded px-3 py-2">
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>
      <div>
        <RichTextEditor
          v-model="form.message"
          label="Message"
          :required="true"
          placeholder="Describe your issue or question..."
          toolbar="basic"
          height="200px"
          :error="error && error.includes('message') ? error : ''"
          :strip-html="true"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Attachments</label>
        <input @change="onFiles" type="file" multiple class="w-full" />
        <p v-if="files.length" class="text-xs text-gray-500 mt-1">{{ files.length }} file(s) selected</p>
      </div>
      <div class="flex gap-3">
        <button :disabled="loading" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">{{ loading ? 'Creating...' : 'Create Ticket' }}</button>
        <router-link to="/tickets" class="px-4 py-2 bg-gray-100 rounded">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ticketsAPI from '@/api/tickets'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const router = useRouter()
const form = ref({ subject: '', message: '', order_id: null, category: '', priority: 'normal' })
const loading = ref(false)
const error = ref('')
const message = ref('')
const files = ref([])

const onFiles = (e) => {
  files.value = Array.from(e.target.files || [])
}

const submit = async () => {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    const payload = { ...form.value, attachments: files.value }
    const res = await ticketsAPI.create(payload)
    message.value = 'Ticket created successfully.'
    setTimeout(() => router.push(`/tickets/${res.data.id}`), 800)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to create ticket'
  } finally {
    loading.value = false
  }
}
</script>


