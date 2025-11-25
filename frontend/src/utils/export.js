/**
 * Utility functions for exporting data to CSV
 */

export const exportToCSV = (data, filename, headers = null) => {
  if (!data || !data.length) {
    console.warn('No data to export')
    return
  }

  // Use provided headers or extract from first row
  const csvHeaders = headers || Object.keys(data[0])
  
  // Create CSV content
  let csv = csvHeaders.join(',') + '\n'
  
  data.forEach(row => {
    const values = csvHeaders.map(header => {
      const value = row[header]
      // Handle nested properties (e.g., user.email)
      const nestedValue = header.includes('.') 
        ? header.split('.').reduce((obj, key) => obj?.[key], row)
        : value
      
      // Format value for CSV
      if (nestedValue === null || nestedValue === undefined) return ''
      if (typeof nestedValue === 'string' && nestedValue.includes(',')) {
        return `"${nestedValue.replace(/"/g, '""')}"`
      }
      return nestedValue
    })
    csv += values.join(',') + '\n'
  })
  
  // Create and download file
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

export const exportTableData = (data, columns, filename) => {
  if (!data || !data.length) {
    console.warn('No data to export')
    return
  }

  const headers = columns.map(col => col.label || col.key)
  const keys = columns.map(col => col.key)
  
  let csv = headers.join(',') + '\n'
  
  data.forEach(row => {
    const values = keys.map(key => {
      const value = row[key]
      if (value === null || value === undefined) return ''
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value
    })
    csv += values.join(',') + '\n'
  })
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

