# Complete Enterprise UI Implementation Plan

## Mockup Analysis
The `gramsetu_enterprise_ui_mockup.html` has:
1. **Custom Header**: Green gradient, logo, language selector, user badge
2. **Three-Column Layout**: 
   - Left (300px): Quick actions, location, profile
   - Center (flexible): Chat interface
   - Right (320px): Weather, market prices, tips
3. **No Sidebar**: All content in main area
4. **Widgets**: Weather card, market prices, daily tips

## Current Streamlit App Issues
1. Uses sidebar for navigation
2. Single-column chat layout
3. No weather/market widgets
4. Standard Streamlit header visible

## Implementation Steps

### Step 1: Backup Current App
```powershell
Copy-Item src/ui/app.py src/ui/app_backup_original.py
```

### Step 2: Key Changes Needed in app.py

#### A. Page Config (Line ~98)
```python
st.set_page_config(
    page_title="GramSetu - Enterprise AI Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar
)
```

#### B. CSS Updates (Line ~108)
Add to existing CSS:
```css
/* Hide all Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Remove padding */
.block-container {
    padding-top: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
```

#### C. Custom Header (Replace line ~649)
Instead of:
```python
st.markdown('<h1 class="main-header">🌾 GramSetu</h1>', unsafe_allow_html=True)
```

Use:
```python
st.markdown("""
<div style="background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); 
            color: white; padding: 1.5rem 2rem; margin: -1rem -1rem 2rem -1rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🌾</div>
            <div>
                <h1 style="margin: 0;">GramSetu</h1>
                <p style="margin: 0; opacity: 0.9;">AI-Powered Rural Assistant</p>
            </div>
        </div>
        <div>
            <select style="background: rgba(255,255,255,0.2); color: white; padding: 0.5rem; border-radius: 8px;">
                <option>🇬🇧 English</option>
                <option>🇮🇳 हिंदी</option>
                <option>🇮🇳 मराठी</option>
            </select>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
```

#### D. Three-Column Layout (Replace line ~966)
Instead of sidebar + main, use:
```python
# Create three columns
left_col, main_col, right_col = st.columns([1, 2.5, 1])

# LEFT COLUMN
with left_col:
    st.markdown("### 🚀 Quick Actions")
    if st.button("🌱 Crop Disease", use_container_width=True):
        st.session_state.quick_action_query = 'Help with crop disease'
        st.rerun()
    # ... more buttons
    
    st.markdown("---")
    st.markdown("### 📍 Location")
    st.success(f"📍 {location_str}")

# MAIN COLUMN
with main_col:
    st.markdown("### 💬 Chat")
    # ... existing chat code

# RIGHT COLUMN
with right_col:
    # Weather Widget
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%); 
                padding: 1.5rem; border-radius: 12px; text-align: center;">
        <div style="font-size: 3rem;">☀️</div>
        <div style="font-size: 2rem; font-weight: 700; color: #2196F3;">28°C</div>
        <p>Sunny, Nashik</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Market Prices
    st.markdown("### 💰 Today's Prices")
    st.markdown("""
    <div style="background: white; padding: 1rem; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
            <span>Onion</span>
            <span style="color: #4CAF50; font-weight: 700;">₹3,000/q</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
            <span>Wheat</span>
            <span style="color: #4CAF50; font-weight: 700;">₹2,125/q</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
```

## Quick Implementation Script

I'll create a Python script that makes these changes automatically.
