@echo off
chcp 65001 > nul
title JsonVerify - Verificateur de dialogues
color 0A

echo ============================================
echo   JsonVerify - Verificateur de dialogues
echo   CC BY-NC-SA 4.0
echo ============================================
echo.

REM Verify Python is installed
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python n'est pas installe ou n'est pas dans le PATH
  echo         Telechargez Python depuis : https://www.python.org/downloads/
  pause
  exit /b 1
)

REM Verify Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Node.js n'est pas installe ou n'est pas dans le PATH
  echo         Telechargez Node.js depuis : https://nodejs.org/
  pause
  exit /b 1
)

echo [OK] Python et Node.js detectes
echo.

echo Lancement du backend...
start "JsonVerify - Backend (Port 8000)" cmd /c "cd /d %~dp0backend && python app.py"

timeout /t 3 /nobreak > nul

echo Lancement du frontend...
start "JsonVerify - Frontend (Port 5173)" cmd /c "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo   Application disponible sur :
echo   http://localhost:5173
echo ============================================
echo.
echo  Pour arreter, fermez les fenetres de terminal.
echo.
pause