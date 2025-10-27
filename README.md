# Fun Run 4 Monitor Bot

A Discord bot that monitors Fun Run 4 updates on Google Play Store and compares configuration files to detect changes in game content.

## Features

🔍 **Automatic Uptodown Monitoring**: Checks for Fun Run 4 updates every 15 minutes (configurable)
📊 **Configuration File Comparison**: Compare two `storeConfig.json` files to see what's changed  
🔧 **Automatic Modification**: Adds `preOwned: true` to newly detected items in config files  
🚨 **Update Notifications**: Get notified when new versions are detected

## Setup

### Option 1: Easy Setup with Batch File (Windows)
1. Double-click `start_bot.bat`
2. The script will automatically:
   - Create a virtual environment
   - Install dependencies
   - Check your configuration
   - Provide a menu to start the bot or test updates

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Configure the Bot
Update `config.json` with your Discord bot token and channel ID:
```json
{
  "discord_token": "YOUR_BOT_TOKEN_HERE",
  "channel_id": "YOUR_CHANNEL_ID_HERE",
  "app_package": "com.dirtybit.fire",
  "check_interval_minutes": 15
}
```

#### 3. Run the Bot
```bash
python main.py
```

## Commands

### `!compare`
Compare two `storeConfig.json` files to detect changes.

**Usage:** 
1. Use the `!compare` command
2. Attach exactly 2 JSON files to your message:
   - First file: Old version of `storeConfig.json`
   - Second file: New version of `storeConfig.json`

**What it does:**
- Identifies added, removed, and modified items across all sections (animals, skins, hats, glasses, chests, feet, etc.)
- Shows a summary of changes
- Automatically creates a modified version of the new config file with `preOwned: true` added to all newly detected items
- Uploads the modified config file for download

**Example:**
```
!compare
[Attach: old_storeConfig.json]
[Attach: new_storeConfig.json]
```

### `!modify <item_ids>`
Add `preOwned: true` to specific item IDs in a storeConfig.json file.

**Usage:** 
1. Use the `!modify` command with a list of item IDs
2. Attach exactly 1 JSON file to your message (the storeConfig.json to modify)

**What it does:**
- Searches for the specified item IDs across all sections (animals, skins, hats, glasses, chests, feet, powerups)
- Adds `"preOwned": true` to each found item
- Shows which items were modified and which weren't found
- Uploads the modified config file for download

**Examples:**
```
!modify 2050,2051,2052
[Attach: storeConfig.json]
```

```
!modify 2050 2051 2052 3071 3072
[Attach: storeConfig.json]
```

### `!check_update`
Manually trigger a check for Fun Run 4 updates on Uptodown.

**Usage:**
```
!check_update
```

**What it does:**
- Checks the current version of Fun Run 4 on Uptodown
- Compares with the last known version
- Reports if there's an update available

## Automatic Monitoring

The bot automatically checks for updates every 15 minutes (configurable in `config.json`). When an update is detected:

1. 🚨 Sends an alert to the configured Discord channel
2. 📝 Shows the new version number
3. 💡 Reminds users to use `!compare` to analyze configuration changes

### Version Persistence
The bot remembers the last known version across restarts by saving it to `version_data.json`. This ensures:
- ✅ No false update notifications after bot restarts
- 🎯 Accurate update detection
- 📊 Proper version tracking history

## File Structure

```
LeakHounds Enhanced/
├── main.py              # Main bot file
├── config.json          # Bot configuration
├── requirements.txt     # Python dependencies
├── start_bot.bat        # Windows launcher script
├── README.md           # This file
├── version_data.json    # Stores last known Play Store version
├── venv/               # Virtual environment (auto-created)
├── game_data/          # Contains example storeConfig.json
│   └── storeConfig.json
└── bot.log             # Bot activity log
```

## How Config Comparison Works

The bot compares these sections in `storeConfig.json`:
- `animals` - Character animals
- `skins` - Animal skins/cosmetics
- `hats` - Hat accessories
- `glasses` - Eyewear accessories  
- `chests` - Torso clothing
- `feet` - Footwear accessories
- `powerups` - Power-up items

### Detection Types:
- **Added**: New items in the new config
- **Removed**: Items that existed in old but not new config
- **Modified**: Items that exist in both but have different properties

### Automatic Modifications:
When new items are detected, the bot automatically:
1. Creates a copy of the new configuration
2. Adds `"preOwned": true` to all newly detected items
3. Provides the modified file for download

## Example Use Case

1. Fun Run 4 releases version 2.31.0 on Uptodown
2. Bot detects the update and alerts your Discord channel
3. You extract the new `storeConfig.json` from the updated game
4. Use `!compare` with the old and new config files
5. Bot shows you exactly what new skins, animals, or items were added
6. Bot provides a modified config file with `preOwned: true` for all new items
7. You can use the modified config in your game mod/hack

## Troubleshooting

### Bot not starting?
- Check that your Discord token is correct in `config.json`
- Ensure the bot has proper permissions in your Discord server
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Update detection not working?
- The bot scrapes Uptodown web pages, which may occasionally fail
- Check the `bot.log` file for detailed error messages
- Try running `!check_update` manually to test

### File comparison errors?
- Ensure both files are valid JSON format
- Files must be named with `.json` extension
- Both files should be `storeConfig.json` structure from Fun Run 4

## Batch File Features (Windows)

The `start_bot.bat` file provides a convenient menu system:

### Menu Options:
1. **Start Bot** - Launches the Discord bot
2. **Test Update Check** - Tests Uptodown connection without starting the bot
3. **View Bot Logs** - Shows the last 50 lines of bot activity
4. **Update Dependencies** - Updates all Python packages to latest versions
5. **Exit** - Closes the launcher

### Automatic Setup:
- ✅ Creates virtual environment if needed
- 🔄 Installs/updates dependencies automatically
- ⚙️ Validates configuration before starting
- 📋 Shows current settings
- 📊 Displays system information

### Update Testing:
Use option 2 to test if the Play Store monitoring is working:
```
[SUCCESS] Found Fun Run 4 version: 2.30.0
[SUCCESS] Confirmed this is the Fun Run 4 page
```

## Configuration Options

In `config.json`:
- `check_interval_minutes`: How often to check for updates (default: 15 minutes)
- `app_package`: Google Play Store package name (default: "com.dirtybit.fire")
- `discord_token`: Your Discord bot token
- `channel_id`: Discord channel ID where notifications are sent

## Logging

The bot logs all activities to `bot.log` with rotation (keeps last 3 files, max 5MB each).
Check this file for detailed information about operations and any errors.