@echo off
cd /d "%~dp0"
docker compose up -d
docker compose ps

@echo off

cd /d "%~dp0\Backend"
start "FastAPI" cmd /k "call .venv\Scripts\activate && fastapi dev src\main.py

timeout /t 5 /nobreak > NUL
start http://localhost:8080
start http://127.0.0.1:8000/docs