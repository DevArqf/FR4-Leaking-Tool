# Build script for FR4 Leaking Tool
Write-Host "Building FR4 Leaking Tool executable..." -ForegroundColor Cyan

# Install PyInstaller if not already installed
Write-Host "`nChecking for PyInstaller..." -ForegroundColor Yellow
pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
Write-Host "`nCleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Build the executable
Write-Host "`nBuilding executable..." -ForegroundColor Green
pyinstaller FR4_Tool.spec --clean

# Check if build was successful
if (Test-Path "dist\FR4_Leaking_Tool.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable location: dist\FR4_Leaking_Tool.exe" -ForegroundColor Cyan
    Write-Host "`nCreating release folder..." -ForegroundColor Yellow
    
    # Create release folder
    $releaseFolder = "release"
    if (Test-Path $releaseFolder) { Remove-Item -Recurse -Force $releaseFolder }
    New-Item -ItemType Directory -Path $releaseFolder | Out-Null
    
    # Copy executable
    Copy-Item "dist\FR4_Leaking_Tool.exe" "$releaseFolder\" -Force
    
    # Copy config example
    Copy-Item "config.example.json" "$releaseFolder\" -Force
    
    # Create README for release
    @"
# FR4 Leaking Tool - Standalone Release

## Quick Start

1. Copy config.example.json to config.json
2. Edit config.json with your Discord bot token and channel ID
3. Run FR4_Leaking_Tool.exe

## First Time Setup

### Discord Bot Setup
1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to the "Bot" section
4. Copy the bot token
5. Paste it into config.json as "discord_token"
6. Enable these intents:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
7. Invite the bot to your server

### Configuration
Edit config.json:
```json
{
  "discord_token": "YOUR_BOT_TOKEN_HERE",
  "channel_id": "YOUR_CHANNEL_ID_HERE",
  "app_package": "com.dirtybit.fire",
  "check_interval_minutes": 15
}
```

## Features
- Monitor Fun Run 4 updates from Uptodown
- Discord notifications with @here ping
- Compare storeConfig.json files
- Modify config files (add preOwned: true)
- Auto-check every 15 minutes
- Beautiful modern GUI

Enjoy! 🎮
"@ | Out-File -FilePath "$releaseFolder\README.txt" -Encoding UTF8
    
    Write-Host "`n✓ Release folder created: $releaseFolder\" -ForegroundColor Green
    Write-Host "`nYou can now distribute the contents of the '$releaseFolder' folder!" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
