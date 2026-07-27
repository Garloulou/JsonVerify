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

REM --- VÉRIFICATION & INSTALLATION BACKEND ---
if exist "%~dp0backend\requirements.txt" (
  echo [INFO] Verification des dependances Python...
  python -m pip install -r "%~dp0backend\requirements.txt" >nul 2>&1
)

REM --- VÉRIFICATION & INSTALLATION FRONTEND ---
if not exist "%~dp0frontend\node_modules\" (
  echo [INFO] Le dossier node_modules est absent. Installation des dependances npm...
  cd /d "%~dp0frontend"
  call npm install
  if errorlevel 1 (
    echo [ERROR] Echec de l'installation des dependances frontend.
    pause
    exit /b 1
  )
  cd /d "%~dp0"
  echo [OK] Dependances Frontend installees avec succes.
  echo.
)

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
