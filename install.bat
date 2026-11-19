@echo off
cd /d "%~dp0"
agy plugin install .
if %errorlevel% neq 0 (
  echo [WARN] agy CLI not found or install failed. Please ensure Antigravity CLI is installed.
  pause
  exit /b 1
)
echo [OK] ai-ops-starter installed! Please restart or open a new Antigravity window.
pause
