# PowerShell script to start the auction application

# Install or update required packages
Write-Host "Installing required packages..." -ForegroundColor Green
pip install -r requirements.txt

# Initialize the database (if needed)
Write-Host "Initializing the database..." -ForegroundColor Green
python init-db.py

# Determine whether to use Flask development server or gunicorn
$useGunicorn = $false  # Change to $true to use gunicorn instead of Flask dev server

if ($useGunicorn) {
    Write-Host "Starting the application with gunicorn..." -ForegroundColor Green
    try {
        gunicorn -c gunicorn_config.py run:app
    } catch {
        Write-Host "Failed to start with gunicorn. Using Flask development server instead." -ForegroundColor Yellow
        python run.py
    }
} else {
    Write-Host "Starting the application with Flask development server..." -ForegroundColor Green
    python run.py
}

Write-Host "Server started! Press Ctrl+C to stop." -ForegroundColor Green
