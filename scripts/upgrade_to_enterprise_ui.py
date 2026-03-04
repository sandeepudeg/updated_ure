#!/usr/bin/env python3
"""
Script to upgrade Streamlit UI to Enterprise Grade
Backs up current app.py and applies enterprise design
"""

import shutil
from pathlib import Path

# Backup current app
src_dir = Path(__file__).parent.parent / "src" / "ui"
backup_path = src_dir / "app_backup.py"
current_app = src_dir / "app.py"

print("Creating backup of current app...")
shutil.copy(current_app, backup_path)
print(f"✓ Backup created: {backup_path}")

print("\nTo apply enterprise UI:")
print("1. Review the mockup: gramsetu_enterprise_ui_mockup.html")
print("2. The enterprise version is being created as app_enterprise.py")
print("3. Test it first, then rename to app.py when ready")
print("\nBackup saved at: src/ui/app_backup.py")
