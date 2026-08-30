@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo          RUNPROOF QUICK START
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [1/5] Creating private Python environment...
  python -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1/5] Python environment already exists.
)

echo [2/5] Installing/updating required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" (
  echo [3/5] Creating .env from .env.example...
  copy /Y ".env.example" ".env" >nul
) else (
  echo [3/5] .env already exists.
)

echo [4/5] Checking project...
".venv\Scripts\python.exe" -m compileall -q backend
if errorlevel 1 goto :error

echo [5/5] Starting RunProof...
echo.
echo Open on this laptop: http://127.0.0.1:8000
echo For another laptop on the same Wi-Fi, open Security Center after login.
echo.
".venv\Scripts\python.exe" run.py
goto :end

:error
echo.
echo RunProof could not start. Read the error above.
pause

:end
endlocal
