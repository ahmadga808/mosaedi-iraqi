@echo off
chcp 65001 >nul
title مساعدي العراقي
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo ثبت Python من https://www.python.org/downloads/windows/ وفعل Add Python to PATH & pause & exit /b 1)
if not exist .venv py -3 -m venv .venv
call .venv\\Scripts\\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo أنشئ مفتاحك من: https://aistudio.google.com/apikey
echo لا تشارك المفتاح ولا تضعه في ملفات الموقع.
set /p GEMINI_API_KEY=الصق مفتاح Gemini API واضغط Enter:
if "%GEMINI_API_KEY%"=="" (echo لم تدخل مفتاح API. & pause & exit /b 1)
set GEMINI_MODEL=gemini-2.5-flash
start "" http://127.0.0.1:5050
python app.py
pause
