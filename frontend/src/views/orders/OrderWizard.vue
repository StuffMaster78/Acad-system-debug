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

    <!-- Main Content with Summary Sidebar -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Form Content -->
      <div class="lg:col-span-2 space-y-6">
    <!-- Step 1: Task Details -->
    <div v-if="currentStep === 1" class="bg-white rounded-lg shadow border border-gray-200 p-6">
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
            placeholder="Enter your paper topic or title"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <p class="text-xs text-gray-500 mt-1">Be specific about what you need help with</p>
        </div>

        <!-- Paper Type and Academic Level -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Paper Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.paper_type_id"
              required
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select paper type</option>
              <option v-for="pt in paperTypes" :key="pt.id" :value="pt.id">
                {{ pt.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Academic Level <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.academic_level_id"
              required
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select academic level</option>
              <option v-for="level in academicLevels" :key="level.id" :value="level.id">
                {{ level.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Subject and Type of Work -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Subject <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.subject_id"
              required
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select subject</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
                <span v-if="subject.is_technical"> (Technical)</span>
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Type of Work
            </label>
            <select
              v-model="form.type_of_work_id"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select type of work</option>
              <option v-for="tow in typesOfWork" :key="tow.id" :value="tow.id">
                {{ tow.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Pages, Slides, and Deadline -->
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
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">Leave 0 if not applicable</p>
          </div>
      <div>
            <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
              Deadline <span class="text-red-500">*</span>
              <Tooltip text="Your deadline helps us assign the right writer and ensure your order is completed on time. Please provide a realistic deadline to ensure quality work." />
            </label>
            <input
              v-model="form.client_deadline"
              type="datetime-local"
              required
              :min="minDeadline"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">When do you need this completed?</p>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-end gap-3 pt-4 border-t">
          <router-link to="/orders" class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
            Cancel
          </router-link>
          <button
            @click="validateStep1"
            :disabled="loading"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            Next: Paper Instructions →
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Paper Instructions -->
    <div v-if="currentStep === 2" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Paper Instructions</h2>
      <div class="space-y-6">
        <!-- Detailed Instructions -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
            Detailed Instructions <span class="text-red-500">*</span>
            <Tooltip text="Detailed instructions help our writers understand exactly what you need. Include specific requirements, formatting guidelines, sources to use, and any other important details. The more details you provide, the better the writer can meet your expectations." />
          </label>
          <RichTextEditor
            v-model="form.order_instructions"
            :required="true"
            placeholder="Provide detailed instructions for the writer. Include:&#10;- Specific requirements&#10;- Key points to cover&#10;- Any sources or materials to use&#10;- Formatting preferences&#10;- Any other important details"
            toolbar="full"
            height="300px"
          />
        </div>

        <!-- Formatting Style and English Type -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Formatting & Citation Style
            </label>
            <select
              v-model="form.formatting_style_id"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select formatting style</option>
              <option v-for="style in formattingStyles" :key="style.id" :value="style.id">
                {{ style.name }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">e.g., APA, MLA, Chicago, Harvard</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              English Type
            </label>
            <select
              v-model="form.english_type_id"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select English type</option>
              <option v-for="et in englishTypes" :key="et.id" :value="et.id">
                {{ et.name }} ({{ et.code }})
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">US, UK, AU, CA, or International</p>
          </div>
        </div>

        <!-- Spacing and Resources -->
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
              v-model.number="form.number_of_references"
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
            label="Additional Notes (Optional)"
            placeholder="Any additional information, special requests, or clarifications"
            toolbar="basic"
            height="150px"
          />
        </div>

        <!-- Navigation -->
        <div class="flex justify-between gap-3 pt-4 border-t">
          <button
            @click="currentStep = 1"
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            ← Back
          </button>
          <button
            @click="validateStep2"
            :disabled="loading"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            Next: Calculate Price →
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Price Calculation -->
    <div v-if="currentStep === 3" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Price Calculation</h2>
      <div class="space-y-6">
        <!-- Discount Code -->
      <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Discount Code (Optional)
          </label>
          <div class="flex gap-2">
            <input
              v-model="discountCode"
              type="text"
              placeholder="Enter discount code"
              class="flex-1 border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              @keyup.enter="applyDiscount"
            />
            <button
              @click="applyDiscount"
              :disabled="validatingDiscount"
              class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {{ validatingDiscount ? 'Validating...' : 'Apply' }}
            </button>
          </div>
          <p v-if="discountMessage" class="text-sm mt-2" :class="discountValid ? 'text-green-600' : 'text-red-600'">
            {{ discountMessage }}
          </p>
        </div>

        <!-- Price Breakdown -->
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

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> Final price may change after adding additional services in the next step.
            </p>
          </div>
      </div>

        <!-- Navigation -->
        <div class="flex justify-between gap-3 pt-4 border-t">
          <button
            @click="currentStep = 2"
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            ← Back
          </button>
          <button
            @click="validateStep3"
            :disabled="loading || !quote"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            Next: Additional Services →
        </button>
        </div>
      </div>
    </div>

    <!-- Step 4: Additional Services -->
    <div v-if="currentStep === 4" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Additional Services</h2>
      <div class="space-y-6">
        <!-- Preferred Writer -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Preferred Writer (Optional)
          </label>
          <select
            v-model="form.preferred_writer_id"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">No preference - assign any available writer</option>
            <option v-for="writer in preferredWriters" :key="writer.id" :value="writer.id">
              {{ formatWriterName(writer) }}
              <span v-if="writer.preferred_writer_cost"> - +${{ parseFloat(writer.preferred_writer_cost).toFixed(2) }}</span>
            </option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            Select a writer you've worked with before, or leave blank for automatic assignment
          </p>
        </div>

        <!-- Writer Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Writer Quality Level (Optional)
          </label>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="level in writerLevels"
              :key="level.id"
              @click="form.writer_level_id = form.writer_level_id === level.id ? null : level.id"
              :class="[
                'border-2 rounded-lg p-4 cursor-pointer transition-all',
                form.writer_level_id === level.id
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="font-semibold text-gray-900">{{ level.name }}</div>
              <div class="text-sm text-gray-600 mt-1">{{ level.description || 'Standard quality' }}</div>
              <div v-if="level.value > 0" class="text-primary-600 font-medium mt-2">
                +${{ parseFloat(level.value).toFixed(2) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Services -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Additional Services (Optional)
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="service in additionalServices"
              :key="service.id"
              @click="toggleService(service.id)"
              :class="[
                'border-2 rounded-lg p-4 cursor-pointer transition-all',
                selectedServices.includes(service.id)
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="font-semibold text-gray-900">{{ service.name }}</div>
                  <div v-if="service.description" class="text-sm text-gray-600 mt-1">
                    {{ service.description }}
                  </div>
                </div>
                <div v-if="service.price > 0" class="text-primary-600 font-medium ml-4">
                  +${{ parseFloat(service.price).toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Updated Price Preview -->
        <div v-if="updatedQuote" class="bg-gray-50 rounded-lg p-4">
          <div class="flex justify-between items-center">
            <span class="font-medium text-gray-700">Updated Total:</span>
            <span class="text-2xl font-bold text-primary-600">
              ${{ parseFloat(updatedQuote.total_price || 0).toFixed(2) }}
            </span>
      </div>
      </div>

        <!-- Navigation -->
        <div class="flex justify-between gap-3 pt-4 border-t">
          <button
            @click="currentStep = 3"
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            ← Back
          </button>
          <button
            @click="validateStep4"
            :disabled="loading"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            Next: Checkout →
        </button>
        </div>
      </div>
    </div>
      </div>

      <!-- Live Summary Panel (Sticky Sidebar) -->
      <div class="lg:col-span-1">
        <div class="sticky top-6 bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>📋</span>
            <span>Order Summary</span>
          </h3>
          
          <!-- Order Details -->
          <div class="space-y-4 mb-6">
            <div v-if="form.topic" class="pb-3 border-b">
              <div class="text-xs text-gray-500 mb-1">Topic</div>
              <div class="text-sm font-medium text-gray-900 line-clamp-2">{{ form.topic }}</div>
            </div>
            
            <div class="space-y-2 text-sm">
              <div v-if="form.paper_type_id" class="flex justify-between">
                <span class="text-gray-600">Paper Type:</span>
                <span class="font-medium">{{ getPaperTypeName(form.paper_type_id) }}</span>
              </div>
              
              <div v-if="form.academic_level_id" class="flex justify-between">
                <span class="text-gray-600">Academic Level:</span>
                <span class="font-medium">{{ getAcademicLevelName(form.academic_level_id) }}</span>
              </div>
              
              <div v-if="form.type_of_work_id" class="flex justify-between">
                <span class="text-gray-600">Type of Work:</span>
                <span class="font-medium">{{ getTypeOfWorkName(form.type_of_work_id) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-gray-600">Pages:</span>
                <span class="font-medium">{{ form.number_of_pages || 0 }}</span>
              </div>
              
              <div v-if="form.number_of_slides > 0" class="flex justify-between">
                <span class="text-gray-600">Slides:</span>
                <span class="font-medium">{{ form.number_of_slides }}</span>
              </div>
              
              <div v-if="form.client_deadline" class="flex justify-between">
                <span class="text-gray-600">Deadline:</span>
                <span class="font-medium text-xs">{{ formatDateTime(form.client_deadline) }}</span>
              </div>
              
              <div v-if="form.preferred_writer_id" class="flex justify-between">
                <span class="text-gray-600">Writer:</span>
                <span class="font-medium text-xs">{{ getWriterName(form.preferred_writer_id) }}</span>
              </div>
              
              <div v-if="form.writer_level_id" class="flex justify-between">
                <span class="text-gray-600">Writer Level:</span>
                <span class="font-medium">{{ getWriterLevelName(form.writer_level_id) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Selected Extra Services -->
          <div v-if="selectedServices.length > 0" class="mb-6 pb-4 border-b">
            <div class="text-xs text-gray-500 mb-2">Extra Services:</div>
            <div class="space-y-1">
              <div
                v-for="serviceId in selectedServices"
                :key="serviceId"
                class="flex items-center justify-between text-xs"
              >
                <span class="text-gray-700">{{ getServiceName(serviceId) }}</span>
                <span class="font-medium text-gray-900">${{ getServicePrice(serviceId).toFixed(2) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Pricing Breakdown -->
          <div v-if="quote || updatedQuote || finalQuote" class="space-y-2 mb-4">
            <div class="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Pricing</div>
            
            <div v-if="currentQuote?.base_price" class="flex justify-between text-sm">
              <span class="text-gray-600">Base Price:</span>
              <span class="font-medium">${{ parseFloat(currentQuote.base_price || 0).toFixed(2) }}</span>
            </div>
            
            <div v-if="currentQuote?.extra_services_price > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Extra Services:</span>
              <span class="font-medium">${{ parseFloat(currentQuote.extra_services_price || 0).toFixed(2) }}</span>
            </div>
            
            <div v-if="currentQuote?.writer_level_price > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Writer Level:</span>
              <span class="font-medium">${{ parseFloat(currentQuote.writer_level_price || 0).toFixed(2) }}</span>
            </div>
            
            <div v-if="currentQuote?.preferred_writer_price > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Preferred Writer:</span>
              <span class="font-medium">${{ parseFloat(currentQuote.preferred_writer_price || 0).toFixed(2) }}</span>
            </div>
            
            <div v-if="currentQuote?.discount_amount > 0" class="flex justify-between text-sm text-green-600">
              <span>Discount:</span>
              <span class="font-medium">-${{ parseFloat(currentQuote.discount_amount || 0).toFixed(2) }}</span>
            </div>
            
            <div class="border-t pt-2 mt-2 flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span class="text-primary-600">${{ parseFloat(currentQuote?.total_price || 0).toFixed(2) }}</span>
            </div>
          </div>
          
          <!-- Placeholder when no pricing yet -->
          <div v-else class="mb-4 p-4 bg-gray-50 rounded-lg text-center text-sm text-gray-500">
            <div class="mb-2">💡</div>
            <div>Fill in order details to see pricing</div>
          </div>
          
          <!-- Discount Code Section -->
          <div v-if="currentStep >= 3" class="mb-4 pb-4 border-b">
            <div class="text-xs text-gray-500 mb-2">Discount Code</div>
            <div class="flex gap-2">
              <input
                v-model="discountCode"
                type="text"
                placeholder="Enter code"
                class="flex-1 text-sm border rounded px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                @keyup.enter="applyDiscount"
              />
              <button
                @click="applyDiscount"
                :disabled="validatingDiscount || !discountCode"
                class="px-3 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                Apply
              </button>
            </div>
            <div v-if="discountMessage" class="mt-2 text-xs" :class="discountValid ? 'text-green-600' : 'text-red-600'">
              {{ discountMessage }}
            </div>
          </div>
          
          <!-- Progress Indicator -->
          <div class="mt-4 pt-4 border-t">
            <div class="text-xs text-gray-500 mb-2">Progress</div>
            <div class="flex items-center gap-2">
              <div class="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${(currentStep / steps.length) * 100}%` }"
                ></div>
              </div>
              <span class="text-xs font-medium text-gray-700">{{ currentStep }}/{{ steps.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 5: Checkout (Full Width) -->
    <div v-if="currentStep === 5" class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Checkout & Payment</h2>
      <div class="space-y-6">
        <!-- Order Summary -->
        <div class="bg-gray-50 rounded-lg p-6 space-y-4">
          <h3 class="font-semibold text-gray-900">Order Summary</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Topic:</span>
              <span class="font-medium">{{ form.topic }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Paper Type:</span>
              <span class="font-medium">{{ getPaperTypeName(form.paper_type_id) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Pages:</span>
              <span class="font-medium">{{ form.number_of_pages }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Deadline:</span>
              <span class="font-medium">{{ formatDateTime(form.client_deadline) }}</span>
            </div>
            <div v-if="form.preferred_writer_id" class="flex justify-between">
              <span class="text-gray-600">Preferred Writer:</span>
              <span class="font-medium">{{ getWriterName(form.preferred_writer_id) }}</span>
            </div>
            <div class="border-t pt-2 flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span class="text-primary-600">${{ parseFloat(finalQuote?.total_price || updatedQuote?.total_price || quote?.total_price || 0).toFixed(2) }}</span>
            </div>
          </div>
      </div>

        <!-- Payment Options -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-4">Payment Method</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              @click="payWithWallet"
              :disabled="paying || !walletBalance || walletBalance < parseFloat(finalQuote?.total_price || updatedQuote?.total_price || quote?.total_price || 0)"
              class="p-6 border-2 rounded-lg text-left transition-all"
              :class="
                paying || !walletBalance || walletBalance < parseFloat(finalQuote?.total_price || updatedQuote?.total_price || quote?.total_price || 0)
                  ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                  : 'border-primary-600 bg-primary-50 hover:bg-primary-100 cursor-pointer'
              "
            >
              <div class="font-semibold text-gray-900 mb-1">Pay from Wallet</div>
              <div class="text-sm text-gray-600">
                Balance: ${{ parseFloat(walletBalance || 0).toFixed(2) }}
              </div>
              <div v-if="walletBalance && walletBalance < parseFloat(finalQuote?.total_price || updatedQuote?.total_price || quote?.total_price || 0)" class="text-xs text-red-600 mt-2">
                Insufficient balance. Top up your wallet first.
              </div>
        </button>
            <button
              @click="payWithCard"
              :disabled="paying"
              class="p-6 border-2 rounded-lg text-left transition-all"
              :class="
                paying
                  ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                  : 'border-gray-300 hover:border-primary-600 hover:bg-gray-50 cursor-pointer'
              "
            >
              <div class="font-semibold text-gray-900 mb-1">Pay with Card</div>
              <div class="text-sm text-gray-600">Credit/Debit card via secure payment gateway</div>
        </button>
      </div>
        </div>

        <!-- Payment Status -->
        <div v-if="paymentMessage" class="p-4 rounded" :class="paymentSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
        {{ paymentMessage }}
      </div>

        <!-- Navigation -->
        <div class="flex justify-between gap-3 pt-4 border-t">
          <button
            @click="currentStep = 4"
            :disabled="paying || createdOrder"
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
          >
            ← Back
          </button>
          <div v-if="createdOrder" class="flex gap-3">
            <router-link
              :to="`/orders/${createdOrder.id}`"
              class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              View Order
            </router-link>
            <router-link
              to="/orders"
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              My Orders
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ordersAPI from '@/api/orders'
import orderConfigsAPI from '@/api/orderConfigs'
import pricingAPI from '@/api/pricing'
import walletAPI from '@/api/wallet'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import Tooltip from '@/components/common/Tooltip.vue'
import { formatWriterName } from '@/utils/formatDisplay'

const router = useRouter()

const steps = [
  { title: 'Task Details', subtitle: 'Basic information' },
  { title: 'Instructions', subtitle: 'Paper requirements' },
  { title: 'Pricing', subtitle: 'Calculate cost' },
  { title: 'Services', subtitle: 'Additional options' },
  { title: 'Checkout', subtitle: 'Payment' }
]

const currentStep = ref(1)
const loading = ref(false)
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

// Form data
const form = ref({
  topic: '',
  paper_type_id: null,
  academic_level_id: null,
  subject_id: null,
  type_of_work_id: null,
  number_of_pages: 1,
  number_of_slides: 0,
  number_of_references: 0,
  client_deadline: '',
  order_instructions: '',
  formatting_style_id: null,
  english_type_id: null,
  spacing: '',
  additional_notes: '',
  preferred_writer_id: null,
  writer_level_id: null,
  discount_code: ''
})

// Configuration data
const paperTypes = ref([])
const academicLevels = ref([])
const subjects = ref([])
const typesOfWork = ref([])
const formattingStyles = ref([])
const englishTypes = ref([])
const writerLevels = ref([])
const additionalServices = ref([])
const preferredWriters = ref([])

// Pricing
const quote = ref(null)
const updatedQuote = ref(null)
const finalQuote = ref(null)
const quoteLoading = ref(false)
const discountCode = ref('')
const appliedDiscount = ref(null)
const discountValid = ref(false)
const discountMessage = ref('')
const validatingDiscount = ref(false)

// Additional services
const selectedServices = ref([])

// Payment
const walletBalance = ref(0)
const createdOrder = ref(null)
const paying = ref(false)
const paymentMessage = ref('')
const paymentSuccess = ref(false)

// Computed
const minDeadline = computed(() => {
  const now = new Date()
  now.setHours(now.getHours() + 1)
  return now.toISOString().slice(0, 16)
})

// Current quote for summary panel
const currentQuote = computed(() => {
  return finalQuote.value || updatedQuote.value || quote.value
})

// Helper functions for summary panel
const getAcademicLevelName = (id) => {
  const level = academicLevels.value.find(l => l.id === id)
  return level?.name || 'N/A'
}

const getTypeOfWorkName = (id) => {
  const type = typesOfWork.value.find(t => t.id === id)
  return type?.name || 'N/A'
}

const getWriterLevelName = (id) => {
  const level = writerLevels.value.find(l => l.id === id)
  return level?.name || 'N/A'
}

const getServiceName = (id) => {
  const service = additionalServices.value.find(s => s.id === id)
  return service?.service_name || service?.name || 'Unknown Service'
}

const getServicePrice = (id) => {
  const service = additionalServices.value.find(s => s.id === id)
  return parseFloat(service?.cost || service?.price || 0)
}

// Load configuration data
const loadConfigData = async () => {
  try {
    const [paperTypesRes, academicLevelsRes, subjectsRes, typesOfWorkRes, formattingStylesRes, englishTypesRes] = await Promise.all([
      orderConfigsAPI.getPaperTypes(),
      orderConfigsAPI.getAcademicLevels(),
      orderConfigsAPI.getSubjects(),
      orderConfigsAPI.getTypesOfWork(),
      orderConfigsAPI.getFormattingStyles(),
      orderConfigsAPI.getEnglishTypes()
    ])
    
    paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
    academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
    subjects.value = subjectsRes.data?.results || subjectsRes.data || []
    typesOfWork.value = typesOfWorkRes.data?.results || typesOfWorkRes.data || []
    formattingStyles.value = formattingStylesRes.data?.results || formattingStylesRes.data || []
    englishTypes.value = englishTypesRes.data?.results || englishTypesRes.data || []
  } catch (e) {
    console.error('Failed to load config data:', e)
    error.value = 'Failed to load order configuration. Please refresh the page.'
  }
}

const loadPricingData = async () => {
  try {
    const [writerLevelsRes, additionalServicesRes, preferredWritersRes] = await Promise.all([
      pricingAPI.getWriterLevels(),
      pricingAPI.getAdditionalServices(),
      ordersAPI.getPreferredWriters().catch(() => ({ data: [] })) // Fallback if endpoint doesn't exist
    ])
    
    writerLevels.value = writerLevelsRes.data?.results || writerLevelsRes.data || []
    additionalServices.value = additionalServicesRes.data?.results || additionalServicesRes.data || []
    preferredWriters.value = preferredWritersRes.data || []
  } catch (e) {
    console.error('Failed to load pricing data:', e)
  }
}

const loadWalletBalance = async () => {
  try {
    const res = await walletAPI.getWallet()
    walletBalance.value = parseFloat(res.data.wallet?.balance || res.data.balance || 0)
  } catch (e) {
    console.error('Failed to load wallet balance:', e)
  }
}

// Step validation
const validateStep1 = () => {
  if (!form.value.topic || !form.value.paper_type_id || !form.value.academic_level_id || 
      !form.value.subject_id || !form.value.number_of_pages || !form.value.client_deadline) {
    error.value = 'Please fill in all required fields'
    return
  }
  currentStep.value = 2
  error.value = ''
}

const validateStep2 = () => {
  if (!form.value.order_instructions) {
    error.value = 'Please provide detailed instructions'
    return
  }
  currentStep.value = 3
  error.value = ''
  calculatePrice()
}

const validateStep3 = () => {
  if (!quote.value) {
    error.value = 'Please wait for price calculation'
    return
  }
  currentStep.value = 4
  error.value = ''
  loadPricingData()
  updatePriceWithServices()
}

const validateStep4 = () => {
  currentStep.value = 5
  error.value = ''
  loadWalletBalance()
  updatePriceWithServices()
}

// Price calculation
const calculatePrice = async () => {
  quoteLoading.value = true
  error.value = ''
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
      writer_level_id: form.value.writer_level_id,
      extra_services: selectedServices.value
    }
    
    const res = await ordersAPI.quote(quoteData)
    quote.value = res.data
  } catch (e) {
    console.error('Failed to calculate price:', e)
    error.value = e?.response?.data?.detail || 'Failed to calculate price'
  } finally {
    quoteLoading.value = false
  }
}

const updatePriceWithServices = async () => {
  if (!quote.value) return
  
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
      writer_level_id: form.value.writer_level_id,
      extra_services: selectedServices.value
    }
    
    const res = await ordersAPI.quote(quoteData)
    updatedQuote.value = res.data
    finalQuote.value = res.data
  } catch (e) {
    console.error('Failed to update price:', e)
  } finally {
    quoteLoading.value = false
  }
}

const applyDiscount = async () => {
  if (!discountCode.value) return
  
  validatingDiscount.value = true
  discountMessage.value = ''
  discountValid.value = false
  
  try {
    // Recalculate price with discount code
    await calculatePrice()
    
    if (quote.value?.discount_amount > 0) {
      discountValid.value = true
      discountMessage.value = `Discount applied! You saved $${parseFloat(quote.value.discount_amount).toFixed(2)}`
      appliedDiscount.value = { code: discountCode.value }
    } else {
      discountValid.value = false
      discountMessage.value = 'Invalid or expired discount code. Please check and try again.'
    }
  } catch (e) {
    discountValid.value = false
    discountMessage.value = e?.response?.data?.detail || 'Failed to apply discount'
  } finally {
    validatingDiscount.value = false
  }
}

const toggleService = (serviceId) => {
  const index = selectedServices.value.indexOf(serviceId)
  if (index > -1) {
    selectedServices.value.splice(index, 1)
  } else {
    selectedServices.value.push(serviceId)
  }
  updatePriceWithServices()
}

// Create order and payment
const createOrder = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const orderData = {
      topic: form.value.topic,
      paper_type_id: form.value.paper_type_id,
      academic_level_id: form.value.academic_level_id,
      subject_id: form.value.subject_id,
      type_of_work_id: form.value.type_of_work_id,
      english_type_id: form.value.english_type_id,
      number_of_pages: form.value.number_of_pages,
      number_of_slides: form.value.number_of_slides || 0,
      number_of_references: form.value.number_of_references || 0,
      client_deadline: form.value.client_deadline,
      order_instructions: form.value.order_instructions,
      formatting_style_id: form.value.formatting_style_id,
      spacing: form.value.spacing,
      discount_code: appliedDiscount.value?.code || discountCode.value || '',
      preferred_writer_id: form.value.preferred_writer_id,
      writer_level_id: form.value.writer_level_id,
      extra_services: selectedServices.value
    }
    
    const res = await ordersAPI.createClient(orderData)
    createdOrder.value = res.data
    return res.data
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Failed to create order'
    throw e
  } finally {
    loading.value = false
  }
}

const payWithWallet = async () => {
  if (!createdOrder.value) {
    await createOrder()
  }
  
  if (!createdOrder.value) return
  
  paying.value = true
  paymentMessage.value = ''
  paymentSuccess.value = false
  
  try {
    const res = await ordersAPI.payWithWallet(createdOrder.value.id)
    createdOrder.value = res.data
    paymentSuccess.value = true
    paymentMessage.value = 'Payment successful! Your order has been placed.'
    message.value = 'Order created and paid successfully!'
    messageSuccess.value = true
  } catch (e) {
    paymentMessage.value = e?.response?.data?.detail || 'Payment failed. Please try again.'
    error.value = paymentMessage.value
  } finally {
    paying.value = false
  }
}

const payWithCard = async () => {
  if (!createdOrder.value) {
    await createOrder()
  }
  
  if (!createdOrder.value) return
  
  paying.value = true
  paymentMessage.value = 'Redirecting to payment gateway...'
  
  // TODO: Integrate with payment gateway
  setTimeout(() => {
    paymentMessage.value = 'Payment gateway integration pending. Please contact support.'
  paying.value = false
  }, 1000)
}

// Helper functions
const getPaperTypeName = (id) => {
  const pt = paperTypes.value.find(p => p.id === id)
  return pt?.name || 'N/A'
}

const getWriterName = (id) => {
  const writer = preferredWriters.value.find(w => w.id === id)
  return writer ? formatWriterName(writer) : 'N/A'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Watch for changes that affect pricing - auto-calculate for summary panel
import { watch } from 'vue'
watch([
  () => form.value.number_of_pages,
  () => form.value.number_of_slides,
  () => form.value.paper_type_id,
  () => form.value.academic_level_id,
  () => form.value.type_of_work_id,
  () => form.value.client_deadline,
  () => form.value.preferred_writer_id,
  () => form.value.writer_level_id,
  () => selectedServices.value
], () => {
  // Auto-calculate price when key fields change (after step 1)
  if (currentStep.value >= 1 && form.value.number_of_pages > 0 && form.value.client_deadline) {
    // Debounce to avoid too many API calls
    clearTimeout(window.priceCalculationTimeout)
    window.priceCalculationTimeout = setTimeout(() => {
      calculatePrice()
    }, 500)
  }
}, { deep: true })

onMounted(async () => {
  await Promise.all([loadConfigData(), loadWalletBalance()])
})
</script>
