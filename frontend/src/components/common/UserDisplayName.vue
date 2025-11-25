<template>
  <span class="font-medium">{{ displayName }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  showRegistrationId: {
    type: Boolean,
    default: false
  }
})

const authStore = useAuthStore()

const displayName = computed(() => {
  // Admins see full info
  if (authStore.isAdmin || authStore.isSuperAdmin) {
    return props.user.username || props.user.email || `User #${props.user.id}`
  }
  
  // Privacy-aware display based on roles
  if (props.user.role === 'writer') {
    // For writers: show pen_name or registration_id
    if (props.user.pen_name) {
      return props.user.pen_name
    }
    if (props.user.registration_id) {
      return props.user.registration_id
    }
    return `Writer #${props.user.id}`
  }
  
  if (props.user.role === 'client') {
    // For clients: show registration_id
    if (props.user.registration_id) {
      return props.user.registration_id
    }
    return `Client #${props.user.id}`
  }
  
  // Fallback
  return props.user.username || props.user.email || `User #${props.user.id}`
})
</script>

