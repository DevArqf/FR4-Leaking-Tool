"""
Quick test to verify GUI launches without errors
"""
import sys

print("Testing FR4 Leaking Tool GUI...")
print("-" * 60)

# Test imports
print("1. Testing imports...")
try:
    import customtkinter as ctk
    print("   ✓ CustomTkinter imported")
except Exception as e:
    print(f"   ✗ CustomTkinter import failed: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print("   ✓ PIL imported")
except Exception as e:
    print(f"   ✗ PIL import failed: {e}")
    sys.exit(1)

try:
    from uptodown_monitor import UptodownMonitor
    print("   ✓ UptodownMonitor imported")
except Exception as e:
    print(f"   ✗ UptodownMonitor import failed: {e}")
    sys.exit(1)

try:
    from config_comparator import ConfigComparator
    print("   ✓ ConfigComparator imported")
except Exception as e:
    print(f"   ✗ ConfigComparator import failed: {e}")
    sys.exit(1)

try:
    import gui_app
    print("   ✓ GUI app module imported")
except Exception as e:
    print(f"   ✗ GUI app import failed: {e}")
    sys.exit(1)

# Test icon availability
print("\n2. Checking icons...")
import os
if os.path.exists('assets'):
    icon_count = len([f for f in os.listdir('assets') if f.endswith('.png')])
    print(f"   ✓ Assets folder exists with {icon_count} PNG files")
else:
    print("   ⚠ Assets folder not found - icons will auto-generate on first launch")

# Test GUI initialization (without showing window)
print("\n3. Testing GUI initialization...")
try:
    print("   Creating GUI instance (not showing window)...")
    # We won't call mainloop() so window won't actually appear
    app = gui_app.FR4LeakingToolGUI()
    print("   ✓ GUI instance created successfully")
    print(f"   ✓ Icons loaded: {len(app.icons)} icons")
    
    # Check key components
    if hasattr(app, 'monitor'):
        print("   ✓ Monitor component initialized")
    if hasattr(app, 'comparator'):
        print("   ✓ Comparator component initialized")
    if hasattr(app, 'monitor_btn'):
        print("   ✓ Navigation buttons created")
    if hasattr(app, 'check_now_btn'):
        print("   ✓ Action buttons created")
    
    # Don't call mainloop, just destroy
    app.destroy()
    print("   ✓ GUI cleaned up successfully")
    
except Exception as e:
    print(f"   ✗ GUI initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nYou can now launch the GUI with:")
print("  python gui_app.py")
print("  or")
print("  launch_gui.bat")
