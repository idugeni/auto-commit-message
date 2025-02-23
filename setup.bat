@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ==============================================
:: AUTO-COMMIT-MESSAGE SETUP
:: ==============================================
:: Operations:
:: 1. Verify and create target directory
:: 2. Create/verify environment configuration
:: 3. Copy all required source files
:: 4. Validate installation success
:: ==============================================

:: Configuration
set "TARGET_DIR=C:\Tools\auto-commit-message"
set "FILES_TO_COPY=main.py config.py exceptions.py models.py logging_setup.py git_manager.py ai_manager.py env_manager.py __init__.py requirements.txt .env.local"

:: Display setup information
echo.
echo ===============================================
echo            AUTO-COMMIT-MESSAGE SETUP           
echo ===============================================
echo Installation Directory: %TARGET_DIR%
echo.
echo Required Files:
echo  - Python Source Files
echo  - Configuration Files
echo  - Environment Settings
echo ===============================================
echo.

:: Directory creation and validation
if not exist "%TARGET_DIR%" (
    echo [INFO] Creating target directory...
    mkdir "%TARGET_DIR%" 2>nul
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create directory.
        echo [ERROR] Please check permissions and try again.
        pause
        exit /b 1
    )
    echo [SUCCESS] Directory created successfully.
)

:: Environment file creation
if not exist "%TARGET_DIR%\.env.local" (
    echo [INFO] Generating environment configuration...
    echo GEMINI_API_KEY=your-api-key> "%TARGET_DIR%\.env.local"
    echo [INFO] Environment file created. Please update API key.
) else (
    echo [INFO] Environment configuration exists.
)

:: File copy operation
echo [INFO] Initiating file transfer...
echo.

for %%a in (%FILES_TO_COPY%) do (
    if exist "%%a" (
        copy /Y "%%a" "%TARGET_DIR%" >nul 2>&1
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to copy %%a
        ) else (
            echo [SUCCESS] Copied: %%a
        )
    ) else (
        echo [WARNING] Source file not found: %%a
    )
)

echo.
echo [INFO] File transfer complete.
echo.

:: Post-installation options
:prompt_open_folder
set /p "OPEN_FOLDER=Would you like to open the installation directory? (Y/N): "
echo.

if /I "%OPEN_FOLDER%"=="Y" (
    start "" "%TARGET_DIR%"
    exit /b 0
) else if /I "%OPEN_FOLDER%"=="N" (
    exit /b 0
) else (
    echo [ERROR] Invalid input. Please enter Y or N.
    goto prompt_open_folder
)

endlocal
exit /b 0