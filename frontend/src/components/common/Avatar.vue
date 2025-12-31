<template>
  <div 
    class="avatar" 
    :class="[sizeClass, shapeClass]"
    :style="avatarStyle"
  >
    <img 
      v-if="safeImageUrl && !imageError" 
      :src="safeImageUrl" 
      :alt="alt || initials"
      @error="handleImageError"
      @load="handleImageLoad"
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

// Validate image URL format - be more lenient to allow various URL formats
const isValidImageUrl = computed(() => {
  if (!props.imageUrl) return false
  
  // Check if it's a data URL (base64 image)
  if (props.imageUrl.startsWith('data:image/')) {
    return true
  }
  
  // Check if it has image file extension
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
  const lowerUrl = props.imageUrl.toLowerCase()
  const hasImageExtension = imageExtensions.some(ext => lowerUrl.includes(ext))
  
  // Also check for common image path patterns (be more lenient)
  const imagePathPatterns = [
    '/media/profile_pictures/', '/media/avatars/', '/static/images/', 
    '/media/', '/static/', 'profile_picture', 'avatar', 'image', 'photo', 'picture'
  ]
  const hasImagePath = imagePathPatterns.some(pattern => lowerUrl.includes(pattern))
  
  // If it's an HTTP/HTTPS URL without extension but has image path, allow it
  const isHttpUrl = props.imageUrl.startsWith('http://') || props.imageUrl.startsWith('https://') || props.imageUrl.startsWith('//')
  
  return hasImageExtension || hasImagePath || (isHttpUrl && hasImagePath)
})

// Computed image URL - only use if valid, otherwise show initials
const safeImageUrl = computed(() => {
  if (!props.imageUrl) return null
  
  // If URL doesn't look like an image, don't try to load it
  if (!isValidImageUrl.value) {
    return null
  }
  
  return props.imageUrl
})

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

const handleImageError = (event) => {
  // Silently handle image errors - just show initials instead
  imageError.value = true
  // Don't log to console to avoid noise
}

const handleImageLoad = (event) => {
  // Verify the loaded content is actually an image
  const img = event.target
  try {
    if (img.naturalWidth === 0 || img.naturalHeight === 0) {
      // Image has no dimensions, likely not a valid image
      imageError.value = true
    } else {
      imageError.value = false
    }
  } catch (e) {
    // If we can't check dimensions, assume it's valid
    imageError.value = false
  }
}

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

