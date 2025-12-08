# Frontend Performance Optimization Guide

## 🎯 Overview

This guide covers the frontend performance optimizations implemented to improve load times, reduce bundle sizes, and enhance user experience.

## ✨ Implemented Optimizations

### 1. Image Lazy Loading

#### LazyImage Component
**File**: `frontend/src/components/common/LazyImage.vue`

A comprehensive lazy loading image component with:
- Intersection Observer API for efficient loading
- Placeholder support with skeleton/spinner
- Fade-in animations
- Responsive image support (srcset, sizes)
- Error handling
- Eager loading option for above-the-fold images

**Usage**:
```vue
<template>
  <LazyImage
    :src="imageUrl"
    alt="Description"
    :eager="false"
    :fade-in="true"
    :show-spinner="true"
    aspect-ratio="16/9"
    class="w-full rounded-lg"
  />
</template>

<script setup>
import LazyImage from '@/components/common/LazyImage.vue'
</script>
```

#### Lazy Image Directive
**File**: `frontend/src/directives/lazyImage.js`

A simpler directive for basic lazy loading:
```vue
<template>
  <img v-lazy-image="imageUrl" alt="Description" />
  <img v-lazy-image.eager="imageUrl" alt="Above fold" />
</template>
```

### 2. Component Lazy Loading

#### useLazyComponent Composable
**File**: `frontend/src/composables/useLazyComponent.js`

Utilities for lazy loading Vue components:

```javascript
import { useLazyComponent, useLazyComponentWithSpinner } from '@/composables/useLazyComponent'

// Basic lazy component
const MyComponent = useLazyComponent(() => import('@/components/MyComponent.vue'))

// With loading spinner
const MyComponent = useLazyComponentWithSpinner(() => import('@/components/MyComponent.vue'))

// With error handling
const MyComponent = useLazyComponentWithError(
  () => import('@/components/MyComponent.vue'),
  () => retryLoad()
)
```

### 3. Enhanced Code Splitting

#### Vite Configuration
**File**: `frontend/vite.config.js`

Optimized build configuration with:
- **Granular vendor chunking**: Separates Vue core, router, Pinia, HTTP client, editors, charts
- **Route-based splitting**: Separate chunks for admin, writers, clients, editors, support
- **Component-based splitting**: Large components (editors, media) in separate chunks
- **Tree shaking**: Removes unused code
- **Production optimizations**: Removes console logs, minifies code

**Chunk Strategy**:
- `vendor-vue-core`: Vue framework
- `vendor-vue-router`: Vue Router
- `vendor-pinia`: State management
- `vendor-http`: Axios
- `vendor-quill`: Rich text editor
- `vendor-charts`: ApexCharts
- `vendor-forms`: Form validation
- `vendor-ui`: UI libraries
- `chunk-admin`: Admin views
- `chunk-writers`: Writer views
- `chunk-client`: Client views
- `chunk-editor`: Editor views
- `chunk-support`: Support views
- `chunk-public`: Public pages

### 4. Production Build Optimizations

- **Console removal**: Automatically removes `console.log`, `console.info`, `console.debug` in production
- **Source maps**: Only generated in development
- **Minification**: esbuild for fast, efficient minification
- **Asset organization**: Images and fonts in separate directories
- **Cache busting**: Hash-based filenames for long-term caching

## 📊 Performance Impact

### Expected Improvements

1. **Initial Bundle Size**: 30-50% reduction
   - Before: ~2-3 MB
   - After: ~1-1.5 MB

2. **Time to Interactive**: 40-60% improvement
   - Before: 3-5 seconds
   - After: 1.5-2.5 seconds

3. **Image Loading**: 60-80% bandwidth savings
   - Only loads images when needed
   - Reduces initial page weight

4. **Code Splitting**: Faster route navigation
   - Only loads code for current route
   - Parallel chunk loading

## 🚀 Usage Examples

### Lazy Loading Images

#### Using Component
```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <LazyImage
      v-for="image in images"
      :key="image.id"
      :src="image.url"
      :alt="image.alt"
      :show-spinner="true"
      class="rounded-lg"
    />
  </div>
</template>

<script setup>
import LazyImage from '@/components/common/LazyImage.vue'
</script>
```

#### Using Directive
```vue
<template>
  <img
    v-lazy-image="imageUrl"
    alt="Description"
    class="w-full rounded-lg"
  />
</template>
```

### Lazy Loading Components

```vue
<template>
  <Suspense>
    <template #default>
      <HeavyComponent />
    </template>
    <template #fallback>
      <div class="flex items-center justify-center p-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'

const HeavyComponent = defineAsyncComponent(() => 
  import('@/components/HeavyComponent.vue')
)
</script>
```

