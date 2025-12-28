<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 px-4 py-12 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Floating circles -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div class="absolute top-40 right-10 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="max-w-4xl mx-auto text-center relative z-10">
      <!-- 404 Illustration -->
      <div class="mb-8 relative">
        <div class="inline-block">
          <!-- SVG Illustration -->
          <svg
            class="w-full max-w-md mx-auto"
            viewBox="0 0 600 400"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- Background Circle -->
            <circle
              cx="300"
              cy="200"
              r="180"
              fill="url(#gradient1)"
              opacity="0.1"
              class="animate-pulse"
            />
            
            <!-- Main 404 Text -->
            <text
              x="300"
              y="180"
              font-family="Arial, sans-serif"
              font-size="120"
              font-weight="bold"
              fill="url(#gradient2)"
              text-anchor="middle"
              class="animate-bounce"
            >
              404
            </text>
            
            <!-- Astronaut/Character Illustration -->
            <g transform="translate(200, 220)">
              <!-- Head -->
              <circle cx="100" cy="50" r="35" fill="#4F46E5" opacity="0.8" />
              <circle cx="90" cy="45" r="5" fill="white" />
              <circle cx="110" cy="45" r="5" fill="white" />
              <ellipse cx="100" cy="55" rx="8" ry="4" fill="white" />
              
              <!-- Body -->
              <ellipse cx="100" cy="100" rx="40" ry="50" fill="#6366F1" opacity="0.8" />
              
              <!-- Arms -->
              <ellipse cx="60" cy="90" rx="15" ry="40" fill="#6366F1" opacity="0.8" transform="rotate(-30 60 90)" />
              <ellipse cx="140" cy="90" rx="15" ry="40" fill="#6366F1" opacity="0.8" transform="rotate(30 140 90)" />
              
              <!-- Legs -->
              <ellipse cx="80" cy="150" rx="12" ry="30" fill="#4F46E5" opacity="0.8" />
              <ellipse cx="120" cy="150" rx="12" ry="30" fill="#4F46E5" opacity="0.8" />
            </g>
            
            <!-- Floating Elements -->
            <circle cx="100" cy="100" r="8" fill="#8B5CF6" opacity="0.6" class="animate-float">
              <animate attributeName="cy" values="100;80;100" dur="3s" repeatCount="indefinite" />
            </circle>
            <circle cx="500" cy="150" r="6" fill="#EC4899" opacity="0.6" class="animate-float">
              <animate attributeName="cy" values="150;130;150" dur="2.5s" repeatCount="indefinite" />
            </circle>
            <circle cx="80" cy="300" r="10" fill="#06B6D4" opacity="0.6" class="animate-float">
              <animate attributeName="cy" values="300;280;300" dur="3.5s" repeatCount="indefinite" />
            </circle>
            
            <!-- Gradients -->
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
              </linearGradient>
              <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#6366F1;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      <!-- Content -->
      <div class="space-y-6">
        <h1 class="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
          Oops! Page Not Found
        </h1>
        
        <p class="text-xl md:text-2xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          The page you're looking for seems to have wandered off into the digital void. 
          Don't worry, we'll help you find your way back!
        </p>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
          <router-link
            to="/dashboard"
            class="group relative px-8 py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
        Go to Dashboard
            <svg class="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>

          <button
            @click="goBack"
            class="px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl shadow-md hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300 flex items-center gap-2 border-2 border-gray-200 hover:border-primary-300"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Go Back
          </button>
        </div>

        <!-- Quick Links -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <p class="text-sm text-gray-500 mb-4">Or try one of these:</p>
          <div class="flex flex-wrap justify-center gap-4">
            <router-link
              to="/orders"
              class="text-primary-600 hover:text-primary-700 font-medium hover:underline transition-colors"
            >
              Orders
            </router-link>
            <router-link
              to="/profile"
              class="text-primary-600 hover:text-primary-700 font-medium hover:underline transition-colors"
            >
              Profile
            </router-link>
            <router-link
              to="/settings"
              class="text-primary-600 hover:text-primary-700 font-medium hover:underline transition-colors"
            >
              Settings
            </router-link>
            <router-link
              to="/help"
              class="text-primary-600 hover:text-primary-700 font-medium hover:underline transition-colors"
            >
              Help Center
      </router-link>
          </div>
        </div>

        <!-- Fun Fact -->
        <div class="mt-12 p-6 bg-white/60 backdrop-blur-sm rounded-2xl shadow-lg max-w-md mx-auto">
          <div class="flex items-start gap-4">
            <div class="shrink-0 w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-500 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="text-left">
              <h3 class="font-semibold text-gray-900 mb-1">Did you know?</h3>
              <p class="text-sm text-gray-600">
                The 404 error got its name from room 404 at CERN, where the web was born. 
                The room didn't exist, just like this page!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style>
