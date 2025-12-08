/**
 * Mock API for Guest Checkout
 * Use this for testing/development without backend
 */

// Mock delay to simulate API calls
const delay = (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms))

// Mock data
const mockPaperTypes = [
  { id: 1, name: 'Essay', website: 1 },
  { id: 2, name: 'Research Paper', website: 1 },
  { id: 3, name: 'Dissertation', website: 1 },
  { id: 4, name: 'Thesis', website: 1 },
  { id: 5, name: 'Case Study', website: 1 }
]

const mockAcademicLevels = [
  { id: 1, name: 'High School', website: 1 },
  { id: 2, name: 'Undergraduate', website: 1 },
  { id: 3, name: 'Master\'s', website: 1 },
  { id: 4, name: 'PhD', website: 1 }
]

const mockFormattingStyles = [
  { id: 1, name: 'APA', website: 1 },
  { id: 2, name: 'MLA', website: 1 },
  { id: 3, name: 'Chicago', website: 1 },
  { id: 4, name: 'Harvard', website: 1 },
  { id: 5, name: 'IEEE', website: 1 }
]

const mockTypesOfWork = [
  { id: 1, name: 'Writing', website: 1 },
  { id: 2, name: 'Editing', website: 1 },
  { id: 3, name: 'Proofreading', website: 1 },
  { id: 4, name: 'Rewriting', website: 1 }
]

const mockSubjects = [
  { id: 1, name: 'English', website: 1 },
  { id: 2, name: 'Mathematics', website: 1 },
  { id: 3, name: 'Science', website: 1 },
  { id: 4, name: 'History', website: 1 },
  { id: 5, name: 'Business', website: 1 },
  { id: 6, name: 'Psychology', website: 1 }
]

// Mock verification tokens (for testing)
const mockTokens = new Map()

// Generate a mock verification token
const generateMockToken = () => {
  return `mock_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export const mockGuestCheckoutAPI = {
  // Mock start guest order
  async startGuestOrder(data) {
    await delay(1500)
    
    const { email, website_id, order_data } = data
    
    // Validate required fields
    if (!email || !order_data?.topic || !order_data?.paper_type_id) {
      throw {
        response: {
          data: {
            detail: 'Missing required fields'
          }
        }
      }
    }

    // Simulate email verification requirement (50% chance)
    const requiresVerification = Math.random() > 0.5
    
    if (requiresVerification) {
      const token = generateMockToken()
      mockTokens.set(token, {
        email,
        website_id,
        order_data,
        created_at: new Date()
      })
      
      return {
        data: {
          verification_required: true,
          verification_token: token,
          message: 'Verification email sent (mock)'
        }
      }
    } else {
      // Simulate immediate order creation
      const orderId = Math.floor(Math.random() * 10000) + 1000
      return {
        data: {
          verification_required: false,
          order_id: orderId,
          message: 'Order created successfully (mock)'
        }
      }
    }
  },

  // Mock verify email
  async verifyGuestEmail(data) {
    await delay(1200)
    
    const { verification_token, website_id, order_data } = data
    
    // Check if token exists
    if (!mockTokens.has(verification_token)) {
      throw {
        response: {
          data: {
            detail: 'Invalid or expired verification token'
          }
        }
      }
    }

    // Remove token (one-time use)
    mockTokens.delete(verification_token)
    
    // Generate order ID
    const orderId = Math.floor(Math.random() * 10000) + 1000
    
    return {
      data: {
        order_id: orderId,
        message: 'Email verified and order created successfully (mock)'
      }
    }
  },

  // Mock price quote
  async quote(data) {
    await delay(800)
    
    const {
      paper_type_id,
      number_of_pages = 1,
      academic_level_id,
      type_of_work_id,
      client_deadline,
      discount_code
    } = data

    // Mock price calculation
    const basePricePerPage = 15
    const basePrice = number_of_pages * basePricePerPage
    
    // Academic level multiplier
    let levelMultiplier = 1.0
    if (academic_level_id === 3) levelMultiplier = 1.2 // Master's
    if (academic_level_id === 4) levelMultiplier = 1.5 // PhD
    
    // Deadline urgency multiplier
    let deadlineMultiplier = 1.0
    if (client_deadline) {
      const deadline = new Date(client_deadline)
      const now = new Date()
      const hoursUntilDeadline = (deadline - now) / (1000 * 60 * 60)
      
      if (hoursUntilDeadline < 24) deadlineMultiplier = 1.5
      else if (hoursUntilDeadline < 48) deadlineMultiplier = 1.3
      else if (hoursUntilDeadline < 72) deadlineMultiplier = 1.15
    }
    
    const adjustedBase = basePrice * levelMultiplier * deadlineMultiplier
    const extraServices = 0 // Mock: no extra services for now
    const discount = discount_code === 'TEST10' ? adjustedBase * 0.1 : 0
    const total = adjustedBase + extraServices - discount
    
    return {
      data: {
        total_price: total.toFixed(2),
        final_total: total.toFixed(2),
        breakdown: {
          base_price: basePrice.toFixed(2),
          extra_services: extraServices.toFixed(2),
          writer_level: 0,
          preferred_writer: 0,
          deadline_multiplier: deadlineMultiplier,
          deadline_info: {
            hours_until_deadline: client_deadline ? Math.round((new Date(client_deadline) - new Date()) / (1000 * 60 * 60)) : null,
            multiplier: deadlineMultiplier
          },
          discount: discount.toFixed(2),
          final_total: total.toFixed(2)
        }
      }
    }
  },

  // Mock order configs
  async getPaperTypes(params) {
    await delay(500)
    return { data: { results: mockPaperTypes } }
  },

  async getAcademicLevels(params) {
    await delay(500)
    return { data: { results: mockAcademicLevels } }
  },

  async getFormattingStyles(params) {
    await delay(500)
    return { data: { results: mockFormattingStyles } }
  },

  async getTypesOfWork(params) {
    await delay(500)
    return { data: { results: mockTypesOfWork } }
  },

  async getSubjects(params) {
    await delay(500)
    return { data: { results: mockSubjects } }
  }
}

