# 🚀 Quick Start Guide - FR4 Leaking Tool GUI

## 🎯 What's New?

Your FR4 Leaking Tool has been transformed into a **modern desktop application** with:

✨ **Beautiful GUI** - Modern, dark-themed interface with intuitive navigation
🖱️ **Easy to Use** - Point-and-click interface, no command line needed
📦 **Standalone EXE** - Build a single executable that runs anywhere
🎨 **Multiple Themes** - Dark, Light, and System theme support
⚡ **Real-time Updates** - Live status updates and notifications

---

## 🏃 Getting Started (3 Options)

### Option 1: Quick Launch (Easiest)
**Just double-click:** `launch_gui.bat`

That's it! The script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Launch the application

### Option 2: Build Standalone EXE
**Double-click:** `build_exe.bat`

Creates a portable `.exe` file in the `dist` folder that you can:
- 📤 Share with others
- 💾 Run without Python
- 🚀 Use on any Windows PC

### Option 3: Manual Launch
```bash
python gui_app.py
```

---

## 📱 Application Layout

### Sidebar Navigation (Left)
- 📡 **Monitor Updates** - Check for Fun Run 4 updates
- 🔍 **Compare Configs** - Compare two config files
- 🔧 **Modify Config** - Edit configs by item IDs
- 📋 **View Logs** - See application activity

### Main Area (Right)
- Shows content for selected tab
- Large text areas for results
- Action buttons at top
- Status displays

---

## 🎮 Common Tasks

### Check for Game Updates
1. Click **"📡 Monitor Updates"** in sidebar
2. Click **"🔍 Check Now"** button
3. See results instantly

### Compare Two Configs
1. Click **"🔍 Compare Configs"** in sidebar
2. Browse and select **Old Config**
3. Browse and select **New Config**
4. Click **"🔍 Compare Files"**
5. Save modified config when prompted

### Unlock Specific Items
1. Click **"🔧 Modify Config"** in sidebar
2. Browse and select your config file
3. Type item IDs: `2050, 2051, 2052`
4. Click **"🔧 Apply Modifications"**
5. Save the modified file

---

## 🔥 Pro Tips

### Auto-Check Mode
Enable automatic checking every 15 minutes:
- Go to **Monitor Updates** tab
- Click **"▶️ Start Auto-Check"**
- Get notified of new versions automatically

### Batch Operations
Unlock multiple items at once:
```
2050, 2051, 2052, 3001, 3002, 4001
```

### Theme Selection
Change appearance in sidebar:
- **Dark** - Best for night use
- **Light** - Traditional look
- **System** - Match Windows theme

### Export Results
All operations can save files:
- Config comparisons → `modified_storeConfig.json`
- Modifications → Custom filename
- Choose location when prompted

---

## 📂 File Structure

```
FR4 Leaking Tool/
│
├── 🚀 launch_gui.bat          ← START HERE (easiest)
├── 🔨 build_exe.bat           ← Build EXE
│
├── gui_app.py                 ← Main application
├── uptodown_monitor.py        ← Update checker
├── config_comparator.py       ← Config tools
│
├── config.json                ← Settings
├── bot.log                    ← Activity logs
│
└── dist/                      ← Built EXE (after build)
    └── FR4_Leaking_Tool.exe   ← Standalone app
```

---

## 🎨 Features Overview

### 📡 Update Monitor
- **Manual Check** - Click to check immediately
- **Auto-Check** - Every 15 minutes automatically
- **Version Tracking** - Remembers last version
- **Notifications** - Popup alerts for updates
- **Status Log** - Real-time activity feed

### 🔍 Config Compare
- **Visual Diff** - See exactly what changed
- **Categories** - Animals, skins, hats, etc.
- **Details** - Item IDs, titles, rarity
- **Auto-Modify** - Adds preOwned flag
- **Export** - Save modified configs

### 🔧 Config Modify
- **ID-Based** - Specify exact items
- **Bulk Edit** - Multiple items at once
- **Validation** - Shows found/not found
- **Preview** - See changes before saving
- **Flexible Input** - Comma or space separated

### 📋 Logs Viewer
- **Real-time** - Auto-refreshes
- **Complete History** - All operations logged
- **Timestamps** - Track when things happen
- **Export** - Save logs to file
- **Clear** - Reset when needed

---

## 🛠️ Building the EXE

### Automatic Build
```bash
build_exe.bat
```

**Output:**
- File: `dist/FR4_Leaking_Tool.exe`
- Size: ~50-80 MB
- Includes: All dependencies
- Portable: Copy anywhere

### What Gets Included
- ✅ Python runtime
- ✅ All libraries (customtkinter, aiohttp, etc.)
- ✅ Your modules
- ✅ Config files
- ✅ Everything needed to run

### Customization
Edit `FR4_Leaking_Tool.spec`:
```python
icon='myicon.ico'        # Add custom icon
console=False            # No console window
name='MyCustomName'      # Change app name
```

---

## ⚡ Keyboard Shortcuts

- **Ctrl+Q** - Quit application
- **F5** - Refresh current view
- **Ctrl+O** - Open file (when applicable)
- **Ctrl+S** - Save file (when applicable)

---

## 🐛 Troubleshooting

### App Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Run with error output
python gui_app.py
```

### Update Check Fails
- Check internet connection
- Verify Uptodown is accessible
- Review logs in **View Logs** tab

### Config Files Won't Load
- Ensure valid JSON format
- Check file encoding (UTF-8)
- Verify file structure

### EXE Build Fails
```bash
# Update PyInstaller
pip install --upgrade pyinstaller

# Clean build
rmdir /s /q build dist
pyinstaller FR4_Leaking_Tool.spec
```

---

## 📞 Need Help?

1. **Check Logs** - View Logs tab shows errors
2. **Read README** - Full details in `README_GUI.md`
3. **Test First** - Try with sample files
4. **Rebuild** - Fresh build often fixes issues

---

## 🎉 You're Ready!

**Start with:** `launch_gui.bat`

**Then explore:**
1. Check for updates
2. Compare configs
3. Modify items
4. View logs

**Finally:** Build your EXE with `build_exe.bat`

---

## 🌟 What Makes This Advanced?

### vs. Command Line Bot
- ❌ No terminal needed
- ✅ Visual interface
- ✅ Real-time feedback
- ✅ File browsers
- ✅ Interactive results

### vs. Basic GUI
- ✅ Modern design (customtkinter)
- ✅ Multiple tabs/features
- ✅ Theme support
- ✅ Async operations
- ✅ Professional layout
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Portable EXE

### Advanced Features
- 🔄 Background update checking
- 📊 Real-time status updates
- 💾 Auto-save with prompts
- 🎨 Dynamic theming
- 📝 Complete logging system
- 🔍 Detailed comparisons
- ⚙️ Modular architecture
- 📦 Single-file deployment

---

**Enjoy your advanced FR4 Leaking Tool! 🚀**

Made with ❤️ for the Fun Run 4 community
