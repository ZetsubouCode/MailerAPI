@echo off
setlocal EnableExtensions

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
if "%PYTHON_BIN%"=="" set "PYTHON_BIN=python"
if "%MAILER_API_PORT%"=="" set "MAILER_API_PORT=5556"

set "LOG_DIR=%ProgramData%\JIGApp\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1
set "LOG_FILE=%LOG_DIR%\mailerapi.log"
set "MAILER_MARKER=JIG_MAILER_API_SERVICE"

cd /d "%PROJECT_DIR%" || exit /b 1

where "%PYTHON_BIN%" >nul 2>&1
if errorlevel 1 if not exist "%PYTHON_BIN%" (
  >>"%LOG_FILE%" echo [%date% %time%] ERROR: Python executable not found: %PYTHON_BIN%
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$marker=[regex]::Escape($env:MAILER_MARKER); $exists=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match $marker }; if ($exists) { exit 0 } else { exit 1 }" >nul 2>&1
if "%errorlevel%"=="0" (
  >>"%LOG_FILE%" echo [%date% %time%] MailerAPI is already running; no new process started.
  exit /b 0
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$port=[int]$env:MAILER_API_PORT; $listening=Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if ($listening) { exit 0 } else { exit 1 }" >nul 2>&1
if "%errorlevel%"=="0" (
  >>"%LOG_FILE%" echo [%date% %time%] Port %MAILER_API_PORT% is already listening; no new MailerAPI process started.
  exit /b 0
)

set "MAILER_COMMAND=set JIG_MAILER_API=%MAILER_MARKER% && "%PYTHON_BIN%" -m uvicorn app.main:app --host 127.0.0.1 --port %MAILER_API_PORT% --no-server-header"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$arg='/d /c ' + $env:MAILER_COMMAND + ' >> ' + [char]34 + $env:LOG_FILE + [char]34 + ' 2>&1'; Start-Process -FilePath 'cmd.exe' -WorkingDirectory $env:PROJECT_DIR -WindowStyle Hidden -ArgumentList $arg" >nul 2>&1
set "ERR=%errorlevel%"
if "%ERR%"=="0" (
  >>"%LOG_FILE%" echo [%date% %time%] MailerAPI started in background on port %MAILER_API_PORT%.
) else (
  >>"%LOG_FILE%" echo [%date% %time%] ERROR: Failed to start MailerAPI. Code=%ERR%.
)
exit /b %ERR%
