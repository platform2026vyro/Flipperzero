@echo off
title Flipper-Z Windows Installer
chcp 65001 >nul

echo ╔═══════════════════════════════════════════╗
echo ║     FLIPPER-Z ANDROID SAFE v3.1-safe      ║
echo ║        Windows Setup Installer             ║
echo ╚═══════════════════════════════════════════╝
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python non trovato!
    echo Scarica Python da: https://www.python.org/downloads/
    echo Assicurati di spuntare "Add Python to PATH" durante l'installazione.
    pause
    exit /b 1
)

echo [OK] Python trovato: 
python --version

:: Create virtual environment (optional)
set /p CREATE_VENV="Creare un ambiente virtuale? (s/N): "
if /i "%CREATE_VENV%"=="s" (
    echo Creazione ambiente virtuale...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtuale creato e attivato.
)

:: Install dependencies
echo.
echo Installazione dipendenze...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [WARN] Alcune dipendenze potrebbero non essere state installate.
    echo Provo a installare manualmente...
    pip install rich requests bleak
)

echo.
echo [OK] Installazione completata!
echo.
echo Per avviare Flipper-Z:
echo   python main.py
echo.
echo Oppure usa il file FLIPPER-Z.BAT (se presente)
echo.
pause
