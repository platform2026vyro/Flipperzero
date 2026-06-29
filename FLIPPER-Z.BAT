@echo off
title Flipper-Z Android SAFE v3.1-safe
chcp 65001 >nul

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python non trovato!
    echo Installa Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Try to activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Check dependencies
python -c "import rich" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Dipendenze mancanti. Esegui installer.bat prima.
    echo.
    echo Installazione rapida...
    pip install rich requests
)

:: Launch application
echo.
echo Avvio Flipper-Z...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Il programma e' terminato con errore %errorlevel%.
    pause
)
