/**
 * Smart Currency Formatter Utility
 * Handles large numbers gracefully with dynamic formatting
 */

/**
 * Format currency with smart abbreviation
 * @param {number} amount - The amount to format
 * @param {object} options - Formatting options
 * @returns {object} - { display: string, full: string, abbreviated: boolean }
 */
export function formatSmartCurrency(amount, options = {}) {
  const {
    maxLength = 10,        // Max characters before abbreviating
    alwaysAbbreviate = false,  // Force abbreviation
    minDecimals = 0,       // Minimum decimal places
    maxDecimals = 2,       // Maximum decimal places
    locale = 'en-US'
  } = options

  if (amount === null || amount === undefined || isNaN(amount)) {
    return {
      display: '$0.00',
      full: '$0.00',
      abbreviated: false,
      raw: 0
    }
  }

  const absAmount = Math.abs(amount)
  const isNegative = amount < 0
  const prefix = isNegative ? '-$' : '$'

  // Full formatted value (for tooltips)
  const fullFormatted = prefix + absAmount.toLocaleString(locale, {
    minimumFractionDigits: minDecimals,
    maximumFractionDigits: maxDecimals
  })

  // Check if we need to abbreviate
  const needsAbbreviation = alwaysAbbreviate || fullFormatted.length > maxLength

  let displayValue = fullFormatted
  let abbreviated = false

  if (needsAbbreviation || absAmount >= 1000) {
    abbreviated = true
    
    if (absAmount >= 1_000_000_000_000) {
      // Trillions
      displayValue = prefix + (absAmount / 1_000_000_000_000).toFixed(2) + 'T'
    } else if (absAmount >= 1_000_000_000) {
      // Billions
      displayValue = prefix + (absAmount / 1_000_000_000).toFixed(2) + 'B'
    } else if (absAmount >= 1_000_000) {
      // Millions
      displayValue = prefix + (absAmount / 1_000_000).toFixed(2) + 'M'
    } else if (absAmount >= 100_000) {
      // Hundreds of thousands (use 1 decimal)
      displayValue = prefix + (absAmount / 1_000).toFixed(1) + 'K'
    } else if (absAmount >= 10_000) {
      // Ten thousands (use 1 decimal)
      displayValue = prefix + (absAmount / 1_000).toFixed(1) + 'K'
    } else if (absAmount >= 1_000) {
      // Thousands (use 2 decimals for precision)
      displayValue = prefix + (absAmount / 1_000).toFixed(2) + 'K'
    } else {
      // Less than 1000, show full
      displayValue = fullFormatted
      abbreviated = false
    }
  }

  return {
    display: displayValue,
    full: fullFormatted,
    abbreviated,
    raw: amount
  }
}

/**
 * Get font size class based on value length
 * @param {string} value - The display value
 * @param {string} baseSize - Base size class
 * @returns {string} - Tailwind font size class
 */
export function getDynamicFontSize(value, baseSize = 'text-3xl') {
  const length = value.length
  
  if (length <= 8) {
    return baseSize  // Full size: text-3xl, text-2xl, etc.
  } else if (length <= 12) {
    // Reduce by one step
    const sizeMap = {
      'text-4xl': 'text-3xl',
      'text-3xl': 'text-2xl',
      'text-2xl': 'text-xl',
      'text-xl': 'text-lg',
    }
    return sizeMap[baseSize] || 'text-2xl'
  } else if (length <= 16) {
    // Reduce by two steps
    const sizeMap = {
      'text-4xl': 'text-2xl',
      'text-3xl': 'text-xl',
      'text-2xl': 'text-lg',
      'text-xl': 'text-base',
    }
    return sizeMap[baseSize] || 'text-xl'
  } else {
    // Reduce by three steps (very long)
    const sizeMap = {
      'text-4xl': 'text-xl',
      'text-3xl': 'text-lg',
      'text-2xl': 'text-base',
      'text-xl': 'text-sm',
    }
    return sizeMap[baseSize] || 'text-lg'
  }
}

/**
 * Format currency for specific contexts
 */
export const currencyFormatters = {
  // Dashboard primary metrics (max 10 chars)
  dashboard: (amount) => formatSmartCurrency(amount, { 
    maxLength: 10, 
    minDecimals: 0,
    maxDecimals: 2 
  }),

  // Stat cards (max 12 chars)
  statCard: (amount) => formatSmartCurrency(amount, { 
    maxLength: 12,
    minDecimals: 0,
    maxDecimals: 2
  }),

  // Tables (max 15 chars, more precision)
  table: (amount) => formatSmartCurrency(amount, { 
    maxLength: 15,
    minDecimals: 2,
    maxDecimals: 2
  }),

  // Compact (always abbreviate)
  compact: (amount) => formatSmartCurrency(amount, { 
    alwaysAbbreviate: true,
    minDecimals: 0,
    maxDecimals: 2
  }),

  // Full (never abbreviate)
  full: (amount) => {
    const formatted = amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
    return {
      display: '$' + formatted,
      full: '$' + formatted,
      abbreviated: false,
      raw: amount
    }
  }
}

/**
 * Get appropriate formatting based on card size
 * @param {number} amount 
 * @param {string} cardSize - 'sm', 'md', 'lg', 'xl'
 * @returns {object}
 */
export function formatCurrencyByCardSize(amount, cardSize = 'md') {
  const maxLengths = {
    sm: 8,   // Small cards: very compact
    md: 10,  // Medium cards: standard
    lg: 12,  // Large cards: more room
    xl: 15   // Extra large: most room
  }

  return formatSmartCurrency(amount, {
    maxLength: maxLengths[cardSize] || 10,
    minDecimals: 0,
    maxDecimals: 2
  })
}

/**
 * Format percentage change with sign
 * @param {number} value 
 * @returns {string}
 */
export function formatPercentageChange(value) {
  if (value === null || value === undefined || isNaN(value)) return '0%'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

/**
 * Format number with K/M/B abbreviation
 * @param {number} value 
 * @returns {string}
 */
export function formatNumber(value) {
  const num = parseInt(value || 0)
  if (num >= 1_000_000_000) {
    return (num / 1_000_000_000).toFixed(1) + 'B'
  }
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(1) + 'M'
  }
  if (num >= 1_000) {
    return (num / 1_000).toFixed(1) + 'K'
  }
  return num.toLocaleString()
}

export default {
  formatSmartCurrency,
  getDynamicFontSize,
  currencyFormatters,
  formatCurrencyByCardSize,
  formatPercentageChange,
  formatNumber
}
