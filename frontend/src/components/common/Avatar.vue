<template>
  <div 
    class="avatar" 
    :class="[sizeClass, shapeClass]"
    :style="avatarStyle"
  >
    <img 
      v-if="imageUrl && !imageError" 
      :src="imageUrl" 
      :alt="alt || initials"
      @error="imageError = true"
      class="avatar-image"
    />
    <div v-else class="avatar-initials">
      {{ initials }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    default: null
  },
  name: {
    type: String,
    default: ''
  },
  firstName: {
    type: String,
    default: ''
  },
  lastName: {
    type: String,
    default: ''
  },
  username: {
    type: String,
    default: ''
  },
  email: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md', // xs, sm, md, lg, xl
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  shape: {
    type: String,
    default: 'circle', // circle, square
    validator: (value) => ['circle', 'square'].includes(value)
  },
  alt: {
    type: String,
    default: ''
  },
  bgColor: {
    type: String,
    default: null // If provided, will use this color instead of generated
  }
})

const imageError = ref(false)

const sizeClass = computed(() => {
  const sizes = {
    xs: 'avatar-xs',
    sm: 'avatar-sm',
    md: 'avatar-md',
    lg: 'avatar-lg',
    xl: 'avatar-xl'
  }
  return sizes[props.size] || sizes.md
})

const shapeClass = computed(() => {
  return props.shape === 'circle' ? 'avatar-circle' : 'avatar-square'
})

const initials = computed(() => {
  // Try to get initials from name, firstName/lastName, username, or email
  let text = ''
  
  if (props.firstName || props.lastName) {
    const first = (props.firstName || '').trim().charAt(0).toUpperCase()
    const last = (props.lastName || '').trim().charAt(0).toUpperCase()
    text = first + last
  } else if (props.name) {
    const parts = props.name.trim().split(/\s+/)
    if (parts.length >= 2) {
      text = parts[0].charAt(0).toUpperCase() + parts[parts.length - 1].charAt(0).toUpperCase()
    } else {
      text = parts[0].charAt(0).toUpperCase()
    }
  } else if (props.username) {
    text = props.username.trim().charAt(0).toUpperCase()
  } else if (props.email) {
    text = props.email.trim().charAt(0).toUpperCase()
  }
  
  return text || '?'
})

const avatarStyle = computed(() => {
  if (props.bgColor) {
    return { backgroundColor: props.bgColor }
  }
  
  // Generate a color based on the initials/name for consistency
  const colors = [
    '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
    '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#330867',
    '#5f72bd', '#9921e8', '#f5576c', '#4facfe', '#00f2fe'
  ]
  
  // Use a simple hash of the initials to pick a consistent color
  let hash = 0
  const text = initials.value
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash)
  }
  const colorIndex = Math.abs(hash) % colors.length
  
  return { backgroundColor: colors[colorIndex] }
})
</script>

<style scoped>
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-circle {
  border-radius: 50%;
}

.avatar-square {
  border-radius: 8px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

/* Size variants */
.avatar-xs {
  width: 24px;
  height: 24px;
  font-size: 10px;
}

.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.avatar-md {
  width: 100px;
  height: 100px;
  font-size: 36px;
}

.avatar-lg {
  width: 150px;
  height: 150px;
  font-size: 48px;
}

.avatar-xl {
  width: 200px;
  height: 200px;
  font-size: 64px;
}
</style>

