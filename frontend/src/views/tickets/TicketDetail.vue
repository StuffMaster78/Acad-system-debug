<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Ticket #{{ ticket?.id }}</h1>
      <router-link to="/tickets" class="text-primary-600">Back to Tickets</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-4">
        <div class="card p-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-lg font-semibold">{{ ticket?.subject }}</div>
              <div class="text-xs text-gray-500">Status: <span :class="badgeClass(ticket?.status)" class="inline-block px-2 py-0.5 rounded">{{ ticket?.status }}</span></div>
            </div>
            <div class="text-xs text-gray-500">Created: {{ toDT(ticket?.created_at) }}</div>
          </div>
          <div class="mt-3 whitespace-pre-line text-sm">{{ ticket?.message }}</div>
          <div v-if="ticket?.attachments?.length" class="mt-3">
            <div class="text-sm font-medium mb-1">Attachments</div>
            <ul class="list-disc list-inside text-sm">
              <li v-for="(a, i) in ticket.attachments" :key="i">
                <a :href="a.url || a" target="_blank" class="text-primary-600">{{ a.name || a.url || 'Attachment' }}</a>
              </li>
            </ul>
          </div>
        </div>

        <div class="card p-4">
          <h2 class="text-lg font-semibold mb-3">Thread</h2>
          <div v-if="threadLoading" class="text-sm text-gray-500">Loading...</div>
          <div v-else class="space-y-3">
            <div v-for="m in thread" :key="m.id" class="p-3 rounded border border-gray-200">
              <div class="text-xs text-gray-500 mb-1">{{ m.author_name || 'User' }} · {{ toDT(m.created_at) }}</div>
              <div class="text-sm whitespace-pre-line">{{ m.message }}</div>
              <div v-if="m.attachments?.length" class="mt-2">
                <div class="text-xs text-gray-500">Attachments:</div>
                <ul class="list-disc list-inside text-xs">
                  <li v-for="(a, i) in m.attachments" :key="i">
                    <a :href="a.url || a" target="_blank" class="text-primary-600">{{ a.name || a.url || 'Attachment' }}</a>
                  </li>
                </ul>
              </div>
            </div>
            <div v-if="!thread.length" class="text-sm text-gray-500">No replies yet.</div>
          </div>
        </div>

        <div class="card p-4">
          <h2 class="text-lg font-semibold mb-3">Add Reply</h2>
          <div v-if="replyMessage" class="mb-2 p-2 rounded" :class="replySuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">{{ replyMessage }}</div>
          <form @submit.prevent="sendReply" class="space-y-3">
            <RichTextEditor
              v-model="replyText"
              label="Reply"
              :required="true"
              placeholder="Write your reply..."
              toolbar="basic"
              height="150px"
              :error="replyMessage && !replySuccess ? replyMessage : ''"
              :strip-html="true"
            />
            <input @change="onReplyFiles" type="file" multiple class="w-full" />
            <div class="flex gap-3">
              <button :disabled="sending" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">{{ sending ? 'Sending...' : 'Send Reply' }}</button>
              <button type="button" @click="refreshThread" class="px-4 py-2 bg-gray-100 rounded">Refresh</button>
            </div>
          </form>
        </div>
      </div>

      <div class="space-y-4">
        <div class="card p-4">
          <div class="text-sm"><strong>Order:</strong> <span v-if="ticket?.order_id">#{{ ticket.order_id }}</span><span v-else>—</span></div>
          <div class="text-sm"><strong>Priority:</strong> {{ ticket?.priority || 'normal' }}</div>
          <div class="text-sm"><strong>Category:</strong> {{ ticket?.category || 'general' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ticketsAPI from '@/api/tickets'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const route = useRoute()
const id = Number(route.params.id)

const ticket = ref(null)
const thread = ref([])
const threadLoading = ref(true)

const replyText = ref('')
const replyFiles = ref([])
const sending = ref(false)
const replyMessage = ref('')
const replySuccess = ref(false)

const toDT = (v) => (v ? new Date(v).toLocaleString() : '')
const badgeClass = (status) => {
  if (status === 'open') return 'bg-green-100 text-green-700'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-700'
  if (status === 'closed') return 'bg-gray-100 text-gray-700'
  return 'bg-gray-100 text-gray-700'
}

const onReplyFiles = (e) => {
  replyFiles.value = Array.from(e.target.files || [])
}

const loadTicket = async () => {
  const res = await ticketsAPI.get(id)
  ticket.value = res.data
}

const loadThread = async () => {
  threadLoading.value = true
  try {
    const res = await ticketsAPI.thread(id)
    thread.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    thread.value = []
  } finally {
    threadLoading.value = false
  }
}

const refreshThread = () => loadThread()

const sendReply = async () => {
  replyMessage.value = ''
  replySuccess.value = false
  sending.value = true
  try {
    await ticketsAPI.reply(id, { message: replyText.value, attachments: replyFiles.value })
    replySuccess.value = true
    replyMessage.value = 'Reply sent.'
    replyText.value = ''
    replyFiles.value = []
    await loadThread()
  } catch (e) {
    replyMessage.value = e?.response?.data?.detail || e.message || 'Failed to send reply'
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  await loadTicket()
  await loadThread()
})
</script>


