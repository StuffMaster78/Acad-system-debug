# Order Communication Components

Reusable components for viewing and managing order messages and threads.

## Components

### OrderThreadsModal
Displays all message threads for a specific order.

**Props:**
- `orderId` (Number|String, required) - The order ID

**Events:**
- `close` - Emitted when modal is closed

**Usage:**
```vue
<template>
  <button @click="showThreads = true">View Threads</button>
  
  <OrderThreadsModal
    v-if="showThreads"
    :order-id="orderId"
    @close="showThreads = false"
  />
</template>

<script setup>
import { ref } from 'vue'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'

const showThreads = ref(false)
const orderId = ref(123)
</script>
```

### OrderMessagesModal
Displays messages within a specific thread and allows sending new messages.

**Props:**
- `thread` (Object, required) - The thread object
- `orderId` (Number|String, required) - The order ID

**Events:**
- `close` - Emitted when modal is closed
- `thread-updated` - Emitted when thread is updated (e.g., enabled)

**Usage:**
```vue
<template>
  <OrderMessagesModal
    v-if="selectedThread"
    :thread="selectedThread"
    :order-id="orderId"
    @close="selectedThread = null"
    @thread-updated="handleThreadUpdate"
  />
</template>

<script setup>
import { ref } from 'vue'
import OrderMessagesModal from '@/components/order/OrderMessagesModal.vue'

const selectedThread = ref(null)
const orderId = ref(123)
</script>
```

## Integration Example

To add these modals to an order detail view:

```vue
<template>
  <div>
    <!-- Order details -->
    <div>
      <h2>Order #{{ order.id }}</h2>
      <!-- Other order info -->
    </div>

    <!-- Button to open threads modal -->
    <button @click="showThreadsModal = true" class="btn btn-primary">
      View Messages
    </button>

    <!-- Threads Modal -->
    <OrderThreadsModal
      v-if="showThreadsModal"
      :order-id="order.id"
      @close="showThreadsModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'

const order = ref({ id: 123 })
const showThreadsModal = ref(false)
</script>
```

