import { onMounted, onUnmounted } from 'vue'

/**
 * Global keyboard shortcuts composable
 * Provides a centralized way to handle keyboard shortcuts across the application
 */
export function useKeyboardShortcuts() {
  const shortcuts = new Map()
  const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPod|iPad/i.test(navigator.userAgent)

  /**
   * Register a keyboard shortcut
   * @param {string} key - The key combination (e.g., 'k', 'ctrl+k', 'cmd+s')
   * @param {Function} handler - The function to call when shortcut is pressed
   * @param {Object} options - Additional options
   * @param {boolean} options.preventDefault - Whether to prevent default behavior
   * @param {boolean} options.stopPropagation - Whether to stop event propagation
   * @param {string} options.description - Description for help menu
   */
  const register = (key, handler, options = {}) => {
    const normalizedKey = normalizeKey(key)
    const id = `${normalizedKey}-${Date.now()}-${Math.random()}`
    
    shortcuts.set(id, {
      key: normalizedKey,
      handler,
      preventDefault: options.preventDefault !== false,
      stopPropagation: options.stopPropagation === true,
      description: options.description || '',
      enabled: options.enabled !== false
    })

    return () => unregister(id)
  }

  /**
   * Unregister a keyboard shortcut
   */
  const unregister = (id) => {
    shortcuts.delete(id)
  }

  /**
   * Normalize key combination to a standard format
   */
  const normalizeKey = (key) => {
    return key.toLowerCase()
      .replace(/cmd|meta/g, isMac ? 'meta' : 'ctrl')
      .replace(/ctrl/g, 'ctrl')
      .replace(/\s+/g, '')
      .split('+')
      .sort()
      .join('+')
  }

  /**
   * Check if a key combination matches
   */
  const matches = (event, key) => {
    const normalized = normalizeKey(key)
    const parts = normalized.split('+')
    
    const modifiers = {
      ctrl: event.ctrlKey,
      meta: event.metaKey,
      shift: event.shiftKey,
      alt: event.altKey
    }

    const keyMatch = parts.includes(event.key.toLowerCase()) || 
                     parts.includes(event.code.toLowerCase())

    const modifierMatch = parts.every(part => {
      if (part === 'ctrl' || part === 'meta') return modifiers.ctrl || modifiers.meta
      if (part === 'shift') return modifiers.shift
      if (part === 'alt') return modifiers.alt
      return true
    })

    return keyMatch && modifierMatch && parts.length > 1
  }

  /**
   * Handle keyboard events
   */
  const handleKeyDown = (event) => {
    // Don't trigger shortcuts when typing in inputs, textareas, or contenteditable
    const target = event.target
    const isInput = target.tagName === 'INPUT' && target.type !== 'checkbox' && target.type !== 'radio'
    const isTextarea = target.tagName === 'TEXTAREA'
    const isContentEditable = target.isContentEditable
    
    // Allow shortcuts in search inputs (Cmd/Ctrl+K should work)
    const isSearchInput = target.tagName === 'INPUT' && 
                         (target.type === 'search' || 
                          target.placeholder?.toLowerCase().includes('search') ||
                          target.classList.contains('search-input'))

    if ((isInput || isTextarea || isContentEditable) && !isSearchInput) {
      return
    }

    for (const [, shortcut] of shortcuts.entries()) {
      if (!shortcut.enabled) continue

      if (matches(event, shortcut.key)) {
        if (shortcut.preventDefault) {
          event.preventDefault()
        }
        if (shortcut.stopPropagation) {
          event.stopPropagation()
        }
        
        try {
          shortcut.handler(event)
        } catch (error) {
          if (import.meta.env.DEV) {
            console.error(`Error executing keyboard shortcut ${shortcut.key}:`, error)
          }
        }
        break // Only trigger one shortcut per event
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
    shortcuts.clear()
  })

  /**
   * Get all registered shortcuts (for help menu)
   */
  const getShortcuts = () => {
    return Array.from(shortcuts.values()).map(s => ({
      key: s.key,
      description: s.description,
      enabled: s.enabled
    }))
  }

  return {
    register,
    unregister,
    getShortcuts,
    isMac
  }
}