### Route-Based Code Splitting

Routes are already lazy-loaded in `router/index.js`:
```javascript
{
  path: '/admin/users',
  component: () => import('@/views/admin/UserManagement.vue')
}
```

## 🔧 Configuration

### Vite Build Options

In `vite.config.js`:

```javascript
build: {
  // Production optimizations
  minify: process.env.NODE_ENV === 'production' ? 'esbuild' : false,
  sourcemap: process.env.NODE_ENV === 'development',
  
  // Chunk size warning
  chunkSizeWarningLimit: 500,
  
  // Target modern browsers
  target: 'es2015',
  
  // CSS code splitting
  cssCodeSplit: true
}
```

### Lazy Image Options

```vue
<LazyImage
  :src="imageUrl"
  :eager="false"              // Load immediately if true
  :root-margin="'50px'"       // Start loading 50px before visible
  :threshold="0.01"           // Load when 1% visible
  :fade-in="true"             // Fade in animation
  :show-spinner="true"        // Show loading spinner
  :decoding="'async'"         // Image decoding strategy
  aspect-ratio="16/9"         // Placeholder aspect ratio
/>
```

## 📈 Monitoring Performance

### Build Analysis

```bash
# Build and analyze bundle
npm run build

# Check bundle sizes
ls -lh dist/assets/
```

### Browser DevTools

1. **Network Tab**: Check chunk loading
2. **Performance Tab**: Measure load times
3. **Lighthouse**: Run performance audit

### Key Metrics

- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 300ms
- **Cumulative Layout Shift (CLS)**: < 0.1

## 🎯 Best Practices

### 1. Image Optimization

- Use `LazyImage` for below-the-fold images
- Use `eager` prop for above-the-fold images
- Provide proper `alt` text for accessibility
- Use appropriate image formats (WebP when possible)
- Set `aspect-ratio` to prevent layout shift

### 2. Component Loading

- Lazy load heavy components (charts, editors, modals)
- Use `Suspense` for better UX
- Preload critical components
- Batch preload related components

### 3. Route Optimization

- All routes are already lazy-loaded
- Group related routes for better chunking
- Avoid importing entire libraries in routes

### 4. Bundle Size

- Monitor chunk sizes (keep under 500KB)
- Split large dependencies
- Remove unused code
- Use tree shaking

## 🐛 Troubleshooting

### Images Not Loading

1. Check `src` is correct
2. Verify IntersectionObserver support
3. Check browser console for errors
4. Ensure image URLs are accessible

### Components Not Loading

1. Check import path is correct
2. Verify component exists
3. Check for circular dependencies
4. Review error component output

### Large Bundle Sizes

1. Analyze bundle with `vite-bundle-visualizer`
2. Check for duplicate dependencies
3. Verify code splitting is working
4. Remove unused imports

## 📚 Related Files

- `frontend/src/components/common/LazyImage.vue` - Lazy image component
- `frontend/src/directives/lazyImage.js` - Lazy image directive
- `frontend/src/composables/useLazyComponent.js` - Component lazy loading
- `frontend/vite.config.js` - Build configuration
- `frontend/src/router/index.js` - Route configuration

## ✅ Implementation Status

- ✅ LazyImage component
- ✅ Lazy image directive
- ✅ Component lazy loading composables
- ✅ Enhanced code splitting
- ✅ Production build optimizations
- ✅ Tree shaking
- ✅ Console removal in production

## 🔄 Migration Guide

### Migrating Existing Images

**Before**:
```vue
<img :src="imageUrl" alt="Description" />
```

**After**:
```vue
<LazyImage :src="imageUrl" alt="Description" />
```

Or with directive:
```vue
<img v-lazy-image="imageUrl" alt="Description" />
```

### Migrating Heavy Components

**Before**:
```vue
<script setup>
import HeavyComponent from '@/components/HeavyComponent.vue'
</script>
```

**After**:
```vue
<script setup>
import { useLazyComponentWithSpinner } from '@/composables/useLazyComponent'

const HeavyComponent = useLazyComponentWithSpinner(
  () => import('@/components/HeavyComponent.vue')
)
</script>
```

## 🎉 Benefits

1. **Faster Initial Load**: Smaller initial bundle
2. **Better UX**: Progressive loading with placeholders
3. **Reduced Bandwidth**: Images load only when needed
4. **Improved SEO**: Better Core Web Vitals scores
5. **Better Caching**: Smaller, focused chunks

