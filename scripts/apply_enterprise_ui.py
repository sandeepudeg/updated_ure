#!/usr/bin/env python3
"""
Script to apply enterprise UI changes to Streamlit app
Transforms app.py to match gramsetu_enterprise_ui_mockup.html
"""

import re
from pathlib import Path
import shutil

def backup_app():
    """Create backup of current app"""
    src = Path("src/ui/app.py")
    backup = Path("src/ui/app_backup_before_enterprise.py")
    shutil.copy(src, backup)
    print(f"✓ Backup created: {backup}")
    return src

def apply_enterprise_ui(app_path):
    """Apply enterprise UI transformations"""
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Applying enterprise UI changes...")
    
    # 1. Update page config
    content = re.sub(
        r'initial_sidebar_state="expanded"',
        'initial_sidebar_state="collapsed"',
        content
    )
    print("✓ Updated page config")
    
    # 2. Add enterprise CSS (find the CSS section and enhance it)
    css_addition = '''
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .block-container {
        padding-top: 0rem !important;
    }
'''
    
    # Insert after the opening <style> tag
    content = content.replace('<style>', '<style>' + css_addition)
    print("✓ Enhanced CSS")
    
    # 3. Replace header section
    header_pattern = r"st\.markdown\('<h1 class=\"main-header\">.*?</h1>', unsafe_allow_html=True\)\nst\.markdown\('<p class=\"sub-header\">.*?</p>', unsafe_allow_html=True\)"
    
    new_header = '''st.markdown("""
<div style="background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); 
            color: white; padding: 1.5rem 2rem; margin: -1rem -1rem 2rem -1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🌾</div>
            <div>
                <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">GramSetu</h1>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">AI-Powered Rural Assistant for India</p>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
            <span>👤 </span><span>{}</span>
        </div>
    </div>
</div>
""".format(st.session_state.user_profile.get('name', 'Guest User')), unsafe_allow_html=True)'''
    
    content = re.sub(header_pattern, new_header, content, flags=re.DOTALL)
    print("✓ Updated header")
    
    # Save changes
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Enterprise UI changes applied!")
    print("\nNext steps:")
    print("1. Review the changes in src/ui/app.py")
    print("2. Run: streamlit run src/ui/app.py")
    print("3. If issues occur, restore from: src/ui/app_backup_before_enterprise.py")

if __name__ == "__main__":
    print("=" * 60)
    print("Enterprise UI Transformation Script")
    print("=" * 60)
    print()
    
    app_path = backup_app()
    apply_enterprise_ui(app_path)
    
    print("\n" + "=" * 60)
