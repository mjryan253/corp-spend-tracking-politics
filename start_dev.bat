@echo off
echo Starting Corporate Spending Tracker Development Environment...
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\Activate.bat

REM Start backend server in background
echo Starting backend server on port 8000...
start "Backend Server" cmd /k "cd backend && python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend server
echo Starting frontend server on port 3000...
start "Frontend Server" cmd /k "cd frontend && python server.py"

echo.
echo Development servers are starting...
echo.
echo Backend API: http://localhost:8000/api/
echo Frontend:    http://localhost:3000
echo Admin Panel: http://localhost:8000/admin/
echo.
echo Press any key to exit this launcher...
pause > nul
