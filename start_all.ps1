# Start all services for Smart PFE Platform

# 1. Start Backend (Django)
Write-Host "🚀 Starting Backend (Django)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python.exe manage.py runserver"

# 2. Start AI Service (FastAPI)
Write-Host "🤖 Starting AI Service (FastAPI)..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ai-service; .\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001"

# 3. Start Frontend (React)
Write-Host "⚛️ Starting Frontend (React)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host "✅ All services initiated. Check the opened terminal windows." -ForegroundColor Green
