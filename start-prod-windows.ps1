# PowerShell script to start production server on Windows

# First check if we can use gunicorn
$canUseGunicorn = $true
try {
    gunicorn --version | Out-Null
} catch {
    $canUseGunicorn = $false
    Write-Host "Gunicorn not available on Windows. Will use waitress instead." -ForegroundColor Yellow
    pip install waitress
}

# Install required packages
Write-Host "Installing required packages..." -ForegroundColor Green
pip install -r requirements.txt

# Initialize database if needed
Write-Host "Initializing database..." -ForegroundColor Green
python init-db.py

# Set production port
$env:PORT = "10000"

if ($canUseGunicorn) {
    Write-Host "Starting server with gunicorn on port $env:PORT..." -ForegroundColor Green
    gunicorn -c gunicorn_config.py run:app
} else {
    Write-Host "Starting server with waitress on port $env:PORT..." -ForegroundColor Green
    python -c "from waitress import serve; from run import app; serve(app, host='0.0.0.0', port=10000, threads=4, connection_limit=1000, channel_timeout=300)"
}

Write-Host "Server started on port $env:PORT!" -ForegroundColor Green
