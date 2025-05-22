@echo off
echo ================================
echo   Starting PteroMonitore Backend
echo ================================

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Found virtual environment: venv
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo Found virtual environment: env
    call env\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Check if Redis is running (optional - comment out if you don't have Redis)
echo Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not running. Some features may not work.
    echo You can install Redis or use Docker: docker run -d -p 6379:6379 redis
    timeout /t 3 >nul
)

REM Apply database migrations
echo Applying database migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo ERROR: Failed to create migrations
    pause
    exit /b 1
)

python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations
    pause
    exit /b 1
)

REM Start services in separate windows
echo Starting Django server...
start "Django Server" cmd /k "python manage.py runserver 8000"

timeout /t 3 >nul

echo Starting Celery worker...
start "Celery Worker" cmd /k "celery -A backend worker --loglevel=info --pool=solo"

timeout /t 2 >nul

echo Starting Celery beat scheduler...
start "Celery Beat" cmd /k "celery -A backend beat --loglevel=info"

echo.
echo ================================
echo   Backend Started Successfully!
echo ================================
echo.
echo Services running:
echo   • Django API: http://localhost:8000
echo   • Admin Panel: http://localhost:8000/admin
echo   • API Documentation: http://localhost:8000/api/
echo.
echo New command windows opened for each service.
echo To stop all services, close those windows or run stop_backend.bat
echo.
pause