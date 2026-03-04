# Enterprise UI Test Checklist

## Quick Start
```powershell
.\run_enterprise_ui.ps1
```
Then open: http://localhost:8501

---

## Visual Verification

### ✅ Header (Top of Page)
- [ ] Header is ONE continuous green bar (no split)
- [ ] Logo (🌾 GramSetu) on the left
- [ ] Language selector in the middle-right
- [ ] User badge (👤 Guest User) on the right
- [ ] All elements aligned horizontally
- [ ] Green gradient background spans full width
- [ ] No visual breaks or gaps

**Expected:**
```
┌────────────────────────────────────────────┐
│ 🌾 GramSetu    🌍 English ▼    👤 User    │
└────────────────────────────────────────────┘
```

---

### ✅ Welcome Screen (Center Column, First Visit)
- [ ] Large centered icon (🌾)
- [ ] "Welcome to GramSetu!" heading
- [ ] Description text below heading
- [ ] 4 feature cards in grid layout:
  - [ ] 🌱 Crop Diseases
  - [ ] 💰 Market Prices
  - [ ] 📋 Govt Schemes
  - [ ] 🌤️ Weather
- [ ] Cards have white background
- [ ] Cards have shadows
- [ ] Grid is responsive (2x2 on desktop)

**Expected:**
```
        🌾
  Welcome to GramSetu!
  Description text...

┌─────────┐ ┌─────────┐
│   🌱    │ │   💰    │
│ Crop    │ │ Market  │
│Diseases │ │ Prices  │
└─────────┘ └─────────┘
┌─────────┐ ┌─────────┐
│   📋    │ │   🌤️    │
│  Govt   │ │Weather  │
│Schemes  │ │         │
└─────────┘ └─────────┘
```

---

### ✅ Chat Header (Center Column)
- [ ] "💬 Chat with GramSetu" heading
- [ ] Green gradient background
- [ ] Bottom border accent
- [ ] Rounded top corners

**Expected:**
```
┌────────────────────────────┐
│ 💬 Chat with GramSetu      │ <- Green gradient
└────────────────────────────┘
```

---

