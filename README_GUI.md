# Fun Run 4 Leaking Tool - Desktop Application

A modern, user-friendly desktop application for monitoring Fun Run 4 updates and comparing/modifying game configuration files.

## ✨ Features

### 📡 **Update Monitoring**
- Automatic checking for Fun Run 4 updates on Uptodown
- Manual update checks with real-time status
- Auto-check mode (15-minute intervals)
- Version tracking and history
- Desktop notifications for new updates

### 🔍 **Config Comparison**
- Compare two `storeConfig.json` files
- Visual diff showing added, removed, and modified items
- Detailed breakdown by category (animals, skins, hats, etc.)
- Automatic generation of modified configs with `preOwned: true`
- Export results to files

### 🔧 **Config Modification**
- Modify config files by specific item IDs
- Support for comma or space-separated IDs
- Bulk modifications
- Instant preview of changes
- Save modified configs directly

### 📋 **Logging & Monitoring**
- Real-time activity logs
- Log viewer with refresh capability
- Export and clear logs
- Status tracking for all operations

### 🎨 **Modern UI**
- Dark/Light/System theme support
- Clean, intuitive interface
- Responsive design
- Emoji icons for better UX
- Professional layout

## 🚀 Quick Start

### Option 1: Run from Source (Recommended for Development)

1. **Launch the GUI:**
   ```bash
   # Double-click launch_gui.bat
   # Or run manually:
   python gui_app.py
   ```

2. The launcher will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Launch the application

### Option 2: Build Standalone Executable

1. **Build the .exe:**
   ```bash
   # Double-click build_exe.bat
   # Or run manually:
   pyinstaller FR4_Leaking_Tool.spec
   ```

2. **Run the executable:**
   - Navigate to `dist` folder
   - Run `FR4_Leaking_Tool.exe`
   - No Python installation required!

## 📦 Installation

### Requirements
- Windows 10/11
- Python 3.8+ (for running from source)

### Manual Installation
```bash
# Clone or download the project
cd "FR4 Leaking Tool"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui_app.py
```

## 🎯 How to Use

### 1. Monitor Updates Tab

**Check for updates manually:**
1. Click **"🔍 Check Now"** button
2. View results in the status log
3. Get notifications for new versions

**Enable automatic checking:**
1. Click **"▶️ Start Auto-Check (15 min)"**
2. App will check every 15 minutes
3. Notifications appear when updates are found
4. Click again to stop auto-checking

**Reset version data:**
- Use **"🔄 Reset Version"** to clear tracked version
- Next check will detect current version as "new"
- Useful for testing notifications

### 2. Compare Configs Tab

**Compare two config files:**
1. Click **Browse** next to "Old Config File"
2. Select your old `storeConfig.json`
3. Click **Browse** next to "New Config File"
4. Select your new `storeConfig.json`
5. Click **"🔍 Compare Files"**
6. Review the detailed comparison results
7. Save modified config with `preOwned: true` added to new items

**Results include:**
- Summary of changes
- Added items with details (ID, title, rarity)
- Removed items
- Modified items
- Option to save modified config

### 3. Modify Config Tab

**Modify specific items:**
1. Click **Browse** to select a config file
2. Enter item IDs in the text field:
   - Format: `2050, 2051, 2052` (comma-separated)
   - Or: `2050 2051 2052` (space-separated)
3. Click **"🔧 Apply Modifications"**
4. Review which items were modified
5. Save the modified config file

**Example use cases:**
- Unlock specific animals: `2050, 2051`
- Unlock specific skins: `3001, 3002, 3003`
- Unlock multiple categories: `2050 3001 4001`

### 4. View Logs Tab

**View activity logs:**
1. Click **"📋 View Logs"** in sidebar
2. Logs auto-refresh when tab is opened
3. Click **"🔄 Refresh Logs"** to update
4. Click **"🗑️ Clear Logs"** to reset log file

**Logs include:**
- Update check results
- File operations
- Errors and warnings
- Timestamp for all events

