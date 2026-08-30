@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run START_RUNPROOF.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m compileall -q backend
if errorlevel 1 (
  echo Python syntax check FAILED.
  pause
  exit /b 1
)
echo Python syntax check PASSED.
".venv\Scripts\python.exe" -c "from backend.app import app; c=app.test_client(); r=c.get('/api/health'); print('Health:',r.status_code,r.get_json())"
pause
