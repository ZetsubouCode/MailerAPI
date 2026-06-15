@echo off
cd /d "%~dp0"
"C:\Users\Cinema III\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn app.main:app --reload --no-server-header --port 5556
pause