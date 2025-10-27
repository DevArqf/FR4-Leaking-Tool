@echo off
title Fun Run 4 Monitor Bot
color 0C

echo ====================================
echo   Fun Run 4 Monitor Bot Launcher
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo [INFO] Python detected: 
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated!
echo.

REM Check and install/update dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt --upgrade
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies are up to date!
echo.

REM Check if config file exists
if not exist "config.json" (
    echo [ERROR] config.json not found!
    echo Please make sure config.json exists with your bot token and channel ID.
    pause
    exit /b 1
)

echo [SUCCESS] Configuration file found!
echo.

REM Display current configuration
echo [INFO] Current Configuration:
python -c "import json; config=json.load(open('config.json')); print(f'  App Package: {config.get(\"app_package\", \"N/A\")}'); print(f'  Check Interval: {config.get(\"check_interval_minutes\", \"N/A\")} minutes'); print(f'  Channel ID: {config.get(\"channel_id\", \"N/A\")}')"
echo.

REM Show menu
:menu
echo ====================================
echo            MAIN MENU
echo ====================================
echo [1] Start Bot
echo [2] Test Update Check (without starting bot)
echo [3] View Bot Logs
echo [4] Update Dependencies
echo [5] Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto test_update
if "%choice%"=="3" goto view_logs
if "%choice%"=="4" goto update_deps
if "%choice%"=="5" goto exit
echo [ERROR] Invalid choice. Please enter 1-5.
echo.
goto menu

:start_bot
echo.
echo ====================================
echo        STARTING BOT
echo ====================================
echo.
echo [INFO] Starting Fun Run 4 Monitor Bot...
echo [INFO] Press Ctrl+C to stop the bot
echo.
python main.py
echo.
echo [INFO] Bot has stopped.
pause
goto menu

:test_update
echo.
echo ====================================
echo      TESTING UPDATE CHECK
echo ====================================
echo.
python test_update.py
echo.
echo [INFO] Update check test completed.
pause
goto menu

:view_logs
echo.
echo ====================================
echo          VIEWING LOGS
echo ====================================
echo.
if exist "bot.log" (
    echo [INFO] Showing last 50 lines of bot.log...
    echo.
    powershell "Get-Content bot.log -Tail 50"
) else (
    echo [INFO] No log file found. The bot hasn't been started yet.
)
echo.
pause
goto menu

:update_deps
echo.
echo ====================================
echo      UPDATING DEPENDENCIES
echo ====================================
echo.
echo [INFO] Updating all dependencies to latest versions...
pip install -r requirements.txt --upgrade
echo.
echo [SUCCESS] Dependencies updated!
pause
goto menu

:exit
echo.
echo [INFO] Deactivating virtual environment...
deactivate
echo [INFO] Goodbye!
pause
exit /b 0