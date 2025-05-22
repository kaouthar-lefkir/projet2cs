@echo off
echo ================================
echo   Stopping PteroMonitore Backend
echo ================================

REM Stop Django development server
echo Stopping Django server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Stop all Python processes related to Django
echo Stopping Django processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Django Server*" >nul 2>&1

REM Stop Celery worker processes
echo Stopping Celery worker...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Celery Worker*" >nul 2>&1

REM Stop Celery beat processes
echo Stopping Celery beat...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Celery Beat*" >nul 2>&1

REM Alternative method - kill all celery processes
taskkill /F /IM celery.exe >nul 2>&1

REM Close command windows if they exist
taskkill /F /FI "WINDOWTITLE eq Django Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Celery Worker*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Celery Beat*" >nul 2>&1

echo.
echo ================================
echo   All Backend Services Stopped!
echo ================================
echo.
pause