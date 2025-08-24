@echo off
echo Setting up PostgreSQL database for Corporate Spending Tracker...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the setup script
python setup_postgres.py

echo.
echo Setup complete! Press any key to exit.
pause > nul
