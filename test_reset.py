"""
Test the reset version functionality
"""
import os
from uptodown_monitor import UptodownMonitor

print("Testing Reset Version Functionality")
print("=" * 60)

# Check if version file exists before
print("\n1. Before Reset:")
if os.path.exists("version_data.json"):
    print("   ✓ version_data.json exists")
    with open("version_data.json", "r") as f:
        print(f"   Content: {f.read()}")
else:
    print("   ✗ version_data.json does not exist")

# Create monitor
monitor = UptodownMonitor()
print(f"\n2. Monitor State:")
print(f"   Current version: {monitor.current_version}")
print(f"   Last check: {monitor.last_check}")

# Reset
print("\n3. Resetting...")
monitor.reset_version()
print(f"   Version after reset_version(): {monitor.current_version}")

# Explicitly set to None
monitor.current_version = None
monitor.last_check = None
print(f"   Version after explicit None: {monitor.current_version}")
print(f"   Last check after explicit None: {monitor.last_check}")

# Check file
print("\n4. After Reset:")
if os.path.exists("version_data.json"):
    print("   ⚠ WARNING: version_data.json still exists!")
    with open("version_data.json", "r") as f:
        print(f"   Content: {f.read()}")
else:
    print("   ✓ version_data.json deleted successfully")

# Try to reload
print("\n5. Reloading data (simulating restart):")
monitor.load_version_data()
print(f"   Version after reload: {monitor.current_version}")
print(f"   Last check after reload: {monitor.last_check}")

print("\n" + "=" * 60)
if monitor.current_version is None:
    print("✓ RESET SUCCESSFUL - Version is None")
else:
    print(f"✗ RESET FAILED - Version is still: {monitor.current_version}")
print("=" * 60)
