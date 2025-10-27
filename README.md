# 🎮 FR4 Leaking Tool

<div align="center">

**A powerful monitoring and configuration tool for Fun Run 4**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)

[Download Latest Release](#-download) • [Features](#-features) • [Setup Guide](#-setup) • [Screenshots](#-screenshots)

</div>

---

## 📥 Download

### Option 1: Standalone Executable (Recommended)
**No Python installation required!**

1. Download the latest release from [Releases](../../releases)
2. Extract the ZIP file
3. Follow the [Quick Start Guide](#quick-start)

### Option 2: Run from Source
```bash
git clone https://github.com/DevArqf/funrun4-config-monitor.git
cd funrun4-config-monitor
pip install -r requirements.txt
python gui_app.py
```

---

## ✨ Features

### 🔔 Real-time Update Monitoring
- **Automatic monitoring** of Fun Run 4 updates from Uptodown
- **Discord notifications** with @here ping when new versions are detected
- **Configurable check intervals** (default: 15 minutes)
- **Desktop popup alerts** for instant awareness

### 🔧 Config File Management
- **Compare** old and new storeConfig.json files side-by-side
- **Automatically add** `preOwned: true` to new items
- **Batch modify** items by ID
- **Change hidden items** from `true` to `false`
- **Export modified configs** for immediate use

### 🎨 Modern GUI Interface
- **Beautiful dark/light themes**
- **Tabbed interface** for easy navigation
- **Real-time status logs**
- **Built-in log viewer**
- **User-friendly design**

### 🤖 Discord Integration
- **Embedded bot** runs automatically with the GUI
- **Rich embeds** with version info and update details
- **@here mentions** for team notifications
- **Status indicators** in the GUI

---

## 🚀 Quick Start

### Step 1: Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Go to the **"Bot"** section
4. Click **"Add Bot"**
5. Under **Privileged Gateway Intents**, enable:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
6. Copy your **bot token**
7. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Mention Everyone`
8. Use the generated URL to invite the bot to your server

### Step 2: Configuration

1. Rename `config.example.json` to `config.json`
2. Edit the file with your details:

```json
{
  "discord_token": "YOUR_BOT_TOKEN_HERE",
  "channel_id": "YOUR_CHANNEL_ID_HERE",
  "app_package": "com.dirtybit.fire",
  "check_interval_minutes": 15
}
```

**How to get Channel ID:**
1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click your channel → Copy ID

### Step 3: Run the Tool

**If using the .exe:**
- Double-click `FR4_Leaking_Tool.exe`

**If running from source:**
```bash
python gui_app.py
```

---

## 📖 Usage Guide

### Monitor Tab
- **Check Now**: Manually check for updates
- **Start Auto-Check**: Enable automatic checking every 15 minutes
- **Reset Version**: Clear version data (for testing)

### Compare Tab
1. Select old storeConfig.json file
2. Select new storeConfig.json file
3. Click **Compare**
4. Review changes and download modified config with `preOwned: true`

### Modify Tab
1. Select a storeConfig.json file
2. Enter item IDs (comma or space separated)
3. Click **Modify**
4. Save the modified config

### Logs Tab
- View all bot activity
- Refresh logs
- Clear log history

---

## 🛠️ Building from Source

### Prerequisites
- Python 3.8 or higher
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Build Executable
```powershell
.\build_exe.ps1
```

The executable will be created in the `release/` folder.

---

## 📋 Requirements

### For Running the Executable
- Windows 10/11
- Internet connection
- Discord bot token (free to create)

### For Running from Source
```
customtkinter>=5.2.0
discord.py>=2.3.0
aiohttp>=3.9.0
Pillow>=10.0.0
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational and monitoring purposes only. Use responsibly and in accordance with Fun Run 4's terms of service.

---

## 💖 Support

If you find this tool useful, consider giving it a ⭐ on GitHub!

---

<div align="center">

Made with ❤️ by [DevArqf](https://github.com/DevArqf)

</div>
