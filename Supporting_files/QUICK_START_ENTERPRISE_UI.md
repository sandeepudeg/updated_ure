# Quick Start: Enterprise UI

## 🚀 Launch in 3 Steps

### Step 1: Open PowerShell
```powershell
cd D:\Learning\Assembler_URE_Rural
```

### Step 2: Run the Script
```powershell
.\run_enterprise_ui.ps1
```

### Step 3: Open Browser
Navigate to: **http://localhost:8501**

---

## ✅ What's New

### 1. Language Selector in Header
- **Location**: Top-right corner
- **Options**: English, Hindi, Marathi
- **How to use**: Click dropdown in header

### 2. Profile Form in Left Column
- **Location**: Left column, below location
- **Fields**: Name, Village, District, Phone, Crops, Land Size
- **How to use**: Fill form and click "💾 Save Profile"

### 3. Three-Column Layout
- **Left**: Quick Actions + Location + Profile
- **Center**: Chat Interface
- **Right**: Weather + Prices + Tips

---

## 📋 Quick Test Checklist

- [ ] Language selector visible in header (top-right)
- [ ] Profile form visible in left column
- [ ] Quick action buttons work
- [ ] Chat works with text queries
- [ ] Image upload works
- [ ] All three columns display correctly

---

## 🎯 Key Features

### Quick Actions (Left Column)
Click any button to populate chat:
- 🌱 Crop Disease Help
- 📋 Government Schemes
- 💰 Market Prices
- 💧 Irrigation Tips
- 🌤️ Weather Forecast

### Profile Form (Left Column)
1. Fill in your details
2. District auto-detects from location
3. Click "💾 Save Profile"
4. Click "✏️ Edit Profile" to modify

### Chat Interface (Center)
1. Type your question
2. Upload crop image (optional)
3. Press Enter or click send
4. Get AI-powered response

### Widgets (Right Column)
- ☀️ Weather: Current conditions
- 💰 Prices: Market rates in ₹
- 💡 Tips: Daily farming advice
- 📢 Schemes: Government programs

---

## 🔧 Troubleshooting

### Issue: Can't access localhost:8501
**Solution**: Check if port is already in use
```powershell
netstat -ano | findstr :8501
```

### Issue: Language selector not visible
**Solution**: Refresh browser (Ctrl+F5)

### Issue: Profile form not saving
**Solution**: Fill all required fields (Name, Village, District)

### Issue: Image upload not working
**Solution**: Check AWS credentials are configured

---

## 📁 Files

### Main Files
- `src/ui/app_enterprise_clean.py` - Enterprise UI (NEW)
- `src/ui/app.py` - Original UI (unchanged)
- `run_enterprise_ui.ps1` - Launch script (NEW)

### Documentation
- `READY_TO_TEST.md` - Complete testing guide
- `ENTERPRISE_UI_UPDATES.md` - Detailed changes
- `ENTERPRISE_UI_VISUAL_GUIDE.md` - Visual comparison
- `QUICK_START_ENTERPRISE_UI.md` - This file

---

## 🎨 Visual Preview

```
┌────────────────────────────────────────────────────────┐
│ 🌾 GramSetu              👤 User  🌍 English ▼        │
└────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────┬──────────────────────┐
│ Quick    │ 💬 Chat              │ ☀️ Weather: 28°C     │
│ Actions  │                      │                      │
│ [🌱]     │ Welcome Message      │ 💰 Prices            │
│ [📋]     │                      │  Onion: ₹3,000/q    │
│ [💰]     │ Chat Messages        │                      │
│ [💧]     │                      │ 💡 Tip               │
│ [🌤️]     │ 📷 Image Upload      │  Irrigation Alert   │
│          │                      │                      │
│ 📍 Loc   │ Chat Input           │ 📢 Scheme            │
│ Nashik   │                      │  PM-Kisan           │
│          │                      │                      │
│ 👤 Form  │                      │                      │
│ [Save]   │                      │                      │
└──────────┴──────────────────────┴──────────────────────┘
```

---

## ✨ Highlights

### Compared to Original
- ✅ Language selector moved to header (was in sidebar)
- ✅ Profile form in left column (was in sidebar)
- ✅ Quick actions added (new feature)
- ✅ Weather widget added (new feature)
- ✅ Market prices widget added (new feature)
- ✅ Tips and schemes widgets added (new features)
- ✅ Three-column layout (was sidebar + main)
- ✅ Enterprise styling (gradients, animations)

### All Original Features Preserved
- ✅ Chat functionality
- ✅ Image upload and analysis
- ✅ Location detection
- ✅ Multi-language support
- ✅ Profile management
- ✅ Vision AI integration
- ✅ Local mode operation

---

## 🎯 Success Criteria

The UI is working correctly when:
1. Language selector appears in header (top-right)
2. Profile form appears in left column
3. All three columns display properly
4. Chat responds to queries
5. Image upload and analysis works
6. Widgets display in right column

---

## 📞 Next Steps

1. **Test**: Run `.\run_enterprise_ui.ps1`
2. **Verify**: Check all features work
3. **Feedback**: Note any issues
4. **Deploy**: Replace original if satisfied

---

## 💡 Pro Tips

- Use Quick Actions for common queries
- Upload clear crop images for best analysis
- Save your profile for personalized responses
- Check weather widget before planning irrigation
- Monitor market prices in right column

---

## Status: ✅ READY

All features implemented and ready for testing!
