@echo off
cd /d "%~dp0"
if "%PYTHON_BIN%"=="" set "PYTHON_BIN=C:\Users\kigna\AppData\Local\Programs\Python\Python311\python.exe"
"%PYTHON_BIN%" -m uvicorn app.main:app --reload --no-server-header --port 5556
pause
