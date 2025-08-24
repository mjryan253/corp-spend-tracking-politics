# Corporate Spending Tracker Development Environment Launcher
Write-Host "Starting Corporate Spending Tracker Development Environment..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Start backend server in background
Write-Host "Starting backend server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python manage.py runserver" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting frontend server on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python server.py" -WindowStyle Normal

Write-Host ""
Write-Host "Development servers are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://localhost:8000/api/" -ForegroundColor Cyan
Write-Host "Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "Admin Panel: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
