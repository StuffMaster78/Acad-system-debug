# Profile Page Visual Design

## Overview
Modern, clean SaaS-style profile page with improved UI/UX for profile image management.

## Layout Structure

### 1. Header Section (Top Card)
- **Background**: White card with subtle border and shadow
- **Layout**: Horizontal flex layout with avatar on left, info in center, settings button on right
- **Avatar**:
  - Size: 32px (mobile) / 36px (desktop) - larger and more prominent
  - Circular with 2px gray border
  - Hover effect: border changes to primary color, shadow increases
  - Edit badge: Small primary-colored button at bottom-right corner
  - Hover overlay: Dark overlay with white edit icon appears on hover
  
- **User Info**:
  - Name: Large, bold heading (3xl/4xl font size)
  - Email: Smaller text with email icon
  - Badges: Small rounded pills for role, active status, verified status
    - Gray background for role
    - Green with dot indicator for active status
    - Blue with checkmark for verified status

- **Settings Button**: 
  - Outlined button with icon
  - Positioned on the right side

### 2. Stats Cards (Below Header)
- **Layout**: 4-column grid (responsive: 1 col mobile, 2 col tablet, 4 col desktop)
- **Design**: 
  - White cards with subtle borders
  - Small shadow that increases on hover
  - Icon in top-right corner
  - Large bold number
  - Optional change indicator with percentage

### 3. Main Content Grid
- **Left Column (2/3 width)**:
  - Personal Information Card
    - Header with icon and "Edit" button
    - Grid layout for information fields
    - Clean labels and values
    - Bio section at bottom if available
  
  - Role-Specific Information Card (if applicable)
    - Similar clean card design
    - Grid layout for role-specific data

- **Right Column (1/3 width)**:
  - Quick Actions Card
    - List of action links with icons
    - Hover effects on each item
    - Settings, Security, Privacy links
  
  - Account Status Card
    - Status indicators
    - Email verification status
    - Clean badge-style indicators

### 4. Avatar Upload Modal
- **Modal Overlay**: Dark backdrop with blur
- **Modal Card**: 
  - White rounded card
  - Compact header with title and close button
  - Clean content area

- **Upload Area** (when no preview):
  - Dashed border container
  - Centered content:
    - Large image icon in primary-colored circle
    - Clear text: "Drag and drop an image here"
    - "or browse to choose a file" with clickable link
    - File format info: "PNG, JPG, GIF up to 5MB"
    - Primary button: "Upload Picture" with upload icon
  
  - Hover/Drag states:
    - Border changes to primary color
    - Background lightens
    - Slight scale effect

- **Preview Area** (when image selected):
  - Large circular preview (40px)
  - Remove button at top-right
  - Action buttons below:
    - Primary "Save Photo" button
    - Secondary "Change" button
  
  - Upload Progress (when uploading):
    - Spinner indicator
    - Progress bar
    - "Uploading..." text

## Color Scheme
- **Primary**: Blue/Purple gradient (primary-600, primary-700)
- **Background**: Light gray (gray-50) / Dark gray (gray-900)
- **Cards**: White / Dark gray (gray-800)
- **Borders**: Light gray (gray-200/300)
- **Text**: Dark gray (gray-900) / White
- **Accents**: Primary colors for interactive elements

## Typography
- **Headings**: Bold, large sizes (3xl, 4xl for name)
- **Body**: Medium weight, readable sizes (sm, base)
- **Labels**: Small, uppercase or medium weight
- **Badges**: Extra small, medium weight

## Spacing
- **Card Padding**: 6-8 (24-32px)
- **Section Gaps**: 4-6 (16-24px)
- **Element Gaps**: 2-3 (8-12px)
- **Compact**: Reduced from previous design for better density

## Interactive Elements
- **Hover States**: Subtle color changes, shadow increases
- **Transitions**: Smooth 200-300ms transitions
- **Focus States**: Ring indicators for accessibility
- **Buttons**: Clear primary/secondary distinction

## Responsive Design
- **Mobile**: Single column, stacked layout
- **Tablet**: 2-column stats, side-by-side content
- **Desktop**: Full 4-column stats, 3-column main grid

## Key Improvements from Previous Design
1. ✅ Removed heavy gradients and patterns
2. ✅ Cleaner, more minimal aesthetic
3. ✅ Better avatar prominence and edit functionality
4. ✅ Improved upload modal with clearer UX
5. ✅ Consistent spacing and typography
6. ✅ Modern SaaS design patterns
7. ✅ Better visual hierarchy
8. ✅ Cleaner form inputs and buttons

