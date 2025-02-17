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

:: Define target directory
set "TARGET_DIR=C:\Tools\auto-commit-message"

:: Display information table (improved formatting)
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  AUTO-COMMIT-MESSAGE SETUP               ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║ This script will copy files to: %TARGET_DIR%             ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║ Files created if not exist:                              ║
echo ║   - .env.local                                           ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║ Files copied:                                            ║
echo ║   - main.py                                              ║
echo ║   - requirements.txt                                     ║
echo ║   - .env.local                                           ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║ After completion, you can open the folder.               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.


:: Check if the folder exists, if not, create it (with error handling)
if not exist "%TARGET_DIR%" (
    echo 📁 Folder not found, creating %TARGET_DIR%...
    mkdir "%TARGET_DIR%" 2>nul
    if !errorlevel! neq 0 (
        echo ❌ Failed to create directory.  Exiting.
        pause
        exit /b 1
    )
)

:: Create .env.local if it doesn't exist (more robust)
if not exist "%TARGET_DIR%\.env.local" (
    echo 🔑 Creating .env.local...
    echo GEMINI_API_KEY=your-api-key > "%TARGET_DIR%\.env.local"  REM No need for parentheses
) else (
    echo ✅ .env.local already exists, skipping creation.
)

:: Copy files to destination (with error handling and more informative output)
echo 🔄 Copying files...

set "FILES_TO_COPY=main.py requirements.txt .env.local"

for %%a in (%FILES_TO_COPY%) do (
    copy /Y "%%a" "%TARGET_DIR%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ❌ Failed to copy %%a.  Continuing...
    ) else (
      echo   - %%a copied.
    )
)

echo ✅ File copying complete.

:: Ask user whether to open the folder (improved input validation and exit)
:open_folder
set /p "openFolder=Do you want to open the folder now? (Y/N): "
echo.

if /I "%openFolder%"=="Y" (
    start "" "%TARGET_DIR%"
    exit /b 0  REM Exit after opening folder
) else if /I "%openFolder%"=="N" (
    echo.
    exit /b 0  REM Exit without opening folder
) else (
    echo ❌ Invalid input. Please enter Y or N.
    goto open_folder
)

endlocal
exit /b 0  REM Ensure script always exits with code 0