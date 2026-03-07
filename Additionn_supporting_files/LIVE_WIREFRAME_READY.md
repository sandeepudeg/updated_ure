# GramSetu Live Interface Wireframe - READY ✅

## Status: COMPLETE (Updated with Accurate UI Representation)

A comprehensive wireframe representation of the live GramSetu interface has been created based on the actual deployed application at https://d3v7khazsfb4vd.cloudfront.net/

## File Location
- **Wireframe**: `deployment/gramsetu-live-wireframe.html`

## Wireframe Features (Accurately Matching Live UI)

### Pre-Interface Elements
1. **Welcome Splash Screen** (5-second auto-hide)
   - Large tractor emoji logo (🌾)
   - "Welcome to GramSetu" title
   - "Your AI-Powered Rural Assistant" subtitle
   - 6 feature cards in 3x2 grid:
     - 🌱 Crop Diseases - Instant disease identification
     - 💰 Market Prices - Real-time price updates
     - 📋 Govt Schemes - Eligibility & benefits
     - 🌤️ Weather - Location-based forecasts
     - 💧 Irrigation - Water management tips
     - 🏞️ Rural Tourism - Extra income opportunities
   - Animated loading dots
   - Click to skip functionality

2. **Onboarding Form Overlay**
   - Appears after splash screen (if user hasn't completed it)
   - Green gradient header with 👋 icon
   - "Welcome, Farmer!" title
   - Form fields:
     - Name (required)
     - State dropdown (required)
     - District (optional)
     - Preferred Language dropdown (required)
     - Main Crops (optional with help text)
     - "Save my information" checkbox
   - Two-button layout: "Skip for Now" | "Get Started 🚀"
   - Saves to localStorage for personalization

### Main Interface Layout

1. **Header Section**
   - Green gradient background (#2e7d32 to #00695c)
   - Three-part layout:
     - Left: Empty space for balance
     - Center: Logo section
       - 🚜 Tractor icon (yellow #ffeb3b)
       - "GramSetu" title (26px, bold)
       - "Bridging Technology and Rural India" tagline
     - Right: Language selector
       - 6 languages: English, हिंदी, मराठी, తెలుగు, தமிழ், ಕನ್ನಡ
       - Glassmorphism effect (backdrop-filter blur)
   - Bottom tagline: "Empowering farmers with AI-driven solutions..."

2. **AI Agents Section**
   - Light green gradient background (#e8f5e9 to #c8e6c9)
   - Title: "Our Digital Assistants" (22px, green)
   - 6 agent cards (140x140px) with:
     - Flip animation on hover (3D perspective transform)
     - Front: Gradient background, icon, name, role
     - Back: White background with description
     - Click to activate agent in chat
   - Agent details:
     1. 🌱 **Krishak Mitra** (Green gradient) - Crop Specialist
     2. 🐛 **Rog Nivaarak** (Red gradient) - Disease Expert
     3. 📈 **Bazaar Darshi** (Orange gradient) - Market Analyst
     4. 📋 **Sarkar Sahayak** (Blue gradient) - Scheme Advisor
     5. 🌤️ **Mausam Gyaata** (Cyan gradient) - Weather Expert
     6. 📚 **Krishi Bodh** (Purple gradient) - Knowledge Guide

3. **Three-Column Grid Layout** (1fr 2fr 1fr)
   
   **Left Panel - Location & Profile**
   - White rounded panel with green header
   - **Your Location** section:
     - Blue gradient card (#e3f2fd to #bbdefb)
     - "Auto-Detected" badge
     - District, State, Country fields
     - Left border accent (4px blue)
   - **User Profile** section:
     - 6 form inputs with bilingual placeholders:
       - Name / नाव
       - Village / गाव
       - District dropdown (Nashik, Pune, Ahmednagar)
       - Phone / फोन (+91XXXXXXXXXX)
       - Crops (comma separated)
       - Land Size (acres)
     - Green "Save Profile" button with 💾 icon
     - Focus states with green border and shadow

   **Middle Panel - Chat Interface**
   - Green gradient header: "💬 GramSetu Assistant"
   - Chat messages area:
     - Light green background (#f5f9f5)
     - Bot messages: Green background, left-aligned
     - User messages: Blue background, right-aligned
     - Rounded corners (16px)
     - Border accents (3px left/right)
   - Input area (3 elements):
     - Text input: "Ask anything about farming..."
     - 📷 Camera button (green, 45x45px) - triggers image upload
     - ✈️ Send button (orange, 45x45px)
   - Image upload functionality:
     - Hidden file input
     - Preview in chat after selection
     - Visual feedback (checkmark animation)

   **Right Panel - Information Hub**
   - Green gradient header: "ℹ️ Information Hub"
   - **Weather Widget**:
     - Blue gradient background (#d6eaf8 to #e3f2fd)
     - Large weather icon (48px)
     - Temperature (32px, bold, blue)
     - Location text
     - 3-day forecast details
   - **Market Prices Card** (Purple gradient):
     - 🔥 "Today's Prices (Nashik)"
     - 4 price items with green values:
       - Onion: ₹3,000/q
       - Wheat: ₹2,125/q
       - Tomato: ₹1,800/q
       - Cotton: ₹6,500/q
   - **Today's Tip Card** (Yellow gradient):
     - 💡 icon
     - Irrigation alert with highlighted text
   - **New Scheme Card** (Green gradient):
     - 📢 icon
     - PM-Kisan 16th Installment info
   - **Rural Tourism Card** (Yellow gradient):
     - 🏞️ icon
     - Income opportunity details
     - Green income highlight: "💰 ₹15,000-₹50,000/month"

### Interactive Features Represented
- Splash screen with 5-second timer
- Onboarding form with validation
- Agent card flip animations
- Agent activation on click
- Image upload with preview
- Language change notifications
- Personalized welcome messages
- Real-time chat interface
- Hover effects on all interactive elements

### Visual Annotations in Wireframe
- Yellow callout boxes with black borders:
  - "Welcome Splash - 6 Feature Cards - Auto-hide after 5s"
  - "Onboarding Form - Name, State, District - Language, Crops"
  - "6 AI Agent Cards - Flip Animation on Hover - Click to Activate"
  - "3-Column Grid Layout - Location | Chat | Info Hub"
  - "Chat with Image Upload - Camera Button + Send Button"
- Feature badges:
  - 📱 Mobile Responsive
  - 🌐 Multi-Language
  - 🔄 Real-time Updates
  - ☁️ Cloud-Native

### Design Specifications
- **Dimensions**: 1920x1080 (PowerPoint presentation size)
- **Color Palette**: 
  - Primary Green: #4caf50, #2e7d32, #388e3c
  - Teal Accent: #00695c
  - Secondary Orange: #ff9800
  - Background Gradients: #e8f5e9 to #c8e6c9
  - Info Card Gradients: Blue, Purple, Yellow, Green variations
- **Typography**: 
  - Font Family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
  - Sizes: 10px-36px range
  - Weights: 400, 600, 700, 800
- **Border Styles**: 
  - Wireframe borders: 3px solid black
  - UI borders: 2px with color accents
  - Left accent borders: 4-5px on info cards
- **Border Radius**: 8px-15px for rounded corners
- **Shadows**: Box shadows for depth (0 4px 8px rgba(0,0,0,0.1))
- **Transitions**: 0.3s ease for hover effects

### Technical Implementation
- Pure HTML/CSS wireframe
- No JavaScript dependencies
- CSS Grid for main layout (1fr 2fr 1fr)
- Flexbox for component alignment
- Gradient backgrounds using linear-gradient()
- Pseudo-elements (::before, ::after) for decorative elements
- Transform effects for 3D card flips
- Backdrop-filter for glassmorphism

## Accuracy Notes
This wireframe is based on:
- Complete review of `src/web/v2/gramsetu-agents.html` (1724 lines)
- Exact color values from CSS variables
- Precise layout measurements and grid specifications
- All interactive elements and their behaviors
- Splash screen and onboarding flow
- Agent card flip animations
- Chat interface with image upload
- Information hub with 5 distinct cards

## Usage
Open `deployment/gramsetu-live-wireframe.html` in any web browser to view the accurate wireframe representation of the live GramSetu interface.

---
**Created**: 2026-03-07  
**Updated**: 2026-03-07 (Accurate UI representation)  
**Based on**: Live deployment at https://d3v7khazsfb4vd.cloudfront.net/  
**Source**: `src/web/v2/gramsetu-agents.html` (complete analysis)