## 🏗️ Project Structure

```
FR4 Leaking Tool/
├── gui_app.py                  # Main GUI application
├── uptodown_monitor.py         # Update monitoring logic
├── config_comparator.py        # Config comparison logic
├── main.py                     # Discord bot (original)
├── config.json                 # Configuration file
├── version_data.json           # Tracked version data
├── bot.log                     # Application logs
├── requirements.txt            # Python dependencies
├── FR4_Leaking_Tool.spec       # PyInstaller build spec
├── build_exe.bat               # Build executable script
├── launch_gui.bat              # Launch GUI script
├── README_GUI.md               # This file
└── dist/                       # Built executable (after build)
    └── FR4_Leaking_Tool.exe
```

## ⚙️ Advanced Features

### Theme Customization
- Switch between **Dark**, **Light**, and **System** themes
- Find theme selector in sidebar
- Changes apply instantly

### Auto-Save Behavior
- All file operations prompt before saving
- Choose custom filenames and locations
- Defaults to `modified_storeConfig.json`

### Error Handling
- Comprehensive error messages
- File validation before processing
- JSON syntax checking
- Network error recovery

## 🔧 Building the Executable

### Prerequisites
```bash
pip install pyinstaller
```

### Build Process
1. **Automatic build:**
   ```bash
   build_exe.bat
   ```

2. **Manual build:**
   ```bash
   pyinstaller FR4_Leaking_Tool.spec
   ```

3. **Output:**
   - Executable: `dist/FR4_Leaking_Tool.exe`
   - Size: ~50-80 MB (standalone, no dependencies)
   - Portable: Copy to any Windows PC

### Customization
Edit `FR4_Leaking_Tool.spec` to:
- Add custom icon: `icon='icon.ico'`
- Include additional files
- Modify build options
- Change executable name

## 🐛 Troubleshooting

### GUI won't start
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt`
- Check `bot.log` for errors
- Try running from command line to see errors

### Update checking fails
- Verify internet connection
- Check if Uptodown is accessible
- Review network firewall settings
- Check `bot.log` for details

### Config comparison errors
- Ensure both files are valid JSON
- Files must follow Fun Run 4 config structure
- Check file encoding (should be UTF-8)
- Verify files are not corrupted

### Executable doesn't run
- Try running as Administrator
- Check Windows Defender/Antivirus
- Ensure all DLLs are in dist folder
- Rebuild with `build_exe.bat`

### Theme not applying
- Restart the application
- Check appearance mode setting
- Try "System" mode first
- Update customtkinter: `pip install --upgrade customtkinter`

## 📝 Configuration

### config.json
```json
{
  "discord_token": "YOUR_BOT_TOKEN",
  "channel_id": "YOUR_CHANNEL_ID",
  "app_package": "com.dirtybit.fire",
  "check_interval_minutes": 15
}
```

**Note:** The GUI application doesn't require Discord settings, but they're kept for backward compatibility with the Discord bot.

## 🎮 Use Cases

1. **Game Modding:**
   - Compare configs between versions
   - Identify new items/features
   - Unlock all items with preOwned flag

2. **Update Tracking:**
   - Monitor for new game versions
   - Get notified immediately
   - Track version history

3. **Content Analysis:**
   - See what items were added/removed
   - Analyze rarity distributions
   - Track game balance changes

4. **Batch Unlocking:**
   - Unlock specific item sets
   - Bulk modifications
   - Quick experimentation

## 🔐 Security & Privacy

- No data collection
- All operations are local
- No telemetry or tracking
- Config files never uploaded
- Open source and transparent

## 📜 License

This is an educational project. Use responsibly and respect game terms of service.

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share improvements

## 📞 Support

- Check logs first: `View Logs` tab
- Review troubleshooting section
- Verify all dependencies installed
- Test with sample config files

## 🎉 Credits

Developed as an advanced tool for Fun Run 4 community.

---

**Enjoy the FR4 Leaking Tool! 🚀**
