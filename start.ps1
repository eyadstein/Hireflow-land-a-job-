$python = ".\venv\Scripts\python.exe"

Write-Host "Building frontend..." -ForegroundColor Cyan
npm run build

Write-Host "Applying migrations..." -ForegroundColor Cyan
& $python manage.py migrate

Write-Host "Starting server at http://localhost:8000" -ForegroundColor Green
& $python manage.py runserver
