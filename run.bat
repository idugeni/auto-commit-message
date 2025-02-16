@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ==============================
:: 🚀 AUTO-COMMIT-MESSAGE SETUP
:: ==============================
:: This script will:
:: 1. Create ".env.local" if it does not exist.
:: 2. Copy "main.py", "requirements.txt", and ".env.local" to "C:\Tools\auto-commit-message".
:: 3. Ask the user whether to open the folder after completion.
:: ==============================

:: Display information table
echo.
echo   ╔══════════════════════════════════════════════════════════╗
echo   ║                 AUTO-COMMIT-MESSAGE SETUP                ║
echo   ╠══════════════════════════════════════════════════════════╣
echo   ║  This script will copy files to the destination folder   ║
echo   ║  Destination : C:\Tools\auto-commit-message\             ║
echo   ╠══════════════════════════════════════════════════════════╣
echo   ║  Files created if not exist:                             ║
echo   ║    - .env.local                                          ║
echo   ╠══════════════════════════════════════════════════════════╣
echo   ║  Files copied to the destination:                        ║
echo   ║    - main.py                                             ║
echo   ║    - requirements.txt                                    ║
echo   ║    - .env.local                                          ║
echo   ╠══════════════════════════════════════════════════════════╣
echo   ║  After completion, you can open the folder.              ║
echo   ╚══════════════════════════════════════════════════════════╝
echo.

:: Ask user before proceeding
:ask
set /p proceed="Do you want to continue? (Y/N): "
if /I "%proceed%"=="Y" goto start
if /I "%proceed%"=="N" exit
echo ❌ Invalid input. Please enter Y or N.
goto ask

:: Start the process after confirmation
:start
:: Define target directory
set "TARGET_DIR=C:\Tools\auto-commit-message"

:: Check if the folder exists, if not, create it
if not exist "%TARGET_DIR%" (
    echo 📁 Folder not found, creating %TARGET_DIR%...
    mkdir "%TARGET_DIR%"
)

:: Create .env.local if it doesn't exist
if not exist "%TARGET_DIR%\.env.local" (
    echo 🔑 Creating .env.local...
    (
        echo GEMINI_API_KEY=
    ) > "%TARGET_DIR%\.env.local"
) else (
    echo ✅ .env.local already exists, skipping creation.
)

:: Copy files to destination
echo 🔄 Copying files to %TARGET_DIR%...
copy /Y main.py "%TARGET_DIR%" >nul 2>&1
copy /Y requirements.txt "%TARGET_DIR%" >nul 2>&1
copy /Y .env.local "%TARGET_DIR%" >nul 2>&1

echo ✅ All files have been successfully copied!

:: Ask user whether to open the folder
:open_folder
set /p openFolder="Do you want to open the folder now? (Y/N): "
if /I "%openFolder%"=="Y" start "" "%TARGET_DIR%"
if /I "%openFolder%"=="N" exit
echo ❌ Invalid input. Please enter Y or N.
goto open_folder

endlocal
exit
