@echo off
setlocal
echo CourtOps Analyst Agent - One-command demo
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama is not in PATH. Please install from https://ollama.ai and ensure 'ollama' is available.
    echo Then start Ollama (e.g. run 'ollama serve' or start the Ollama app) and re-run this script.
    pause
    exit /b 1
)

echo Checking Ollama...
curl -s -o nul -w "%%{http_code}" http://localhost:11434/api/tags 2>nul | findstr /r "200" >nul 2>&1
if errorlevel 1 (
    echo Ollama does not appear to be running. Start it (e.g. 'ollama serve' or the Ollama app), then re-run.
    pause
    exit /b 1
)

echo Pulling model if missing (qwen3:8b)...
ollama pull qwen3:8b 2>nul
echo.

echo Starting Docker Compose...
docker compose up -d --build
if errorlevel 1 (
    echo Docker Compose failed.
    pause
    exit /b 1
)

echo Waiting for backend to be ready...
timeout /t 15 /nobreak >nul

echo Running seed script...
docker compose exec -T backend python -m app.seed_demo_data 2>nul
echo.

echo.
echo --- Next steps ---
echo 1. Open the app:  http://localhost:3000
echo 2. Log in:  supervisor / password
echo 3. Go to Agent Console:  http://localhost:3000/agent
echo 4. Run "daily_ops_demo" with or without dry run.
echo 5. Reports:  http://localhost:3000/reports
echo.
pause
