<template>
  <div id="app">
    <router-view />
    <!-- Session timeout warning (optional) -->
    <div v-if="sessionStatus?.should_warn" class="session-warning">
      <p>Your session will expire in {{ Math.floor(sessionStatus.remaining_seconds / 60) }} minutes.</p>
      <button @click="extendSession" class="btn btn-primary btn-sm">Extend Session</button>
    </div>
  </div>
</template>

<script>
import { useSessionManagement } from '@/composables/useSessionManagement'

export default {
  name: 'App',
  setup() {
    // Initialize session management globally
    // This will automatically poll the status endpoint with rate limiting
    const { sessionStatus, extendSession } = useSessionManagement({
      checkInterval: 60000, // Check every 60 seconds
      autoExtend: true // Automatically extend when needed
    })
    
    return {
      sessionStatus,
      extendSession
    }
  }
}
</script>

<style>
@import './styles/dashboard.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  /* Prevent font size adjustment on iOS */
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1f2937;
  background: #f9fafb;
  font-size: 16px; /* Base font size for mobile readability */
  line-height: 1.5;
  /* Prevent text selection on buttons for better mobile UX */
  -webkit-tap-highlight-color: transparent;
  /* Stripe-like font rendering */
  font-feature-settings: 'kern' 1, 'liga' 1;
  text-rendering: optimizeLegibility;
}

#app {
  min-height: 100vh;
  width: 100%;
}

/* Global utility classes */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px; /* Minimum 16px to prevent iOS zoom on focus */
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  /* Touch-friendly minimum size (44x44px) */
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  /* Better touch targets */
  touch-action: manipulation;
  user-select: none;
  -webkit-user-select: none;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled),
.btn-primary:active:not(:disabled) {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled),
.btn-secondary:active:not(:disabled) {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-block {
  width: 100%;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 14px;
  min-height: 36px;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.error {
  background: #fee;
  color: #c33;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 20px 0;
  font-size: 14px;
  line-height: 1.5;
}

.success {
  background: #d4edda;
  color: #155724;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 20px 0;
  font-size: 14px;
  line-height: 1.5;
}

/* Form inputs - mobile optimized */
input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
input[type="tel"],
input[type="url"],
textarea,
select {
  font-size: 16px; /* Prevents iOS zoom on focus */
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: border-color 0.3s, box-shadow 0.3s;
  -webkit-appearance: none;
  appearance: none;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Responsive typography */
h1 {
  font-size: clamp(24px, 5vw, 32px);
  line-height: 1.2;
}

h2 {
  font-size: clamp(20px, 4vw, 28px);
  line-height: 1.3;
}

h3 {
  font-size: clamp(18px, 3.5vw, 24px);
  line-height: 1.4;
}

/* Container utilities */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.container-sm {
  max-width: 768px;
}

.container-lg {
  max-width: 1400px;
}

/* Responsive utilities */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  
  body {
    font-size: 15px;
  }
  
  .btn {
    padding: 14px 20px; /* Larger touch targets on mobile */
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 12px;
  }
  
  .btn {
    padding: 12px 16px;
    width: 100%; /* Full width buttons on small screens */
  }
  
  .btn:not(.btn-block) {
    width: auto;
  }
}

/* Safe area insets for notched devices */
@supports (padding: max(0px)) {
  body {
    padding-left: max(0px, env(safe-area-inset-left));
    padding-right: max(0px, env(safe-area-inset-right));
  }
}

/* Session warning banner */
.session-warning {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 400px;
}

.session-warning p {
  margin: 0;
  color: #856404;
  font-size: 14px;
  flex: 1;
}

.session-warning .btn-sm {
  padding: 8px 16px;
  font-size: 14px;
  min-height: 36px;
}

@media (max-width: 480px) {
  .session-warning {
    bottom: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
    flex-direction: column;
    align-items: stretch;
  }
  
  .session-warning .btn-sm {
    width: 100%;
  }
}

/* Print styles */
@media print {
  body {
    background: white;
  }
  
  .btn {
    display: none;
  }
  
  .session-warning {
    display: none;
  }
}
</style>

