@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo === AI Ops Starter 一键离线安装向导 (Windows) ===

set "HAS_PY=0"
python --version 2>nul | findstr /C:"Python 3." >nul && set "HAS_PY=1"
if "%HAS_PY%"=="0" (
  py -3 --version 2>nul | findstr /C:"Python 3." >nul && set "HAS_PY=1"
)
if "%HAS_PY%"=="0" (
  echo [提示] 未检测到 Python 3，Hooks 护栏需要 Python 3（可从 https://www.python.org/downloads/ 安装）。
) else (
  echo [OK] 已检测到 Python 3 环境
)

where agy >nul 2>nul
if %errorlevel%==0 (
  agy plugin install .
  if %errorlevel%==0 goto :success
)

echo [执行] 正在将插件直接安装到 %USERPROFILE%\.gemini\config\plugins\ai-ops-starter ...
set "DST=%USERPROFILE%\.gemini\config\plugins\ai-ops-starter"
if not exist "%DST%" mkdir "%DST%"
copy /Y "plugin.json" "%DST%\" >nul
copy /Y "hooks.json" "%DST%\" >nul
xcopy /E /I /Y "rules" "%DST%\rules" >nul
xcopy /E /I /Y "skills" "%DST%\skills" >nul
xcopy /E /I /Y "scripts" "%DST%\scripts" >nul

:success
echo.
echo [OK] ai-ops-starter 安装完成！请重启或新开一个 Antigravity 窗口即可生效。
pause
