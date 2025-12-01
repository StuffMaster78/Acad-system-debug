<template>
  <div class="max-w-6xl mx-auto p-6">
    <!-- Progress Steps -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div
          v-for="(stepInfo, index) in steps"
          :key="index"
          class="flex items-center flex-1"
        >
          <div class="flex items-center flex-1">
            <div
              :class="[
                'flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors',
                currentStep > index
                  ? 'bg-primary-600 border-primary-600 text-white'
                  : currentStep === index
                  ? 'bg-primary-100 border-primary-600 text-primary-600'
                  : 'bg-gray-100 border-gray-300 text-gray-400'
              ]"
            >
              <span v-if="currentStep > index">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="ml-3 hidden md:block">
              <div
                :class="[
                  'text-sm font-medium',
                  currentStep >= index ? 'text-gray-900' : 'text-gray-500'
                ]"
              >
                {{ stepInfo.title }}
              </div>
              <div class="text-xs text-gray-500">{{ stepInfo.subtitle }}</div>
            </div>
          </div>
          <div
            v-if="index < steps.length - 1"
            :class="[
              'h-0.5 flex-1 mx-4 hidden md:block',
              currentStep > index ? 'bg-primary-600' : 'bg-gray-300'
            ]"
          ></div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="mb-4 p-4 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="mb-4 p-4 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Step 1: Order Type & Attribution -->
    <div v-if="currentStep === 1" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Order Type & Attribution</h2>
      <div class="space-y-6">
        <!-- Order Type Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            Order Type <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              type="button"
              @click="orderType = 'attributed'"
              :class="[
                'p-4 border-2 rounded-lg text-left transition-all',
                orderType === 'attributed'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="font-semibold mb-1">Attributed Order</div>
              <div class="text-sm text-gray-600">Link to an existing client account</div>
            </button>
            <button
              type="button"
              @click="orderType = 'unattributed'"
              :class="[
                'p-4 border-2 rounded-lg text-left transition-all',
                orderType === 'unattributed'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="font-semibold mb-1">Unattributed Order</div>
              <div class="text-sm text-gray-600">External contact (WhatsApp, chat, etc.)</div>
            </button>
          </div>
        </div>

        <!-- Attributed Order: Client Selection -->
        <div v-if="orderType === 'attributed'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Select Client <span class="text-red-500">*</span>
            </label>
            <div class="flex gap-2">
              <select
                v-model="form.client_id"
                required
                class="flex-1 border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Search or select client...</option>
                <option v-for="client in clients" :key="client.id" :value="client.id">
                  {{ formatClientName(client) }}
                </option>
              </select>
              <button
                type="button"
                @click="showClientSearch = true"
                class="px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                🔍 Search
              </button>
            </div>
          </div>
        </div>

        <!-- Unattributed Order: Info -->
        <div v-if="orderType === 'unattributed'" class="space-y-4 border-t pt-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> For unattributed orders, you (admin/superadmin) will act as the client. 
              Writers will see a system-generated client ID. No external contact information is needed.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Task Details -->
    <div v-if="currentStep === 2" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Task Details</h2>
      <div class="space-y-6">
        <!-- Topic -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Topic/Title <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.topic"
            type="text"
            required
            placeholder="Enter paper topic or title"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <!-- Paper Type and Academic Level -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DatabaseSelect
            v-model="form.paper_type_id"
            source="paper-types"
            label="Paper Type"
            placeholder="Select a paper type..."
            required
            @change="loadPricing"
          />
          <DatabaseSelect
            v-model="form.academic_level_id"
            source="academic-levels"
            label="Academic Level"
            placeholder="Select an academic level..."
            required
            @change="loadPricing"
          />
        </div>

        <!-- Pages and Deadline -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Number of Pages <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="form.number_of_pages"
              type="number"
              min="1"
              required
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              @change="loadPricing"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Number of Slides
            </label>
            <input
              v-model.number="form.number_of_slides"
              type="number"
              min="0"
              default="0"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              @change="loadPricing"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
              Deadline <span class="text-red-500">*</span>
              <Tooltip text="The client's deadline helps us assign the right writer and ensure the order is completed on time. Please provide a realistic deadline to ensure quality work." />
            </label>
            <input
              v-model="form.client_deadline"
              type="datetime-local"
              required
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        <!-- Subject and Type of Work -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DatabaseSelect
            v-model="form.subject_id"
            source="subjects"
            label="Subject"
            placeholder="Select a subject..."
            required
            :sort-fn="(a, b) => a.name.localeCompare(b.name)"
            @change="loadPricing"
          />
          <DatabaseSelect
            v-model="form.type_of_work_id"
            source="types-of-work"
            label="Type of Work"
            placeholder="Select type of work..."
            @change="loadPricing"
          />
        </div>

      </div>
    </div>

    <!-- Step 3: Instructions & Files -->
    <div v-if="currentStep === 3" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Instructions & Files</h2>
      <div class="space-y-6">
        <!-- Detailed Instructions -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
            Detailed Instructions <span class="text-red-500">*</span>
            <Tooltip text="Detailed instructions help our writers understand exactly what the client needs. Include specific requirements, formatting guidelines, sources to use, and any other important details. The more details you provide, the better the writer can meet expectations." />
          </label>
          <RichTextEditor
            v-model="form.order_instructions"
            :required="true"
            placeholder="Provide detailed instructions for the writer. Include:&#10;- Specific requirements&#10;- Key points to cover&#10;- Any sources or materials to use&#10;- Formatting preferences&#10;- Any other important details"
            toolbar="full"
            height="300px"
            :allow-images="true"
          />
          <p class="text-xs text-gray-500 mt-1">The more details you provide, the better the writer can meet your expectations</p>
        </div>

        <!-- Formatting Style and English Type -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DatabaseSelect
            v-model="form.formatting_style_id"
            source="formatting-styles"
            label="Formatting & Citation Style"
            placeholder="Select formatting style..."
            helper-text="e.g., APA, MLA, Chicago, Harvard"
          />
          <DatabaseSelect
            v-model="form.english_type_id"
            source="english-types"
            label="English Type"
            placeholder="Select English type..."
            helper-text="US, UK, AU, CA, or International"
          />
        </div>

        <!-- Spacing and References -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Line Spacing
            </label>
            <select
              v-model="form.spacing"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Default</option>
              <option value="single">Single</option>
              <option value="1.5">1.5</option>
              <option value="double">Double</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Number of References/Sources
            </label>
            <input
              v-model.number="form.number_of_refereces"
              type="number"
              min="0"
              placeholder="Optional"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">Minimum number of sources required</p>
          </div>
        </div>

        <!-- Additional Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Additional Notes (Optional)
          </label>
          <RichTextEditor
            v-model="form.additional_notes"
            placeholder="Any additional information, special requests, or clarifications"
            toolbar="basic"
            height="150px"
          />
        </div>

        <!-- File Uploads -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Attach Files (Optional)
          </label>
          <FileUpload
            v-model="uploadedFiles"
            :multiple="true"
            :max-size="100 * 1024 * 1024"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf,.zip,.rar"
            label="Drop files here or click to browse"
            @uploaded="handleFilesUploaded"
          />
          <p class="text-xs text-gray-500 mt-1">
            Upload reference materials, sample papers, or any files that will help the writer understand your requirements
          </p>
        </div>
      </div>
    </div>

    <!-- Step 4: Pricing & Services -->
    <div v-if="currentStep === 4" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Pricing & Services</h2>
      <div class="space-y-6">
        <!-- Price Calculation -->
        <div v-if="quoteLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="text-gray-500 mt-2">Calculating price...</p>
        </div>

        <div v-else-if="quote" class="space-y-4">
          <div class="bg-gray-50 rounded-lg p-6 space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Base Price ({{ form.number_of_pages }} pages)</span>
              <span class="font-medium">${{ parseFloat(quote.base_price || 0).toFixed(2) }}</span>
            </div>
            <div v-if="quote.slides_price > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Slides ({{ form.number_of_slides || 0 }})</span>
              <span class="font-medium">${{ parseFloat(quote.slides_price || 0).toFixed(2) }}</span>
            </div>
            <div v-if="quote.academic_level_multiplier" class="flex justify-between text-sm">
              <span class="text-gray-600">Academic Level Multiplier</span>
              <span class="font-medium">×{{ parseFloat(quote.academic_level_multiplier || 1).toFixed(2) }}</span>
            </div>
            <div v-if="quote.deadline_multiplier" class="flex justify-between text-sm">
              <span class="text-gray-600">Urgency Multiplier</span>
              <span class="font-medium">×{{ parseFloat(quote.deadline_multiplier || 1).toFixed(2) }}</span>
            </div>
            <div v-if="quote.technical_multiplier" class="flex justify-between text-sm">
              <span class="text-gray-600">Technical Subject Multiplier</span>
              <span class="font-medium">×{{ parseFloat(quote.technical_multiplier || 1).toFixed(2) }}</span>
            </div>
            <div v-if="quote.discount_amount > 0" class="flex justify-between text-sm text-green-600">
              <span>Discount ({{ appliedDiscount?.code || discountCode }})</span>
              <span class="font-medium">-${{ parseFloat(quote.discount_amount || 0).toFixed(2) }}</span>
            </div>
            <div class="border-t pt-3 flex justify-between text-lg font-bold">
              <span>Total Price</span>
              <span class="text-primary-600">${{ parseFloat(quote.total_price || 0).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Discount Code -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Discount Code (Optional)
          </label>
          <DiscountCodeInput
            v-model="discountCode"
            :order-total="quote?.total_price || totalPrice"
            @applied="handleDiscountApplied"
            @removed="handleDiscountRemoved"
          />
        </div>

        <!-- Preferred Writer -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Preferred Writer (Optional)
          </label>
          <select
            v-model="form.preferred_writer_id"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            @change="updatePriceWithServices"
          >
            <option value="">No preference - assign any available writer</option>
            <option v-for="writer in writers" :key="writer.id" :value="writer.id">
              {{ formatWriterName(writer) }}
            </option>
          </select>
        </div>

        <!-- Extra Services -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            Additional Services (Optional)
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <label
              v-for="service in extraServices"
              :key="service.id"
              class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
              :class="selectedServices.includes(service.id) ? 'border-primary-600 bg-primary-50' : 'border-gray-200'"
            >
              <input
                type="checkbox"
                :value="service.id"
                v-model="selectedServices"
                class="mr-3"
                @change="updatePriceWithServices"
              />
              <div class="flex-1">
                <div class="font-medium">{{ service.service_name || service.name }}</div>
                <div class="text-sm text-gray-600">${{ parseFloat(service.cost || service.price || 0).toFixed(2) }}</div>
                <div v-if="service.description" class="text-xs text-gray-500 mt-1">{{ service.description }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Payment Options for Unattributed Orders -->
        <div v-if="orderType === 'unattributed'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p class="text-sm text-yellow-800">
            <strong>Note:</strong> Unattributed orders can be marked as paid or unpaid. 
            Use "Allow Unpaid Access" to make the order visible to writers even if unpaid.
          </p>
          <div class="mt-3 space-y-2">
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="form.allow_unpaid_access"
                class="mr-2"
              />
              <span class="text-sm">Allow unpaid access (order visible to writers)</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 5: Review & Submit -->
    <div v-if="currentStep === 5" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Review & Submit</h2>
      <div class="space-y-6">
        <!-- Order Summary -->
        <div class="bg-gray-50 rounded-lg p-6 space-y-4">
          <h3 class="font-semibold text-lg">Order Summary</h3>
          
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="font-medium text-gray-600">Order Type:</span>
              <span class="ml-2">{{ orderType === 'attributed' ? 'Attributed' : 'Unattributed' }}</span>
            </div>
            <div v-if="orderType === 'attributed'">
              <span class="font-medium text-gray-600">Client:</span>
              <span class="ml-2">{{ selectedClient?.username || 'Not selected' }}</span>
            </div>
            <div v-if="orderType === 'unattributed'">
              <span class="font-medium text-gray-600">Type:</span>
              <span class="ml-2">Unattributed (Admin as Client)</span>
            </div>
            <div>
              <span class="font-medium text-gray-600">Topic:</span>
              <span class="ml-2">{{ form.topic }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-600">Paper Type:</span>
              <span class="ml-2">{{ selectedPaperType?.name || 'Not selected' }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-600">Pages:</span>
              <span class="ml-2">{{ form.number_of_pages }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-600">Deadline:</span>
              <span class="ml-2">{{ formatDateTime(form.client_deadline) }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-600">Total Price:</span>
              <span class="ml-2 font-bold">${{ formatCurrency(totalPrice) }}</span>
            </div>
          </div>
        </div>

        <!-- Instructions Preview -->
        <div>
          <h3 class="font-semibold mb-2">Instructions Preview</h3>
          <div class="bg-white border rounded-lg p-4 max-h-64 overflow-y-auto">
            <SafeHtml :content="form.order_instructions" />
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex justify-between mt-8">
      <button
        v-if="currentStep > 1"
        @click="previousStep"
        class="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
      >
        ← Previous
      </button>
      <div v-else></div>
      
      <div class="flex gap-3">
        <button
          v-if="currentStep < steps.length"
          @click="nextStep"
          :disabled="!canProceed"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next →
        </button>
        <button
          v-if="currentStep === steps.length"
          @click="submitOrder"
          :disabled="loading || !canProceed"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? 'Creating...' : 'Create Order' }}
        </button>
      </div>
    </div>

    <!-- Client Search Modal -->
    <Modal
      :visible="showClientSearch"
      title="Search and Select Client"
      size="lg"
      @update:visible="showClientSearch = $event"
    >
      <div class="space-y-4">
        <!-- Search Input -->
        <div>
          <input
            v-model="clientSearchQuery"
            type="text"
            placeholder="Search by username or email..."
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            @input="searchClients"
          />
        </div>

        <!-- Loading State -->
        <div v-if="clientSearchLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-500">Searching clients...</p>
        </div>

        <!-- Results -->
        <div v-else-if="filteredClients.length > 0" class="max-h-96 overflow-y-auto space-y-2">
          <button
            v-for="client in filteredClients"
            :key="client.id"
            @click="selectClient(client)"
            class="w-full text-left p-3 border rounded-lg hover:bg-gray-50 transition-colors"
            :class="form.client_id === client.id ? 'border-primary-600 bg-primary-50' : 'border-gray-200'"
          >
            <div class="font-medium">{{ client.username }}</div>
            <div class="text-sm text-gray-600">{{ client.email }}</div>
            <div v-if="client.full_name" class="text-xs text-gray-500 mt-1">{{ client.full_name }}</div>
          </button>
        </div>

        <!-- Empty State -->
        <div v-else-if="clientSearchQuery && !clientSearchLoading" class="text-center py-8 text-gray-500">
          <p>No clients found matching "{{ clientSearchQuery }}"</p>
        </div>

        <!-- Initial State -->
        <div v-else class="text-center py-8 text-gray-500">
          <p>Start typing to search for clients...</p>
        </div>
      </div>

      <template #footer>
        <button
          @click="showClientSearch = false"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Close
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminAPI from '@/api/admin'
import ordersAPI from '@/api/orders'
import usersAPI from '@/api/users'
import orderConfigsAPI from '@/api/orderConfigs'
import pricingAPI from '@/api/pricing'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import DiscountCodeInput from '@/components/common/DiscountCodeInput.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import Modal from '@/components/common/Modal.vue'
import Tooltip from '@/components/common/Tooltip.vue'
import DatabaseSelect from '@/components/common/DatabaseSelect.vue'
import { formatWriterName, formatClientName } from '@/utils/formatDisplay'

const router = useRouter()
const authStore = useAuthStore()

const currentStep = ref(1)
const steps = [
  { title: 'Order Type', subtitle: 'Attribution' },
  { title: 'Task Details', subtitle: 'Basic information' },
  { title: 'Instructions & Files', subtitle: 'Requirements & attachments' },
  { title: 'Pricing & Services', subtitle: 'Cost & options' },
  { title: 'Review & Submit', subtitle: 'Final check' },
]

const orderType = ref('attributed') // 'attributed' or 'unattributed'
const loading = ref(false)
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)
const showClientSearch = ref(false)
const clientSearchQuery = ref('')
const clientSearchLoading = ref(false)
const filteredClients = ref([])

// Form data
const form = ref({
  // Attribution
  client_id: null,
  
  // Task details
  topic: '',
  paper_type_id: null,
  academic_level_id: null,
  formatting_style_id: null,
  subject_id: null,
  type_of_work_id: null,
  english_type_id: null,
  number_of_pages: 1,
  number_of_slides: 0,
  number_of_refereces: 0,
  spacing: 'single',
  preferred_writer_id: null,
  client_deadline: '',
  
  // Instructions
  order_instructions: '',
  additional_notes: '',
  
  // Pricing
  discount_code: '',
  allow_unpaid_access: false,
})

// File uploads
const uploadedFiles = ref([])
const fileUploadsPending = ref([])

// Options
const clients = ref([])
const paperTypes = ref([])
const academicLevels = ref([])
const formattingStyles = ref([])
const subjects = ref([])
const typesOfWork = ref([])
const englishTypes = ref([])
const writers = ref([])
const extraServices = ref([])
const selectedServices = ref([])

// Pricing
const quote = ref(null)
const quoteLoading = ref(false)
const basePrice = ref(0)
const discountCode = ref('')
const discountAmount = ref(0)
const appliedDiscount = ref(null)

// Computed
const selectedClient = computed(() => {
  return clients.value.find(c => c.id === form.value.client_id)
})

const selectedPaperType = computed(() => {
  return paperTypes.value.find(pt => pt.id === form.value.paper_type_id)
})

const extraServicesTotal = computed(() => {
  return selectedServices.value.reduce((sum, serviceId) => {
    const service = extraServices.value.find(s => s.id === serviceId)
    return sum + (parseFloat(service?.cost || service?.price || 0))
  }, 0)
})

const totalPrice = computed(() => {
  if (quote.value) {
    return parseFloat(quote.value.total_price || 0)
  }
  return Math.max(0, basePrice.value + extraServicesTotal.value - discountAmount.value)
})

const canProceed = computed(() => {
  if (currentStep.value === 1) {
    if (orderType.value === 'attributed') {
      return !!form.value.client_id
    } else {
      // Unattributed orders don't need external contact info
      return true
    }
  }
  if (currentStep.value === 2) {
    // Validate required fields
    if (!form.value.topic || !form.value.topic.trim()) return false
    if (!form.value.paper_type_id) return false
    if (!form.value.academic_level_id) return false
    if (!form.value.subject_id) return false
    if (!form.value.number_of_pages || form.value.number_of_pages < 1) return false
    if (!form.value.client_deadline) return false
    
    // Validate deadline is in the future
    if (form.value.client_deadline) {
      const deadline = new Date(form.value.client_deadline)
      const now = new Date()
      if (deadline <= now) return false
    }
    
    return true
  }
  if (currentStep.value === 3) {
    return !!form.value.order_instructions
  }
  return true
})

// Methods
const nextStep = () => {
  if (canProceed.value && currentStep.value < steps.length) {
    currentStep.value++
    if (currentStep.value === 4) {
      calculatePrice()
    }
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const loadClients = async () => {
  try {
    // The users endpoint is at /users/users/ (from router registration)
    const res = await usersAPI.list({ role: 'client' })
    clients.value = res.data?.results || res.data || []
    filteredClients.value = clients.value
    console.log('Loaded clients:', clients.value.length)
  } catch (e) {
    console.error('Failed to load clients:', e)
    error.value = 'Failed to load clients. Please refresh the page.'
  }
}

const searchClients = () => {
  if (!clientSearchQuery.value.trim()) {
    filteredClients.value = clients.value
    return
  }
  
  const query = clientSearchQuery.value.toLowerCase().trim()
  filteredClients.value = clients.value.filter(client => {
    const username = (client.username || '').toLowerCase()
    const email = (client.email || '').toLowerCase()
    const fullName = (client.full_name || '').toLowerCase()
    return username.includes(query) || email.includes(query) || fullName.includes(query)
  })
}

const selectClient = (client) => {
  form.value.client_id = client.id
  showClientSearch.value = false
  clientSearchQuery.value = ''
  filteredClients.value = clients.value
}

const loadOrderConfigs = async () => {
  try {
    const [paperTypesRes, academicLevelsRes, formattingStylesRes, subjectsRes, typesOfWorkRes, englishTypesRes] = await Promise.all([
      orderConfigsAPI.getPaperTypes(),
      orderConfigsAPI.getAcademicLevels(),
      orderConfigsAPI.getFormattingStyles(),
      orderConfigsAPI.getSubjects(),
      orderConfigsAPI.getTypesOfWork(),
      orderConfigsAPI.getEnglishTypes(),
    ])
    
    paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
    academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
    formattingStyles.value = formattingStylesRes.data?.results || formattingStylesRes.data || []
    subjects.value = subjectsRes.data?.results || subjectsRes.data || []
    typesOfWork.value = typesOfWorkRes.data?.results || typesOfWorkRes.data || []
    englishTypes.value = englishTypesRes.data?.results || englishTypesRes.data || []
    
    console.log('Loaded order configs:', {
      paperTypes: paperTypes.value.length,
      academicLevels: academicLevels.value.length,
      formattingStyles: formattingStyles.value.length,
      subjects: subjects.value.length,
      typesOfWork: typesOfWork.value.length,
      englishTypes: englishTypes.value.length,
    })
  } catch (e) {
    console.error('Failed to load order configs:', e)
    error.value = 'Failed to load order configuration data. Please refresh the page.'
  }
}

const loadWriters = async () => {
  try {
    const res = await usersAPI.list({ role: 'writer' })
    writers.value = res.data?.results || res.data || []
    console.log('Loaded writers:', writers.value.length)
  } catch (e) {
    console.error('Failed to load writers:', e)
    error.value = 'Failed to load writers. Please refresh the page.'
  }
}

const loadExtraServices = async () => {
  try {
    // Load extra services from pricing configs API
    const res = await pricingAPI.getAdditionalServices()
    extraServices.value = res.data?.results || res.data || []
    console.log('Loaded extra services:', extraServices.value.length)
  } catch (e) {
    console.error('Failed to load extra services:', e)
    // Don't show error for extra services as they're optional
    extraServices.value = []
  }
}

const calculatePrice = async () => {
  if (!form.value.paper_type_id || !form.value.number_of_pages) {
    quote.value = null
    return
  }
  
  quoteLoading.value = true
  try {
    const quoteData = {
      topic: form.value.topic,
      paper_type_id: form.value.paper_type_id,
      academic_level_id: form.value.academic_level_id,
      subject_id: form.value.subject_id,
      type_of_work_id: form.value.type_of_work_id,
      english_type_id: form.value.english_type_id,
      number_of_pages: form.value.number_of_pages,
      number_of_slides: form.value.number_of_slides || 0,
      client_deadline: form.value.client_deadline,
      order_instructions: form.value.order_instructions,
      discount_code: appliedDiscount.value?.code || discountCode.value || '',
      preferred_writer_id: form.value.preferred_writer_id,
      extra_services: selectedServices.value
    }
    
    const res = await ordersAPI.quote(quoteData)
    quote.value = res.data
    basePrice.value = parseFloat(res.data?.total_price || 0)
  } catch (e) {
    console.error('Failed to calculate price:', e)
    quote.value = null
    // Fallback calculation
    basePrice.value = form.value.number_of_pages * 10
  } finally {
    quoteLoading.value = false
  }
}

const loadPricing = calculatePrice

const updatePriceWithServices = async () => {
  await calculatePrice()
}

const handleDiscountApplied = (discount, amount) => {
  appliedDiscount.value = discount
  discountAmount.value = amount
  form.value.discount_code = discount.code
  calculatePrice()
}

const handleDiscountRemoved = () => {
  appliedDiscount.value = null
  discountAmount.value = 0
  form.value.discount_code = ''
  calculatePrice()
}

const handleFilesUploaded = (files) => {
  uploadedFiles.value = files
  fileUploadsPending.value = files.filter(f => f.id && !f.uploaded)
}

const uploadFilesToOrder = async (orderId) => {
  if (!uploadedFiles.value.length) return
  
  const orderFilesAPI = (await import('@/api/order-files')).default
  
  for (const file of uploadedFiles.value) {
    if (file.file && !file.uploaded) {
      try {
        const formData = new FormData()
        formData.append('file', file.file)
        formData.append('order', orderId)
        if (file.category) formData.append('category', file.category)
        
        await orderFilesAPI.upload(formData)
      } catch (e) {
        console.error('Failed to upload file:', e)
      }
    }
  }
}

const validateForm = () => {
  const errors = []
  
  // Step 1 validation
  if (orderType.value === 'attributed' && !form.value.client_id) {
    errors.push('Please select a client for attributed orders.')
  }
  
  // Step 2 validation
  if (!form.value.topic || !form.value.topic.trim()) {
    errors.push('Topic is required.')
  }
  if (!form.value.paper_type_id) {
    errors.push('Paper type is required.')
  }
  if (!form.value.academic_level_id) {
    errors.push('Academic level is required.')
  }
  if (!form.value.subject_id) {
    errors.push('Subject is required.')
  }
  if (!form.value.number_of_pages || form.value.number_of_pages < 1) {
    errors.push('Number of pages must be at least 1.')
  }
  if (!form.value.client_deadline) {
    errors.push('Client deadline is required.')
  } else {
    const deadline = new Date(form.value.client_deadline)
    const now = new Date()
    if (deadline <= now) {
      errors.push('Client deadline must be in the future.')
    }
  }
  
  // Step 3 validation
  if (!form.value.order_instructions || !form.value.order_instructions.trim()) {
    errors.push('Order instructions are required.')
  }
  
  return errors
}

const submitOrder = async () => {
  // Validate form
  const validationErrors = validateForm()
  if (validationErrors.length > 0) {
    error.value = validationErrors.join(' ')
    message.value = ''
    messageSuccess.value = false
    // Navigate to the first step with errors
    if (!form.value.topic || !form.value.paper_type_id) {
      currentStep.value = 2
    } else if (!form.value.order_instructions) {
      currentStep.value = 3
    }
    return
  }
  
  if (!canProceed.value) {
    error.value = 'Please complete all required fields before submitting.'
    return
  }
  
  error.value = ''
  message.value = ''
  loading.value = true
  
  try {
    const payload = {
      topic: form.value.topic,
      paper_type_id: form.value.paper_type_id,
      number_of_pages: form.value.number_of_pages,
      client_deadline: form.value.client_deadline,
      order_instructions: form.value.order_instructions,
      discount_code: form.value.discount_code || null,
      allow_unpaid_access: form.value.allow_unpaid_access,
    }
    
    // Add optional fields
    if (form.value.academic_level_id) payload.academic_level_id = form.value.academic_level_id
    if (form.value.formatting_style_id) payload.formatting_style_id = form.value.formatting_style_id
    if (form.value.subject_id) payload.subject_id = form.value.subject_id
    if (form.value.type_of_work_id) payload.type_of_work_id = form.value.type_of_work_id
    if (form.value.english_type_id) payload.english_type_id = form.value.english_type_id
    if (form.value.number_of_slides) payload.number_of_slides = form.value.number_of_slides
    if (form.value.number_of_refereces) payload.number_of_refereces = form.value.number_of_refereces
    if (form.value.spacing) payload.spacing = form.value.spacing
    if (form.value.preferred_writer_id) payload.preferred_writer_id = form.value.preferred_writer_id
    if (selectedServices.value.length) payload.extra_services = selectedServices.value
    
    // Attribution
    if (orderType.value === 'attributed') {
      payload.client_id = form.value.client_id
    }
    // For unattributed orders, no external contact info is needed
    // The admin/superadmin will be set as the client upon completion
    
    const res = await adminAPI.placeOrder(payload)
    const orderId = res.data.id
    
    // Upload files if any
    if (uploadedFiles.value.length) {
      await uploadFilesToOrder(orderId)
    }
    
    message.value = `Order #${orderId} created successfully!`
    messageSuccess.value = true
    
    setTimeout(() => {
      router.push(`/orders/${orderId}`)
    }, 1500)
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.response?.data?.error || e.message || 'Failed to create order'
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  await Promise.all([
    loadClients(),
    loadOrderConfigs(),
    loadWriters(),
    loadExtraServices(),
  ])
})
</script>

<style scoped>
/* Add any custom styles if needed */
</style>