### ✅ Chat Container (Center Column)
- [ ] Light gray background (#FAFAFA)
- [ ] Rounded corners
- [ ] Padding around messages
- [ ] Scrolls when messages exceed height
- [ ] Custom green scrollbar (when scrolling)
- [ ] Scrollbar is 8px wide
- [ ] Scrollbar has rounded edges

**To Test Scrolling:**
1. Send multiple messages (5-10)
2. Container should scroll
3. Scrollbar should appear on right
4. Scrollbar should be green

---

### ✅ Chat Messages
- [ ] User messages: Blue gradient, right-aligned
- [ ] Assistant messages: White with green left border
- [ ] Agent badges show above assistant messages
- [ ] Messages have rounded corners
- [ ] Smooth fade-in animation
- [ ] Feedback buttons (👍 👎) below assistant messages

**Expected:**
```
User message:
┌────────────────────┐
│ Your question here │ <- Blue gradient
└────────────────────┘

Assistant message:
┌────────────────────┐
│ 🎯 Supervisor      │ <- Badge
│ Response text...   │ <- White with green border
│ [👍] [👎]          │ <- Feedback
└────────────────────┘
```

---

### ✅ Left Column
- [ ] Quick Actions section with 5 buttons:
  - [ ] 🌱 Crop Disease Help
  - [ ] 📋 Government Schemes
  - [ ] 💰 Market Prices
  - [ ] 💧 Irrigation Tips
  - [ ] 🌤️ Weather Forecast
- [ ] Location card shows detected location
- [ ] Profile form OR profile display
- [ ] All buttons full width
- [ ] Green gradient on buttons

**Profile Form (if not saved):**
- [ ] Name field
- [ ] Village field
- [ ] District dropdown (auto-detected)
- [ ] Phone field
- [ ] Crops multi-select
- [ ] Land size number input
- [ ] Save button

**Profile Display (if saved):**
- [ ] Shows saved information
- [ ] Edit button to modify

---

### ✅ Right Column
- [ ] Weather widget:
  - [ ] Large temperature (28°C)
  - [ ] Weather icon (☀️)
  - [ ] Location (Nashik)
  - [ ] 3-day forecast
  - [ ] Blue gradient background
- [ ] Market Prices widget:
  - [ ] 4 crop prices in ₹
  - [ ] Purple gradient background
- [ ] Daily Tip widget:
  - [ ] Tip text
  - [ ] Orange gradient background
- [ ] Government Scheme widget:
  - [ ] Scheme info
  - [ ] Green gradient background

---

## Functionality Testing

### ✅ Language Selector
- [ ] Click language dropdown in header
- [ ] Options show: English, Hindi, Marathi
- [ ] Selection updates (check session state)
- [ ] Dropdown closes after selection

---

### ✅ Quick Actions
- [ ] Click "Crop Disease Help" button
- [ ] Query appears in chat input area
- [ ] "Send" and "Clear" buttons appear
- [ ] Click "Send" to submit query
- [ ] Click "Clear" to cancel
- [ ] Test all 5 quick action buttons

---

### ✅ Profile Form
**If profile not saved:**
- [ ] Fill in all fields
- [ ] District auto-detects from location
- [ ] Click "Save Profile"
- [ ] Success message appears
- [ ] Form changes to display mode
- [ ] Header shows saved name

**If profile saved:**
- [ ] Profile information displays
- [ ] Click "Edit Profile"
- [ ] Form reappears with saved data
- [ ] Can modify and save again

---

### ✅ Chat Functionality
- [ ] Type a question in chat input
- [ ] Press Enter or click send
- [ ] Message appears as user message (blue)
- [ ] Loading indicator shows
- [ ] Response appears as assistant message (white)
- [ ] Agent badge shows correct agent
- [ ] Feedback buttons appear
- [ ] Click 👍 shows success message
- [ ] Click 👎 shows feedback message

---

### ✅ Image Upload
- [ ] Click "Browse files" or drag image
- [ ] Image preview appears
- [ ] "Remove image" button shows
- [ ] Type question about image
- [ ] Send message
- [ ] Vision AI analyzes image
- [ ] Response includes image analysis
- [ ] Click "Remove image" to clear

---

### ✅ Location Detection
- [ ] Location card shows city and state
- [ ] "Auto-detected from IP" caption shows
- [ ] District in profile form matches location
- [ ] Location context added to queries

---

## Responsive Testing

### Desktop (>1200px)
- [ ] Three columns visible side-by-side
- [ ] Left: 1 unit width
- [ ] Center: 2.5 units width
- [ ] Right: 1 unit width
- [ ] Header spans full width
- [ ] Feature grid shows 2x2

### Tablet (768px-1200px)
- [ ] Columns stack vertically
- [ ] Header remains full width
- [ ] Feature grid shows 2x2 or 1x4
- [ ] All content readable

### Mobile (<768px)
- [ ] Single column layout
- [ ] Header stacks elements
- [ ] Feature grid shows 1x4
- [ ] Chat input full width
- [ ] All buttons full width

---

## Browser Testing

### Chrome
- [ ] All features work
- [ ] Scrollbar appears green
- [ ] Animations smooth
- [ ] No console errors

### Firefox
- [ ] All features work
- [ ] Scrollbar appears green
- [ ] Animations smooth
- [ ] No console errors

### Safari
- [ ] All features work
- [ ] Scrollbar styling works
- [ ] Animations smooth
- [ ] No console errors

### Edge
- [ ] All features work
- [ ] Scrollbar appears green
- [ ] Animations smooth
- [ ] No console errors

---

## Performance Testing

- [ ] Page loads in < 2 seconds
- [ ] Chat input responds instantly
- [ ] Image upload completes in < 1 second
- [ ] API responses in 2-5 seconds
- [ ] Smooth scrolling in chat
- [ ] No lag when typing
- [ ] Animations don't stutter

---

## Comparison with HTML Mockup

### Open Both Side-by-Side
1. Open `gramsetu_enterprise_ui_mockup.html` in browser
2. Open Streamlit app at http://localhost:8501
3. Compare visually

### Check These Elements
- [ ] Header layout matches
- [ ] Welcome screen matches
- [ ] Chat container matches
- [ ] Left column matches
- [ ] Right column matches
- [ ] Colors match
- [ ] Spacing matches
- [ ] Typography matches

---

## Known Issues to Ignore

None - all features should work perfectly!

---

## If Something Doesn't Work

### Header Split
**Issue**: Header appears split into two sections
**Fix**: Refresh browser (Ctrl+F5)

### Language Selector Not Visible
**Issue**: Language selector missing from header
**Fix**: Check browser zoom level, refresh page

### Scrollbar Not Green
**Issue**: Scrollbar is default color
**Fix**: Check browser (webkit browsers only), try Chrome

### Profile Not Saving
**Issue**: Profile form doesn't save
**Fix**: Fill all required fields (Name, Village, District)

### Image Upload Error
**Issue**: Image upload fails
**Fix**: Check AWS credentials, verify Bedrock access

### Chat Not Responding
**Issue**: No response to queries
**Fix**: Check console for errors, verify local agents working

---

## Success Criteria

The UI is working correctly when:

✅ Header is unified (no split)
✅ Language selector in header
✅ Welcome screen shows feature grid
✅ Chat container scrolls with green scrollbar
✅ All three columns display correctly
✅ Profile form works
✅ Quick actions work
✅ Chat functionality works
✅ Image upload works
✅ All widgets display correctly
✅ Matches HTML mockup visually

---

## Final Verification

### Visual Match: 100%
- [ ] Header: Matches mockup
- [ ] Welcome: Matches mockup
- [ ] Chat: Matches mockup
- [ ] Layout: Matches mockup
- [ ] Colors: Matches mockup
- [ ] Typography: Matches mockup

### Functionality: 100%
- [ ] All features work
- [ ] No errors in console
- [ ] Smooth performance
- [ ] Responsive design works

---

## Sign-Off

**Tested by**: _______________
**Date**: _______________
**Browser**: _______________
**Result**: ☐ Pass  ☐ Fail

**Notes**:
_________________________________
_________________________________
_________________________________

---

## Status

☐ Not Started
☐ In Progress
☐ Testing Complete - Issues Found
☐ Testing Complete - All Pass ✅

---

**Ready for deployment when all checkboxes are checked!** 🚀
